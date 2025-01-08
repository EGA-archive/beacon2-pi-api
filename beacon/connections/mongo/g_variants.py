from beacon.request.parameters import RequestParams
from beacon.response.schemas import DefaultSchemas
from beacon.connections.mongo.__init__ import client
from beacon.connections.mongo.utils import get_docs_by_response_type
from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level
from beacon.connections.mongo.filters import apply_filters
from beacon.connections.mongo.request_parameters import apply_request_parameters
from typing import Optional
from bson import json_util

@log_with_args(level)
def get_variants(self, entry_id: Optional[str], qparams: RequestParams, dataset: str):
    collection = 'g_variants'
    mongo_collection = client.beacon.genomicVariations
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
    query = apply_filters(self, query, qparams.query.filters, collection,query_parameters, dataset)
    include = qparams.query.include_resultset_responses
    limit = qparams.query.pagination.limit
    skip = qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100
    schema = DefaultSchemas.GENOMICVARIATIONS
    idq="caseLevelData.biosampleId"
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip, mongo_collection, idq)
    #∫docs = json_util.dumps(docs)

    return schema, count, dataset_count, docs, dataset

@log_with_args(level)
def get_variant_with_id(self, entry_id: Optional[str], qparams: RequestParams, dataset: str):
    collection = 'g_variants'
    mongo_collection = client.beacon.genomicVariations
    query = {"$and": [{"variantInternalId": entry_id}]}
    query_parameters, parameters_as_filters = apply_request_parameters(self, query, qparams, dataset)
    if parameters_as_filters == True:
        query, parameters_as_filters = apply_request_parameters(self, {}, qparams, dataset)# pragma: no cover
        query_parameters={}# pragma: no cover
    else:
        query=query_parameters
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
def get_biosamples_of_variant(self, entry_id: Optional[str], qparams: RequestParams, dataset: str):
    collection = 'g_variants'
    mongo_collection = client.beacon.biosamples
    query = {"$and": [{"variantInternalId": entry_id}]}
    query_parameters, parameters_as_filters = apply_request_parameters(self, query, qparams, dataset)
    if parameters_as_filters == True:
        query, parameters_as_filters = apply_request_parameters(self, query, qparams, dataset)# pragma: no cover
        query_parameters={}# pragma: no cover
    else:
        query=query_parameters
    collection='biosamples'
    HGVSIds = client.beacon.genomicVariations \
        .find(query, {"identifiers.genomicHGVSId": 1, "datasetId": 1, "_id": 0})
    HGVSDataset=HGVSIds[0]["datasetId"]
    if dataset != HGVSDataset:
        schema = DefaultSchemas.BIOSAMPLES
        return schema, 0, 0, [], dataset
    HGVSIds=list(HGVSIds)
    HGVSId=HGVSIds[0]["identifiers"]["genomicHGVSId"]
    queryHGVSId={"datasetId": dataset, "id": HGVSId}
    string_of_ids = client.beacon.caseLevelData \
        .find(queryHGVSId)
    targets = client.beacon.targets \
        .find({"datasetId": HGVSDataset}, {"biosampleIds": 1, "_id": 0})
    targets=list(targets)
    list_of_targets=targets[0]["biosampleIds"]
    list_of_positions_strings= string_of_ids[0]
    biosampleIds=[]
    filters=qparams.query.filters
    if filters != []:
        for filter in filters:
            if filter['id']=='GENO:GENO_0000458':
                for key, value in list_of_positions_strings.items():
                    if key != 'datasetId' and key != 'id' and key != '_id' and value != '11':
                        biosampleIds.append(list_of_targets[int(key)])
                qparams.query.filters.remove(filter)
            elif filter['id']=='GENO:GENO_0000136':
                for key, value in list_of_positions_strings.items():
                    if key != 'datasetId' and key != 'id' and key != '_id' and value != '10' and value != '01':
                        biosampleIds.append(list_of_targets[int(key)])
                qparams.query.filters.remove(filter)
            else:
                for key, value in list_of_positions_strings.items():
                    if key != 'datasetId' and key != 'id' and key != '_id':
                        biosampleIds.append(list_of_targets[int(key)])
    else:
        for key, value in list_of_positions_strings.items():
            if key != 'datasetId' and key != 'id' and key != '_id':
                biosampleIds.append(list_of_targets[int(key)])
    finalids=biosampleIds
    try:
        finalids=[]
        for bioid in biosampleIds:
            finalids.append({"id": bioid})
    except Exception:# pragma: no cover
        finalids=[]
    query = {"$and": [{"$or": finalids}]}
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

