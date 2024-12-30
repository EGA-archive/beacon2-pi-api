from beacon.request.parameters import RequestParams
from beacon.response.schemas import DefaultSchemas
from beacon.connections.mongo.__init__ import client
from beacon.logs.logs import log_with_args_mongo
from beacon.conf.conf import level
from beacon.connections.mongo.filters import apply_filters
from typing import Optional
from beacon.connections.mongo.utils import get_count, get_documents, get_documents_for_cohorts
from beacon.connections.mongo.utils import get_docs_by_response_type, query_id, get_cross_query
import yaml

@log_with_args_mongo(level)
def get_cohorts(self, entry_id: Optional[str], qparams: RequestParams):
    collection = 'cohorts'
    limit = qparams.query.pagination.limit
    query = apply_filters(self, {}, qparams.query.filters, collection, {}, "a")
    schema = DefaultSchemas.COHORTS
    count = get_count(self, client.beacon.cohorts, query)
    docs = get_documents(self,
        client.beacon.cohorts,
        query,
        qparams.query.pagination.skip,
        qparams.query.pagination.skip*limit
    )
    response_converted = (
        [r for r in docs] if docs else []
    )
    return response_converted, count, schema

@log_with_args_mongo(level)
def get_cohort_with_id(self, entry_id: Optional[str], qparams: RequestParams):
    collection = 'cohorts'
    limit = qparams.query.pagination.limit
    query = apply_filters(self, {}, qparams.query.filters, collection, {}, "a")
    query = query_id(self, query, entry_id)
    schema = DefaultSchemas.COHORTS
    count = get_count(self, client.beacon.cohorts, query)
    docs = get_documents(self,
        client.beacon.cohorts,
        query,
        qparams.query.pagination.skip,
        qparams.query.pagination.skip*limit
    )
    response_converted = (
        [r for r in docs] if docs else []
    )
    return response_converted, count, schema

@log_with_args_mongo(level)
def get_individuals_of_cohort(self, entry_id: Optional[str], qparams: RequestParams, dataset: str):
    collection = 'cohorts'
    mongo_collection = client.beacon.individuals
    dataset_count=0
    limit = qparams.query.pagination.limit
    include = qparams.query.include_resultset_responses
    query = apply_filters(self, {}, qparams.query.filters, collection, {}, dataset)
    query = query_id(self, query, entry_id)
    count = get_count(self, client.beacon.cohorts, query)
    dict_in={}
    dict_in['datasetId']=dataset
    query = apply_filters(self, dict_in, qparams.query.filters, collection, {}, dataset)

    schema = DefaultSchemas.INDIVIDUALS
    skip = qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100# pragma: no cover
    idq="id"
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip, mongo_collection, idq)
    return schema, count, dataset_count, docs, dataset

@log_with_args_mongo(level)
def get_analyses_of_cohort(self, entry_id: Optional[str], qparams: RequestParams, dataset: str):
    collection = 'cohorts'
    mongo_collection = client.beacon.analyses
    dataset_count=0
    limit = qparams.query.pagination.limit
    include = qparams.query.include_resultset_responses
    query = apply_filters(self, {}, qparams.query.filters, collection, {}, dataset)
    query = query_id(self, query, entry_id)
    count = get_count(self, client.beacon.cohorts, query)
    dict_in={}
    dict_in['datasetId']=dataset
    query = apply_filters(self, dict_in, qparams.query.filters, collection, {}, dataset)
    schema = DefaultSchemas.ANALYSES
    skip = qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100# pragma: no cover
    idq="biosampleId"
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip, mongo_collection, idq)
    return schema, count, dataset_count, docs, dataset

@log_with_args_mongo(level)
def get_variants_of_cohort(self,entry_id: Optional[str], qparams: RequestParams, dataset: str):
    collection = 'cohorts'
    mongo_collection = client.beacon.genomicVariations
    dataset_count=0
    limit = qparams.query.pagination.limit
    include = qparams.query.include_resultset_responses
    query = apply_filters(self, {}, qparams.query.filters, collection, {}, dataset)
    query = query_id(self, query, entry_id)
    count = get_count(self, client.beacon.cohorts, query)
    query_count={}
    query_count["$or"]=[]
    docs = get_documents_for_cohorts(self,
        client.beacon.cohorts,
        query,
        qparams.query.pagination.skip,
        qparams.query.pagination.skip*limit
    )
    for doc in docs:
        if doc["datasetId"] == dataset:
            entry_id = dataset
    if dataset == entry_id:
        queryid={}
        queryid["datasetId"]=dataset
        query_count["$or"].append(queryid)
    else:
        schema = DefaultSchemas.GENOMICVARIATIONS# pragma: no cover
        return schema, 0, 0, None, dataset# pragma: no cover
    query = apply_filters(self, query_count, qparams.query.filters, collection, {}, dataset)
    schema = DefaultSchemas.GENOMICVARIATIONS
    skip = qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100# pragma: no cover
    idq="caseLevelData.biosampleId"
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip, mongo_collection, idq)
    return schema, count, dataset_count, docs, dataset

@log_with_args_mongo(level)
def get_runs_of_cohort(self, entry_id: Optional[str], qparams: RequestParams, dataset: str):
    collection = 'cohorts'
    mongo_collection = client.beacon.runs
    dataset_count=0
    limit = qparams.query.pagination.limit
    include = qparams.query.include_resultset_responses
    query = apply_filters(self, {}, qparams.query.filters, collection, {}, dataset)
    query = query_id(self, query, entry_id)
    count = get_count(self, client.beacon.cohorts, query)
    dict_in={}
    dict_in['datasetId']=dataset
    query = apply_filters(self, dict_in, qparams.query.filters, collection, {}, dataset)
    schema = DefaultSchemas.RUNS
    skip = qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100# pragma: no cover
    idq="biosampleId"
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip, mongo_collection, idq)
    return schema, count, dataset_count, docs, dataset

@log_with_args_mongo(level)
def get_biosamples_of_cohort(self, entry_id: Optional[str], qparams: RequestParams, dataset: str):
    collection = 'cohorts'
    mongo_collection = client.beacon.biosamples
    dataset_count=0
    limit = qparams.query.pagination.limit
    include = qparams.query.include_resultset_responses
    query = apply_filters(self, {}, qparams.query.filters, collection, {}, dataset)
    query = query_id(self, query, entry_id)
    count = get_count(self, client.beacon.cohorts, query)
    dict_in={}
    dict_in['datasetId']=dataset
    query = apply_filters(self, dict_in, qparams.query.filters, collection, {}, dataset)
    schema = DefaultSchemas.BIOSAMPLES
    skip = qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100# pragma: no cover
    idq="id"
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip, mongo_collection, idq)
    return schema, count, dataset_count, docs, dataset