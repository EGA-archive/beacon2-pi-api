from beacon.connections.mongo.__init__ import client
from beacon.exceptions.exceptions import raise_exception
from beacon.logs.logs import log_with_args, log_with_args_mongo
from beacon.logs.logs import LOG

from beacon.connections.mongo.utils import get_count, get_documents
from beacon.connections.mongo.request_parameters import apply_request_parameters
from beacon.connections.mongo.utils import get_docs_by_response_type, query_id

from beacon.conf.conf import level
from typing import Optional
from beacon.response.schemas import DefaultSchemas
from beacon.request.parameters import RequestParams
from beacon.connections.omopcdm.biosamples import get_biosamples
from beacon.connections.omopcdm.individuals import get_individuals

@log_with_args_mongo(level)
def get_datasets(self):
    try:
        collection = client.beacon.datasets
        query = {}
        query = collection.find(query)
        return query
    except Exception as e:# pragma: no cover
        err = str(e)
        errcode=500
        raise_exception(err, errcode)

@log_with_args_mongo(level)
def get_full_datasets(self, entry_id: Optional[str], qparams: RequestParams):
    try:
        collection = client.beacon.datasets
        if entry_id == None:
            query = {}
        else:# pragma: no cover
            query = {'id': entry_id}
        count = get_count(self, client.beacon.datasets, query)
        query = collection.find(query)
        entity_schema = DefaultSchemas.DATASETS
        response_converted = (
            [r for r in query] if query else []
        )
        return response_converted, count, entity_schema
    except Exception as e:# pragma: no cover
        err = str(e)
        errcode=500
        raise_exception(err, errcode)

@log_with_args_mongo(level)
def get_list_of_datasets(self):
    try:
        datasets = get_datasets(self)
        beacon_datasets = [ r for r in datasets ]
        LOG.debug(beacon_datasets)
        return beacon_datasets
    except Exception as e:# pragma: no cover
        err = str(e)
        errcode=500
        raise_exception(err, errcode)

@log_with_args_mongo(level)
def get_dataset_with_id(self, entry_id: Optional[str], qparams: RequestParams):
    limit = qparams.query.pagination.limit
    query_parameters, parameters_as_filters = apply_request_parameters(self, {}, qparams, entry_id)
    if parameters_as_filters == True:
        query, parameters_as_filters = apply_request_parameters(self, {}, qparams, entry_id)# pragma: no cover
    else:
        query={}
    query = query_id(self, query, entry_id)
    schema = DefaultSchemas.DATASETS
    count = get_count(self, client.beacon.datasets, query)
    docs = get_documents(self,
        client.beacon.datasets,
        query,
        qparams.query.pagination.skip,
        qparams.query.pagination.skip*limit
    )
    response_converted = (
                [r for r in docs] if docs else []
            )
    return response_converted, count, schema

# # There are no different datasets in OMOPCDM
# @log_with_args(level)
# def get_full_datasets(self, entry_id: Optional[str], qparams: RequestParams):
#     schema = DefaultSchemas.DATASETS
#     response = [{'id':'cdm', 'name':'OMOP CDM dataset'}]
#     count = 1
#     return response, count, schema

# @log_with_args(level)
# def get_list_of_datasets(self):
#     datasets, count, schema = get_full_datasets(self, None, None)
#     return datasets

# @log_with_args(level)
# def get_dataset_with_id(self, entry_id: Optional[str], qparams: RequestParams):
#     schema = DefaultSchemas.DATASETS
#     if entry_id=='cdm':
#         response = [{'id':'cdm', 'name':'OMOP CDM dataset'}]
#         count = 1
#         return response, count, schema
#     return {}, 0, schema

# @log_with_args(level)
# def get_biosamples_of_dataset(self, entry_id: Optional[str], qparams: RequestParams, dataset: str):
#     schema = DefaultSchemas.BIOSAMPLES
#     if entry_id=='cdm':
#         return get_biosamples(self, None, qparams, dataset)
#     return schema, 0, 0, {}, dataset

# @log_with_args(level)
# def get_individuals_of_dataset(self, entry_id: Optional[str], qparams: RequestParams, dataset: str):
#     schema = DefaultSchemas.INDIVIDUALS
#     if entry_id=='cdm':
#         return get_individuals(self, None, qparams, dataset)
#     return schema, 0, 0, {}, dataset