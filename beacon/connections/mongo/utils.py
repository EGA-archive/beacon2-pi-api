from pymongo.cursor import Cursor
from beacon.connections.mongo.__init__ import client, counts as counts_, filtering_terms, genomicVariations, targets as targets_, caseLevelData, biosamples, runs, cohorts, analyses, datasets, individuals
from pymongo.collection import Collection
from beacon.logs.logs import log_with_args_mongo, LOG
from beacon.conf.conf import level
from beacon.exceptions.exceptions import InvalidRequest
import aiohttp.web as web
from beacon.conf import genomicVariant, analysis, run, biosample, individual, dataset, cohort
from beacon.request.classes import RequestAttributes
from beacon.response.classes import SingleDatasetResponse

@log_with_args_mongo(level)
def lengthquery(self, collection: Collection,query: dict):
    #LOG.debug(query)
    return collection.find(query, {"_id": 1, "variation.location.interval.start.value": 1, "variation.location.interval.end.value": 1}).max_time_ms(100 * 1000)

@log_with_args_mongo(level)
def query_id(self, query: dict, document_id) -> dict:
    query["id"] = document_id
    return query

@log_with_args_mongo(level)
def join_query(self, mongo_collection, query: dict, original_id, dataset: str):
    #LOG.debug(query)
    excluding_fields={"_id": 0, original_id: 1}
    try:
        query["$and"].append({"datasetId": dataset})
    except Exception:
        query["$and"]=[]
        query["$and"].append({"datasetId": dataset})
    return mongo_collection.find(query, excluding_fields).max_time_ms(100 * 1000)

@log_with_args_mongo(level)
def get_documents(self, collection: Collection, query: dict, skip: int, limit: int) -> Cursor:
    return collection.find(query,{"_id": 0, "datasetId": 0}).skip(skip).limit(limit).max_time_ms(100 * 1000)

@log_with_args_mongo(level)
def get_documents_for_cohorts(self, collection: Collection, query: dict, skip: int, limit: int) -> Cursor:
    return collection.find(query,{"_id": 0}).skip(skip).limit(limit).max_time_ms(100 * 1000)

@log_with_args_mongo(level)
def get_count(self, collection: Collection, query: dict) -> int:
    if not query:
        return collection.estimated_document_count()
    else:
        counts=counts_.find({"id": str(query), "collection": str(collection)})
        try:
            counts=list(counts)
            if counts == []:
                total_counts=collection.count_documents(query)
                insert_dict={}
                insert_dict['id']=str(query)
                insert_dict['num_results']=total_counts
                insert_dict['collection']=str(collection)
                insert_total=counts_.insert_one(insert_dict)
            else:
                total_counts=counts[0]["num_results"]
        except Exception as e:
            insert_dict={}
            insert_dict['id']=str(query)
            total_counts=0
            insert_dict['num_results']=total_counts
            insert_dict['collection']=str(collection)
            insert_total=counts_.insert_one(insert_dict)
        return total_counts

@log_with_args_mongo(level)
def get_docs_by_response_type(self, include: str, query: dict, dataset: SingleDatasetResponse, limit: int, skip: int):
    if include == 'ALL':
        query_count=query
        query_count["$or"]=[]
        queryid={}
        queryid['datasetId']=dataset.dataset
        query_count["$or"].append(queryid)
        if query_count["$or"]!=[]:
            dataset_count = get_count(self, RequestAttributes.mongo_collection, query_count)
            docs = get_documents(
                self,
                RequestAttributes.mongo_collection,
                query_count,
                skip*limit,
                limit
            )
            docs=list(docs)
    elif include == 'MISS':
        query_count=query
        query_count["$or"]=[]
        queryid={}
        queryid['datasetId']=dataset.dataset
        query_count["$or"].append(queryid)
        if query_count["$or"]!=[]:
            dataset_count = get_count(self, RequestAttributes.mongo_collection, query_count)
            docs = get_documents(
                self,
                RequestAttributes.mongo_collection,
                query_count,
                skip*limit,
                limit
            )
            docs=list(docs)
        else:
            dataset_count=0
        if dataset_count !=0:
            dataset.dataset_count=-1
            return dataset
    else:
        query_count=query
        query_count["$or"]=[]
        queryid={}
        queryid['datasetId']=dataset.dataset
        query_count["$or"].append(queryid)
        if query_count["$or"]!=[]:
            dataset_count = get_count(self, RequestAttributes.mongo_collection, query_count)
            if dataset_count == 0:
                docs = []
            else:
                docs = get_documents(
                    self,
                    RequestAttributes.mongo_collection,
                    query_count,
                    skip*limit,
                    limit
                )
                docs=list(docs)
        else:
            dataset_count=0
        if dataset_count==0:
            dataset.dataset_count=-1
            return dataset
    dataset.dataset_count=dataset_count
    dataset.docs=docs
    return dataset

@log_with_args_mongo(level)
def get_filtering_documents(self, collection: Collection, query: dict, remove_id: dict,skip: int, limit: int) -> Cursor:
    ##LOG.debug("FINAL QUERY: {}".format(query))
    return collection.find(query,remove_id).skip(skip).limit(limit).max_time_ms(100 * 1000)

