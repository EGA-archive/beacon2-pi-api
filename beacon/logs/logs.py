import logging
import time
from beacon.conf.conf import level
from beacon.conf.conf import log_file
from typing import Optional
import os

LOG = logging.getLogger(__name__)
fmt = '%(levelname)s - %(asctime)s - %(message)s'
formatter = logging.Formatter(fmt)

if log_file:
    fh = logging.FileHandler(log_file)
    fh.setLevel(level)
    fh.setFormatter(formatter)
    LOG.addHandler(fh)
else:
    sh = logging.StreamHandler()
    sh.setLevel(level)
    sh.setFormatter(formatter)
    LOG.addHandler(sh)

if len(LOG.handlers) > 0:
    # Remove the first handler
    LOG.removeHandler(LOG.handlers[0])

# LOGS per iniciar i parar el contenidor (INFO)
# LOGS per he rebut una request i retorno una response (INFO)
# Tota la resta per DEBUG

# Acabar de fer els unit tests
# Formular l'exception bubbling --> mirar qui controla el tall de connexions per netejar que no quedi cap connexió ni procés obert
# Crear graceful shutdown amb missatge de LOG body + status dins de l'exception bubbling a cada capa
# Auditing -> registre de accions que s'han fet i que es guardin
# DTO entre classe i classe quan es retorna un objecte 

def log_with_args_initial(level):
    def add_logging(func):
        def wrapper(self, *args, **kwargs):
            try:
                start = time.time()
                logging.basicConfig(format=fmt, level=level)
                result = func(self, *args, **kwargs)
                LOG.debug(f"{result} - {func.__name__} - initial call")
                finish = time.time()
                LOG.debug(f"{result} - {func.__name__}- {finish-start} - returned OK")
                if f"{func.__name__}" == 'initialize':
                    LOG.info(f"{result} - Initialization done")# pragma: no cover
                elif f"{func.__name__}" == 'destroy':
                    LOG.info(f"{result} - Shutting down")# pragma: no cover
                return result
            except:# pragma: no cover
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
                start = time.time()
                logging.basicConfig(format=fmt, level=level)
                LOG.debug(f"{self._id} - {func.__name__} - initial call")
                result = func(self, *args, **kwargs)
                finish = time.time()
                LOG.debug(f"{self._id} - {func.__name__} - {finish-start} - returned OK")
                if f"{func.__name__}" == 'initialize':
                    LOG.info(f"{self._id} - Initialization done")# pragma: no cover
                elif f"{func.__name__}" == 'destroy':
                    LOG.info(f"{self._id} - Shutting down")# pragma: no cover
                return result
            except:
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
                start = time.time()
                logging.basicConfig(format=fmt, level=level)
                LOG.debug(f"{self._id} - {func.__name__} - initial call")
                result = func(self, *args, **kwargs)
                finish = time.time()
                LOG.debug(f"{self._id} - {func.__name__} - {finish-start} - returned OK")
                if f"{func.__name__}" == 'initialize':
                    LOG.info(f"{self._id} - Initialization done")# pragma: no cover
                elif f"{func.__name__}" == 'destroy':
                    LOG.info(f"{self._id} - Shutting down")# pragma: no cover
                return result
            except Exception:# pragma: no cover
                err = "There was an exception in  "
                err += func.__name__
                LOG.error(f"{self._id} - {err}")
                raise
        return wrapper
    return add_logging
    