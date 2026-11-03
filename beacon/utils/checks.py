from beacon.logs.logs import log_with_args
from beacon.conf.conf_override import config
from beacon.utils.database_health import (
    get_cached_connections,
    check_selected_database_connections,
)

def state_check(func):
    @log_with_args(config.level)
    async def wrapper(self, *args, **kwargs):

        connections = get_cached_connections(
            entry_type=self.request_attributes.entry_type,
            pre_entry_type=self.request_attributes.pre_entry_type,
        )


        await check_selected_database_connections(
            LOG=self.LOG,
            connections=connections,
        )


        result = await func(self, *args, **kwargs)


        return result

    return wrapper