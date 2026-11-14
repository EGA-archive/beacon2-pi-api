
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

    SENSITIVE_QUERY_PARAMETERS = {
        "token",
        "access_token",
        "refresh_token",
        "api_key",
        "apikey",
        "secret",
        "client_secret",
        "password",
        "authorization",
    }

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
            },

            semantic_actions=[]
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
        """
        Generate AuditContext class per request and capture the parts of the context that already can be populated when doing so.
        """

        # Initialize class with transaction id
        audit = cls(request_id=handler._id)

        # Capture raw HTTP request information.
        await audit.capture_request(handler.request)

        # Capture configuration that is available at initialization.
        audit.capture_budget(config)
        audit.capture_runtime(config)

        return audit

    def enrich_from_handler(self, handler, config):
        """
        After deconstruct_request happens, which comes after the creation of the context class, enrich the context class with the request_attributes and configuration from request parsing.
        """

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

    @staticmethod
    def fingerprint_value(value):
        """
        Method to hash the values that are sensitive to be stored and this way it can be reutilized.
        """

        digest = hashlib.sha256(
            str(value).encode("utf-8")
        ).hexdigest()

        return f"sha256:{digest}"

    @classmethod
    def sanitize_query_value(cls, key, value):
        """
        In case any parameter is sensitive to be shown, this method masks it and grabs the initial 3 letters or just *** in case the variable is shorter than 3.
        """

        if key.casefold() in cls.SENSITIVE_QUERY_PARAMETERS:

            value = str(value)

            return {
                "present": True,
                "masked": (
                    value[:2] + "***"
                    if len(value) > 2
                    else "***"
                )
            }

        return value

    async def capture_request(self, request):
        """
        Get all the values to audit from the request object received.
        """
        #Get a dictionary of all parameters that come by the query string.
        query_parameters = dict(
            parse_qsl(
                request.query_string,
                keep_blank_values=True
            )
        )
        # The values that are sensitive, mask them.
        query_parameters = {
            key: self.sanitize_query_value(key, value)
            for key, value in query_parameters.items()
        }

        # Mask the headers values as well in case they are sensitive.
        headers = {
            key: self.sanitize_query_value(key, value) if key.lower() in self.SENSITIVE_HEADERS else value
            for key, value in request.headers.items()
        }

        # Check if request has body and initialize the variables.
        body_present = request.has_body
        body_size = 0
        body_content_hash = None

        # If the request has body, store the length of the body as string and then hash the body string.
        if body_present:
            raw_body = await request.read()

            body_size = len(raw_body)

            if raw_body:
                body_content_hash = self.fingerprint_value(raw_body)


        # Insert the request values processed and others grab them from request straight away.
        self.update_request(
            method=request.method,
            path=request.path_qs, # TODO: Check that parameters are not stored here.
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
        # Insert the incoming args in the request part of the auditing
        self.data.request = self._update_model(
            self.data.request,
            **kwargs
        )

    def update_identity(self, **kwargs):
        # Add identity to the auditing context
        self.data.identity = self._update_model(
            self.data.identity,
            **kwargs
        )

    def update_authorization(self, **kwargs):
        # Add authorization to the auditing context
        self.data.authorization = self._update_model(
            self.data.authorization,
            **kwargs
        )

    def capture_configuration(self, handler, config):
        # Get the request_attributes generated for the current request
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

        # Hash the snapshot of the configuration
        fingerprint = self.fingerprint_value(canonical)

        # Update the configuration with the snapshot and the hash aside
        self.update_configuration(
            **snapshot,
            configuration_fingerprint=fingerprint
        )

    def update_configuration(self, **kwargs):
        # Add configuration to the auditing context
        self.data.configuration = self._update_model(
            self.data.configuration,
            **kwargs
        )

    def capture_budget(self, config):
        # Collect budget enabling variables
        per_user = config.query_budget_per_user
        per_ip = config.query_budget_per_ip
        # State if budget is enabled or not
        enabled = per_user or per_ip
        # Set the scope of budget
        if per_user and per_ip:
            scope = "user_and_ip"
        elif per_user:
            scope = "user"
        elif per_ip:
            scope = "ip"
        else:
            scope = None
        # Add budget to the auditing context
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
        """
        Method to determine which is the budget strategy configured and what is the current situation of the available budget.
        """
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
        # Insert budget to the auditing context.
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
        """
        Method to add all the events that happen during a request processing to the auditing context.
        """
        event_name = name or event or "unknown"

        details = {}

        if function:
            details["function"] = function

        details.update(kwargs)
        # Get the current events already in the auditing context
        events = list(self.data.execution.events)

        sequence = len(events)

        now = datetime.now(timezone.utc)
        # Initialize data context for the event to populate
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

        # In case an event hasn't finished, add the time where the event is added. Otherwise, add the time as completed.
        if status == "started":
            self._event_timers[sequence] = perf_counter()
        else:
            event_data["completed_at"] = now

        # Update the list of events
        events.append(event_data)

        # Insert the event to the context
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
        """
        Method to state that an event has finished
        """

        # Collect the current list of events from execution
        events = list(self.data.execution.events)

        # In case the number of the sequence is already parsed, don't do anything.
        if sequence >= len(events):
            return

        # Grab the sequence event from execution in auditing context
        event = events[sequence]

        if event.sequence != sequence:
            return

        # Add the timers of completion to the event
        completed_at = datetime.now(timezone.utc)

        started = self._event_timers.pop(sequence, None)

        duration_ms = (
            round((perf_counter() - started) * 1000, 2)
            if started is not None
            else None
        )


        # Update the event while validating it
        updated_event = event.model_copy(
            update={
                "status": status,
                "completed_at": completed_at,
                "duration_ms": duration_ms,
                "error_type": error_type
            }
        )

        events[sequence] = updated_event

        # Update execution to auditing context
        self.data.execution = self._update_model(
            self.data.execution,
            events=events
        )

    def record_database_operation(self, operation):
        """
        Record an individual database operation in a thread-safe
        temporary collection.

        Operations are accumulated in memory and transferred to the
        audit model during finalization, avoiding direct modifications
        to the audit model from concurrent database operations.
        """
        with self._database_lock:
            self._database_operations.append(operation)

    def update_database(self, **kwargs):
        """
        Update the database section of the audit record.

        Allows partial updates to database auditing information,
        such as selected connections and health checks, while
        preserving existing values and validating the updated
        data against the Pydantic model.
        """
        self.data.database = self._update_model(
            self.data.database,
            **kwargs
        )

    def capture_effective_granularity(self, response_data):
        """
        Determine the effective granularity of each dataset based
        on the data actually returned in the API response.

        The function inspects the response resultSets and identifies
        the granularity according to the returned content:

            - record:   Individual records were returned.
            - count:    Only the number of records was returned.
            - boolean:  Only a boolean existence result was returned.

        It then matches each result set to its corresponding dataset
        in the authorization decisions and updates its
        effective_granularity field.

        This allows the audit record to distinguish between the
        granularity requested, the maximum granularity authorized,
        and the granularity actually disclosed by the API.
        """

        result_sets = (
            response_data
            .get("response", {})
            .get("resultSets", [])
        )

        decisions = self.data.authorization.decisions

        # Build a mapping between dataset IDs and their actual
        # returned granularity.
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

        # Update each authorization decision with the granularity
        # observed in the actual API response.
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

        # Validate and store the updated authorization information.
        self.data.authorization = self._update_model(
            self.data.authorization,
            decisions=updated_decisions
        )

    def capture_response(self, response):
        # Get the response the API returned to the client
        body = response.body

        response_data = {}

        # Serialize the response into json
        if body and response.content_type == "application/json":

            try:
                response_data = json.loads(body)

            except (json.JSONDecodeError, UnicodeDecodeError):
                response_data = {}

        # In case the response had resultSets, capture the effective granularity returned
        if response_data.get("response", {}).get("resultSets"):

            self.capture_effective_granularity(
                response_data
            )

        meta = response_data.get("meta", {})
        summary = response_data.get("responseSummary", {})

        response_type = None

        # Set the response type depending on if response was splitted per dataset or not
        if "resultSets" in response_data:
            response_type = "resultSet"

        elif "exists" in summary:
            response_type = "boolean"

        elif "totalCount" in summary:
            response_type = "count"

        returned_schemas = meta.get("returnedSchemas", [])

        # Insert response to the auditing context
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
        # Insert response to the auditing context
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
        # Populat the error of the auditing context
        self.data.error = {
            "type": error_type,
            "stage": stage,
            "message": message,
            **kwargs
        }

    def capture_runtime(self, config):
        """
        Collect runtime and deployment information about the API
        instance processing the current request.

        Captures the execution environment, application version,
        hostname, process ID, Python version and current application
        state.

        The application version is extracted from the configuration.
        If api_version_yaml is a dictionary, its 'api_version' field
        is used instead of storing the entire dictionary.

        The collected information is passed to update_runtime()
        to be stored in the audit record.
        """

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
        """
        Update the runtime section of the audit record.

        Supports partial updates to runtime information while
        preserving existing values and validating the updated
        data against the corresponding Pydantic model.
        """

        self.data.runtime = self._update_model(
            self.data.runtime,
            **kwargs
        )


    def set_action(
        self,
        name,
        category,
        target=None,
        attributes=None
    ):
        """
        Initialize the semantic action associated with the current request.
        """

        self.update_action(
            name=name,
            category=category,
            target=target,
            attributes=attributes or {},
            outcome="pending"
        )

    def record_semantic_action(self, action):
        """
        Append a secondary semantic event to the current audit record.
        """

        self.data.semantic_actions.append(action)

    def update_action(self, **kwargs):
        """
        Update the semantic action associated with the current audit record.

        Allows decorators and other application components to define
        the action being performed, its target, outcome and context.
        """

        self.data.action = self._update_model(
            self.data.action,
            **kwargs
        )



    def calculate_record_hash(self):
        """
        Calculate a SHA-256 hash of the audit record to guarantee
        its integrity and allow subsequent detection of modifications.

        The audit record is first converted into a JSON-compatible
        dictionary. The integrity fields 'record_hash' and
        'persistence_status' are excluded from the hash calculation
        because they are either the hash itself or persistence
        metadata that may change after the record is created.

        The remaining data is serialized into canonical JSON:
            - Keys are sorted alphabetically.
            - Unnecessary whitespace is removed.
            - UTF-8 characters are preserved.
            - NaN and Infinity values are rejected.

        The canonical JSON is then passed to fingerprint_value()
        to generate the final cryptographic hash.

        Returns:
            str: The calculated hash of the audit record.
        """

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

        digest = self.fingerprint_value(canonical)

        return digest


    def prepare_integrity(self, previous_record_hash=None):
        """
        Prepare the integrity information before persisting an audit
        record.

        Stores the hash of the previous audit record to establish a
        cryptographic chain between consecutive audit records.

        Clears any existing record hash and calculates a new hash
        using the current audit contents, including the previous
        record hash.

        The resulting hash is stored in the audit record and returned
        for persistence.

        Args:
            previous_record_hash (str | None): Hash of the previous
                audit record in the chain.

        Returns:
            str: The newly calculated record hash.
        """

        self.data.integrity.previous_record_hash = (
            previous_record_hash
        )

        self.data.integrity.record_hash = None

        record_hash = self.calculate_record_hash()

        self.data.integrity.record_hash = record_hash

        return record_hash


    def verify_integrity(self):
        """
        Verify that the current audit record has not been modified
        since its hash was originally calculated.

        Retrieves the stored record hash and independently
        recalculates the hash using the current audit contents.

        If the stored hash is missing, verification fails.

        Returns:
            bool: True if the calculated hash matches the stored
            hash, otherwise False.
        """

        stored_hash = self.data.integrity.record_hash

        if not stored_hash:
            return False

        calculated_hash = self.calculate_record_hash()

        return stored_hash == calculated_hash


    @staticmethod
    def verify_chain_link(previous_record, current_record):
        """
        Verify the cryptographic link between two consecutive
        audit records.

        Compares the record hash of the previous audit record
        against the previous_record_hash stored in the current
        audit record.

        This allows detection of broken links in the audit chain,
        indicating that a record may have been removed, replaced
        or disconnected from the sequence.

        Args:
            previous_record: The preceding audit record.
            current_record: The audit record being verified.

        Returns:
            bool: True if the chain link is valid, otherwise False.
        """

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
