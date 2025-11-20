from typing import List, Union
import re
from beacon.request.parameters import AlphanumericFilter, CustomFilter, OntologyFilter
from beacon.request.classes import Operator, Similarity
from beacon.connections.mongo.utils import get_documents, join_query, choose_scope
from beacon.connections.mongo.__init__ import client, genomicVariations, individuals, datasets, cohorts, analyses, biosamples, runs, targets as targets_, caseLevelData, filtering_terms, similarities, synonyms as synonyms_
from beacon.conf.filtering_terms import alphanumeric_terms
from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level
from beacon.models.ga4gh.beacon_v2_default_model.conf import analysis, biosample, cohort, dataset, genomicVariant, individual, run
from beacon.request.classes import RequestAttributes
from beacon.connections.mongo.filters.cross_request_parameters import cross_request_parameters 

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
        total_query = cross_request_parameters(self, total_query)
        if total_query["$and"] == [{'$or': []}] or total_query['$and'] == []:
            total_query = {}
    if total_query == {} and query != {}:
        total_query=query
    return total_query