# Base exception for all application-specific errors
# Provides a unified structure: HTTP-like status + message payload
class AppError(Exception):
    def __init__(self, message):
        # Default status is unset unless overridden by subclass
        self.status = None

        # Human-readable or API-facing error description
        self.message = message


# 400-level error: request is structurally valid but logically inconsistent
# Example: conflicting parameters or invalid combinations in request payload
class IncoherenceInRequestError(AppError):
    def __init__(self, message):
        self.status = 400  # Bad Request
        self.message = message


# Generic invalid request error (syntactic or semantic issues)
# Typically used when request cannot be processed as-is
class InvalidRequest(AppError):
    def __init__(self, message):
        self.status = 400  # Bad Request
        self.message = message


# Raised when the URL path does not match any known route
# Usually indicates malformed or unsupported endpoint usage
class WrongURIPath(AppError):
    def __init__(self, message):
        self.status = 400  # Bad Request
        self.message = message


# Raised when query filtering is explicitly disallowed by API rules
# Used for endpoints that enforce fixed query structures
class NoFiltersAllowed(AppError):
    def __init__(self, message):
        self.status = 400  # Bad Request
        self.message = message


# Validation error for structured payloads (schema mismatch, missing fields, etc.)
# Commonly maps to HTTP 422 Unprocessable Entity
class InvalidData(AppError):
    def __init__(self, message):
        self.status = 422  # Semantic validation failure
        self.message = message


# Authentication/authorization failure
# Indicates missing or invalid credentials or insufficient permissions
class NoPermissionsAvailable(AppError):
    def __init__(self, message):
        self.status = 401  # Unauthorized
        self.message = message


# Service-level failure indicating backend infrastructure is unavailable
# Typically used for database outages or connection failures
class DatabaseIsDown(AppError):
    def __init__(self, message):
        self.status = 503  # Service Unavailable
        self.message = message


# Resource lookup failure where expected file/data is missing
# Note: uses 503 here, though often mapped to 404 in REST conventions
class FileNotFound(AppError):
    def __init__(self, message):
        self.status = 503
        self.message = message


# Business rule violation: no datasets exist matching request criteria
# Used when query succeeds structurally but returns no valid data sources
class NoDatasetsFound(AppError):
    def __init__(self, message):
        self.status = 400  # Bad Request (domain-specific choice)
        self.message = message


# Rate limiting / quota enforcement error
# Triggered when user exceeds allowed number of queries in a time window
class NumberOfQueriesExceeded(AppError):
    def __init__(self, message):
        self.status = 429  # Too Many Requests
        self.message = message