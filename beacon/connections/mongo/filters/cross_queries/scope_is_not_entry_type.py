from beacon.connections.mongo.utils import join_query
from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level

@log_with_args(level)
def scope_is_not_entry_type(self, original_id, final_id, def_list, mongo_collection, query, dataset):
    """
    If the scope is not the entry type, perform the id translation for the intersection of the ids of the cross query.
    """
    LOG.warning(original_id)
    LOG.warning(final_id)
    LOG.warning(query)
    LOG.warning(mongo_collection)
    join_ids=list(join_query(self, mongo_collection, query, original_id, dataset))
    LOG.warning(join_ids)
    if join_ids == []:
        return query
    for id_item in join_ids:
        new_id={}
        new_id[final_id] = id_item.pop(original_id)
        def_list.append(new_id)
    query={}
    query['$or']=def_list
    return query