from beacon.connections.mongo.__init__ import client
from beacon.logs.logs import log_with_args_mongo
from beacon.conf.conf import level
from beacon.connections.mongo.utils import get_count, get_documents
from typing import Optional
from beacon.response.schemas import DefaultSchemas
from beacon.request.parameters import RequestParams
from beacon.connections.mongo.filters import apply_filters
from beacon.connections.mongo.utils import get_docs_by_response_type, query_id, get_cross_query
from beacon.connections.mongo.request_parameters import apply_request_parameters
from beacon.request.classes import ErrorClass

@log_with_args_mongo(level)
def get_datasets(self):
    try:
        collection = client.beacon.datasets
        query = {}
        query = collection.find(query)
        return query
    except Exception as e:# pragma: no cover
        ErrorClass.error_code=500
        ErrorClass.error_message=str(e)
        raise

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

@log_with_args_mongo(level)
def get_variants_of_dataset(self, entry_id: Optional[str], qparams: RequestParams, dataset: str):
    collection = 'datasets'
    mongo_collection = client.beacon.genomicVariations
    dataset_count=0
    limit = qparams.query.pagination.limit
    query_count={}
    idq="caseLevelData.biosampleId"
    query_count["$or"]=[]
    if dataset == entry_id:
        queryid={}
        queryid["datasetId"]=dataset
        query_count["$or"].append(queryid)
    else:
        schema = DefaultSchemas.GENOMICVARIATIONS# pragma: no cover
        return schema, 0, 0, None, dataset# pragma: no cover
    query = apply_filters(self, query_count, qparams.query.filters, collection, {}, dataset)
    schema = DefaultSchemas.GENOMICVARIATIONS
    include = qparams.query.include_resultset_responses
    limit = qparams.query.pagination.limit
    skip = qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100# pragma: no cover
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip, mongo_collection, idq)
    return schema, count, dataset_count, docs, dataset

@log_with_args_mongo(level)
def get_biosamples_of_dataset(self, entry_id: Optional[str], qparams: RequestParams, dataset: str):
    collection = 'datasets'
    mongo_collection = client.beacon.biosamples
    dataset_count=0
    limit = qparams.query.pagination.limit
    query = apply_filters(self, {}, qparams.query.filters, collection, {}, dataset)
    query = query_id(self, query, entry_id)
    count = get_count(self, client.beacon.datasets, query)
    dict_in={}
    if dataset == entry_id:
        dict_in['datasetId']=entry_id
    else:
        schema = DefaultSchemas.BIOSAMPLES# pragma: no cover
        return schema, 0, 0, None, dataset# pragma: no cover
    query = apply_filters(self, dict_in, qparams.query.filters, collection, {}, dataset)
    schema = DefaultSchemas.BIOSAMPLES
    include = qparams.query.include_resultset_responses
    limit = qparams.query.pagination.limit
    skip = qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100# pragma: no cover
    idq="id"
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip, mongo_collection, idq)
    return schema, count, dataset_count, docs, dataset

@log_with_args_mongo(level)
def get_individuals_of_dataset(self, entry_id: Optional[str], qparams: RequestParams, dataset: str):
    collection = 'datasets'
    mongo_collection = client.beacon.individuals
    dataset_count=0
    limit = qparams.query.pagination.limit
    query = apply_filters(self, {}, qparams.query.filters, collection, {}, dataset)
    query = query_id(self, query, entry_id)
    count = get_count(self, client.beacon.datasets, query)
    dict_in={}
    if dataset == entry_id:
        dict_in['datasetId']=entry_id
    else:
        schema = DefaultSchemas.INDIVIDUALS# pragma: no cover
        return schema, 0, 0, None, dataset# pragma: no cover
    query = apply_filters(self, dict_in, qparams.query.filters, collection, {}, dataset)
    schema = DefaultSchemas.INDIVIDUALS
    include = qparams.query.include_resultset_responses
    limit = qparams.query.pagination.limit
    skip = qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100# pragma: no cover
    idq="id"
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip, mongo_collection, idq)
    return schema, count, dataset_count, docs, dataset

@log_with_args_mongo(level)
def get_runs_of_dataset(self, entry_id: Optional[str], qparams: RequestParams, dataset: str):
    collection = 'datasets'
    mongo_collection = client.beacon.runs
    dataset_count=0
    limit = qparams.query.pagination.limit
    query = apply_filters(self, {}, qparams.query.filters, collection, {}, dataset)
    query = query_id(self, query, entry_id)
    count = get_count(self, client.beacon.datasets, query)
    dict_in={}
    dict_in={}
    if dataset == entry_id:
        dict_in['datasetId']=entry_id
    else:
        schema = DefaultSchemas.RUNS# pragma: no cover
        return schema, 0, 0, None, dataset# pragma: no cover
    query = apply_filters(self, dict_in, qparams.query.filters, collection, {}, dataset)
    schema = DefaultSchemas.RUNS
    include = qparams.query.include_resultset_responses
    limit = qparams.query.pagination.limit
    skip = qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100# pragma: no cover
    idq="biosampleId"
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip, mongo_collection, idq)
    list_of_records = (
            [r for r in docs] if docs else []
        )
    return schema, count, dataset_count, list_of_records, dataset

@log_with_args_mongo(level)
def get_analyses_of_dataset(self, entry_id: Optional[str], qparams: RequestParams, dataset: str):
    collection = 'datasets'
    idq="biosampleId"
    mongo_collection = client.beacon.analyses
    dataset_count=0
    limit = qparams.query.pagination.limit
    query = apply_filters(self, {}, qparams.query.filters, collection, {}, dataset)
    query = query_id(self, query, entry_id)
    count = get_count(self, client.beacon.datasets, query)
    dict_in={}
    dict_in={}
    if dataset == entry_id:
        dict_in['datasetId']=entry_id
    else:
        schema = DefaultSchemas.ANALYSES# pragma: no cover
        return schema, 0, 0, None, dataset# pragma: no cover
    query = apply_filters(self, dict_in, qparams.query.filters, collection, {}, dataset)
    schema = DefaultSchemas.ANALYSES
    include = qparams.query.include_resultset_responses
    limit = qparams.query.pagination.limit
    skip = qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100# pragma: no cover
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip, mongo_collection, idq)
    return schema, count, dataset_count, docs, dataset