from beacon.auditing.context_vars import current_audit
from functools import wraps
from inspect import iscoroutinefunction


def audit_event(event_name):

    def decorator(func):

        if iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args, **kwargs):

                audit = current_audit.get()

                if audit is None:
                    return await func(*args, **kwargs)

                event_id = audit.add_execution_event(
                    event=event_name,
                    function=func.__name__
                )

                try:
                    result = await func(*args, **kwargs)

                    audit.complete_execution_event(
                        event_id,
                        status="success"
                    )

                    return result

                except Exception as exc:

                    audit.complete_execution_event(
                        event_id,
                        status="failed",
                        error_type=type(exc).__name__
                    )

                    raise

            return async_wrapper

        @wraps(func)
        def sync_wrapper(*args, **kwargs):

            audit = current_audit.get()

            if audit is None:
                return func(*args, **kwargs)

            event_id = audit.add_execution_event(
                event=event_name,
                function=func.__name__
            )

            try:
                result = func(*args, **kwargs)

                audit.complete_execution_event(
                    event_id,
                    status="success"
                )

                return result

            except Exception as exc:

                audit.complete_execution_event(
                    event_id,
                    status="failed",
                    error_type=type(exc).__name__
                )

                raise

        return sync_wrapper

    return decorator