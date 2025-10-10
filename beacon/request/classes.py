from strenum import StrEnum
import aiohttp.web as web

class Granularity(StrEnum):
    BOOLEAN = "boolean",
    COUNT = "count",
    RECORD = "record"

class ErrorClass:
    def __init__(self) -> None: #       
            self.error_message=None
            self.error_code=None

    def handle_exception(self, exception, message):
        try:
            if message==None:
                self.error_message = type(exception).__name__
            else:
                self.error_message = message
            # Això és del tipus web.HTTPException? i posar status
            if exception == web.HTTPException:
                self.error_code = exception.status
            elif exception == web.HTTPBadRequest:
                self.error_code = 400
            elif exception == web.HTTPUnauthorized:
                self.error_code = 401
            elif exception == web.HTTPTooManyRequests:
                self.error_code = 429
            elif exception == NotImplementedError:
                self.error_code = 501
            elif exception == OSError:
                self.error_code = 507
            elif exception in [AssertionError,AttributeError,EOFError,FloatingPointError,GeneratorExit,ImportError,ModuleNotFoundError,IndexError,KeyError,KeyboardInterrupt,
                            MemoryError,NameError,OverflowError,RecursionError,ReferenceError,RuntimeError,StopIteration,StopAsyncIteration,SyntaxError,IndentationError,
                            TabError,SystemError,SystemExit,TypeError,UnboundLocalError,UnicodeError,UnicodeEncodeError,UnicodeDecodeError,UnicodeTranslateError,
                            ValueError,ZeroDivisionError]:
                self.error_code = 500
            else:
                self.error_code = 500
        except Exception:
            self.error_message = 'unknown error'
            self.error_code = 500

    def return_message(self):
        return self.error_message

    def return_code(self):
        return self.error_code

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