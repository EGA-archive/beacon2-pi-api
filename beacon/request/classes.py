from strenum import StrEnum

class Granularity(StrEnum):
    BOOLEAN = "boolean",
    COUNT = "count",
    RECORD = "record"

class ErrorClass():
    def __init__(self) -> None:# pragma: no cover
        self.error_message=None
        self.error_code=None

class RequestAttributes():
    def __init__(self) -> None:# pragma: no cover, explicar cada component què significa i una explicació del que és la classe
        self.ip=None
        self.headers=None
        self.entry_type=None
        self.entry_id=None
        self.pre_entry_type=None # root? base?
        self.source=None # database del entry type
        self.allowed_granularity=None
        self.entry_type_id=None