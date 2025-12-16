from pymongo.cursor import Cursor
from beacon.connections.mongo.__init__ import client, counts as counts_, filtering_terms
from pymongo.collection import Collection
from beacon.logs.logs import log_with_args_mongo, LOG
from beacon.conf.conf_override import config
from beacon.exceptions.exceptions import InvalidRequest
import aiohttp.web as web
from beacon.request.classes import RequestAttributes
from beacon.response.classes import SingleDatasetResponse
from beacon.models.ga4gh.beacon_v2_default_model.connections.mongo.utils import import_genomicVariant_confile

@log_with_args_mongo(config.level)
def query_id(self, query: dict, document_id) -> dict:
    query["id"] = document_id
    return query

@log_with_args_mongo(config.level)
def query_patientId(self, query: dict, document_id) -> dict:
    query["patientId"] = document_id
    return query

@log_with_args_mongo(config.level)
def join_query(self, mongo_collection, query: dict, original_id, dataset: str):
    #LOG.debug(query)
    excluding_fields={"_id": 0, original_id: 1}
    if dataset != None:
        try:
            query["$and"].append({"datasetId": dataset})
        except Exception:
            query["$and"]=[]
            query["$and"].append({"datasetId": dataset})
    return mongo_collection.find(query, excluding_fields).max_time_ms(100 * 1000)

@log_with_args_mongo(config.level)
def get_documents(self, collection: Collection, query: dict, skip: int, limit: int) -> Cursor:
    return collection.find(query,{"_id": 0, "datasetId": 0}).skip(skip).limit(limit).max_time_ms(100 * 1000)

@log_with_args_mongo(config.level)
def get_documents_for_cohorts(self, collection: Collection, query: dict, skip: int, limit: int) -> Cursor:
    return collection.find(query,{"_id": 0}).skip(skip).limit(limit).max_time_ms(100 * 1000)

@log_with_args_mongo(config.level)
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

@log_with_args_mongo(config.level)
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
            dataset.exists=False
        if dataset_count !=0:
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
            dataset.exists=False
        if dataset_count==0:
            return dataset
    if dataset_count > 0:
        dataset.exists=True
    dataset.dataset_count=dataset_count
    dataset.docs=docs
    return dataset

@log_with_args_mongo(config.level)
def get_filtering_documents(self, collection: Collection, query: dict, remove_id: dict,skip: int, limit: int) -> Cursor:
    ##LOG.debug("FINAL QUERY: {}".format(query))
    # Get the docs by removing the unwanted id
    return collection.find(query,remove_id).skip(skip).limit(limit).max_time_ms(100 * 1000)

@log_with_args_mongo(config.level)
def choose_scope(self, scope, filter):
    # Initiate the dictionaries and create the syntax to query the filtering terms database to get the available scopes
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
    # If there are no docs with the requested filtering term, raise an exception
    if docs == []:
        raise InvalidRequest("The filtering term: {} is not a valid filtering term.".format(filter.id))
    try:
        fterm=docs[0]
        scopes=fterm["scopes"]
    except Exception:
        scopes=[]
    # If there is no scope requested, check if there are any scopes in the filtering term requested
    genomicVariant_confile= import_genomicVariant_confile()
    if scope is None:
        if scopes == []:
            # If there aren't any, check if the filtering term is not a zygosity term
            if filter.id not in ["GENO:0000136", "GENO:0000458"]:
                # If it's not a zygosity term, add the entry type as scop
                if RequestAttributes.entry_type == genomicVariant_confile["genomicVariant"]["endpoint_name"]:
                    scope = 'genomicVariation'
                else:
                    scope = RequestAttributes.entry_type[0:-1]
            else: # If it's a zygosity term, return scope = None, as this is an internal filtering term
                scope = None
            return scope
        else:
            for scoped in scopes:
                # If there are scopes and is an array, check if any scope is equal to the entry type requested, to assign it as the scope
                if str(scoped)+'s'==RequestAttributes.entry_type and RequestAttributes.entry_type != genomicVariant_confile["genomicVariant"]["endpoint_name"]:
                    scope=str(scoped)
                    return scope
                elif str(scoped)=='genomicVariation' and RequestAttributes.entry_type==genomicVariant_confile["genomicVariant"]["endpoint_name"]:
                    scope=str(scoped)
                    return scope
            # If there is only one scope for the filtering term, assign this scope
            if len(scopes) == 1:
                scope = scopes[0]
                return scope
            # Otherwise, make compulsory to select a scope for the filtering term
            else:
                raise InvalidRequest("Look at filtering terms endpoint and select a scope from one of the available scope values for this filtering term: {}".format(filter.id))
    else:
        # If a scope is requested, use it as the scope
        for scoped in scopes:
            if scope == scoped:
                return scope
        raise InvalidRequest("Scope requested in filtering term does not match any of its possible scopes. Look at filtering terms endpoint to know which scopes you can select for this filtering term: {}".format(filter.id))