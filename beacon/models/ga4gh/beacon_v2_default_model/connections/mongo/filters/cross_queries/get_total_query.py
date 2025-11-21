from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level

@log_with_args(level)
def get_total_query(self, biosampleIds, total_query, original_id):
    try:
        finalids=[]
        for bioid in biosampleIds:
            finalids.append({original_id: bioid})
    except Exception:
        finalids=[]
    try:
        total_query["$and"].append({"$or": finalids})
    except Exception:
        total_query["$and"]=[]
        total_query["$and"].append({"$or": finalids})
    return total_query