
import uuid
from beacon.logs.logs import log_with_args_initial
from beacon.conf.conf import level

@log_with_args_initial(level)
def generate_txid(self):
    # Generate a unique id and get the first 9 characters to show it in the logs as the transaction id.
    uniqueid = uuid.uuid4()
    uniqueid = str(uniqueid)[0:8]
    return uniqueid
