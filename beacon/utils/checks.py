from beacon.utils.modules import check_database_connections
from beacon.request.classes import RequestAttributes
from beacon.logs.logs import log_with_args
from beacon.conf.conf_override import config

def state_check(func):
    @log_with_args(config.level)
    async def state_check(self, *args, **kwargs):
        await check_database_connections(LOG=self.LOG, entry_type=RequestAttributes.entry_type, pre_entry_type=RequestAttributes.pre_entry_type)
        return await func(self, *args, **kwargs)
    return state_check