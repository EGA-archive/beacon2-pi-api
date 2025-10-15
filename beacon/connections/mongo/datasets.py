from beacon.logs.logs import log_with_args_mongo
from beacon.conf.conf import level
from beacon.connections.mongo.utils import get_count, get_documents
from beacon.connections.mongo.utils import query_id
from beacon.connections.mongo.request_parameters import apply_request_parameters
from beacon.request.classes import RequestAttributes
from beacon.connections.mongo.__init__ import datasets
from beacon.logs.logs import LOG

@log_with_args_mongo(level)
def get_datasets(self):
    collection = datasets
    query = {}
    query = collection.find(query)
    return query

@log_with_args_mongo(level)
def get_full_datasets(self):
    collection = datasets
    if RequestAttributes.entry_id == None:
        query = {}
    else:
        query = {'id': RequestAttributes.entry_id}
    query = collection.find(query, {"_id": 0})
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
    return response_converted, count

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
    return response_converted, count

# 1. Mirar si hi ha connexió amb la base de dades de budget a MongoDB. Si no, retornar 404, data not found.