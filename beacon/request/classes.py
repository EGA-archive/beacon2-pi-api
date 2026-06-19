from strenum import StrEnum
from humps.main import camelize
import warnings

warnings.filterwarnings("ignore", category=UserWarning)
from pydantic import BaseModel

class CamelModel(BaseModel, extra='forbid'):
    """Generic class that allows others to read the same attributes and not repeat the settings again"""
    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True

class IncludeResultsetResponses(StrEnum):
    """Class to keep the determine the different type of possible responses to be returned"""
    ALL = "ALL",
    HIT = "HIT",
    MISS = "MISS",
    NONE = "NONE"

class Similarity(StrEnum):
    """Class to keep the precision of the closeness of terms that need to be added as similar to the one being searched"""
    EXACT = "exact",
    HIGH = "high",
    MEDIUM = "medium",
    LOW = "low"

class Operator(StrEnum):
    """Class to keep the different comparison signs for alphanumeric filters"""
    EQUAL = "=",
    LESS = "<",
    GREATER = ">",
    NOT = "!",
    LESS_EQUAL = "<=",
    GREATER_EQUAL = ">="

class Granularity(StrEnum):
    """Class to keep the three possible typs of granularity"""
    BOOLEAN = "boolean",
    COUNT = "count",
    RECORD = "record"

class RequestAttributes():
    def __init__(self) -> None:
        # ip from the request client
        self.ip=None
        # headers in the request (e.g. authorization token...)
        self.headers=None 
        # the entry type for the returning response
        self.entry_type=None
        # the internal id requested if there is one (e.g. entry_type/{id})
        self.entry_id=None
        # in case of a cross query, the entry type where the {id} is taken from
        self.pre_entry_type=None
        # database where the returning entry type is stored
        self.source=None
        # the maximum granularity allowed for the returning entry type
        self.allowed_granularity=None
        # the name of a single record of the returning entry type (e.g. individual for individuals)
        self.entry_type_id=None
        # the query parameters collected from the request
        self.qparams=None
        # the type of response (resultSet or not: countresponse, booleanresponse)
        self.response_type=None
        # the granularity returned: record, count or boolean
        self.returned_granularity=None
        # The framework version
        self.returned_apiVersion="v2.2.0"
        # The returned schema values
        self.returned_schema=None
        # The connection to mongo needed to be used for the query
        self.mongo_collection=None
        # Initialize the variable for the function needed to be executed for the query
        self.function=None
        # Initialize the variable for the client string needed to perform the database connection
        self.client=None