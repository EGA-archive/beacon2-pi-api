import sys
import traceback
import aiohttp.web as web
from typing import Optional

class HandleException():
    def __init__(self) -> None:
        self.status=None
        self.output=None 
    """
    def handle_exception(self, exception, message=None):
        try:
            self.output = "{}: {}".format(type(exception).__name__, exception if not message else message)
            if exception == web.HTTPBadRequest:
                self.status = 404
            elif type(exception).__name__ == "ValidationError":
                self.status = 404
            elif exception == NotImplementedError:
                self.status = 501
            elif exception == OSError:
                self.status = 507
            elif exception in [AssertionError,AttributeError,EOFError,FloatingPointError,GeneratorExit,ImportError,ModuleNotFoundError,IndexError,KeyError,KeyboardInterrupt,
                                    MemoryError,NameError,OverflowError,RecursionError,ReferenceError,RuntimeError,StopIteration,StopAsyncIteration,SyntaxError,IndentationError,
                                    TabError,SystemError,SystemExit,TypeError,UnboundLocalError,UnicodeError,UnicodeEncodeError,UnicodeDecodeError,UnicodeTranslateError,
                                    ValueError,ZeroDivisionError]:
                self.status = 500
            else:
                self.status = 500
        except Exception:
            self.output = 'yesss'
            self.status = 300
    """