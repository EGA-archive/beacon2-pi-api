from typing import List
import re
from beacon.request.parameters import AlphanumericFilter, CustomFilter, OntologyFilter
from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level
from beacon.connections.mongo.filters.request_parameters import request_parameters_from_modules
from beacon.connections.mongo.filters.alphanumeric import apply_alphanumeric_filter
from beacon.connections.mongo.filters.ontology import apply_ontology_filter
from beacon.connections.mongo.filters.custom import apply_custom_filter

CURIE_REGEX = r'^([a-zA-Z0-9]*):\/?[a-zA-Z0-9./]*$'

@log_with_args(level)
def apply_filters(self, query: dict, filters: List[dict], query_parameters: dict, dataset: str) -> dict:
    request_parameters = query_parameters
    total_query={}
    if len(filters) >= 1:
        total_query["$and"] = []
        if query != {} and request_parameters == {}:
            total_query["$and"].append(query)
        for filter in filters:
            partial_query = {}
            if "value" in filter:
                filter = AlphanumericFilter(**filter)
                partial_query = apply_alphanumeric_filter(self, partial_query, filter, dataset, False)
            elif "includeDescendantTerms" not in filter and '.' not in filter["id"] and filter["id"].isupper():
                filter=OntologyFilter(**filter)
                filter.includeDescendantTerms=True
                partial_query = apply_ontology_filter(self, partial_query, filter, request_parameters, dataset)
            elif "similarity" in filter or "includeDescendantTerms" in filter or re.match(CURIE_REGEX, filter["id"]) and filter["id"].isupper():
                filter = OntologyFilter(**filter)
                partial_query = apply_ontology_filter(self, partial_query, filter, request_parameters, dataset)
            else:
                filter = CustomFilter(**filter)
                partial_query = apply_custom_filter(self, partial_query, filter, dataset)
            total_query["$and"].append(partial_query)
            if total_query["$and"] == [{'$or': []}] or total_query['$and'] == []:
                total_query = {}
    if request_parameters != {}:
        total_query = request_parameters_from_modules(self, total_query, request_parameters)
        if total_query["$and"] == [{'$or': []}] or total_query['$and'] == []:
            total_query = {}
    if total_query == {} and query != {}:
        total_query=query
    return total_query