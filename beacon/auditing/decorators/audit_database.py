from functools import wraps
from inspect import iscoroutinefunction

from beacon.auditing.database.context import _CURRENT_AUDIT


def audit_database(func):
    """
    Decorator that propagates the current audit context to database
    operations, allowing database activity to be associated with
    the HTTP request that initiated it.

    Supports both synchronous and asynchronous functions.

    The decorator:

        - Retrieves the audit context from the instance's audit
          attribute.
        - Checks whether an audit context is available.
        - If available, sets the _CURRENT_AUDIT ContextVar so that
          database operations can access the current audit context.
        - Executes the original function.
        - Resets the ContextVar after execution, restoring its
          previous value.

    If no audit context is available, the original function
    executes normally without database auditing.

    ContextVar tokens ensure that the previous context is restored
    correctly, preventing audit context from leaking between
    independent operations or requests.

    The decorator preserves the original function's metadata
    through functools.wraps.
    """

    # Check whether the decorated function is asynchronous
    # to select the appropriate wrapper.
    if iscoroutinefunction(func):

        @wraps(func)
        async def async_wrapper(self, *args, **kwargs):

            # Retrieve the audit context associated with the instance.
            audit = getattr(self, "audit", None)

            # Execute normally if no audit context is available.
            if audit is None:
                return await func(self, *args, **kwargs)

            # Set the current audit context for database operations.
            token = _CURRENT_AUDIT.set(audit)

            try:
                # Execute the original asynchronous function.
                return await func(self, *args, **kwargs)

            finally:
                # Restore the previous audit context after execution,
                # even if the function raises an exception.
                _CURRENT_AUDIT.reset(token)

        return async_wrapper

    @wraps(func)
    def sync_wrapper(self, *args, **kwargs):

        # Retrieve the audit context associated with the instance.
        audit = getattr(self, "audit", None)

        # Execute normally if no audit context is available.
        if audit is None:
            return func(self, *args, **kwargs)

        # Set the current audit context for database operations.
        token = _CURRENT_AUDIT.set(audit)

        try:
            # Execute the original synchronous function.
            return func(self, *args, **kwargs)

        finally:
            # Restore the previous audit context after execution,
            # even if the function raises an exception.
            _CURRENT_AUDIT.reset(token)

    return sync_wrapper