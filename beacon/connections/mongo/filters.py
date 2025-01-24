from typing import List, Union
import re
from beacon.request.parameters import AlphanumericFilter, CustomFilter, OntologyFilter, Operator, Similarity
from beacon.connections.mongo.utils import get_documents, join_query
from beacon.connections.mongo.__init__ import client
from beacon.conf import conf
from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level

CURIE_REGEX = r'^([a-zA-Z0-9]*):\/?[a-zA-Z0-9./]*$'


@log_with_args(level)
def cross_query(self, query: dict, scope: str, collection: str, request_parameters: dict, dataset: str):
    if scope == 'genomicVariation' and collection == 'g_variants' or scope == collection[0:-1]:
        subquery={}
        subquery["$or"]=[]
        if request_parameters != {}:
            listHGVS=[]
            queryHGVS={}
            HGVSIds = client.beacon.genomicVariations.find(request_parameters, {"identifiers.genomicHGVSId": 1, "_id": 0})
            HGVSIds=list(HGVSIds)
            for HGVSId in HGVSIds:
                justid=HGVSId["identifiers"]["genomicHGVSId"]
                listHGVS.append(justid)
            queryHGVS["$in"]=listHGVS
            queryHGVSId={"datasetId": dataset, "identifiers.genomicHGVSId": queryHGVS}
            try:
                query["$and"] = []
                query["$and"].append(queryHGVSId)
            except Exception:# pragma: no cover
                pass
    else:
        def_list=[]                
        if scope == 'individual' and collection == 'g_variants':
            mongo_collection=client.beacon.individuals
            original_id="id"
            join_ids=list(join_query(self, mongo_collection, query, original_id))
            targets = client.beacon.targets \
                .find({"datasetId": dataset}, {"biosampleIds": 1, "_id": 0})
            bioids=targets[0]["biosampleIds"]
            positions_list=[]
            for id_item in join_ids:
                new_id={}
                biosampleId=id_item.pop(original_id)
                try:
                    position=bioids.index(biosampleId)
                except Exception:
                    continue
                positions_list.append(position)
            query_cl={}
            query_cl["$or"]=[]
            for position in positions_list:
                position=str(position)
                query_cl["$or"].append({ position: "10", "datasetId": dataset})
                query_cl["$or"].append({ position: "11", "datasetId": dataset})
                query_cl["$or"].append({ position: "01", "datasetId": dataset})
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
        elif scope == 'individual' and collection in ['runs','biosamples','analyses']:
            mongo_collection=client.beacon.individuals
            original_id="id"
            join_ids=list(join_query(self, mongo_collection, query, original_id))
            final_id="individualId"
            for id_item in join_ids:
                new_id={}
                new_id[final_id] = id_item.pop(original_id)
                def_list.append(new_id)
            query={}
            query['$or']=def_list
        elif scope == 'genomicVariation' and collection == 'individuals':
            HGVSIds = client.beacon.genomicVariations \
                .find(query, {"identifiers.genomicHGVSId": 1, "_id": 0})
            HGVSIds=list(HGVSIds)
            list_of_variants_found=[]
            for variant_found in HGVSIds:
                list_of_variants_found.append(variant_found["identifiers"]["genomicHGVSId"])
            queryHGVSId={"datasetId": dataset, "id": {"$in": list_of_variants_found}}
            string_of_ids = client.beacon.caseLevelData \
                .find(queryHGVSId)
            targets = client.beacon.targets \
                .find({"datasetId": dataset}, {"biosampleIds": 1, "_id": 0})
            targets=list(targets)
            list_of_targets=targets[0]["biosampleIds"]
            list_of_positions_strings= string_of_ids[0]
            biosampleIds=[]
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
            except Exception:# pragma: no cover
                finalids=biosampleIds
            query={}
            query["$or"]=[]
            for finalid in finalids:
                finalquery = {"id": finalid}
                query["$or"].append(finalquery)
        elif scope == 'genomicVariation' and collection == 'biosamples':
            HGVSIds = client.beacon.genomicVariations \
                .find(query, {"identifiers.genomicHGVSId": 1, "_id": 0})
            HGVSIds=list(HGVSIds)
            list_of_variants_found=[]
            for variant_found in HGVSIds:
                list_of_variants_found.append(variant_found["identifiers"]["genomicHGVSId"])
            queryHGVSId={"datasetId": dataset, "id": {"$in": list_of_variants_found}}
            string_of_ids = client.beacon.caseLevelData \
                .find(queryHGVSId)
            targets = client.beacon.targets \
                .find({"datasetId": dataset}, {"biosampleIds": 1, "_id": 0})
            targets=list(targets)
            list_of_targets=targets[0]["biosampleIds"]
            list_of_positions_strings= string_of_ids[0]
            biosampleIds=[]
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
        elif scope == 'genomicVariation' and collection in ['analyses','runs']:
            HGVSIds = client.beacon.genomicVariations \
                .find(query, {"identifiers.genomicHGVSId": 1, "_id": 0})
            HGVSIds=list(HGVSIds)
            list_of_variants_found=[]
            for variant_found in HGVSIds:
                list_of_variants_found.append(variant_found["identifiers"]["genomicHGVSId"])
            queryHGVSId={"datasetId": dataset, "id": {"$in": list_of_variants_found}}
            string_of_ids = client.beacon.caseLevelData \
                .find(queryHGVSId)
            targets = client.beacon.targets \
                .find({"datasetId": dataset}, {"biosampleIds": 1, "_id": 0})
            targets=list(targets)
            list_of_targets=targets[0]["biosampleIds"]
            list_of_positions_strings= string_of_ids[0]
            biosampleIds=[]
            for key, value in list_of_positions_strings.items():
                if key != 'datasetId' and key != 'id' and key != '_id':
                    biosampleIds.append(list_of_targets[int(key)])
            finalids=biosampleIds
            try:
                finalids=[]
                for bioid in biosampleIds:
                    finalids.append({"biosampleId": bioid})
            except Exception:# pragma: no cover
                finalids=[]
            query = {"$and": [{"$or": finalids}]}
        elif scope == 'run' and collection != 'runs':
            mongo_collection=client.beacon.runs
            if collection == 'g_variants':
                original_id="biosampleId"
                join_ids=list(join_query(self, mongo_collection, query, original_id))
                targets = client.beacon.targets \
                    .find({"datasetId": dataset}, {"biosampleIds": 1, "_id": 0})
                bioids=targets[0]["biosampleIds"]
                positions_list=[]
                for id_item in join_ids:
                    new_id={}
                    biosampleId=id_item.pop(original_id)
                    position=bioids.index(biosampleId)
                    positions_list.append(position)
                query_cl={}
                query_cl["$or"]=[]
                for position in positions_list:
                    position=str(position)
                    query_cl["$or"].append({ position: "10", "datasetId": dataset})
                    query_cl["$or"].append({ position: "11", "datasetId": dataset})
                    query_cl["$or"].append({ position: "01", "datasetId": dataset})
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
            elif collection == 'individuals':
                original_id="individualId"
                join_ids=list(join_query(self, mongo_collection, query, original_id))
                final_id="id"
                for id_item in join_ids:
                    new_id={}
                    new_id[final_id] = id_item.pop(original_id)
                    def_list.append(new_id)
                    query={}
                    query['$or']=def_list
            elif collection == 'analyses':
                original_id="biosampleId"
                join_ids=list(join_query(self, mongo_collection, query, original_id))
                final_id="biosampleId"
                for id_item in join_ids:
                    new_id={}
                    new_id[final_id] = id_item.pop(original_id)
                    def_list.append(new_id)
                    query={}
                    query['$or']=def_list
            elif collection == 'biosamples':
                original_id="biosampleId"
                join_ids=list(join_query(self, mongo_collection, query, original_id))
                final_id="id"
                for id_item in join_ids:
                    new_id={}
                    new_id[final_id] = id_item.pop(original_id)
                    def_list.append(new_id)
                    query={}
                    query['$or']=def_list
        elif scope == 'analyse' and collection != 'analyses':# pragma: no cover
            mongo_collection=client.beacon.analyses
            if collection == 'g_variants':
                original_id="biosampleId"
                join_ids=list(join_query(self, mongo_collection, query, original_id))
                targets = client.beacon.targets \
                    .find({"datasetId": dataset}, {"biosampleIds": 1, "_id": 0})
                bioids=targets[0]["biosampleIds"]
                positions_list=[]
                for id_item in join_ids:
                    new_id={}
                    biosampleId=id_item.pop(original_id)
                    position=bioids.index(biosampleId)
                    positions_list.append(position)
                query_cl={}
                query_cl["$or"]=[]
                for position in positions_list:
                    position=str(position)
                    query_cl["$or"].append({ position: "10", "datasetId": dataset})
                    query_cl["$or"].append({ position: "11", "datasetId": dataset})
                    query_cl["$or"].append({ position: "01", "datasetId": dataset})
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
            elif collection == 'individuals':
                original_id="individualId"
                join_ids=list(join_query(self, mongo_collection, query, original_id))
                final_id="id"
                for id_item in join_ids:
                    new_id={}
                    new_id[final_id] = id_item.pop(original_id)
                    def_list.append(new_id)
                query={}
                query['$or']=def_list
            elif collection == 'runs':
                original_id="biosampleId"
                join_ids=list(join_query(self, mongo_collection, query, original_id))
                final_id="biosampleId"
                for id_item in join_ids:
                    new_id={}
                    new_id[final_id] = id_item.pop(original_id)
                    def_list.append(new_id)
                query={}
                query['$or']=def_list
            elif collection == 'biosamples':
                original_id="biosampleId"
                join_ids=list(join_query(self, mongo_collection, query, original_id))
                final_id="id"
                for id_item in join_ids:
                    new_id={}
                    new_id[final_id] = id_item.pop(original_id)
                    def_list.append(new_id)
                query={}
                query['$or']=def_list
        elif scope == 'biosample' and collection != 'biosamples':
            mongo_collection=client.beacon.biosamples
            if collection == 'g_variants':
                original_id="id"
                join_ids=list(join_query(self, mongo_collection, query, original_id))
                targets = client.beacon.targets \
                    .find({"datasetId": dataset}, {"biosampleIds": 1, "_id": 0})
                bioids=targets[0]["biosampleIds"]
                positions_list=[]
                for id_item in join_ids:
                    new_id={}
                    biosampleId=id_item.pop(original_id)
                    position=bioids.index(biosampleId)
                    positions_list.append(position)
                query_cl={}
                query_cl["$or"]=[]
                for position in positions_list:
                    position=str(position)
                    query_cl["$or"].append({ position: "10", "datasetId": dataset})
                    query_cl["$or"].append({ position: "11", "datasetId": dataset})
                    query_cl["$or"].append({ position: "01", "datasetId": dataset})
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
            elif collection == 'individuals':
                original_id="individualId"
                join_ids=list(join_query(self, mongo_collection, query, original_id))
                final_id="id"
                for id_item in join_ids:
                    new_id={}
                    new_id[final_id] = id_item.pop(original_id)
                    def_list.append(new_id)
                query={}
                query['$or']=def_list
            elif collection == 'analyses':
                original_id="id"
                join_ids=list(join_query(self, mongo_collection, query, original_id))
                final_id="biosampleId"
                for id_item in join_ids:
                    new_id={}
                    new_id[final_id] = id_item.pop(original_id)
                    def_list.append(new_id)
                query={}
                query['$or']=def_list
            elif collection == 'runs':
                original_id="id"
                join_ids=list(join_query(self, mongo_collection, query, original_id))
                final_id="biosampleId"
                for id_item in join_ids:
                    new_id={}
                    new_id[final_id] = id_item.pop(original_id)
                    def_list.append(new_id)
                query={}
                query['$or']=def_list
    return query



