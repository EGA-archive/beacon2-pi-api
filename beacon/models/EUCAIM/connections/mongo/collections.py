from beacon.logs.logs import log_with_args_mongo
from beacon.conf.conf import level
from beacon.connections.mongo.utils import get_count, get_documents, query_id, get_documents_for_cohorts
from beacon.models.ga4gh.beacon_v2_default_model.connections.mongo.utils import get_phenotypic_cross_query_attributes
from beacon.connections.mongo.filters.filters import apply_filters
from beacon.models.ga4gh.beacon_v2_default_model.connections.mongo.filters.request_parameters.apply_request_parameters import apply_request_parameters
from beacon.request.classes import RequestAttributes
from beacon.connections.mongo.__init__ import datasets, cohorts
from beacon.logs.logs import LOG
from beacon.response.classes import CollectionsResponse

@log_with_args_mongo(level)
def get_datasets(self):
    # Find all the datasets in the mongo database.
    query = {}
    query = datasets.find(query)
    return query

@log_with_args_mongo(level)
def get_full_datasets(self):
    # Create the query syntax depending on it there is any entry id queried.
    if RequestAttributes.entry_id == None:
        query = {}
    else:
        query = {'id': RequestAttributes.entry_id}
    query = datasets.find(query, {"_id": 0})
    try:
        # Collect all the datasets found with the query performed.
        if RequestAttributes.qparams.query.requestParameters["datasets"] != []: # If there are datasets requested, then, query just for those datasets.
            response_converted = (
                [r for r in query if r["id"] in RequestAttributes.qparams.query.requestParameters["datasets"]] if query else []
            )
        else:
            response_converted = (
                [r for r in query] if query else []
            ) 
    except Exception:
        response_converted = (
            [r for r in query] if query else []
        )
    # Count how many datasets are to be returned in response.
    count = len(response_converted)
    return CollectionsResponse(docs=response_converted, count=count)

@log_with_args_mongo(level)
def get_list_of_datasets(self):
    # Get all the datasets to be returned in response and put them in a list.
    datasets = get_datasets(self)
    beacon_datasets = [ r for r in datasets ]
    return beacon_datasets

@log_with_args_mongo(level)
def get_dataset_with_id(self):
    limit = RequestAttributes.qparams.query.pagination.limit
    # Handle the request parameters and create the first built of the query.
    query_parameters, parameters_as_filters = apply_request_parameters(self, {}, RequestAttributes.entry_id)
    if parameters_as_filters == True:
        query, parameters_as_filters = apply_request_parameters(self, {}, RequestAttributes.entry_id)
    else:
        query={}
    # Include the id queried in the query.
    query = query_id(self, query, RequestAttributes.entry_id)
    # Count all the datasets to be returned in response.
    count = get_count(self, datasets, query)
    # Find the datasets to be returned in response.
    docs = get_documents(self,
        datasets,
        query,
        RequestAttributes.qparams.query.pagination.skip,
        RequestAttributes.qparams.query.pagination.skip*limit
    )
    response_converted = (
                [r for r in docs] if docs else []
            )
    return CollectionsResponse(docs=response_converted, count=count)