from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level
from beacon.models.EUCAIM.conf.entry_types import imaging, disease, tumor, patient
from beacon.request.classes import RequestAttributes
from beacon.models.ga4gh.beacon_v2_default_model.connections.mongo.filters.request_parameters.apply_request_parameters import apply_request_parameters
from beacon.connections.mongo.filters.filters import apply_filters
from beacon.connections.mongo.utils import get_docs_by_response_type, query_id
from beacon.connections.mongo.utils import get_count, get_documents_for_cohorts
from beacon.models.EUCAIM.connections.mongo.utils import get_non_collections_cross_query_attributes
from beacon.response.classes import SingleDatasetResponse

@log_with_args(level)
def get_endpoint(self, dataset: SingleDatasetResponse):
    # Initialize the query dictionary.
    query = {}
    # Process the filters
    query = apply_filters(self, query, RequestAttributes.qparams.query.filters, {}, dataset.dataset)
    #if query == {}: # If the filters didn't build any query, just return the dataset.
    #    return dataset
    # Save the include, limit and skip parameters so they are used later.
    include = RequestAttributes.qparams.query.includeResultsetResponses
    limit = RequestAttributes.qparams.query.pagination.limit
    skip = RequestAttributes.qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100
    # Get the docs with the query syntax built.
    responseClass = get_docs_by_response_type(self, include, query, dataset, limit, skip)
    return responseClass

@log_with_args(level)
def get_endpoint_with_id(self, dataset: SingleDatasetResponse):
    query = {}
    # Process filters
    query = apply_filters(self, query, RequestAttributes.qparams.query.filters, {}, dataset.dataset)
    # If the entry type records are not variants, include the id queried in the query.
    if RequestAttributes.entry_type == imaging.endpoint_name:
        query["imageId"] = RequestAttributes.entry_id
    elif RequestAttributes.entry_type == disease.endpoint_name:
        query["diseaseId"] = RequestAttributes.entry_id
    elif RequestAttributes.entry_type == tumor.endpoint_name:
        query["tumorId"] = RequestAttributes.entry_id
    elif RequestAttributes.entry_type == patient.endpoint_name:
        query["patientId"] = RequestAttributes.entry_id
    # Save the include, limit and skip parameters so they are used later.
    include = RequestAttributes.qparams.query.includeResultsetResponses
    limit = RequestAttributes.qparams.query.pagination.limit
    skip = RequestAttributes.qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100
    # Get the docs with the query syntax built.
    responseClass = get_docs_by_response_type(self, include, query, dataset, limit, skip)
    return responseClass

@log_with_args(level)
def get_endpoint_cross_query(self, dataset: SingleDatasetResponse):
    # Get the translation of ids for the entry types lookup for the cross query.
    mapping = get_non_collections_cross_query_attributes(self, RequestAttributes.entry_type, RequestAttributes.pre_entry_type)
    # Get the ids found for the initial entry type query.
    items_found = mapping["secondary_collection"] \
    .find({mapping["idq"]: RequestAttributes.entry_id, "datasetId": dataset.dataset}, {mapping["idq2"]: 1, "_id": 0})
    # Translate the ids.
    list_of_itemsfound=[]
    for itemfound in items_found:
        list_of_itemsfound.append(itemfound[mapping["idq2"]])
    query = {mapping["idq2"]: {"$in": list_of_itemsfound}}
    # Process filters.
    query = apply_filters(self, query, RequestAttributes.qparams.query.filters, {}, dataset.dataset)
    # Save the include, limit and skip parameters so they are used later.
    include = RequestAttributes.qparams.query.includeResultsetResponses
    limit = RequestAttributes.qparams.query.pagination.limit
    skip = RequestAttributes.qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100
    # Get the docs with the query syntax built.
    responseClass = get_docs_by_response_type(self, include, query, dataset, limit, skip)
    return responseClass
