from beacon.models.ga4gh.beacon_v2_default_model.connections.mongo.filters.cross_queries.entry_type_is_variant import cross_query_entry_type_is_genomicVariant_and_scope_is_not
from beacon.models.ga4gh.beacon_v2_default_model.connections.mongo.filters.cross_queries.scope_is_variant import cross_query_scope_is_genomicVariant_and_entry_type_is_not
from beacon.connections.mongo.filters.cross_queries.scope_is_not_entry_type import scope_is_not_entry_type
from beacon.connections.mongo.__init__ import diseases, patients, tumors, images
from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level
from beacon.models.EUCAIM.conf.entry_types import imaging, disease, tumor, patient
from beacon.request.classes import RequestAttributes
from beacon.models.EUCAIM.connections.mongo.utils import get_non_collections_cross_query_attributes

@log_with_args(level)
def cross_query(self, query: dict, scope: str, request_parameters: dict, dataset: str):
    # Check for the different scopes and entry types to apply a different query syntax built.
    def_list=[]
    if scope == 'imaging' and RequestAttributes.entry_type != imaging.endpoint_name or scope == 'tumor' and RequestAttributes.entry_type != tumor.endpoint_name or scope == 'disease' and RequestAttributes.entry_type != disease.endpoint_name or scope == 'patient' and RequestAttributes.entry_type != patient.endpoint_name:
        original_id = get_non_collections_cross_query_attributes[RequestAttributes.pre_entry_type][RequestAttributes.entry_type]["idq"]
        final_id = get_non_collections_cross_query_attributes[RequestAttributes.pre_entry_type][RequestAttributes.entry_type]["idq2"]
        mongo_collection = get_non_collections_cross_query_attributes[RequestAttributes.pre_entry_type][RequestAttributes.entry_type]["secondary_collection"]
        query=scope_is_not_entry_type(self, original_id, final_id, def_list, mongo_collection, query, dataset)
    return query