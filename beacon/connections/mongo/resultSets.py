from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level
from beacon.conf import genomicVariant, analysis, run, biosample
from beacon.request.classes import ErrorClass
from beacon.connections.mongo.request_parameters import apply_request_parameters
from beacon.connections.mongo.filters import apply_filters
from beacon.request.parameters import RequestParams
from typing import Optional
from beacon.connections.mongo.utils import get_docs_by_response_type, query_id
from beacon.connections.mongo import client, genomicVariations
from beacon.connections.mongo.utils import get_count, get_documents_for_cohorts

@log_with_args(level)
def get_resultSet(self, entry_id: Optional[str], qparams: RequestParams, dataset: str, collection, mongo_collection, schema, idq, entry_type):
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
    if query == {} and query_parameters != {} and parameters_as_filters == False:
        return schema, 0, -1, None, dataset
    include = qparams.query.include_resultset_responses
    limit = qparams.query.pagination.limit
    skip = qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip, mongo_collection, idq)
    return schema, count, dataset_count, docs, dataset

@log_with_args(level)
def get_resultSet_with_id(self, entry_id: Optional[str], qparams: RequestParams, dataset: str, collection, mongo_collection, schema, idq, entry_type):
    if collection == genomicVariant.endpoint_name:
        query = {"$and": [{"variantInternalId": entry_id}]}
        query_parameters, parameters_as_filters = apply_request_parameters(self, query, qparams, dataset)
        if parameters_as_filters == True:
            query, parameters_as_filters = apply_request_parameters(self, {}, qparams, dataset)# pragma: no cover
            query_parameters={}# pragma: no cover
        else:
            query=query_parameters
    else:
        query, parameters_as_filters = apply_request_parameters(self, {}, qparams, dataset)
    query = apply_filters(self, query, qparams.query.filters, collection, {}, dataset)
    if collection != genomicVariant.endpoint_name:
        query = query_id(self, query, entry_id)
    include = qparams.query.include_resultset_responses
    limit = qparams.query.pagination.limit
    skip = qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100# pragma: no cover
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip, mongo_collection, idq)
    return schema, count, dataset_count, docs, dataset

@log_with_args(level)
def get_variants_of_resultSet(self, entry_id: Optional[str], qparams: RequestParams, dataset: str, collection, mongo_collection, schema, idq, entry_type):
    if collection == analysis.endpoint_name or collection == run.endpoint_name:
        query = {"$and": [{"id": entry_id}]}
        query = apply_filters(self, query, qparams.query.filters, collection, {}, dataset)
        initial_ids = collection \
            .find_one(query, {"biosampleId": 1, "_id": 0})
        entry_id = initial_ids["biosampleId"]
    try:
        targets = client.beacon.targets \
            .find({"datasetId": dataset}, {"biosampleIds": 1, "_id": 0})
        position=0
        bioids=targets[0]["biosampleIds"]
    except Exception:
        return schema, 0, -1, None, dataset
    for bioid in bioids:
        if bioid == entry_id:
            break
        position+=1
    if position == len(bioids):# pragma: no cover
        return schema, 0, -1, None, dataset
    position=str(position)
    query_cl={"$or": [{ position: "10", "datasetId": dataset},{ position: "11", "datasetId": dataset}, { position: "01", "datasetId": dataset}, { position: "y", "datasetId": dataset}]}
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
    query, parameters_as_filters = apply_request_parameters(self, query, qparams, dataset)
    query = apply_filters(self, query, qparams.query.filters, collection, {}, dataset)
    include = qparams.query.include_resultset_responses
    limit = qparams.query.pagination.limit
    skip = qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100# pragma: no cover
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip, mongo_collection, idq)
    return schema, count, dataset_count, docs, dataset

