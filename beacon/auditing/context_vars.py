from contextvars import ContextVar

current_audit = ContextVar("beacon_current_audit", default=None)
current_handler = ContextVar("beacon_current_handler", default=None)