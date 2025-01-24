from beacon.request.parameters import RequestParams
from beacon.response.schemas import DefaultSchemas
import yaml
from beacon.connections.mongo.__init__ import client
from beacon.connections.mongo.utils import get_docs_by_response_type, query_id
from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level
from beacon.connections.mongo.filters import apply_filters
from beacon.connections.mongo.request_parameters import apply_request_parameters
from typing import Optional

@log_with_args(level)
def get_individuals(self, entry_id: Optional[str], qparams: RequestParams, dataset: str):
    collection = 'individuals'
    mongo_collection = client.beacon.individuals
    parameters_as_filters=False
    query_parameters, parameters_as_filters = apply_request_parameters(self, {}, qparams, dataset)
    if parameters_as_filters == True and query_parameters != {'$and': []}:
        query, parameters_as_filters = apply_request_parameters(self, {}, qparams, dataset)# pragma: no cover
        query_parameters={}# pragma: no cover
    elif query_parameters != {'$and': []}:
        query=query_parameters
    elif query_parameters == {'$and': []}:
        query_parameters = {}
        query={}
    query = apply_filters(self, query, qparams.query.filters, collection, query_parameters, dataset)
    schema = DefaultSchemas.INDIVIDUALS
    include = qparams.query.include_resultset_responses
    limit = qparams.query.pagination.limit
    skip = qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100
    idq="id"
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip, mongo_collection, idq)
    return schema, count, dataset_count, docs, dataset

@log_with_args(level)
def get_individual_with_id(self, entry_id: Optional[str], qparams: RequestParams, dataset: str):
    collection = 'individuals'
    idq="id"
    mongo_collection = client.beacon.individuals
    query, parameters_as_filters = apply_request_parameters(self, {}, qparams, dataset)
    query = apply_filters(self, query, qparams.query.filters, collection, {}, dataset)
    query = query_id(self, query, entry_id)
    schema = DefaultSchemas.INDIVIDUALS
    include = qparams.query.include_resultset_responses
    limit = qparams.query.pagination.limit
    skip = qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100# pragma: no cover
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip, mongo_collection, idq)
    return schema, count, dataset_count, docs, dataset

@log_with_args(level)
def get_variants_of_individual(self, entry_id: Optional[str], qparams: RequestParams, dataset: str):
    collection = 'g_variants'
    targets = client.beacon.targets \
        .find({"datasetId": dataset}, {"biosampleIds": 1, "_id": 0})
    position=0
    bioids=targets[0]["biosampleIds"]
    for bioid in bioids:
        if bioid == entry_id:
            break
        position+=1
    if position == len(bioids):# pragma: no cover
        schema = DefaultSchemas.GENOMICVARIATIONS
        return schema, 0, -1, None, dataset
    position=str(position)
    query_cl={"$or": [{ position: "10", "datasetId": dataset},{ position: "11", "datasetId": dataset}, { position: "01", "datasetId": dataset}]}
    string_of_ids = client.beacon.caseLevelData \
        .find(query_cl, {"id": 1, "_id": 0}).limit(qparams.query.pagination.limit).skip(qparams.query.pagination.skip)
    HGVSIds=list(string_of_ids)
    query={}
    queryHGVS={}
    listHGVS=[]
    for HGVSId in HGVSIds:
        justid=HGVSId["id"]
        listHGVS.append(justid)
    queryHGVS["$in"]=listHGVS
    query["identifiers.genomicHGVSId"]=queryHGVS
    mongo_collection = client.beacon.genomicVariations
    query, parameters_as_filters = apply_request_parameters(self, query, qparams, dataset)
    query = apply_filters(self, query, qparams.query.filters, collection, {}, dataset)
    schema = DefaultSchemas.GENOMICVARIATIONS
    include = qparams.query.include_resultset_responses
    limit = qparams.query.pagination.limit
    skip = qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100# pragma: no cover
    idq="caseLevelData.biosampleId"
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip, mongo_collection, idq)
    return schema, count, dataset_count, docs, dataset

@log_with_args(level)
def get_biosamples_of_individual(self, entry_id: Optional[str], qparams: RequestParams, dataset: str):
    collection = 'biosamples'
    mongo_collection = client.beacon.biosamples
    query = {"individualId": entry_id}
    query, parameters_as_filters = apply_request_parameters(self, query, qparams, dataset)
    query = apply_filters(self, query, qparams.query.filters, collection, {}, dataset)
    schema = DefaultSchemas.BIOSAMPLES
    include = qparams.query.include_resultset_responses
    limit = qparams.query.pagination.limit
    skip = qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100# pragma: no cover
    idq="id"
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip, mongo_collection, idq)
    return schema, count, dataset_count, docs, dataset