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
        self.status=404
        self.message=message

class NoFiltersAllowed(AppError):
    def __init__(self, message):
        self.status=400
        self.message=message

class InvalidData(AppError):
    def __init__(self, message):
        self.status=422
        self.message=message