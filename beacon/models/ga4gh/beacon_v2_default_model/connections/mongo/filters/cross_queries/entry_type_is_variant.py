from beacon.connections.mongo.utils import join_query
from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf_override import config
from beacon.connections.mongo.__init__ import targets as targets_, caseLevelData

@log_with_args(config.level)
def cross_query_entry_type_is_genomicVariant_and_scope_is_not(self, mongo_collection, original_id, query, dataset):
    join_ids=list(join_query(self, mongo_collection, query, original_id, dataset))
    if join_ids == []:
        return query
    targets = targets_ \
        .find({"datasetId": dataset}, {"biosampleIds": 1, "_id": 0})
    bioids=targets[0]["biosampleIds"]
    positions_list=[]
    for id_item in join_ids:
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
    if query_cl["$or"]==[]:
        return query
    string_of_ids = caseLevelData \
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
    return query