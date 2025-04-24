from strenum import StrEnum

class Granularity(StrEnum):
    BOOLEAN = "boolean",
    COUNT = "count",
    RECORD = "record"

class ErrorClass():
    def __init__(self) -> None:# pragma: no cover
        self.error_message=None
        self.error_code=None