from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level
from beacon.utils.modules import get_all_modules_mongo_connections_script

@log_with_args(level)
def request_parameters_from_modules(self, total_query, request_parameters, dataset): 
    list_modules = get_all_modules_mongo_connections_script("filters.request_parameters.request_parameters")
    for module in list_modules:
        total_query = module.request_parameters(self, total_query, request_parameters, dataset)
    return total_query