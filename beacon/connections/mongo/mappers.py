from beacon.utils.modules import get_all_modules_mongo_connections_script
from beacon.logs.logs import log_with_args_mongo, LOG
from beacon.conf.conf import level

@log_with_args_mongo(level)
def get_function(self):
    # Load all the mappers from each of model's mongo connection and execute the choose_function from it
    list_modules = get_all_modules_mongo_connections_script("mappers")
    for module in list_modules:
        function = module.choose_function(self)
    return function

@log_with_args_mongo(level)
def get_collections_function(self):
    # Load all the mappers from each of model's mongo connection and execute the choose_collections_function from it
    list_modules = get_all_modules_mongo_connections_script("mappers")
    for module in list_modules:
        function = module.choose_collections_function(self)
    return function