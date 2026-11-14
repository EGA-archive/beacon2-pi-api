
from functools import wraps
from aiohttp import web

from beacon.logs.logs import log_with_args
from beacon.conf.conf_override import config

from beacon.auditing.context import (
    AuditContext,
    current_audit,
    current_handler
)

from beacon.auditing.actions import SemanticActionResolver
from beacon.auditing.models import Action, Target, Outcome

def audit_trace(func):

    @log_with_args(config.level)
    @wraps(func)
    async def wrapper(self, *args, **kwargs):

        # Create the audit context using the current request handler.
        audit = await AuditContext.from_handler(
            self,
            config
        )

        # Attach the audit context to the handler.
        self.audit = audit

        # Set the audit and handler contexts so that other decorators
        # and application components can access them during execution.
        audit_token = current_audit.set(audit)
        handler_token = current_handler.set(self)

        # Resolve the semantic action associated with this HTTP request.
        # Resolve the semantic action associated with this HTTP request.
        try:

            resolver = SemanticActionResolver(
                uri_subpath=config.uri_subpath
            )

            action = resolver.resolve(
                self.request.path,
                outcome=Outcome.pending
            )

            audit.record_semantic_action(action)

        except Exception as exc:

            self.LOG.warning(
                "Could not resolve semantic action: %s",
                exc
            )

        # Register the beginning of the HTTP request execution.
        event_id = audit.add_execution_event(
            event="http_request",
            function=func.__name__
        )

        status = "interrupted"

        try:

            # Execute the original HTTP handler.
            result = await func(self, *args, **kwargs)

            # Enrich the audit with attributes populated during
            # request processing.
            audit.enrich_from_handler(
                self,
                config
            )

            # Capture the HTTP response and determine its outcome.
            if isinstance(result, web.Response):

                audit.capture_response(result)

                if result.status < 400:
                    status = "completed"

                elif result.status < 500:
                    status = "rejected"

                else:
                    status = "failed"

            # Mark the HTTP request execution event as successful.
            audit.complete_execution_event(
                event_id,
                status="success"
            )

            return result

        except Exception as exc:

            # Capture the exception in the audit context.
            audit.set_error(
                error_type=type(exc).__name__,
                message=str(exc),
                stage="execution"
            )

            # Mark the HTTP request execution event as failed.
            audit.complete_execution_event(
                event_id,
                status="failed",
                error_type=type(exc).__name__
            )

            status = "failed"

            raise

        finally:

            # Capture any request attributes populated before
            # the request completed or failed.
            audit.enrich_from_handler(
                self,
                config
            )

            try:

                # Finalize the audit record by setting its final
                # execution status and completion information.
                audit.finalize(
                    status=status
                )

                # Log the audit record for diagnostic purposes.
                self.LOG.warning(
                    audit.serialize()
                )

                # Obtain the hash of the preceding audit record.
                previous_hash = None
                # TODO: Retrieve this from persistent storage.

                # Calculate the current audit record hash and
                # establish its link to the preceding record.
                audit.prepare_integrity(
                    previous_record_hash=previous_hash
                )

                # Persistence has not yet been implemented.
                # Keep the status pending until actual persistence.
                audit.data.integrity.persistence_status = "pending"

                try:

                    # TODO: Persist the serialized audit record.
                    # await persist_audit(audit.serialize())

                    # TODO: Update the persistence status after
                    # successful persistence.
                    # await update_audit_status(
                    #     audit.data.audit_id,
                    #     "success"
                    # )

                    pass

                except Exception as exc:

                    audit.data.integrity.persistence_status = "failed"

                    self.LOG.error(
                        "Failed to persist audit record: %s",
                        exc
                    )

                    # TODO: Update the persistence status in storage.
                    # await update_audit_status(
                    #     audit.data.audit_id,
                    #     "failed"
                    # )

            finally:

                # Restore the previous context variables to avoid
                # leaking audit information into other requests.
                current_handler.reset(handler_token)
                current_audit.reset(audit_token)

    return wrapper