@log_with_args(level)
def get_runs_of_variant(self, entry_id: Optional[str], qparams: RequestParams, dataset: str):
    collection = 'g_variants'
    mongo_collection = client.beacon.runs
    query = {"$and": [{"variantInternalId": entry_id}]}
    query_parameters, parameters_as_filters = apply_request_parameters(self, query, qparams, dataset)
    if parameters_as_filters == True:
        query, parameters_as_filters = apply_request_parameters(self, query, qparams, dataset)# pragma: no cover
        query_parameters={}# pragma: no cover
    else:
        query=query_parameters
    collection='runs'
    HGVSIds = client.beacon.genomicVariations \
        .find(query, {"identifiers.genomicHGVSId": 1, "datasetId": 1, "_id": 0})
    HGVSDataset=HGVSIds[0]["datasetId"]
    if dataset != HGVSDataset:
        schema = DefaultSchemas.INDIVIDUALS
        return schema, 0, 0, [], dataset
    HGVSIds=list(HGVSIds)
    HGVSId=HGVSIds[0]["identifiers"]["genomicHGVSId"]
    queryHGVSId={"datasetId": dataset, "id": HGVSId}
    string_of_ids = client.beacon.caseLevelData \
        .find(queryHGVSId)
    targets = client.beacon.targets \
        .find({"datasetId": HGVSDataset}, {"biosampleIds": 1, "_id": 0})
    targets=list(targets)
    list_of_targets=targets[0]["biosampleIds"]
    list_of_positions_strings= string_of_ids[0]
    biosampleIds=[]
    filters=qparams.query.filters
    if filters != []:
        for filter in filters:
            if filter['id']=='GENO:GENO_0000458':
                for key, value in list_of_positions_strings.items():
                    if key != 'datasetId' and key != 'id' and key != '_id' and value != '11':
                        biosampleIds.append(list_of_targets[int(key)])
                qparams.query.filters.remove(filter)
            elif filter['id']=='GENO:GENO_0000136':
                for key, value in list_of_positions_strings.items():
                    if key != 'datasetId' and key != 'id' and key != '_id' and value != '10' and value != '01':
                        biosampleIds.append(list_of_targets[int(key)])
                qparams.query.filters.remove(filter)
            else:
                for key, value in list_of_positions_strings.items():
                    if key != 'datasetId' and key != 'id' and key != '_id':
                        biosampleIds.append(list_of_targets[int(key)])
    else:
        for key, value in list_of_positions_strings.items():
            if key != 'datasetId' and key != 'id' and key != '_id':
                biosampleIds.append(list_of_targets[int(key)])
    try:
        finalids=[]
        for bioid in biosampleIds:
            finalids.append({"biosampleId": bioid})
    except Exception:# pragma: no cover
        finalids=[]
    query = {"$and": [{"$or": finalids}]}
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

@log_with_args(level)
def get_analyses_of_variant(self, entry_id: Optional[str], qparams: RequestParams, dataset: str):
    collection = 'g_variants'
    mongo_collection = client.beacon.analyses
    query = {"$and": [{"variantInternalId": entry_id}]}
    query_parameters, parameters_as_filters = apply_request_parameters(self, query, qparams, dataset)
    if parameters_as_filters == True:
        query, parameters_as_filters = apply_request_parameters(self, query, qparams, dataset)# pragma: no cover
        query_parameters={}# pragma: no cover
    else:
        query=query_parameters
    collection='analyses'
    HGVSIds = client.beacon.genomicVariations \
        .find(query, {"identifiers.genomicHGVSId": 1, "datasetId": 1, "_id": 0})
    HGVSDataset=HGVSIds[0]["datasetId"]
    if dataset != HGVSDataset:
        schema = DefaultSchemas.INDIVIDUALS
        return schema, 0, 0, [], dataset
    HGVSIds=list(HGVSIds)
    HGVSId=HGVSIds[0]["identifiers"]["genomicHGVSId"]
    queryHGVSId={"datasetId": dataset, "id": HGVSId}
    string_of_ids = client.beacon.caseLevelData \
        .find(queryHGVSId)
    targets = client.beacon.targets \
        .find({"datasetId": HGVSDataset}, {"biosampleIds": 1, "_id": 0})
    targets=list(targets)
    list_of_targets=targets[0]["biosampleIds"]
    list_of_positions_strings= string_of_ids[0]
    biosampleIds=[]
    filters=qparams.query.filters
    if filters != []:
        for filter in filters:
            if filter['id']=='GENO:GENO_0000458':
                for key, value in list_of_positions_strings.items():
                    if key != 'datasetId' and key != 'id' and key != '_id' and value != '11':
                        biosampleIds.append(list_of_targets[int(key)])
                qparams.query.filters.remove(filter)
            elif filter['id']=='GENO:GENO_0000136':
                for key, value in list_of_positions_strings.items():
                    if key != 'datasetId' and key != 'id' and key != '_id' and value != '10' and value != '01':
                        biosampleIds.append(list_of_targets[int(key)])
                qparams.query.filters.remove(filter)
            else:
                for key, value in list_of_positions_strings.items():
                    if key != 'datasetId' and key != 'id' and key != '_id':
                        biosampleIds.append(list_of_targets[int(key)])
    else:
        for key, value in list_of_positions_strings.items():
            if key != 'datasetId' and key != 'id' and key != '_id':
                biosampleIds.append(list_of_targets[int(key)])
    try:
        finalids=[]
        for bioid in biosampleIds:
            finalids.append({"biosampleId": bioid})
    except Exception:# pragma: no cover
        finalids=[]
    query = {"$and": [{"$or": finalids}]}
    query = apply_filters(self, query, qparams.query.filters, collection, {}, dataset)
    schema = DefaultSchemas.ANALYSES
    include = qparams.query.include_resultset_responses
    limit = qparams.query.pagination.limit
    skip = qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100# pragma: no cover
    idq="biosampleId"
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip, mongo_collection, idq)
    return schema, count, dataset_count, docs, dataset

