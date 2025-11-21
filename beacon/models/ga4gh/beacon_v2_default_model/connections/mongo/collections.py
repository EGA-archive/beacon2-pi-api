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
    query = {}
    query = datasets.find(query)
    return query

@log_with_args_mongo(level)
def get_full_datasets(self):
    if RequestAttributes.entry_id == None:
        query = {}
    else:
        query = {'id': RequestAttributes.entry_id}
    query = datasets.find(query, {"_id": 0})
    try:
        if RequestAttributes.qparams.query.requestParameters["datasets"] != []:
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
    count = len(response_converted)
    return CollectionsResponse(docs=response_converted, count=count)

@log_with_args_mongo(level)
def get_list_of_datasets(self):
    datasets = get_datasets(self)
    beacon_datasets = [ r for r in datasets ]
    return beacon_datasets

@log_with_args_mongo(level)
def get_dataset_with_id(self):
    limit = RequestAttributes.qparams.query.pagination.limit
    query_parameters, parameters_as_filters = apply_request_parameters(self, {}, RequestAttributes.entry_id)
    if parameters_as_filters == True:
        query, parameters_as_filters = apply_request_parameters(self, {}, RequestAttributes.entry_id)
    else:
        query={}
    query = query_id(self, query, RequestAttributes.entry_id)
    count = get_count(self, datasets, query)
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


@log_with_args_mongo(level)
def get_cohorts(self):
    limit = RequestAttributes.qparams.query.pagination.limit
    query = apply_filters(self, {}, RequestAttributes.qparams.query.filters, {}, None)
    try:
        if RequestAttributes.qparams.query.requestParameters["datasets"] != None:
            try:
                query["$and"].append({"datasetId": {"$in": RequestAttributes.qparams.query.requestParameters["datasets"]}})
            except Exception:
                query["$and"]=[]
                query["$and"].append({"datasetId": {"$in": RequestAttributes.qparams.query.requestParameters["datasets"]}})
    except Exception:
        pass
    count = get_count(self, cohorts, query)
    docs = get_documents(self,
        cohorts,
        query,
        RequestAttributes.qparams.query.pagination.skip,
        RequestAttributes.qparams.query.pagination.skip*limit
    )
    response_converted = (
        [r for r in docs] if docs else []
    )
    return CollectionsResponse(docs=response_converted, count=count)

@log_with_args_mongo(level)
def get_cohort_with_id(self):
    limit = RequestAttributes.qparams.query.pagination.limit
    query = apply_filters(self, {}, RequestAttributes.qparams.query.filters, {}, "a")
    query = query_id(self, query, RequestAttributes.entry_id)
    count = get_count(self, cohorts, query)
    docs = get_documents(self,
        cohorts,
        query,
        RequestAttributes.qparams.query.pagination.skip,
        RequestAttributes.qparams.query.pagination.skip*limit
    )
    response_converted = (
        [r for r in docs] if docs else []
    )
    return CollectionsResponse(docs=response_converted, count=count)

@log_with_args_mongo(level)
def get_cross_collections(self):
    limit = RequestAttributes.qparams.query.pagination.limit
    query = apply_filters(self, {}, RequestAttributes.qparams.query.filters, {}, "a")
    query = query_id(self, query, RequestAttributes.entry_id)
    mapping = get_phenotypic_cross_query_attributes(self, RequestAttributes.entry_type, RequestAttributes.pre_entry_type)
    docs = get_documents_for_cohorts(self,
        mapping["secondary_collection"],
        query,
        0,
        0
    )
    final_query = {mapping["idq"]: {"$in": [doc[mapping["idq2"]] for doc in docs]}}
    docs = get_documents(self,
        RequestAttributes.mongo_collection,
        final_query,
        RequestAttributes.qparams.query.pagination.skip,
        RequestAttributes.qparams.query.pagination.skip*limit
    )
    count = get_count(self, RequestAttributes.mongo_collection, final_query)
    response_converted = (
        [r for r in docs] if docs else []
    )
    return CollectionsResponse(docs=response_converted, count=count)