@log_with_args(level)
def get_resultSet_of_variants(self, entry_id: Optional[str], qparams: RequestParams, dataset: str, collection, mongo_collection, schema, idq, entry_type):
    query = {"$and": [{"variantInternalId": entry_id}]}
    query_parameters, parameters_as_filters = apply_request_parameters(self, query, qparams, dataset)
    if parameters_as_filters == True and query_parameters != {'$and': []}:
        query, parameters_as_filters = apply_request_parameters(self, query, qparams, dataset)# pragma: no cover
        query_parameters={}# pragma: no cover
    elif query_parameters != {'$and': []}:
        query=query_parameters
    elif query_parameters == {'$and': []}:
        query_parameters = {}
        query={}
    HGVSIds = genomicVariations \
        .find(query, {"identifiers.genomicHGVSId": 1, "datasetId": 1, "_id": 0})
    HGVSIds=list(HGVSIds)
    HGVSDataset=HGVSIds[0]["datasetId"]
    if dataset != HGVSDataset:# pragma: no cover
        return schema, 0, 0, [], dataset
    HGVSId=HGVSIds[0]["identifiers"]["genomicHGVSId"]
    queryHGVSId={"datasetId": HGVSDataset, "id": HGVSId}
    string_of_ids = client.beacon.caseLevelData \
        .find(queryHGVSId)
    try:
        targets = client.beacon.targets \
            .find({"datasetId": HGVSDataset}, {"biosampleIds": 1, "_id": 0})
        targets=list(targets)
        list_of_targets=targets[0]["biosampleIds"]
        list_of_positions_strings= string_of_ids[0]
    except Exception:
        return schema, 0, 0, [], dataset
    biosampleIds=[]
    biosampleIds_restricted=[]
    filters=qparams.query.filters
    new_filters=[]
    if filters != []:
        for filter in filters:
            if filter['id']=='GENO:0000458':
                for key, value in list_of_positions_strings.items():
                    if key != 'datasetId' and key != 'id' and key != '_id' and value != '11':
                        biosampleIds_restricted.append(list_of_targets[int(key)])
                qparams.query.filters.remove(filter)
            elif filter['id']=='GENO:0000136':
                for key, value in list_of_positions_strings.items():
                    if key != 'datasetId' and key != 'id' and key != '_id' and value != '10' and value != '01' and value != 'y':
                        biosampleIds_restricted.append(list_of_targets[int(key)])
                qparams.query.filters.remove(filter)
            else:
                new_filters.append(filter)
                for key, value in list_of_positions_strings.items():
                    if key != 'datasetId' and key != 'id' and key != '_id':
                        biosampleIds.append(list_of_targets[int(key)])
    else:
        for key, value in list_of_positions_strings.items():
            if key != 'datasetId' and key != 'id' and key != '_id':
                biosampleIds.append(list_of_targets[int(key)])
    if biosampleIds_restricted != [] and biosampleIds != []:
        for biosampleId in biosampleIds:
            if biosampleId not in biosampleIds_restricted:
                biosampleIds.remove(biosampleId)
    elif biosampleIds_restricted != [] and biosampleIds == []:
        biosampleIds = biosampleIds_restricted
    if collection == biosample.endpoint_name:
        finalids=biosampleIds
        try:
            finalids=[]
            for bioid in biosampleIds:
                finalids.append({idq: bioid})
        except Exception:# pragma: no cover
            finalids=[]
        superfinalquery = {"$and": [{"$or": finalids}]}
    else:
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
                finalids=biosampleIds# pragma: no cover
        except Exception:# pragma: no cover
            finalids=biosampleIds
        finalquery={}
        finalquery["$or"]=[]
        for finalid in finalids:
            query = {idq: finalid}
            finalquery["$or"].append(query)
        superfinalquery={}
        superfinalquery["$and"]=[finalquery]
    query = apply_filters(self, superfinalquery, new_filters, collection, {}, dataset)
    include = qparams.query.include_resultset_responses
    limit = qparams.query.pagination.limit
    skip = qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100# pragma: no cover
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip, mongo_collection, idq)
    return schema, count, dataset_count, docs, dataset

@log_with_args(level)
def get_analyses_of_resultSet(self, entry_id: Optional[str], qparams: RequestParams, dataset: str, collection, mongo_collection, schema, idq, entry_type):
    if collection == run.endpoint_name:
        query = {"id": entry_id}
    else:
        query = {"biosampleId": entry_id}
    query = apply_filters(self, query, qparams.query.filters, collection, {}, dataset)
    include = qparams.query.include_resultset_responses
    limit = qparams.query.pagination.limit
    skip = qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100# pragma: no cover
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip, mongo_collection, idq)
    return schema, count, dataset_count, docs, dataset

