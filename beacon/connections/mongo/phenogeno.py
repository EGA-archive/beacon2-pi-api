from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level
from beacon.conf import genomicVariant, analysis, run, biosample, individual
from beacon.request.classes import RequestAttributes
from beacon.connections.mongo.request_parameters import apply_request_parameters
from beacon.connections.mongo.filters import apply_filters
from beacon.connections.mongo.utils import get_docs_by_response_type, query_id
from beacon.connections.mongo.__init__ import genomicVariations, targets as targets_, caseLevelData, biosamples, runs, cohorts, analyses, datasets, individuals
from beacon.connections.mongo.utils import get_count, get_documents_for_cohorts, get_phenotypic_cross_query_attributes

@log_with_args(level)
def get_phenotypic_endpoint(self, dataset: str):
    parameters_as_filters=False
    query_parameters, parameters_as_filters = apply_request_parameters(self, {}, dataset)
    if parameters_as_filters == True and query_parameters != {'$and': []}:
        query, parameters_as_filters = apply_request_parameters(self, {}, dataset)
        query_parameters={}
    elif query_parameters != {'$and': []}:
        query=query_parameters
    elif query_parameters == {'$and': []}:
        query_parameters = {}
        query={}
    query = apply_filters(self, query, RequestAttributes.qparams.query.filters, query_parameters, dataset)
    if query == {} and query_parameters != {} and parameters_as_filters == False:
        return 0, -1, None, dataset
    include = RequestAttributes.qparams.query.includeResultsetResponses
    limit = RequestAttributes.qparams.query.pagination.limit
    skip = RequestAttributes.qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip)
    return count, dataset_count, docs, dataset

@log_with_args(level)
def get_phenotypic_endpoint_with_id(self, dataset: str):
    if RequestAttributes.entry_type == genomicVariant.endpoint_name:
        query = {"$and": [{"_id": RequestAttributes.entry_id}]}
        query_parameters, parameters_as_filters = apply_request_parameters(self, query, dataset)
        if parameters_as_filters == True:
            query, parameters_as_filters = apply_request_parameters(self, {}, dataset)
            query_parameters={}
        else:
            query=query_parameters
    else:
        query, parameters_as_filters = apply_request_parameters(self, {}, dataset)
    query = apply_filters(self, query, RequestAttributes.qparams.query.filters, {}, dataset)
    if RequestAttributes.entry_type != genomicVariant.endpoint_name:
        query = query_id(self, query, RequestAttributes.entry_id)
    include = RequestAttributes.qparams.query.includeResultsetResponses
    limit = RequestAttributes.qparams.query.pagination.limit
    skip = RequestAttributes.qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip)
    return count, dataset_count, docs, dataset

@log_with_args(level)
def get_variants_of_phenotypic_endpoint(self, dataset: str):
    if RequestAttributes.pre_entry_type == analysis.endpoint_name or RequestAttributes.pre_entry_type == run.endpoint_name:
        query = {"$and": [{"id": RequestAttributes.entry_id}]}
        query = apply_filters(self, query, RequestAttributes.qparams.query.filters, {}, dataset)
        if RequestAttributes.pre_entry_type == analysis.endpoint_name:
            initial_ids = analyses \
                .find_one(query, {"biosampleId": 1, "_id": 0})
        else:
            initial_ids = runs \
                .find_one(query, {"biosampleId": 1, "_id": 0})   
        RequestAttributes.entry_id = initial_ids["biosampleId"]
    try:
        targets = targets_ \
            .find({"datasetId": dataset}, {"biosampleIds": 1, "_id": 0})
        position=0
        bioids=targets[0]["biosampleIds"]
    except Exception:
        return 0, -1, None, dataset
    for bioid in bioids:
        if bioid == RequestAttributes.entry_id:
            break
        position+=1
    if position == len(bioids):
        return 0, -1, None, dataset
    position=str(position)
    query_cl={"$or": [{ position: "10", "datasetId": dataset},{ position: "11", "datasetId": dataset}, { position: "01", "datasetId": dataset}, { position: "y", "datasetId": dataset}]}
    string_of_ids = caseLevelData \
        .find(query_cl, {"id": 1, "_id": 0}).limit(RequestAttributes.qparams.query.pagination.limit).skip(RequestAttributes.qparams.query.pagination.skip)
    HGVSIds=list(string_of_ids)
    query={}
    queryHGVS={}
    listHGVS=[]
    for HGVSId in HGVSIds:
        justid=HGVSId["id"]
        listHGVS.append(justid)
    queryHGVS["$in"]=listHGVS
    query["identifiers.genomicHGVSId"]=queryHGVS
    query, parameters_as_filters = apply_request_parameters(self, query, dataset)
    query = apply_filters(self, query, RequestAttributes.qparams.query.filters, {}, dataset)
    include = RequestAttributes.qparams.query.includeResultsetResponses
    limit = RequestAttributes.qparams.query.pagination.limit
    skip = RequestAttributes.qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip)
    return count, dataset_count, docs, dataset