@log_with_args(level)
def get_individuals_of_variant(self, entry_id: Optional[str], qparams: RequestParams, dataset: str):
    collection = 'g_variants'
    mongo_collection = client.beacon.individuals
    query = {"$and": [{"variantInternalId": entry_id}]}
    query_parameters, parameters_as_filters = apply_request_parameters(self, query, qparams, dataset)
    if parameters_as_filters == True:
        query, parameters_as_filters = apply_request_parameters(self, query, qparams, dataset)# pragma: no cover
        query_parameters={}# pragma: no cover
    else:
        query=query_parameters
    collection='individuals'
    HGVSIds = client.beacon.genomicVariations \
        .find(query, {"identifiers.genomicHGVSId": 1, "datasetId": 1, "_id": 0})
    HGVSIds=list(HGVSIds)
    HGVSDataset=HGVSIds[0]["datasetId"]
    if dataset != HGVSDataset:
        schema = DefaultSchemas.INDIVIDUALS
        return schema, 0, 0, [], dataset
    HGVSId=HGVSIds[0]["identifiers"]["genomicHGVSId"]
    queryHGVSId={"datasetId": HGVSDataset, "id": HGVSId}
    string_of_ids = client.beacon.caseLevelData \
        .find(queryHGVSId)
    targets = client.beacon.targets \
        .find({"datasetId": HGVSDataset}, {"biosampleIds": 1, "_id": 0})
    targets=list(targets)
    list_of_targets=targets[0]["biosampleIds"]
    list_of_positions_strings= string_of_ids[0]
    biosampleIds=[]
    filters=qparams.query.filters
    if filters != []:
        for filter in filters:
            if filter['id']=='GENO:GENO_0000458':
                for key, value in list_of_positions_strings.items():
                    if key != 'datasetId' and key != 'id' and key != '_id' and value != '11':
                        biosampleIds.append(list_of_targets[int(key)])
                qparams.query.filters.remove(filter)
            elif filter['id']=='GENO:GENO_0000136':
                for key, value in list_of_positions_strings.items():
                    if key != 'datasetId' and key != 'id' and key != '_id' and value != '10' and value != '01':
                        biosampleIds.append(list_of_targets[int(key)])
                qparams.query.filters.remove(filter)
            else:
                for key, value in list_of_positions_strings.items():
                    if key != 'datasetId' and key != 'id' and key != '_id':
                        biosampleIds.append(list_of_targets[int(key)])
    else:
        for key, value in list_of_positions_strings.items():
            if key != 'datasetId' and key != 'id' and key != '_id':
                biosampleIds.append(list_of_targets[int(key)])
    try:
        finalquery={}
        finalquery["$or"]=[]
        for finalid in biosampleIds:
            query = {"id": finalid}
            finalquery["$or"].append(query)
        individual_id = client.beacon.biosamples \
            .find(finalquery, {"individualId": 1, "_id": 0})
        try:
            finalids=[]
            for indid in individual_id:
                finalids.append(indid["individualId"])
        except Exception:# pragma: no cover
            finalids=[]
        if finalids==[]:
            finalids=biosampleIds
    except Exception:
        finalids=biosampleIds
    finalquery={}
    finalquery["$or"]=[]
    for finalid in finalids:
        query = {"id": finalid}
        finalquery["$or"].append(query)
    superfinalquery={}
    superfinalquery["$and"]=[finalquery]
    query = apply_filters(self, superfinalquery, qparams.query.filters, collection, {}, dataset)
    schema = DefaultSchemas.INDIVIDUALS
    include = qparams.query.include_resultset_responses
    limit = qparams.query.pagination.limit
    skip = qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100# pragma: no cover
    idq="id"
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip, mongo_collection, idq)
    return schema, count, dataset_count, docs, dataset