@log_with_args(level)
def apply_filters(self, query: dict, filters: List[dict], collection: str, query_parameters: dict, dataset: str) -> dict:
    request_parameters = query_parameters
    total_query={}
    if len(filters) >= 1:
        total_query["$and"] = []
        if query != {} and request_parameters == {}:
            total_query["$and"].append(query)# pragma: no cover
        for filter in filters:
            partial_query = {}
            if "value" in filter:
                filter = AlphanumericFilter(**filter)
                partial_query = apply_alphanumeric_filter(self, partial_query, filter, collection, dataset)
            elif "includeDescendantTerms" not in filter and '.' not in filter["id"] and filter["id"].isupper():
                filter=OntologyFilter(**filter)
                filter.include_descendant_terms=True
                partial_query = apply_ontology_filter(self, partial_query, filter, collection, request_parameters, dataset)
            elif "similarity" in filter or "includeDescendantTerms" in filter or re.match(CURIE_REGEX, filter["id"]) and filter["id"].isupper():
                filter = OntologyFilter(**filter)# pragma: no cover
                partial_query = apply_ontology_filter(self, partial_query, filter, collection, request_parameters, dataset)# pragma: no cover
            else:
                filter = CustomFilter(**filter)
                partial_query = apply_custom_filter(self, partial_query, filter, collection, dataset)
            total_query["$and"].append(partial_query)
            if total_query["$and"] == [{'$or': []}] or total_query['$and'] == []:
                total_query = {}# pragma: no cover

    if request_parameters != {}:
        try:
            if collection == 'individuals':
                HGVSIds = client.beacon.genomicVariations \
                    .find(query, {"identifiers.genomicHGVSId": 1, "datasetId": 1, "_id": 0})
                HGVSIds=list(HGVSIds)
                HGVSDataset=HGVSIds[0]["datasetId"]
                HGVSId=HGVSIds[0]["identifiers"]["genomicHGVSId"]
                if dataset != HGVSDataset:# pragma: no cover
                    return {}
                queryHGVSId={"datasetId": dataset, "id": HGVSId}
                string_of_ids = client.beacon.caseLevelData \
                    .find(queryHGVSId)
                targets = client.beacon.targets \
                    .find({"datasetId": HGVSDataset}, {"biosampleIds": 1, "_id": 0})
                targets=list(targets)
                list_of_targets=targets[0]["biosampleIds"]
                list_of_positions_strings= string_of_ids[0]
                biosampleIds=[]
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
                    if finalids==[]:# pragma: no cover
                        finalids=biosampleIds
                except Exception:# pragma: no cover
                    finalids=biosampleIds
                finalquery={}
                finalquery["$or"]=[]
                for finalid in finalids:
                    query = {"id": finalid}
                    finalquery["$or"].append(query)
                try:
                    total_query["$and"].append(finalquery)
                except Exception:
                    total_query["$and"]=[]
                    total_query["$and"].append(finalquery)
            elif collection == 'biosamples':
                HGVSIds = client.beacon.genomicVariations \
                    .find(query, {"identifiers.genomicHGVSId": 1, "datasetId": 1, "_id": 0})
                HGVSIds=list(HGVSIds)
                HGVSDataset=HGVSIds[0]["datasetId"]
                HGVSId=HGVSIds[0]["identifiers"]["genomicHGVSId"]
                if dataset != HGVSDataset:# pragma: no cover
                    return {}
                queryHGVSId={"datasetId": dataset, "id": HGVSId}
                string_of_ids = client.beacon.caseLevelData \
                    .find(queryHGVSId)
                targets = client.beacon.targets \
                    .find({"datasetId": HGVSDataset}, {"biosampleIds": 1, "_id": 0})
                targets=list(targets)
                list_of_targets=targets[0]["biosampleIds"]
                list_of_positions_strings= string_of_ids[0]
                biosampleIds=[]
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
                try:
                    total_query["$and"].append({"$or": finalids})
                except Exception:
                    total_query["$and"]=[]
                    total_query["$and"].append({"$or": finalids})
            elif collection == 'analyses' or collection == 'runs':
                HGVSIds = client.beacon.genomicVariations \
                    .find(query, {"identifiers.genomicHGVSId": 1, "datasetId": 1, "_id": 0})
                HGVSIds=list(HGVSIds)
                HGVSDataset=HGVSIds[0]["datasetId"]
                HGVSId=HGVSIds[0]["identifiers"]["genomicHGVSId"]
                if dataset != HGVSDataset:# pragma: no cover
                    return {}
                queryHGVSId={"datasetId": dataset, "id": HGVSId}
                string_of_ids = client.beacon.caseLevelData \
                    .find(queryHGVSId)
                targets = client.beacon.targets \
                    .find({"datasetId": HGVSDataset}, {"biosampleIds": 1, "_id": 0})
                targets=list(targets)
                list_of_targets=targets[0]["biosampleIds"]
                list_of_positions_strings= string_of_ids[0]
                biosampleIds=[]
                for key, value in list_of_positions_strings.items():
                    if key != 'datasetId' and key != 'id' and key != '_id':
                        biosampleIds.append(list_of_targets[int(key)])
                try:
                    finalids=[]
                    for bioid in biosampleIds:
                        finalids.append({"biosampleId": bioid})
                except Exception:# pragma: no cover
                    finalids=[]
                try:
                    total_query["$and"].append({"$or": finalids})
                except Exception:
                    total_query["$and"]=[]
                    total_query["$and"].append({"$or": finalids})
            else:
                try:
                    total_query["$and"].append(request_parameters)
                except Exception:
                    total_query["$and"]=[]
                    total_query["$and"].append(request_parameters)
            if total_query["$and"] == [{'$or': []}] or total_query['$and'] == []:
                total_query = {}# pragma: no cover
        except Exception:# pragma: no cover
            pass
    if total_query == {} and query != {}:
        total_query=query
    return total_query