@log_with_args(level)
def get_phenotypic_endpoint_of_variants(self, dataset: str):
    query = {"$and": [{"_id": RequestAttributes.entry_id}]}
    query_parameters, parameters_as_filters = apply_request_parameters(self, query, dataset)
    if parameters_as_filters == True and query_parameters != {'$and': []}:
        query, parameters_as_filters = apply_request_parameters(self, query, dataset)
        query_parameters={}
    elif query_parameters != {'$and': []}:
        query=query_parameters
    elif query_parameters == {'$and': []}:
        query_parameters = {}
        query={}
    HGVSIds = genomicVariations \
        .find(query, {"identifiers.genomicHGVSId": 1, "datasetId": 1, "_id": 0})
    HGVSIds=list(HGVSIds)
    HGVSDataset=HGVSIds[0]["datasetId"]
    if dataset != HGVSDataset:
        return 0, 0, [], dataset
    HGVSId=HGVSIds[0]["identifiers"]["genomicHGVSId"]
    queryHGVSId={"datasetId": HGVSDataset, "id": HGVSId}
    string_of_ids = caseLevelData \
        .find(queryHGVSId)
    try:
        targets = targets_ \
            .find({"datasetId": HGVSDataset}, {"biosampleIds": 1, "_id": 0})
        targets=list(targets)
        list_of_targets=targets[0]["biosampleIds"]
        list_of_positions_strings= string_of_ids[0]
    except Exception:
        return 0, 0, [], dataset
    biosampleIds=[]
    biosampleIds_restricted=[]
    filters=RequestAttributes.qparams.query.filters
    new_filters=[]
    if filters != []:
        for filter in filters:
            if filter['id']=='GENO:0000458':
                for key, value in list_of_positions_strings.items():
                    if key != 'datasetId' and key != 'id' and key != '_id' and value != '11':
                        biosampleIds_restricted.append(list_of_targets[int(key)])
                RequestAttributes.qparams.query.filters.remove(filter)
            elif filter['id']=='GENO:0000136':
                for key, value in list_of_positions_strings.items():
                    if key != 'datasetId' and key != 'id' and key != '_id' and value != '10' and value != '01' and value != 'y':
                        biosampleIds_restricted.append(list_of_targets[int(key)])
                RequestAttributes.qparams.query.filters.remove(filter)
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
    if RequestAttributes.entry_type != individual.endpoint_name:
        finalids=biosampleIds
        try:
            finalids=[]
            if RequestAttributes.entry_type == biosample.endpoint_name:
                idq = 'id'
            else:
                idq = 'biosampleId'
            for bioid in biosampleIds:
                finalids.append({idq: bioid})
        except Exception:
            finalids=[]
        superfinalquery = {"$and": [{"$or": finalids}]}
    else:
        try:
            finalquery={}
            finalquery["$or"]=[]
            for finalid in biosampleIds:
                query = {"id": finalid}
                finalquery["$or"].append(query)
            individual_id = biosamples \
                .find(finalquery, {"individualId": 1, "_id": 0})
            try:
                finalids=[]
                for indid in individual_id:
                    finalids.append(indid["individualId"])
            except Exception:
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
    query = apply_filters(self, superfinalquery, new_filters, {}, dataset)
    include = RequestAttributes.qparams.query.includeResultsetResponses
    limit = RequestAttributes.qparams.query.pagination.limit
    skip = RequestAttributes.qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip)
    return count, dataset_count, docs, dataset

@log_with_args(level)
def get_variants_of_dataset(self, dataset: str):
    dataset_count=0
    limit = RequestAttributes.qparams.query.pagination.limit
    query_count={}
    query_count["$or"]=[]
    if dataset == RequestAttributes.entry_id:
        queryid={}
        queryid["datasetId"]=dataset
        query_count["$or"].append(queryid)
    else:
        return 0, 0, None, dataset
    query = apply_filters(self, query_count, RequestAttributes.qparams.query.filters, {}, dataset)
    include = RequestAttributes.qparams.query.includeResultsetResponses
    limit = RequestAttributes.qparams.query.pagination.limit
    skip = RequestAttributes.qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip)
    return count, dataset_count, docs, dataset

