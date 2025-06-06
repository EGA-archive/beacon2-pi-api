from beacon.logs.logs import log_with_args_mongo
from beacon.conf.conf import level
from beacon.connections.mongo.utils import get_count, get_documents
from typing import Optional
from beacon.response.schemas import DefaultSchemas
from beacon.request.parameters import RequestParams
from beacon.connections.mongo.utils import get_docs_by_response_type, query_id, get_cross_query
from beacon.connections.mongo.request_parameters import apply_request_parameters
from beacon.request.classes import ErrorClass, RequestAttributes
from beacon.connections.mongo.__init__ import datasets

@log_with_args_mongo(level)
def get_datasets(self):
    try:
        collection = datasets
        query = {}
        query = collection.find(query)
        return query
    except Exception as e:# pragma: no cover
        ErrorClass.error_code=500
        ErrorClass.error_message=str(e)
        raise

@log_with_args_mongo(level)
def get_full_datasets(self, qparams: RequestParams):
    try:
        collection = datasets
        if RequestAttributes.entry_id == None:
            query = {}
        else:# pragma: no cover
            query = {'id': RequestAttributes.entry_id}
        count = get_count(self, datasets, query)
        query = collection.find(query)
        entity_schema = DefaultSchemas.DATASETS
        response_converted = (
            [r for r in query] if query else []
        )
        return response_converted, count, entity_schema
    except Exception as e:# pragma: no cover
        ErrorClass.error_code=500
        ErrorClass.error_message=str(e)
        raise

@log_with_args_mongo(level)
def get_list_of_datasets(self):
    try:
        datasets = get_datasets(self)
        beacon_datasets = [ r for r in datasets ]
        return beacon_datasets
    except Exception as e:# pragma: no cover
        ErrorClass.error_code=500
        ErrorClass.error_message=str(e)
        raise

@log_with_args_mongo(level)
def get_dataset_with_id(self, qparams: RequestParams):
    limit = qparams.query.pagination.limit
    query_parameters, parameters_as_filters = apply_request_parameters(self, {}, qparams, RequestAttributes.entry_id)
    if parameters_as_filters == True:
        query, parameters_as_filters = apply_request_parameters(self, {}, qparams, RequestAttributes.entry_id)# pragma: no cover
    else:
        query={}
    query = query_id(self, query, RequestAttributes.entry_id)
    schema = DefaultSchemas.DATASETS
    count = get_count(self, datasets, query)
    docs = get_documents(self,
        datasets,
        query,
        qparams.query.pagination.skip,
        qparams.query.pagination.skip*limit
    )
    response_converted = (
                [r for r in docs] if docs else []
            )
    return response_converted, count, schema