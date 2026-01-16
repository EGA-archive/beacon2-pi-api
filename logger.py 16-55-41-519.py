import logging
import time
from beacon.conf.conf_override import config
from typing import Optional

LOG = logging.getLogger(__name__)
formatter = logging.Formatter(
    '%(levelname)s - %(asctime)sZ - %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)
formatter.converter = time.gmtime
sh = logging.StreamHandler()
sh.setFormatter(formatter)
LOG.addHandler(sh)
print(time.gmtime())

LOG.warning('hola')