@log_with_args(level)
def get_biosamples_of_resultSet(self, entry_id: Optional[str], qparams: RequestParams, dataset: str, collection, mongo_collection, schema, idq, entry_type):
    query = {"individualId": entry_id}
    query, parameters_as_filters = apply_request_parameters(self, query, qparams, dataset)
    query = apply_filters(self, query, qparams.query.filters, collection, {}, dataset)
    include = qparams.query.include_resultset_responses
    limit = qparams.query.pagination.limit
    skip = qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100# pragma: no cover
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip, mongo_collection, idq)
    return schema, count, dataset_count, docs, dataset

@log_with_args(level)
def get_variants_of_dataset(self, entry_id: Optional[str], qparams: RequestParams, dataset: str, collection, mongo_collection, schema, idq, entry_type):
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
        return schema, 0, 0, None, dataset# pragma: no cover
    query = apply_filters(self, query_count, qparams.query.filters, collection, {}, dataset)
    include = qparams.query.include_resultset_responses
    limit = qparams.query.pagination.limit
    skip = qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100# pragma: no cover
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip, mongo_collection, idq)
    return schema, count, dataset_count, docs, dataset

@log_with_args(level)
def get_resultSet_of_dataset(self, entry_id: Optional[str], qparams: RequestParams, dataset: str, collection, mongo_collection, schema, idq, entry_type):
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
        return schema, 0, 0, None, dataset# pragma: no cover
    query = apply_filters(self, dict_in, qparams.query.filters, collection, {}, dataset)
    include = qparams.query.include_resultset_responses
    limit = qparams.query.pagination.limit
    skip = qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100# pragma: no cover
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip, mongo_collection, idq)
    return schema, count, dataset_count, docs, dataset

@log_with_args(level)
def get_resultSet_of_cohort(self, entry_id: Optional[str], qparams: RequestParams, dataset: str, collection, mongo_collection, schema, idq, entry_type):
    dataset_count=0
    limit = qparams.query.pagination.limit
    include = qparams.query.include_resultset_responses
    dataset_found = client.beacon.cohorts \
        .find({"id": entry_id}, {"datasetId": 1, "_id": 0})
    dataset_found=list(dataset_found)
    dict_in={}
    dataset_found=dataset_found[0]["datasetId"]
    if dataset == dataset_found:
        dict_in['datasetId']=dataset_found
    else:
        return schema, 0, 0, None, dataset# pragma: no cover
    query = apply_filters(self, dict_in, qparams.query.filters, collection, {}, dataset)
    count = get_count(self, client.beacon.cohorts, query)
    skip = qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100# pragma: no cover
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip, mongo_collection, idq)
    return schema, count, dataset_count, docs, dataset

@log_with_args(level)
def get_variants_of_cohort(self, entry_id: Optional[str], qparams: RequestParams, dataset: str, collection, mongo_collection, schema, idq, entry_type):
    dataset_count=0
    limit = qparams.query.pagination.limit
    include = qparams.query.include_resultset_responses
    dataset_found = client.beacon.cohorts \
        .find({"id": entry_id}, {"datasetId": 1, "_id": 0})
    dataset_found=list(dataset_found)
    dict_in={}
    dataset_found=dataset_found[0]["datasetId"]
    if dataset == dataset_found:
        dict_in['datasetId']=dataset_found
    else:
        return schema, 0, 0, None, dataset# pragma: no cover
    query = apply_filters(self, dict_in, qparams.query.filters, collection, {}, dataset)
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
        return schema, 0, 0, None, dataset# pragma: no cover
    query = apply_filters(self, query_count, qparams.query.filters, collection, {}, dataset)
    skip = qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100# pragma: no cover
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip, mongo_collection, idq)
    return schema, count, dataset_count, docs, dataset

@log_with_args(level)
def get_runs_of_resultSet(self, entry_id: Optional[str], qparams: RequestParams, dataset: str, collection, mongo_collection, schema, idq, entry_type):
    query = {"individualId": entry_id}
    query = apply_filters(self, query, qparams.query.filters, collection, {}, dataset)
    include = qparams.query.include_resultset_responses
    limit = qparams.query.pagination.limit
    skip = qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100# pragma: no cover
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip, mongo_collection, idq)
    return schema, count, dataset_count, docs, dataset
