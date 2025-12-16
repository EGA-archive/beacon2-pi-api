from beacon.request.parameters import CustomFilter
from beacon.connections.mongo.utils import choose_scope
from beacon.conf.filtering_terms import alphanumeric_terms
from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf_override import config
from beacon.utils.modules import get_all_modules_mongo_connections_script

@log_with_args(config.level)
def apply_custom_filter(self, query: dict, filter: CustomFilter, dataset: str) -> dict:
    # Check if there is a valid scope for the filter and build the query syntax for the custom filter
    scope = filter.scope
    scope=choose_scope(self, scope, filter)
    value_splitted = filter.id.split(':')
    if value_splitted[0] in alphanumeric_terms:
        query_term = value_splitted[0]
    else:
        query_term = value_splitted[0] + '.label'
    query[query_term]=value_splitted[1]
    list_modules = get_all_modules_mongo_connections_script("filters.cross_queries.cross_query")
    for module in list_modules:
        query = module.cross_query(self, query, scope, {}, dataset)

    return query
