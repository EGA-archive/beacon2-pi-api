from functools import wraps

from beacon.logs.logs import log_with_args
from beacon.conf.conf_override import config

from beacon.auditing.context import AuditContext


def audit_check(func):

    @log_with_args(config.level)
    @wraps(func)
    async def wrapper(self, *args, **kwargs):

        audit = await AuditContext.from_handler(
            self,
            config
        )

        self.audit = audit

        try:

            audit.add_execution_event(
                event="function_started",
                function=func.__name__
            )

            result = await func(self, *args, **kwargs)

            audit.capture_identity(self)

            audit.add_execution_event(
                event="function_completed",
                function=func.__name__
            )

            audit.finalize(status="success")

            return result

        except Exception as exc:

            audit.capture_identity(self)

            audit.set_error(
                error_type=type(exc).__name__,
                message=str(exc)
            )

            audit.finalize(status="error")

            raise

        finally:

            audit.capture_identity(self)
            audit.capture_authorization(self)

            audit_data = audit.serialize()

            self.LOG.warning(audit_data)

    return wrapper