from functools import wraps
from inspect import iscoroutinefunction

from beacon.auditing.database.context import _CURRENT_AUDIT


def audit_database(func):

    if iscoroutinefunction(func):

        @wraps(func)
        async def async_wrapper(self, *args, **kwargs):

            audit = getattr(self, "audit", None)

            if audit is None:
                return await func(self, *args, **kwargs)

            token = _CURRENT_AUDIT.set(audit)

            try:
                return await func(self, *args, **kwargs)

            finally:
                _CURRENT_AUDIT.reset(token)

        return async_wrapper

    @wraps(func)
    def sync_wrapper(self, *args, **kwargs):

        audit = getattr(self, "audit", None)

        if audit is None:
            return func(self, *args, **kwargs)

        token = _CURRENT_AUDIT.set(audit)

        try:
            return func(self, *args, **kwargs)

        finally:
            _CURRENT_AUDIT.reset(token)

    return sync_wrapper