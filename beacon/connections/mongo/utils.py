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

@log_with_args_mongo(level)
def choose_scope(self, scope, collection, filter):
    query_filtering={}
    query_filtering['$and']=[]
    if scope is None:
        dict_id={}
        dict_id['id']=filter.id
        query_filtering['$and'].append(dict_id)
        docs = get_documents(self,
        client.beacon.filtering_terms,
        query_filtering,
        0,
        1
        )
        try:
            try:
                scopes=docs[0]["scopes"]
            except Exception:
                scopes=[]
            if len(scopes)==1:
                scope=scopes[0]
            elif len(scopes) > 1:
                for scoped in scopes:
                    if str(scoped)+'s'==collection and collection != 'g_variants':
                        scope=str(scoped)
                    elif str(scoped)=='genomicVariation' and collection=='g_variants':
                        scope=str(scoped)
                    else:
                        scope=None
            else:
                individuals_keys=['disease', 'sex', 'ethnicity', 'exposure', 'geographic', 'interventions', 'procedure', 'measure', 'karyotypic', 'pedigree', 'phenotypic', 'treatment']
                biosamples_keys=['biosample', 'collection', 'diagnostic', 'histological', 'measurement', 'obtention', 'pathological', 'sample', 'processing', 'storage', 'tumor']
                analyses_keys=['aligner', 'analysis', 'pipeline', 'variantcaller']
                cohorts_keys=['cohort', 'collectionevents', 'inclusion', 'exclusion', 'criteria']
                datasets_keys=['create', 'datause', 'externalurl', 'update', 'dataset']
                genomicVariations_keys=['zygosity', 'gene', 'aminoacid', 'molecular', 'caseleveldata', 'variant']
                runs_keys=['library', 'layout', 'source', 'strategy', 'platform', 'model', 'rundate']
                for indk in individuals_keys:
                    if indk in filter.id.lower():
                        scope='individual'
                if scope is None:
                    for biok in biosamples_keys:
                        if biok in filter.id.lower():
                            scope='biosample'
                if scope is None:
                    for ank in analyses_keys:
                        if ank in filter.id.lower():
                            scope='analysis'
                if scope is None:
                    for cohk in cohorts_keys:
                        if cohk in filter.id.lower():
                            scope='cohort'
                if scope is None:
                    for datk in datasets_keys:
                        if datk in filter.id.lower():
                            scope='dataset'
                if scope is None:
                    for genk in genomicVariations_keys:
                        if genk in filter.id.lower():
                            scope='genomicVariation'
                if scope is None:
                    for runk in runs_keys:
                        if runk in filter.id.lower():
                            scope='run'
                else:
                    scope='individual'
        except Exception as e:
            scope='individual'
    return scope