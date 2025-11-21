from beacon.utils.modules import get_all_modules_mongo_connections_script
from beacon.logs.logs import log_with_args_mongo, LOG
from beacon.conf.conf import level

@log_with_args_mongo(level)
def get_function(self):
    list_modules = get_all_modules_mongo_connections_script("mappers")
    for module in list_modules:
        function = module.choose_function(self)
    return function

@log_with_args_mongo(level)
def get_collections_function(self):
    list_modules = get_all_modules_mongo_connections_script("mappers")
    for module in list_modules:
        function = module.choose_collections_function(self)
    return function