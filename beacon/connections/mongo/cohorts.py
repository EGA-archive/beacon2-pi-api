from beacon.logs.logs import log_with_args_mongo
from beacon.conf.conf import level
from beacon.connections.mongo.filters import apply_filters
from typing import Optional
from beacon.connections.mongo.utils import get_count, get_documents, get_documents_for_cohorts
from beacon.connections.mongo.utils import get_docs_by_response_type, query_id, get_cross_query
from beacon.conf import cohort
from beacon.connections.mongo.__init__ import cohorts
from beacon.request.classes import RequestAttributes

@log_with_args_mongo(level)
def get_cohorts(self):
    collection = cohort.endpoint_name
    limit = RequestAttributes.qparams.query.pagination.limit
    query = apply_filters(self, {}, RequestAttributes.qparams.query.filters, collection, {}, None)
    try:
        if RequestAttributes.qparams.query.requestParameters["datasets"] != None:
            try:
                query["$and"].append({"datasetId": {"$in": RequestAttributes.qparams.query.requestParameters["datasets"]}})
            except Exception:
                query["$and"]=[]
                query["$and"].append({"datasetId": {"$in": RequestAttributes.qparams.query.requestParameters["datasets"]}})
    except Exception:
        pass
    count = get_count(self, cohorts, query)
    docs = get_documents(self,
        cohorts,
        query,
        RequestAttributes.qparams.query.pagination.skip,
        RequestAttributes.qparams.query.pagination.skip*limit
    )
    response_converted = (
        [r for r in docs] if docs else []
    )
    return response_converted, count

@log_with_args_mongo(level)
def get_cohort_with_id(self):
    collection = cohort.endpoint_name
    limit = RequestAttributes.qparams.query.pagination.limit
    query = apply_filters(self, {}, RequestAttributes.qparams.query.filters, collection, {}, "a")
    query = query_id(self, query, RequestAttributes.entry_id)
    count = get_count(self, cohorts, query)
    docs = get_documents(self,
        cohorts,
        query,
        RequestAttributes.qparams.query.pagination.skip,
        RequestAttributes.qparams.query.pagination.skip*limit
    )
    response_converted = (
        [r for r in docs] if docs else []
    )
    return response_converted, count