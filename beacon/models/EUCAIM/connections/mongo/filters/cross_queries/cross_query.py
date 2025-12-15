from beacon.connections.mongo.filters.cross_queries.scope_is_not_entry_type import scope_is_not_entry_type
from beacon.connections.mongo.__init__ import patients, imagestudies, collections
from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf_override import config
from beacon.models.EUCAIM.connections.mongo.utils import import_patients_confile
from beacon.request.classes import RequestAttributes
from beacon.models.EUCAIM.connections.mongo.utils import get_non_collections_cross_query_attributes

@log_with_args(config.level)
def cross_query(self, query: dict, scope: str, request_parameters: dict, dataset: str):
    patients_confile=import_patients_confile()
    # Check for the different scopes and entry types to apply a different query syntax built.
    def_list=[]
    if scope == 'patients' and RequestAttributes.entry_type != patients_confile["patients"]["endpoint_name"]:
        end = 'patients'
        original_id = get_non_collections_cross_query_attributes(self,RequestAttributes.entry_type, end)["idq"]
        final_id = get_non_collections_cross_query_attributes(self,RequestAttributes.entry_type, end)["idq2"]
        mongo_collection = get_non_collections_cross_query_attributes(self, RequestAttributes.entry_type, end)["secondary_collection"]

        query=scope_is_not_entry_type(self, original_id, final_id, def_list, mongo_collection, query, dataset)
    return query