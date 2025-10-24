from strenum import StrEnum
import aiohttp.web as web

class Granularity(StrEnum):
    BOOLEAN = "boolean",
    COUNT = "count",
    RECORD = "record"

class RequestAttributes():
    def __init__(self) -> None:
        self.ip=None # ip from the request client
        self.headers=None # headers in the request (e.g. authorization token...)
        self.entry_type=None # the entry type for the returning response
        self.entry_id=None # the internal id requested if there is one (e.g. entry_type/{id})
        self.pre_entry_type=None # in case of a cross query, the entry type where the {id} is taken from
        self.source=None # database where the returning entry type is stored
        self.allowed_granularity=None # the maximum granularity allowed for the returning entry type
        self.entry_type_id=None # the name of a single record of the returning entry type (e.g. individual for individuals)
        self.qparams=None # the query parameters collected from the request
        self.response_type=None # the type of response (resultSet or not: countresponse, booleanresponse)
        self.returned_granularity=None # the granularity returned: record, count or boolean
        self.returned_apiVersion="v2.0.0"
        self.returned_schema=None
        self.mongo_collection=None