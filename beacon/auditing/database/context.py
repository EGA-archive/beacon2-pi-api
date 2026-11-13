from contextvars import ContextVar

_CURRENT_AUDIT = ContextVar(
    "beacon_current_audit",
    default=None
)