@log_with_args(level)
def get_phenotypic_endpoint_of_dataset(self, dataset: str):
    dataset_count=0
    query = apply_filters(self, {}, RequestAttributes.qparams.query.filters, {}, dataset)
    query = query_id(self, query, RequestAttributes.entry_id)
    count = get_count(self, datasets, query)
    dict_in={}
    if dataset == RequestAttributes.entry_id:
        dict_in['datasetId']=RequestAttributes.entry_id
    else:
        return 0, 0, None, dataset
    query = apply_filters(self, dict_in, RequestAttributes.qparams.query.filters, {}, dataset)
    include = RequestAttributes.qparams.query.includeResultsetResponses
    limit = RequestAttributes.qparams.query.pagination.limit
    skip = RequestAttributes.qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip)
    return count, dataset_count, docs, dataset

@log_with_args(level)
def get_phenotypic_endpoint_of_cohort(self, dataset: str):
    dataset_count=0
    dataset_found = cohorts \
        .find({"id": RequestAttributes.entry_id}, {"datasetId": 1, "_id": 0})
    dataset_found=list(dataset_found)
    dict_in={}
    dataset_found=dataset_found[0]["datasetId"]
    if dataset == dataset_found:
        dict_in['datasetId']=dataset_found
    else:
        return 0, 0, None, dataset
    query = apply_filters(self, dict_in, RequestAttributes.qparams.query.filters, {}, dataset)
    count = get_count(self, cohorts, query)
    limit = RequestAttributes.qparams.query.pagination.limit
    include = RequestAttributes.qparams.query.includeResultsetResponses
    skip = RequestAttributes.qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip)
    return count, dataset_count, docs, dataset

@log_with_args(level)
def get_variants_of_cohort(self, dataset: str):
    dataset_count=0
    limit = RequestAttributes.qparams.query.pagination.limit
    include = RequestAttributes.qparams.query.includeResultsetResponses
    dataset_found = cohorts \
        .find({"id": RequestAttributes.entry_id}, {"datasetId": 1, "_id": 0})
    dataset_found=list(dataset_found)
    dict_in={}
    dataset_found=dataset_found[0]["datasetId"]
    if dataset == dataset_found:
        dict_in['datasetId']=dataset_found
    else:
        return 0, 0, None, dataset
    query = apply_filters(self, dict_in, RequestAttributes.qparams.query.filters, {}, dataset)
    count = get_count(self, cohorts, query)
    query_count={}
    query_count["$or"]=[]
    docs = get_documents_for_cohorts(self,
        cohorts,
        query,
        RequestAttributes.qparams.query.pagination.skip,
        RequestAttributes.qparams.query.pagination.skip*limit
    )
    for doc in docs:
        if doc["datasetId"] == dataset:
            RequestAttributes.entry_id = dataset
    if dataset == RequestAttributes.entry_id:
        queryid={}
        queryid["datasetId"]=dataset
        query_count["$or"].append(queryid)
    else:
        return 0, 0, None, dataset
    query = apply_filters(self, query_count, RequestAttributes.qparams.query.filters, {}, dataset)
    skip = RequestAttributes.qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip)
    return count, dataset_count, docs, dataset

@log_with_args(level)
def get_phenotypic_cross_query(self, dataset: str):
    mapping = get_phenotypic_cross_query_attributes(self, RequestAttributes.entry_type, RequestAttributes.pre_entry_type)
    items_found = mapping["secondary_collection"] \
    .find({"id": RequestAttributes.entry_id, "datasetId": dataset}, {mapping["idq2"]: 1, "_id": 0})
    list_of_itemsfound=[]
    for itemfound in items_found:
        list_of_itemsfound.append(itemfound[mapping["idq2"]])
    query = {mapping["idq"]: {"$in": list_of_itemsfound}}
    query = apply_filters(self, query, RequestAttributes.qparams.query.filters, {}, dataset)
    include = RequestAttributes.qparams.query.includeResultsetResponses
    limit = RequestAttributes.qparams.query.pagination.limit
    skip = RequestAttributes.qparams.query.pagination.skip
    if limit > 100 or limit == 0:
        limit = 100
    count, dataset_count, docs = get_docs_by_response_type(self, include, query, dataset, limit, skip)
    return count, dataset_count, docs, dataset