@log_with_args(level)
def apply_ontology_filter(self, query: dict, filter: OntologyFilter, collection: str, request_parameters: dict, dataset: str) -> dict:
    final_term_list=[]
    query_synonyms={}
    query_synonyms['id']=filter.id
    synonyms=get_documents(self,
        client.beacon.synonyms,
        query_synonyms,
        0,
        1
    )

    try:
        synonym_id=synonyms[0]['synonym']
    except Exception:
        synonym_id=None
    if synonym_id is not None:
        final_term_list.append(filter.id)# pragma: no cover
        filter.id=synonym_id# pragma: no cover
    
    
    scope = filter.scope
    if scope is None and collection != 'g_variants':
        scope = collection[0:-1]
    elif scope is None:
        scope = 'genomicVariation'# pragma: no cover
    is_filter_id_required = True
    # Search similar
    if filter.similarity != Similarity.EXACT:# pragma: no cover
        is_filter_id_required = False
        ontology_list=filter.id.split(':')
        try:
            if filter.similarity == Similarity.HIGH:
                similarity_high=[]
                ontology_dict=client.beacon.similarities.find({"id": filter.id})
                final_term_list = ontology_dict[0]["similarity_high"]
            elif filter.similarity == Similarity.MEDIUM:
                similarity_medium=[]
                ontology_dict=client.beacon.similarities.find({"id": filter.id})
                final_term_list = ontology_dict[0]["similarity_medium"]
            elif filter.similarity == Similarity.LOW:
                similarity_low=[]
                ontology_dict=client.beacon.similarities.find({"id": filter.id})
                final_term_list = ontology_dict[0]["similarity_low"]
        except Exception:
            pass
        


        final_term_list.append(filter.id)
        query_filtering={}
        query_filtering['$and']=[]
        dict_scope={}
        dict_scope['scopes']=scope
        query_filtering['$and'].append(dict_scope)
        dict_id={}
        dict_id['id']=filter.id
        query_filtering['$and'].append(dict_id)
        docs = get_documents(self,
            client.beacon.filtering_terms,
            query_filtering,
            0,
            1
        )
            
        for doc_term in docs:
            label = doc_term['label']
        if scope == 'genomicVariation' and collection == 'g_variants' or scope == collection:
            query_filtering={}
            query_filtering['$and']=[]
            query_filtering['$and'].append(dict_scope)
            dict_regex={}
            try:
                dict_regex['$regex']=label
                dict_regex['$options']='i'
            except Exception:
                dict_regex['$regex']=''
            dict_id={}
            dict_id['id']=dict_regex
            query_filtering['$and'].append(dict_id)
            docs_2 = get_documents(self,
                client.beacon.filtering_terms,
                query_filtering,
                0,
                1
            )
            for doc2 in docs_2:
                query_terms = doc2['id']
            query_terms = query_terms.split(':')
            query_term = query_terms[0] + '.id'
            if final_term_list !=[]:
                new_query={}
                query_id={}
                new_query['$or']=[]
                for simil in final_term_list:
                    query_id={}
                    query_id[query_term]=simil
                    new_query['$or'].append(query_id)
                query = new_query
        else:
            pass
        

    # Apply descendant terms
    if filter.include_descendant_terms == True:
        final_term_list.append(filter.id)
        is_filter_id_required = False
        ontology=filter.id.replace("\n","")
        list_descendant = []
        try:
            ontology_dict=client.beacon.similarities.find({"id": ontology})
            list_descendant = ontology_dict[0]["descendants"]
            for descendant in list_descendant:
                final_term_list.append(descendant)
        except Exception:
            pass

        try: 
            if query['$or']:
                pass# pragma: no cover
            else:# pragma: no cover
                query['$or']=[]# pragma: no cover
        except Exception:
            query['$or']=[]
        list_descendant.append(filter.id)
        query_filtering={}
        query_filtering['$and']=[]
        dict_scope={}

        dict_scope['scopes']=scope
        dict_id={}
        dict_id['id']=filter.id
        query_filtering['$and'].append(dict_id)
        query_filtering['$and'].append(dict_scope)
        docs = get_documents(self,
            client.beacon.filtering_terms,
            query_filtering,
            0,
            1
        )

        for doc_term in docs:
            label = doc_term['label']
        query_filtering={}
        query_filtering['$and']=[]
        dict_regex={}
        try:
            dict_regex['$regex']=label
            dict_regex['$options']='i'
        except Exception:# pragma: no cover
            dict_regex['$regex']=''
        dict_id={}
        dict_id['id']=dict_regex
        dict_scope={}
        dict_scope['scopes']=scope
        query_filtering['$and'].append(dict_id)
        query_filtering['$and'].append(dict_scope)
        docs_2 = get_documents(self,
            client.beacon.filtering_terms,
            query_filtering,
            0,
            1
        )
        for doc2 in docs_2:
            query_terms = doc2['id']
            query_terms = query_terms.split(':')
            query_term = query_terms[0] + '.id'
        
        if final_term_list !=[]:
            new_query={}
            query_id={}
            new_query['$or']=[]
            for simil in final_term_list:
                query_id={}
                query_id[query_term]=simil
                new_query['$or'].append(query_id)
            query = new_query
        query=cross_query(self, query, scope, collection, request_parameters, dataset)

            
    if is_filter_id_required:# pragma: no cover
        query_filtering={}
        query_filtering['$and']=[]
        dict_scope={}
        dict_scope['scopes']=scope
        query_filtering['$and'].append(dict_scope)
        dict_id={}
        dict_id['id']=filter.id
        query_filtering['$and'].append(dict_id)
        docs = get_documents(self,
        client.beacon.filtering_terms,
        query_filtering,
        0,
        1
    )
        
        for doc_term in docs:
            label = doc_term['label']
        query_filtering={}
        query_filtering['$and']=[]
        query_filtering['$and'].append(dict_scope)
        dict_regex={}
        dict_regex['$regex']=label
        dict_regex['$options']='i'
        dict_id={}
        dict_id['id']=dict_regex
        query_filtering['$and'].append(dict_id)
        docs_2 = get_documents(self,
        client.beacon.filtering_terms,
        query_filtering,
        0,
        1
    )
        for doc2 in docs_2:
            query_terms = doc2['id']
        query_terms = query_terms.split(':')
        query_term = query_terms[0] + '.id'
        query[query_term]=filter.id
        if final_term_list !=[]:
            new_query={}
            query_id={}
            new_query['$or']=[]
            for simil in final_term_list:
                query_id={}
                query_id[query_term]=simil
                new_query['$or'].append(query_id)
            new_query['$or'].append(query)
            query = new_query
        query=cross_query(self, query, scope, collection, request_parameters, dataset)
    return query



