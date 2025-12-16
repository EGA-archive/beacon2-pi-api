from beacon.connections.mongo.__init__ import genomicVariations, biosamples, targets as targets_, caseLevelData
from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf_override import config

@log_with_args(config.level)
def cross_query_scope_is_genomicVariant_and_entry_type_is_not(self, original_id, query, dataset):
    if original_id == 'datasetId' or original_id == 'cohortId':
        HGVSIds = genomicVariations \
            .find(query, {"datasetId": 1, "_id": 0})
        HGVSIds=list(HGVSIds)
        if len(HGVSIds) > 0:
            if original_id == 'cohortId':
                query = {"$and": [{"$or": [{"datasetId": HGVSIds[0]["datasetId"]}]}]}
                return query
            else:
                query = {"$and": [{"$or": [{"id": HGVSIds[0]["datasetId"]}]}]}
                return query
    else:
        HGVSIds = genomicVariations \
            .find(query, {"identifiers.genomicHGVSId": 1, "_id": 0})
        HGVSIds=list(HGVSIds)
    list_of_variants_found=[]
    for variant_found in HGVSIds:
        list_of_variants_found.append(variant_found["identifiers"]["genomicHGVSId"])
    queryHGVSId={"datasetId": dataset, "id": {"$in": list_of_variants_found}}
    string_of_ids = caseLevelData \
        .find(queryHGVSId)
    targets = targets_ \
        .find({"datasetId": dataset}, {"biosampleIds": 1, "_id": 0})
    targets=list(targets)
    try:
        list_of_targets=targets[0]["biosampleIds"]
        list_of_positions_strings= string_of_ids
    except Exception:
        return query
    biosampleIds=[]
    for item in list_of_positions_strings:
        for key, value in item.items():
            if key != 'datasetId' and key != 'id' and key != '_id' and list_of_targets[int(key)] not in biosampleIds:
                biosampleIds.append(list_of_targets[int(key)])
    if original_id == 'individualId':
        try:
            finalquery={}
            finalquery["$or"]=[]
            for finalid in biosampleIds:
                query = {"id": finalid}
                finalquery["$or"].append(query)
            individual_id = biosamples \
                .find(finalquery, {original_id: 1, "_id": 0})
            try:
                finalids=[]
                for indid in individual_id:
                    finalids.append(indid[original_id])
            except Exception:
                finalids=[]
            if finalids==[]:
                finalids=biosampleIds
        except Exception:
            finalids=biosampleIds
        query={}
        query["$or"]=[]
        for finalid in finalids:
            finalquery = {"id": finalid}
            query["$or"].append(finalquery)
    else:
        finalids=biosampleIds
        try:
            finalids=[]
            for bioid in biosampleIds:
                finalids.append({original_id: bioid})
        except Exception:
            finalids=[]
        query = {"$and": [{"$or": finalids}]}
    return query