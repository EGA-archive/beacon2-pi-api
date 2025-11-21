from beacon.connections.mongo.utils import join_query
from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level

@log_with_args(level)
def scope_is_not_entry_type(self, original_id, final_id, def_list, mongo_collection, query, dataset):
    join_ids=list(join_query(self, mongo_collection, query, original_id, dataset))
    if join_ids == []:
        return query
    for id_item in join_ids:
        new_id={}
        new_id[final_id] = id_item.pop(original_id)
        def_list.append(new_id)
    query={}
    query['$or']=def_list
    return query