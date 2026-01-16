import logging
import time
from beacon.conf.conf_override import config
from typing import Optional

def initialize_logger(level):
    # Start the logger
    LOG = logging.getLogger(__name__)
    # Remove pre-existing default handlers
    for handler in LOG.handlers[:]:
        LOG.removeHandler(handler)
    # Avoid loggers to set as default
    LOG.propagate = False
    # Apply desired level of logs
    LOG.setLevel(level)
    # Conver the times to timestamp depending on your area
    formatter = logging.Formatter(
        '%(levelname)s - %(asctime)sZ - %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S'
    )
    formatter.converter = time.gmtime
    # Choose which type of logs you want (in a file or in stream)
    if config.log_file:
        handler = logging.FileHandler(config.log_file)
    else:
        handler = logging.StreamHandler()
    # Set the same lavel and format to the handlers
    handler.setLevel(level)
    handler.setFormatter(formatter)
    # Add handler to the logger
    LOG.addHandler(handler)
    return LOG

LOG = initialize_logger(config.level)

# LOGS per iniciar i parar el contenidor (INFO)
# LOGS per he rebut una request i retorno una response (INFO)
# Tota la resta per DEBUG

# Acabar de fer els unit tests
# Formular l'exception bubbling --> mirar qui controla el tall de connexions per netejar que no quedi cap connexió ni procés obert
# Crear graceful shutdown amb missatge de LOG body + status dins de l'exception bubbling a cada capa
# Auditing -> registre de accions que s'han fet i que es guardin
# DTO entre classe i classe quan es retorna un objecte 

def log_with_args_check_configuration(level):
    def add_logging(func):
        def wrapper(*args, **kwargs):
            try:
                # Store the initial time before the function is executed
                start = time.time()
                # Initialize the logger
                LOG = initialize_logger(level)
                # Execute the function and log when is initiated
                result = func(*args, **kwargs)
                LOG.debug(f"{result} - {func.__name__} - initial call")
                # Store the final time after the function is executed and log when ends
                finish = time.time()
                LOG.debug(f"{result} - {func.__name__}- {finish-start} - returned OK")
                # Specific hard-coded logs for the initialize and shutting down of the app
                if f"{func.__name__}" == 'initialize':
                    LOG.info(f"{result} - Initialization done")
                elif f"{func.__name__}" == 'destroy':
                    LOG.info(f"{result} - Shutting down")
                return result
            except:
                # Catch and log the error of the exception in case there is one for the funcion adding the function's name
                err = "There was an exception in  "
                err += func.__name__
                LOG.error(f"check_configuration - {err}")
                raise
        return wrapper
    return add_logging

def log_with_args_initial(level):
    def add_logging(func):
        def wrapper(self, *args, **kwargs):
            try:
                # Store the initial time before the function is executed
                start = time.time()
                # Initialize the logger
                LOG = initialize_logger(level)
                result = func(self, *args, **kwargs)
                LOG.debug(f"{result} - {func.__name__} - initial call")
                # Store the final time after the function is executed and log when ends
                finish = time.time()
                LOG.debug(f"{result} - {func.__name__}- {finish-start} - returned OK")
                # Specific hard-coded logs for the initialize and shutting down of the app
                if f"{func.__name__}" == 'initialize':
                    LOG.info(f"{result} - Initialization done")
                elif f"{func.__name__}" == 'destroy':
                    LOG.info(f"{result} - Shutting down")
                return result
            except:
                # Catch and log the error of the exception in case there is one for the funcion adding the function's name
                err = "There was an exception in  "
                err += func.__name__
                LOG.error(f"{result} - {err}")
                raise
        return wrapper
    return add_logging

def log_with_args(level):
    def add_logging(func):
        def wrapper(self, *args, **kwargs):
            try:
                # Store the initial time before the function is executed
                start = time.time()
                # Initialize the logger
                LOG = initialize_logger(level)
                LOG.debug(f"{self._id} - {func.__name__} - initial call")
                result = func(self, *args, **kwargs)
                # Store the final time after the function is executed and log when ends
                finish = time.time()
                LOG.debug(f"{self._id} - {func.__name__} - {finish-start} - returned OK")
                # Specific hard-coded logs for the initialize and shutting down of the app
                if f"{func.__name__}" == 'initialize':
                    LOG.info(f"{self._id} - Initialization done")
                elif f"{func.__name__}" == 'destroy':
                    LOG.info(f"{self._id} - Shutting down")
                return result
            except:
                # Catch and log the error of the exception in case there is one for the funcion adding the function's name
                err = "There was an exception in  "
                err += func.__name__
                LOG.error(f"{self._id} - {err}")
                raise
        return wrapper
    return add_logging

def log_with_args_mongo(level):
    def add_logging(func):
        def wrapper(self, *args, **kwargs):
            try:
                # Store the initial time before the function is executed
                start = time.time()
                # Initialize the logger
                LOG = initialize_logger(level)
                LOG.debug(f"{self._id} - {func.__name__} - initial call")
                result = func(self, *args, **kwargs)
                # Store the final time after the function is executed and log when ends
                finish = time.time()
                LOG.debug(f"{self._id} - {func.__name__} - {finish-start} - returned OK")
                # Specific hard-coded logs for the initialize and shutting down of the app
                if f"{func.__name__}" == 'initialize':
                    LOG.info(f"{self._id} - Initialization done")
                elif f"{func.__name__}" == 'destroy':
                    LOG.info(f"{self._id} - Shutting down")
                return result
            except Exception:
                # Catch and log the error of the exception in case there is one for the funcion adding the function's name
                err = "There was an exception in  "
                err += func.__name__
                LOG.error(f"{self._id} - {err}")
                raise
        return wrapper
    return add_logging
    