from pymongo.cursor import Cursor
from beacon.connections.mongo.__init__ import client
from pymongo.collection import Collection
from beacon.logs.logs import log_with_args_mongo, LOG
from beacon.conf.conf import level
from bson import json_util

@log_with_args_mongo(level)
def get_cross_query(self, ids: dict, cross_type: str, collection_id: str):# pragma: no cover
    id_list=[]
    dict_in={}
    id_dict={}
    if cross_type == 'biosampleId' or cross_type=='id':# pragma: no cover
        list_item=ids
        id_list.append(str(list_item))
        dict_in["$in"]=id_list
        id_dict[collection_id]=dict_in
        query = id_dict
    elif cross_type == 'individualIds' or cross_type=='biosampleIds':
        list_individualIds=ids
        dict_in["$in"]=list_individualIds
        id_dict[collection_id]=dict_in
        query = id_dict
    else:# pragma: no cover
        for k, v in ids.items():
            for item in v:
                id_list.append(item[cross_type])
        dict_in["$in"]=id_list
        id_dict[collection_id]=dict_in
        query = id_dict

    return query

@log_with_args_mongo(level)
def query_id(self, query: dict, document_id) -> dict:
    query["id"] = document_id
    return query

@log_with_args_mongo(level)
def join_query(self, collection: Collection,query: dict, original_id):
    #LOG.debug(query)
    excluding_fields={"_id": 0, original_id: 1}
    return collection.find(query, excluding_fields).max_time_ms(100 * 1000)

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
        counts=client.beacon.counts.find({"id": str(query), "collection": str(collection)})
        try:
            counts=list(counts)
            if counts == []:
                total_counts=collection.count_documents(query)# pragma: no cover
                insert_dict={}# pragma: no cover
                insert_dict['id']=str(query)# pragma: no cover
                insert_dict['num_results']=total_counts# pragma: no cover
                insert_dict['collection']=str(collection)# pragma: no cover
                insert_total=client.beacon.counts.insert_one(insert_dict)# pragma: no cover
            else:
                total_counts=counts[0]["num_results"]
        except Exception as e:# pragma: no cover
            LOG.debug(e)
            insert_dict={}
            insert_dict['id']=str(query)
            total_counts=0
            insert_dict['num_results']=total_counts# pragma: no cover
            insert_dict['collection']=str(collection)# pragma: no cover
            insert_total=client.beacon.counts.insert_one(insert_dict)
        return total_counts

@log_with_args_mongo(level)
def get_docs_by_response_type(self, include: str, query: dict, dataset: str, limit: int, skip: int, mongo_collection, idq: str):
    if include == 'NONE':
        count = get_count(self, mongo_collection, query)
        dataset_count=0
        docs = get_documents(
        self,
        mongo_collection,
        query,
        skip*limit,
        limit
        )
    elif include == 'ALL':
        count=0
        query_count=query
        i=1
        query_count["$or"]=[]
        queryid={}
        queryid['datasetId']=dataset
        query_count["$or"].append(queryid)
        if query_count["$or"]!=[]:
            dataset_count = get_count(self, mongo_collection, query_count)
            docs = get_documents(
                self,
                mongo_collection,
                query_count,
                skip*limit,
                limit
            )
            docs=list(docs)
    elif include == 'HIT':
        count=0
        query_count=query
        query_count["$or"]=[]
        queryid={}
        queryid['datasetId']=dataset
        query_count["$or"].append(queryid)
        LOG.debug(query_count)
        if query_count["$or"]!=[]:
            dataset_count = get_count(self, mongo_collection, query_count)
            if dataset_count == 0:
                docs = []
            else:
                docs = get_documents(
                    self,
                    mongo_collection,
                    query_count,
                    skip*limit,
                    limit
                )
                docs=list(docs)
        else:
            dataset_count=0# pragma: no cover
        if dataset_count==0:
            return count, -1, None
    elif include == 'MISS':
        count=0
        query_count=query
        i=1
        query_count["$or"]=[]
        queryid={}
        queryid['datasetId']=dataset
        query_count["$or"].append(queryid)
        if query_count["$or"]!=[]:
            dataset_count = get_count(self, mongo_collection, query_count)
            docs = get_documents(
                self,
                mongo_collection,
                query_count,
                skip*limit,
                limit
            )
            docs=list(docs)
        else:
            dataset_count=0# pragma: no cover
        if dataset_count !=0:
            return count, -1, None
    return count, dataset_count, docs

@log_with_args_mongo(level)
def get_filtering_documents(self, collection: Collection, query: dict, remove_id: dict,skip: int, limit: int) -> Cursor:
    ##LOG.debug("FINAL QUERY: {}".format(query))
    return collection.find(query,remove_id).skip(skip).limit(limit).max_time_ms(100 * 1000)