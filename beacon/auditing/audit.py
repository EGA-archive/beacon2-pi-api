
from functools import wraps
from aiohttp import web

from beacon.logs.logs import log_with_args
from beacon.conf.conf_override import config
from beacon.auditing.context import AuditContext
from beacon.auditing.context import current_audit, current_handler


def audit_trace(func):

    @log_with_args(config.level)
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        request_attributes = getattr(
            self,
            "request_attributes",
            None
        )

        audit = await AuditContext.from_handler(
            self,
            config
        )

        self.audit = audit

        audit_token = current_audit.set(audit)
        handler_token = current_handler.set(self)

        event_id = audit.add_execution_event(
            event="http_request",
            function=func.__name__
        )

        status = "interrupted"

        try:

            result = await func(self, *args, **kwargs)

            # Enrich audit with attributes populated during request processing.
            audit.enrich_from_handler(
                self,
                config
            )


            if isinstance(result, web.Response):

                audit.capture_response(result)

                if result.status < 400:
                    status = "completed"
                elif result.status < 500:
                    status = "rejected"
                else:
                    status = "failed"

            audit.complete_execution_event(
                event_id,
                status="success"
            )

            return result

        except Exception as exc:

            audit.set_error(
                error_type=type(exc).__name__,
                message=str(exc),
                stage="execution"
            )

            audit.complete_execution_event(
                event_id,
                status="failed",
                error_type=type(exc).__name__
            )

            status = "failed"

            raise

        finally:
            # Capture whatever request attributes were successfully populated.
            audit.enrich_from_handler(
                self,
                config
            )

            try:
                audit.capture_identity(self)
                audit.capture_authorization(self)

                audit.finalize(status=status)

                # Obtain the hash of the preceding audit record.
                previous_hash = None  # Retrieve this from persistent storage.

                # Calculate the current record hash.
                audit.prepare_integrity(
                    previous_record_hash=previous_hash
                )

                try:

                    # TODO: Create persist_audit and update_audit_status functions to make the serlaziation persistence and update the persistence_status
                    #await persist_audit(audit.serialize())

                    #await update_audit_status(audit.data.audit_id,"success")

                    audit.data.integrity.persistence_status = "success"

                except Exception as exc:

                    audit.data.integrity.persistence_status = "failed"

                    #await update_audit_status(audit.data.audit_id,"failed")

                    self.LOG.error(
                        "Failed to persist audit record: %s",
                        exc
                    )

            finally:
                current_handler.reset(handler_token)
                current_audit.reset(audit_token)


    return wrapper
