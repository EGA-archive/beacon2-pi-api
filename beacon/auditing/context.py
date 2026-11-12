
import hashlib

from uuid import uuid4
from datetime import datetime, timezone
from urllib.parse import parse_qsl
from time import perf_counter

from beacon.auditing.models import AuditModel
import json


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
                "previous_query_count": None,
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
                "git_commit": None,
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

        await audit.capture_request(
            handler.request,
            handler.request_attributes,
            config
        )

        audit.capture_configuration(
            handler,
            config
        )

        audit.capture_budget(config)

        return audit


    async def capture_request(
        self,
        request,
        request_attributes,
        config
    ):

        query_parameters = dict(
            parse_qsl(
                request.query_string,
                keep_blank_values=True
            )
        )

        headers = {
            key: (
                "[REDACTED]" #TODO: what parts can be stored instead of REDACTED
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

        http_version = (
            f"{request.version.major}."
            f"{request.version.minor}"
        )

        self.update_request(
            method=request.method,
            path=request.path_qs,
            route=(
                config.uri_subpath + "/"
                + request_attributes.entry_type
            ),
            path_parameters={},
            query_parameters=query_parameters,
            headers=headers,
            http_version=http_version, #TODO: don't write 2 times the code for storing things in audit

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
            database=config.query_budget_database,
            db_name=config.query_budget_db_name,
            table=config.query_budget_table,
            decision=(
                "not_evaluated"
                if enabled
                else "not_applicable"
            ),
            reason=None
        )

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

    def update_database(self, **kwargs):

        self.data.database = self._update_model(
            self.data.database,
            **kwargs
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

    def update_runtime(self, **kwargs):

        self.data.runtime = self._update_model(
            self.data.runtime,
            **kwargs
        )

    def finalize(self, status: str):

        if self._finalized:
            return

        self.data.status = status

        self.data.completed_at = datetime.now(timezone.utc)

        self.data.duration_ms = round(
            (perf_counter() - self._started) * 1000,
            2
        )

        self._finalized = True

    def serialize(self):

        return self.data.model_dump(mode="json")
