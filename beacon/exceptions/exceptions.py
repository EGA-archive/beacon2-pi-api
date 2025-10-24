class AppError(Exception):
    def __init__(self, message):
        self.status=None
        self.message=message

class IncoherenceInRequestError(AppError):
    def __init__(self, message):
        self.status=400
        self.message=message

class InvalidRequest(AppError):
    def __init__(self, message):
        self.status=400
        self.message=message

class WrongURIPath(AppError):
    def __init__(self, message):
        self.status=400
        self.message=message

class NoFiltersAllowed(AppError):
    def __init__(self, message):
        self.status=400
        self.message=message

class InvalidData(AppError):
    def __init__(self, message):
        self.status=422
        self.message=message

class NoPermissionsAvailable(AppError):
    def __init__(self, message):
        self.status=401
        self.message=message

class DatabaseIsDown(AppError):
    def __init__(self, message):
        self.status=503
        self.message=message

class FileNotFound(AppError):
    def __init__(self, message):
        self.status=503
        self.message=message

class NoDatasetsFound(AppError):
    def __init__(self, message):
        self.status=400
        self.message=message

class NumberOfQueriesExceeded(AppError):
    def __init__(self, message):
        self.status=429
        self.message=message