@log_with_args(level)
def format_value(self, value: Union[str, List[int]]) -> Union[List[int], str, int, float]:
    if isinstance(value, list):
        return value# pragma: no cover
    elif isinstance(value, int):
        return value# pragma: no cover
    
    elif value.isnumeric():
        if float(value).is_integer():
            return int(value)
        else:
            return float(value)# pragma: no cover
    
    else:
        return value

@log_with_args(level)
def format_operator(self, operator: Operator) -> str:
    if operator == Operator.EQUAL:
        return "$eq"
    elif operator == Operator.NOT:
        return "$ne"
    elif operator == Operator.GREATER:
        return "$gt"
    elif operator == Operator.GREATER_EQUAL:
        return "$gte"
    elif operator == Operator.LESS:
        return "$lt"
    elif operator == Operator.LESS_EQUAL:
        return "$lte"

@log_with_args(level)
def apply_alphanumeric_filter(self, query: dict, filter: AlphanumericFilter, collection: str, dataset: str) -> dict:
    scope = filter.scope
    if scope is None and collection != 'g_variants':
        scope = collection[0:-1]
    elif scope is None:
        scope = 'genomicVariation'
    formatted_value = format_value(self, filter.value)
    formatted_operator = format_operator(self, filter.operator)
    if collection == 'g_variants' and scope != 'individual' and scope != 'run':
        if filter.id == "identifiers.genomicHGVSId":
            list_chromosomes = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','X','Y']
            dict_regex={}
            if filter.value == 'GRCh38':
                dict_regex['$regex']="11:"
            elif filter.value == 'GRCh37':
                dict_regex['$regex']="10:"
            elif filter.value == 'NCBI36':
                dict_regex['$regex']="9:"
            elif filter.value in list_chromosomes:
                if filter.value == 'X':
                    dict_regex['$regex']='^NC_0000'+'23'
                elif filter.value == 'Y':
                    dict_regex['$regex']='^NC_0000'+'24'
                else:
                    dict_regex['$regex']='^NC_0000'+filter.value+'.'+'10:g'+'|'+'^NC_0000'+filter.value+'.'+'11:g'+'|'+'^NC_0000'+filter.value+'.'+'9:g'
            elif '&gt;' in filter.value:# pragma: no cover
                newvalue=filter.value.replace("&gt;",">")
                dict_regex=newvalue
            elif '.' in filter.value:# pragma: no cover
                valuesplitted = filter.value.split('.')
                dict_regex['$regex']=valuesplitted[0]+".*"+valuesplitted[-1]+":"
                dict_regex['$options']= "si"
            query[filter.id] = dict_regex
        elif filter.id == 'molecularAttributes.aminoacidChanges':
            query[filter.id] = filter.value# pragma: no cover
        elif filter.id == 'molecularAttributes.geneIds':
            query[filter.id] = filter.value# pragma: no cover
        elif filter.id == "caseLevelData.clinicalInterpretations.clinicalRelevance":
            query[filter.id] = filter.value# pragma: no cover
        elif filter.id == "variantInternalId":
            if 'max' in filter.value:
                valuereplaced = filter.value.replace('max', '')
                length=40+int(valuereplaced)+1
                array_min=[]
                dict_len={}
                dict_len['$strLenCP']="$variantInternalId"
                array_min.append(dict_len)
                array_min.append(length)
                dict_gt={}
                dict_gt['$lt']=array_min
                dict_expr={}
                dict_expr['$expr']=dict_gt

                            
                query=dict_expr

            elif 'min' in filter.value:
                valuereplaced = filter.value.replace('min', '')
                length=40+int(valuereplaced)-1
                array_min=[]
                dict_len={}
                dict_len['$strLenCP']="$variantInternalId"
                array_min.append(dict_len)
                array_min.append(length)
                dict_gt={}
                dict_gt['$gt']=array_min
                dict_expr={}
                dict_expr['$expr']=dict_gt

                            
                query=dict_expr





        else:
            formatted_value = format_value(self, filter.value)
            formatted_operator = format_operator(self, filter.operator)
            query[filter.id] = { formatted_operator: formatted_value }

    elif isinstance(formatted_value,str):
        if filter.id in conf.alphanumeric_terms:
            query_term = filter.id# pragma: no cover
        else:
            query_term = filter.id + '.' + 'label'
        if formatted_operator == "$eq":
            if '%' in filter.value:
                try: 
                    if query['$or']:
                        pass# pragma: no cover
                    else:# pragma: no cover
                        query['$or']=[]# pragma: no cover
                except Exception:
                    query['$or']=[]
                value_splitted=filter.value.split('%')
                regex_dict={}
                regex_dict['$regex']=value_splitted[1]
                query_id={}
                query_id[query_term]=regex_dict
                query['$or'].append(query_id)
                query=cross_query(self, query, scope, collection, {}, dataset)
                
            else:
                try: 
                    if query['$or']:
                        pass# pragma: no cover
                    else:# pragma: no cover
                        query['$or']=[]# pragma: no cover
                except Exception:
                    query['$or']=[]
                query_id={}
                query_id[query_term]=filter.value
                query['$or'].append(query_id) 
                query=cross_query(self, query, scope, collection, {}, dataset)
                

        elif formatted_operator == "$ne":
            if '%' in filter.value:
                try: 
                    if query['$nor']:
                        pass# pragma: no cover
                    else:# pragma: no cover
                        query['$nor']=[]# pragma: no cover
                except Exception:
                    query['$nor']=[]
                value_splitted=filter.value.split('%')
                regex_dict={}
                regex_dict['$regex']=value_splitted[1]
                query_id={}
                query_id[query_term]=regex_dict
                query['$nor'].append(query_id)
            else:
                try: 
                    if query['$nor']:
                        pass# pragma: no cover
                    else:# pragma: no cover
                        query['$nor']=[]# pragma: no cover
                except Exception:
                    query['$nor']=[]

                query_id={}
                query_id[query_term]=filter.value
                query['$nor'].append(query_id) 
        
    else:
        if "iso8601duration" in filter.id:
            if '>' in filter.operator:
                age_in_number=""
                for char in filter.value:
                    try:
                        int(char)
                        age_in_number = age_in_number+char
                    except Exception:# pragma: no cover
                        continue
                new_age_list=''
                
                if "=" in filter.operator:
                    z = int(age_in_number)# pragma: no cover
                else:
                    z = int(age_in_number)+1
                while z < 150:
                    newagechar="P"+str(z)+"Y"
                    if new_age_list == '':
                        new_age_list+=newagechar
                    else:
                        new_age_list+='|'+newagechar
                    z+=1
                dict_in={}
                dict_in["$regex"]=new_age_list
                query[filter.id] = dict_in
                query=cross_query(self, query, scope, collection, {}, dataset)
            elif '<' in filter.operator:
                age_in_number=""
                for char in filter.value:
                    try:
                        int(char)
                        age_in_number = age_in_number+char
                    except Exception:# pragma: no cover
                        continue
                new_age_list=''
                if "=" in filter.operator:
                    z = int(age_in_number)# pragma: no cover
                else:
                    z = int(age_in_number)-1
                while z > 0:
                    newagechar="P"+str(z)+"Y"
                    if new_age_list == '':
                        new_age_list+=newagechar
                    else:
                        new_age_list+='|'+newagechar
                    z-=1
                dict_in={}
                dict_in["$regex"]=new_age_list
                query[filter.id] = dict_in
                query=cross_query(self, query, scope, collection, {}, dataset)
            elif '=' in filter.operator:
                age_in_number=""
                for char in filter.value:
                    try:
                        int(char)
                        age_in_number = age_in_number+char
                    except Exception:# pragma: no cover
                        continue
                z = int(age_in_number)# pragma: no cover
                newagechar="P"+str(z)+"Y"
                dict_in={}
                dict_in["$regex"]=newagechar
                query[filter.id] = dict_in
                query=cross_query(self, query, scope, collection, {}, dataset)
        else:
            query_filtering={}
            query_filtering['$and']=[]
            dict_type={}
            dict_id={}
            dict_regex={}
            dict_regex['$regex']=filter.id
            dict_regex['$options']='i'
            dict_type['type']='custom'
            dict_id['id']=dict_regex
            query_filtering['$and'].append(dict_type)
            query_filtering['$and'].append(dict_id)
            docs = get_documents(self,
                client.beacon.filtering_terms,
                query_filtering,
                0,
                1
            )
            for doc in docs:
                prefield_splitted = doc['id'].split(':')
                prefield = prefield_splitted[0]
            field = prefield.replace('assayCode', 'measurementValue.value')
            
            assayfield = 'assayCode' + '.label'
            fieldsplitted = field.split('.')
            measuresfield=fieldsplitted[0]

            field = field.replace(measuresfield+'.', '')

            query[field] = { formatted_operator: float(formatted_value) }
            query[assayfield]=filter.id
            dict_elemmatch={}
            dict_elemmatch['$elemMatch']=query
            dict_measures={}
            dict_measures[measuresfield]=dict_elemmatch
            query = dict_measures
            query=cross_query(self, query, scope, collection, {}, dataset)
    return query


@log_with_args(level)
def apply_custom_filter(self, query: dict, filter: CustomFilter, collection:str, dataset: str) -> dict:
    scope = filter.scope
    if scope is None and collection != 'g_variants':
        scope = collection[0:-1]
    elif scope is None:# pragma: no cover
        scope = 'genomicVariation'
    value_splitted = filter.id.split(':')
    if value_splitted[0] in conf.alphanumeric_terms:
        query_term = value_splitted[0]# pragma: no cover
    else:
        query_term = value_splitted[0] + '.label'
    query[query_term]=value_splitted[1]
    query=cross_query(self, query, scope, collection, {}, dataset)

    return query
