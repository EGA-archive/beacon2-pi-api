
import hashlib

from uuid import uuid4
from datetime import datetime, timezone
from urllib.parse import parse_qsl
from time import perf_counter

from beacon.auditing.models import AuditModel
import json

import threading

import socket

import os

import platform
from contextvars import ContextVar

current_audit = ContextVar(
    "current_audit",
    default=None
)

current_handler = ContextVar(
    "current_handler",
    default=None
)


class AuditContext:

    SENSITIVE_HEADERS = {
        "authorization",
        "cookie",
        "set-cookie",
        "x-api-key",
        "proxy-authorization",
    }

    def __init__(self, request_id: str):

        self._started = perf_counter()
        self._finalized = False

        self.data = AuditModel(
            audit_schema_version="1.0.0",
            audit_id=str(uuid4()),
            request_id=request_id,

            status="in_progress",
            started_at=datetime.now(timezone.utc),
            completed_at=None,
            duration_ms=None,

            request={
                "method": "",
                "path": "",
                "route": None,
                "path_parameters": {},
                "query_parameters": {},
                "headers": {},
                "http_version": None,
                "client": {
                    "ip": None,
                    "user_agent": None
                },
                "body": {
                    "present": False,
                    "size_bytes": 0,
                    "content_hash": None
                }
            },

            identity={
                "authenticated": None,
                "user_id": None,
                "authentication_method": None,
                "authentication_status": "not_attempted"
            },

            authorization={
                "requested_datasets": [],
                "authorized_datasets": [],
                "rejected_datasets": [],
                "decisions": []
            },

            configuration={
                "api_version": None,
                "requested_schema": [],
                "returned_schema": [],
                "entry_type": None,
                "pre_entry_type": None,
                "source": None,
                "response_type": None,
                "test_mode": False,
                "configuration_fingerprint": None
            },

            budget={
                "enabled": False,
                "scope": None,
                "period_seconds": None,
                "maximum_queries": None,
                "previous_query_counts": {
                    "user": None,
                    "ip": None
                },
                "decision": "not_evaluated",
                "reason": None
            },

            database={
                "connections_selected": [],
                "health_checks": [],
                "operations": []
            },

            execution={
                "events": []
            },

            response={
                "status_code": None,
                "response_type": None,
                "exists": None,
                "total_results": None,
                "returned_results": None,
                "returned_granularity": None,
                "returned_schemas": [],
                "size_bytes": None,
                "validation_status": "not_attempted",
                "serialization_status": "not_attempted"
            },

            error=None,

            runtime={
                "environment": None,
                "application_version": None,
                "instance_id": None,
                "process_id": None,
                "python_version": None,
                "application_state": None
            },

            integrity={
                "persistence_status": "pending",
                "record_hash": None,
                "previous_record_hash": None
            }
        )

        self._event_timers = {}

        # Database auditing state
        self._database_lock = threading.Lock()
        self._database_operations = []
        self._database_health_checks = []
        self._database_connections = []

    @staticmethod
    def _update_model(model, **kwargs):
        """
        Update a nested Pydantic model while preserving
        validation.
        """

        current = model.model_dump()

        current.update(kwargs)

        return type(model).model_validate(current)

    @classmethod
    async def from_handler(cls, handler, config):

        audit = cls(request_id=handler._id)

        # Capture raw HTTP request information.
        await audit.capture_request(handler.request)

        # Capture configuration that is available at initialization.
        audit.capture_budget(config)
        audit.capture_runtime(config)

        return audit

    def enrich_from_handler(self, handler, config):

        # Capture parsed request attributes.
        self.update_request(
            route=(
                config.uri_subpath + "/"
                + handler.request_attributes.entry_type
                if handler.request_attributes.entry_type
                else None
            )
        )

        # Capture configuration derived from request parsing.
        self.capture_configuration(handler, config)

    def capture_request_attributes(
        self,
        request_attributes,
        config
    ):

        self.update_request(
            route=(
                config.uri_subpath + "/"
                + request_attributes.entry_type
                if request_attributes.entry_type
                else None
            ),
            path_parameters={
                # Populate these if your router exposes them.
            }
        )

    async def capture_request(self, request):

        query_parameters = dict(
            parse_qsl(
                request.query_string,
                keep_blank_values=True
            )
        )

        headers = {
            key: (
                "[REDACTED]"
                if key.lower() in self.SENSITIVE_HEADERS
                else value
            )
            for key, value in request.headers.items()
        }

        body_present = request.has_body
        body_size = 0
        body_content_hash = None

        if body_present:
            raw_body = await request.read()

            body_size = len(raw_body)

            if raw_body:
                body_content_hash = hashlib.sha256(
                    raw_body
                ).hexdigest()

        self.update_request(
            method=request.method,
            path=request.path_qs,
            query_parameters=query_parameters,
            headers=headers,
            http_version=(
                f"{request.version.major}."
                f"{request.version.minor}"
            ),
            client={
                "ip": request.remote,
                "user_agent": request.headers.get("User-Agent")
            },
            body={
                "present": body_present,
                "size_bytes": body_size,
                "content_hash": body_content_hash
            }
        )

    def update_request(self, **kwargs):

        self.data.request = self._update_model(
            self.data.request,
            **kwargs
        )

    def capture_identity(self, handler):

        identity = getattr(
            handler,
            "request_context",
            {}
        ).get("identity")

        if identity:
            self.update_identity(**identity)

    def update_identity(self, **kwargs):

        if kwargs.get("authentication_status") == "failure":
            kwargs["authentication_status"] = "failed"

        self.data.identity = self._update_model(
            self.data.identity,
            **kwargs
        )

    def capture_authorization(self, handler):

        authorization = getattr(
            handler,
            "request_context",
            {}
        ).get("authorization")

        if authorization:
            self.update_authorization(**authorization)

    def update_authorization(self, **kwargs):

        self.data.authorization = self._update_model(
            self.data.authorization,
            **kwargs
        )

    def capture_configuration(self, handler, config):

        request_attributes = handler.request_attributes

        # Extract only configuration relevant to auditing.
        snapshot = {
            "api_version": config.api_version,
            "source": request_attributes.source,
            "test_mode": request_attributes.qparams.query.testMode,
            "entry_type": request_attributes.entry_type,
            "requested_schema": request_attributes.qparams.meta.requestedSchemas,
            "returned_schema": request_attributes.returned_schema, # TODO: Check what happens with returned_schema in case of an error
            "response_type": request_attributes.response_type,
            "pre_entry_type": getattr(
                request_attributes,
                "pre_entry_type",
                None
            ),
        }

        # Generate deterministic JSON.
        canonical = json.dumps(
            snapshot,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False
        )

        fingerprint = hashlib.sha256(
            canonical.encode("utf-8")
        ).hexdigest()

        self.update_configuration(
            **snapshot,
            configuration_fingerprint=f"sha256:{fingerprint}"
        )

    def update_configuration(self, **kwargs):

        self.data.configuration = self._update_model(
            self.data.configuration,
            **kwargs
        )

    def capture_budget(self, config):

        per_user = config.query_budget_per_user
        per_ip = config.query_budget_per_ip

        enabled = per_user or per_ip

        if per_user and per_ip:
            scope = "user_and_ip"
        elif per_user:
            scope = "user"
        elif per_ip:
            scope = "ip"
        else:
            scope = None

        self.update_budget(
            enabled=enabled,
            scope=scope,
            period_seconds=config.query_budget_time_in_seconds,
            maximum_queries=config.query_budget_amount,
            previous_query_counts={
                "user": None,
                "ip": None
            },
            decision=(
                "not_evaluated"
                if enabled
                else "not_applicable"
            ),
            reason=None
        )


    def capture_budget_decision(
        self,
        enabled: bool,
        scope: str | None = None,
        period_seconds: int | None = None,
        maximum_queries: int | None = None,
        previous_query_counts: dict | None = None,
        decision: str = "not_evaluated",
        reason: str | None = None
    ):
        self.data.budget.enabled = enabled
        self.data.budget.scope = scope
        self.data.budget.period_seconds = period_seconds
        self.data.budget.maximum_queries = maximum_queries

        self.data.budget.previous_query_counts = (
            previous_query_counts
            if previous_query_counts is not None
            else {"user": None, "ip": None}
        )

        self.data.budget.decision = decision
        self.data.budget.reason = reason


    def update_budget(self, **kwargs):

        self.data.budget = self._update_model(
            self.data.budget,
            **kwargs
        )


    def add_execution_event(
        self,
        event=None,
        function=None,
        name=None,
        status="started",
        **kwargs
    ):

        event_name = name or event or "unknown"

        details = {}

        if function:
            details["function"] = function

        details.update(kwargs)

        events = list(self.data.execution.events)

        sequence = len(events)

        now = datetime.now(timezone.utc)

        event_data = {
            "sequence": sequence,
            "name": event_name,
            "status": status,
            "started_at": now,
            "completed_at": None,
            "duration_ms": None,
            "details": details,
            "error_type": None
        }

        if status == "started":
            self._event_timers[sequence] = perf_counter()
        else:
            event_data["completed_at"] = now

        events.append(event_data)

        self.data.execution = self._update_model(
            self.data.execution,
            events=events
        )

        return sequence

    def complete_execution_event(
        self,
        sequence,
        status="success",
        error_type=None
    ):

        events = list(self.data.execution.events)

        if sequence >= len(events):
            return

        event = events[sequence]

        if event.sequence != sequence:
            return

        completed_at = datetime.now(timezone.utc)

        started = self._event_timers.pop(sequence, None)

        duration_ms = (
            round((perf_counter() - started) * 1000, 2)
            if started is not None
            else None
        )

        updated_event = event.model_copy(
            update={
                "status": status,
                "completed_at": completed_at,
                "duration_ms": duration_ms,
                "error_type": error_type
            }
        )

        events[sequence] = updated_event

        self.data.execution = self._update_model(
            self.data.execution,
            events=events
        )

    def record_database_operation(self, operation):

        with self._database_lock:
            self._database_operations.append(operation)

    def update_database(self, **kwargs):

        self.data.database = self._update_model(
            self.data.database,
            **kwargs
        )

    def capture_effective_granularity(self, response_data):

        result_sets = (
            response_data
            .get("response", {})
            .get("resultSets", [])
        )

        decisions = self.data.authorization.decisions

        effective_granularities = {
            result["id"]: (
                "record"
                if result.get("results") is not None
                else "count"
                if result.get("resultsCount") is not None
                else "boolean"
            )
            for result in result_sets
        }

        updated_decisions = []

        for decision in decisions:

            effective = effective_granularities.get(
                decision.dataset
            )

            updated_decisions.append(
                decision.model_copy(
                    update={
                        "effective_granularity": effective
                    }
                )
            )

        self.data.authorization = self._update_model(
            self.data.authorization,
            decisions=updated_decisions
        )

    def capture_response(self, response):

        body = response.body

        response_data = {}

        if body and response.content_type == "application/json":

            try:
                response_data = json.loads(body)

            except (json.JSONDecodeError, UnicodeDecodeError):
                response_data = {}

        if response_data.get("response", {}).get("resultSets"):

            self.capture_effective_granularity(
                response_data
            )

        meta = response_data.get("meta", {})
        summary = response_data.get("responseSummary", {})

        response_type = None

        if "resultSets" in response_data:
            response_type = "resultSet"

        elif "exists" in summary:
            response_type = "boolean"

        elif "totalCount" in summary:
            response_type = "count"

        returned_schemas = meta.get("returnedSchemas", [])

        self.update_response(
            status_code=response.status,
            response_type=response_type,
            exists=summary.get("exists"),
            total_results=summary.get("totalCount"),
            returned_granularity=meta.get("returnedGranularity"),
            returned_schemas=returned_schemas,
            size_bytes=(
                len(body)
                if body is not None
                else None
            ),
            serialization_status="success"
        )


    def update_response(self, **kwargs):

        self.data.response = self._update_model(
            self.data.response,
            **kwargs
        )

    def set_error(
        self,
        error_type,
        stage="execution",
        message=None,
        **kwargs
    ):

        self.data.error = {
            "type": error_type,
            "stage": stage,
            "message": message,
            **kwargs
        }

    def capture_runtime(self, config):

        application_version = config.api_version_yaml

        if isinstance(application_version, dict):
            application_version = application_version.get("api_version")

        self.update_runtime(
            environment=config.environment,
            application_version=application_version,
            instance_id=socket.gethostname(),
            process_id=os.getpid(),
            python_version=platform.python_version(),
            application_state="running"
        )

    def update_runtime(self, **kwargs):

        self.data.runtime = self._update_model(
            self.data.runtime,
            **kwargs
        )

    def calculate_record_hash(self):

        payload = self.data.model_dump(mode="json")

        integrity = payload.get("integrity", {})

        # Exclude fields that are not part of the immutable audit content.
        integrity.pop("record_hash", None)
        integrity.pop("persistence_status", None)

        canonical = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False
        )

        digest = hashlib.sha256(
            canonical.encode("utf-8")
        ).hexdigest()

        return f"sha256:{digest}"

    def prepare_integrity(self, previous_record_hash=None):

        self.data.integrity.previous_record_hash = (
            previous_record_hash
        )

        self.data.integrity.record_hash = None

        record_hash = self.calculate_record_hash()

        self.data.integrity.record_hash = record_hash

        return record_hash

    def verify_integrity(self):

        stored_hash = self.data.integrity.record_hash

        if not stored_hash:
            return False

        calculated_hash = self.calculate_record_hash()

        return stored_hash == calculated_hash

    def verify_chain_link(previous_record, current_record):

        expected_previous_hash = (
            previous_record.integrity.record_hash
        )

        actual_previous_hash = (
            current_record.integrity.previous_record_hash
        )

        return expected_previous_hash == actual_previous_hash

    def finalize(self, status: str):

        if self._finalized:
            return

        # Transfer database operations into the audit model.
        with self._database_lock:

            operations = list(
                self._database_operations
            )

        self.data.database = self._update_model(
            self.data.database,
            operations=operations
        )

        # Finalize the audit record.
        self.data.status = status

        self.data.completed_at = datetime.now(timezone.utc)

        self.data.duration_ms = round(
            (perf_counter() - self._started) * 1000,
            2
        )

        self._finalized = True

    def serialize(self):

        return self.data.model_dump(mode="json")