@log_with_args_mongo(level)
def choose_scope(self, scope, filter):
    query_filtering={}
    query_filtering['$and']=[]
    dict_id={}
    dict_id['id']=filter.id
    query_filtering['$and'].append(dict_id)
    docs = get_documents(self,
    filtering_terms,
    query_filtering,
    0,
    1
    )
    docs = list(docs)
    if docs == []:
        raise InvalidRequest("The filtering term: {} is not a valid filtering term.".format(filter.id))
    try:
        fterm=docs[0]
        scopes=fterm["scopes"]
    except Exception:
        scopes=[]
    if scope is None:
        if scopes == []:
            if filter.id not in ["GENO:0000136", "GENO:0000458"]:
                if RequestAttributes.entry_type == genomicVariant.endpoint_name:
                    scope = 'genomicVariation'
                else:
                    scope = RequestAttributes.entry_type[0:-1]
            else:
                scope = None
            return scope
        else:
            for scoped in scopes:
                if str(scoped)+'s'==RequestAttributes.entry_type and RequestAttributes.entry_type != genomicVariant.endpoint_name:
                    scope=str(scoped)
                    return scope
                elif str(scoped)=='genomicVariation' and RequestAttributes.entry_type==genomicVariant.endpoint_name:
                    scope=str(scoped)
                    return scope
            if len(scopes) == 1:
                scope = scopes[0]
                return scope
            else:
                raise InvalidRequest("Look at filtering terms endpoint and select a scope from one of the available scope values for this filtering term: {}".format(filter.id))
    else:
        for scoped in scopes:
            if scope == scoped:
                return scope
        raise InvalidRequest("Scope requested in filtering term does not match any of its possible scopes. Look at filtering terms endpoint to know which scopes you can select for this filtering term: {}".format(filter.id))
    
@log_with_args_mongo(level)
def get_phenotypic_cross_query_attributes(self, entry_type, pre_entry_type):
    mapping = {individual.endpoint_name: {analysis.endpoint_name: {"idq": "id",
                                                         "idq2": "individualId",
                                                         "secondary_collection": analyses},
                                        biosample.endpoint_name: {"idq": "id",
                                                         "idq2": "individualId",
                                                         "secondary_collection": biosamples},
                                        run.endpoint_name: {"idq": "id",
                                                        "idq2": "individualId",
                                                        "secondary_collection": runs}},
    biosample.endpoint_name: {analysis.endpoint_name: {"idq": "id",
                                                    "idq2": "biosampleId",
                                                    "secondary_collection": analyses},
                            individual.endpoint_name: {"idq": "individualId",
                                                    "idq2": "id",
                                                    "secondary_collection": individuals},
                            run.endpoint_name: {"idq": "id",
                                                    "idq2": "biosampleId",
                                                    "secondary_collection": runs}},
    analysis.endpoint_name: {run.endpoint_name: {"idq": "biosampleId",
                                                    "idq2": "biosampleId",
                                                    "secondary_collection": runs},
                            biosample.endpoint_name: {"idq": "biosampleId",
                                                    "idq2": "id",
                                                    "secondary_collection": biosamples},
                            individual.endpoint_name: {"idq": "individualId",
                                                    "idq2": "id",
                                                    "secondary_collection": individuals}},
    run.endpoint_name: {biosample.endpoint_name: {"idq": "biosampleId",
                                                    "idq2": "id",
                                                    "secondary_collection": biosamples},
                        analysis.endpoint_name: {"idq": "biosampleId",
                                                    "idq2": "biosampleId",
                                                    "secondary_collection": analyses},
                        individual.endpoint_name: {"idq": "individualId",
                                                    "idq2": "id",
                                                    "secondary_collection": individuals}},                                                                                                                                                                                                                                                                                                                                                                                                                                  
    cohort.endpoint_name: {biosample.endpoint_name: {"idq": "datasetId",
                                                    "idq2": "datasetId",
                                                    "secondary_collection": biosamples},
                        analysis.endpoint_name: {"idq": "datasetId",
                                                    "idq2": "datasetId",
                                                    "secondary_collection": analyses},
                        dataset.endpoint_name: {"idq": "datasetId",
                                                    "idq2": "id",
                                                    "secondary_collection": datasets},
                        genomicVariant.endpoint_name: {"idq": "datasetId",
                                                    "idq2": "datasetId",
                                                    "secondary_collection": genomicVariations},
                        individual.endpoint_name: {"idq": "datasetId",
                                                    "idq2": "datasetId",
                                                    "secondary_collection": individuals},
                        run.endpoint_name: {"idq": "datasetId",
                                                    "idq2": "datasetId",
                                                    "secondary_collection": runs}},
    dataset.endpoint_name: {biosample.endpoint_name: {"idq": "id",
                                                    "idq2": "datasetId",
                                                    "secondary_collection": biosamples},
                        analysis.endpoint_name: {"idq": "id",
                                                    "idq2": "datasetId",
                                                    "secondary_collection": analyses},
                        cohort.endpoint_name: {"idq": "id",
                                                    "idq2": "datasetId",
                                                    "secondary_collection": cohorts},
                        genomicVariant.endpoint_name: {"idq": "id",
                                                    "idq2": "datasetId",
                                                    "secondary_collection": genomicVariations},
                        individual.endpoint_name: {"idq": "id",
                                                    "idq2": "datasetId",
                                                    "secondary_collection": individuals},
                        run.endpoint_name: {"idq": "id",
                                                    "idq2": "datasetId",
                                                    "secondary_collection": runs}}}
    return mapping[entry_type][pre_entry_type]