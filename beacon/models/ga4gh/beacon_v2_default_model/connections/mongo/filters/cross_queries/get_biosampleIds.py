from beacon.connections.mongo.__init__ import genomicVariations, caseLevelData, targets as targets_
from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level

@log_with_args(level)
def get_biosampleIds(self, request_parameters, query, dataset):
    HGVSIds = genomicVariations \
        .find(request_parameters, {"identifiers.genomicHGVSId": 1, "datasetId": 1, "_id": 0})
    HGVSIds=list(HGVSIds)
    if HGVSIds == []:
        return {}
    HGVSDataset=HGVSIds[0]["datasetId"]
    HGVSList=[]
    for HGVSId in HGVSIds:
        HGVSList.append(HGVSId["identifiers"]["genomicHGVSId"])
    if dataset != HGVSDataset:
        return {}
    queryHGVSId={"datasetId": dataset, "id": {"$in": HGVSList}}
    string_of_ids = caseLevelData \
        .find(queryHGVSId)
    targets = targets_ \
        .find({"datasetId": HGVSDataset}, {"biosampleIds": 1, "_id": 0})
    targets=list(targets)
    list_of_targets=targets[0]["biosampleIds"]
    try:
        list_of_positions_strings= string_of_ids[0]
    except Exception:
        return query
    biosampleIds=[]
    for key, value in list_of_positions_strings.items():
        if key != 'datasetId' and key != 'id' and key != '_id':
            biosampleIds.append(list_of_targets[int(key)])
    return biosampleIds