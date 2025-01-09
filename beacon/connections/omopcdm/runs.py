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
def get_runs(self, entry_id: Optional[str], qparams: RequestParams, dataset: str):
    collection = 'runs'
    mongo_collection = client.beacon.runs
    parameters_as_filters=False
    query_parameters, parameters_as_filters = apply_request_parameters(self, {}, qparams, dataset)
    if parameters_as_filters == True:
        query, parameters_as_filters = apply_request_parameters(self, {}, qparams, dataset)# pragma: no cover
        query_parameters={}# pragma: no cover
    else:
        query={}
    query = apply_filters(self, query, qparams.query.filters, collection, query_parameters, dataset)
    schema = DefaultSchemas.RUNS
    include = qparams.query.include_resultset_responses
    limit = qparams.query.pagination.limit
    skip = qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100
    idq="biosampleId"
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip, mongo_collection, idq)
    return schema, count, dataset_count, docs, dataset

@log_with_args(level)
def get_run_with_id(self, entry_id: Optional[str], qparams: RequestParams, dataset: str):
    collection = 'runs'
    mongo_collection = client.beacon.runs
    query = apply_filters(self, {}, qparams.query.filters, collection, {}, dataset)
    query = query_id(self, query, entry_id)
    schema = DefaultSchemas.RUNS
    include = qparams.query.include_resultset_responses
    limit = qparams.query.pagination.limit
    skip = qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100# pragma: no cover
    idq="biosampleId"
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip, mongo_collection, idq)
    return schema, count, dataset_count, docs, dataset

@log_with_args(level)
def get_variants_of_run(self, entry_id: Optional[str], qparams: RequestParams, dataset: str):
    collection = 'runs'
    mongo_collection = client.beacon.genomicVariations
    query = {"$and": [{"id": entry_id}]}
    query = apply_filters(self, query, qparams.query.filters, collection, {}, dataset)
    run_ids = client.beacon.runs \
        .find_one(query, {"biosampleId": 1, "_id": 0})
    targets = client.beacon.targets \
        .find({"datasetId": dataset}, {"biosampleIds": 1, "_id": 0})
    position=0
    bioids=targets[0]["biosampleIds"]
    for bioid in bioids:
        if bioid == run_ids["biosampleId"]:
            break
        position+=1
    position=str(position)
    position1="^"+position+","
    position2=","+position+","
    position3=","+position+"$"
    query_cl={ "$or": [
    {"biosampleIds": {"$regex": position1}}, 
    {"biosampleIds": {"$regex": position2}},
    {"biosampleIds": {"$regex": position3}}
    ]}
    string_of_ids = client.beacon.caseLevelData \
        .find(query_cl, {"id": 1, "_id": 0})
    HGVSIds=list(string_of_ids)
    query={}
    queryHGVS={}
    listHGVS=[]
    for HGVSId in HGVSIds:
        justid=HGVSId["id"]
        listHGVS.append(justid)
    queryHGVS["$in"]=listHGVS
    query["identifiers.genomicHGVSId"]=queryHGVS
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
def get_analyses_of_run(self, entry_id: Optional[str], qparams: RequestParams, dataset: str):
    collection = 'runs'
    mongo_collection = client.beacon.analyses
    query = {"runId": entry_id}
    query = apply_filters(self, query, qparams.query.filters, collection, {}, dataset)
    schema = DefaultSchemas.RUNS
    include = qparams.query.include_resultset_responses
    limit = qparams.query.pagination.limit
    skip = qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100# pragma: no cover
    idq="biosampleId"
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip, mongo_collection, idq)
    return schema, count, dataset_count, docs, dataset