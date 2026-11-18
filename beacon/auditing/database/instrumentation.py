import threading

from pymongo.monitoring import CommandListener

from beacon.auditing.database.context import _CURRENT_AUDIT
from beacon.auditing.database.fingerprints import query_fingerprint


class MongoAuditListener(CommandListener):

    READ_OPERATIONS = {
        "find",
        "aggregate",
        "getMore",
        "count",
        "distinct"
    }

    def __init__(self):

        self._pending = {}
        self._lock = threading.Lock()

    @staticmethod
    def _get_collection(command_name, command):

        value = command.get(command_name)

        if isinstance(value, str):
            return value

        return None

    @staticmethod
    def _get_records_returned(reply):

        if not isinstance(reply, dict):
            return None

        count = 0

        for key in ("firstBatch", "nextBatch"):

            batch = reply.get("cursor", {}).get(key)

            if isinstance(batch, list):
                count += len(batch)

        if count:
            return count

        return reply.get("n")

    @staticmethod
    def _get_error_type(failure):

        if isinstance(failure, Exception):
            return type(failure).__name__

        if isinstance(failure, dict):
            return failure.get("codeName") or "MongoDBError"

        return "MongoDBError"

    @staticmethod
    def _get_status(failure):

        error_name = (
            type(failure).__name__
            if isinstance(failure, Exception)
            else ""
        )

        if "Timeout" in error_name:
            return "timeout"

        return "failed"

    def started(self, event):

        audit = _CURRENT_AUDIT.get()

        if audit is None:
            return

        # Ignore MongoDB internal connection and authentication commands.
        if event.command_name in {
            "hello",
            "isMaster",
            "saslStart",
            "saslContinue",
            "authenticate",
            "getnonce",
            "ping"
        }:
            return

        thread_id = threading.get_ident()

        key = (
            thread_id,
            event.request_id
        )

        command = event.command

        operation = event.command_name

        collection = self._get_collection(
            operation,
            command
        )

        fingerprint = query_fingerprint(command)

        with self._lock:

            self._pending[key] = {
                "audit": audit,
                "connection": str(event.connection_id),
                "operation": operation,
                "collection": collection,
                "query_fingerprint": fingerprint,
            }

    def succeeded(self, event):

        self._complete(
            event,
            status="success",
            failure=None
        )

    def failed(self, event):

        self._complete(
            event,
            status=self._get_status(event.failure),
            failure=event.failure
        )

    def _complete(
        self,
        event,
        status,
        failure
    ):

        thread_id = threading.get_ident()

        key = (
            thread_id,
            event.request_id
        )

        with self._lock:
            operation_data = self._pending.pop(
                key,
                None
            )

        if operation_data is None:
            return

        # Calculate execution duration.
        duration_ms = round(
            event.duration_micros / 1000,
            2
        )

        # Retrieve the MongoDB response.
        reply = getattr(event, "reply", None)

        # Only collect returned records for read operations.
        records_returned = None

        if (
            status == "success"
            and operation_data["operation"] in self.READ_OPERATIONS
        ):
            records_returned = self._get_records_returned(
                reply
            )

        # Build the database audit event.
        operation = {
            "connection": operation_data["connection"],
            "operation": operation_data["operation"],
            "collection": operation_data["collection"],
            "query_fingerprint": operation_data["query_fingerprint"],
            "status": status,
            "duration_ms": duration_ms,
            "records_returned": records_returned,
            "retry_count": 0,
            "error_type": (
                self._get_error_type(failure)
                if failure is not None
                else None
            )
        }

        # Append the event to the associated audit context.
        operation_data["audit"].record_database_operation(
            operation
        )

    def close(self):

        with self._lock:
            self._pending.clear()


MONGO_AUDIT_LISTENER = MongoAuditListener()