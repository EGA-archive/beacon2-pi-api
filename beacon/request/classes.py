from strenum import StrEnum
import aiohttp.web as web

class Granularity(StrEnum):
    BOOLEAN = "boolean",
    COUNT = "count",
    RECORD = "record"

class ErrorClass():
    def __init__(self) -> None: #       
        self.error_message=None
        self.error_code=None

    def handle_exception(self, exception):
        try:
            if self.error_message==None:
                self.error_message = type(exception).__name__
            if exception == web.HTTPBadRequest:
                    self.error_code = 400
            elif exception == web.HTTPUnauthorized:
                    self.error_code = 401
            elif exception == web.HTTPPaymentRequired:
                    self.error_code = 402
            elif exception == web.HTTPForbidden:
                    self.error_code = 403
            elif exception == web.HTTPNotFound:
                    self.error_code = 404
            elif exception == web.HTTPMethodNotAllowed:
                    self.error_code = 405
            elif exception == web.HTTPNotAcceptable:
                    self.error_code = 406
            elif exception == web.HTTPProxyAuthenticationRequired:
                    self.error_code = 407
            elif exception == web.HTTPRequestTimeout:
                    self.error_code = 408
            elif exception == web.HTTPConflict:
                    self.error_code = 409
            elif exception == web.HTTPGone:
                    self.error_code = 410
            elif exception == web.HTTPLengthRequired:
                    self.error_code = 411
            elif exception == web.HTTPPreconditionFailed:
                    self.error_code = 412
            elif exception == web.HTTPRequestEntityTooLarge:
                    self.error_code = 413
            elif exception == web.HTTPRequestURITooLong:
                    self.error_code = 414
            elif exception == web.HTTPUnsupportedMediaType:
                    self.error_code = 415
            elif exception == web.HTTPRequestRangeNotSatisfiable:
                    self.error_code = 416
            elif exception == web.HTTPExpectationFailed:
                    self.error_code= 417
            elif exception == web.HTTPMisdirectedRequest:
                    self.error_code = 421
            elif exception == web.HTTPUnprocessableEntity:
                    self.error_code = 422
            elif exception == web.HTTPFailedDependency:
                    self.error_code = 424
            elif exception == web.HTTPUpgradeRequired:
                    self.error_code = 426
            elif exception == web.HTTPPreconditionRequired:
                    self.error_code = 428
            elif exception == web.HTTPTooManyRequests:
                    self.error_code = 429
            elif exception == web.HTTPRequestHeaderFieldsTooLarge:
                    self.error_code = 431
            elif exception == web.HTTPUnavailableForLegalReasons:
                    self.error_code = 451
            elif exception == web.HTTPInternalServerError:
                    self.error_code = 500
            elif exception == web.HTTPNotImplemented:
                    self.error_code = 501
            elif exception == web.HTTPBadGateway:
                    self.error_code = 502
            elif exception == web.HTTPServiceUnavailable:
                    self.error_code = 503
            elif exception == web.HTTPGatewayTimeout:
                    self.error_code = 504
            elif exception == web.HTTPVersionNotSupported:
                    self.error_code = 505
            elif exception == web.HTTPVariantAlsoNegotiates:
                    self.error_codee = 506
            elif exception == web.HTTPInsufficientStorage:
                    self.error_code = 507
            elif exception == web.HTTPNotExtended:
                    self.error_code = 510
            elif exception == web.HTTPNetworkAuthenticationRequired:
                    self.error_code = 511
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
        return self.error_code, self.error_message

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