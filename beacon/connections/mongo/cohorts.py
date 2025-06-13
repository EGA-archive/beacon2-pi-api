from beacon.request.parameters import RequestParams
from beacon.response.schemas import DefaultSchemas
from beacon.connections.mongo.__init__ import client
from beacon.logs.logs import log_with_args_mongo
from beacon.conf.conf import level
from beacon.connections.mongo.filters import apply_filters
from typing import Optional
from beacon.connections.mongo.utils import get_count, get_documents, get_documents_for_cohorts
from beacon.connections.mongo.utils import get_docs_by_response_type, query_id, get_cross_query
import yaml
from beacon.conf import cohort, individual, analysis, genomicVariant, run, biosample
from beacon.connections.mongo.__init__ import cohorts
from beacon.request.classes import RequestAttributes

@log_with_args_mongo(level)
def get_cohorts(self, qparams: RequestParams):
    collection = cohort.endpoint_name
    limit = qparams.query.pagination.limit
    query = apply_filters(self, {}, qparams.query.filters, collection, {}, "a")
    schema = DefaultSchemas.COHORTS
    count = get_count(self, cohorts, query)
    docs = get_documents(self,
        cohorts,
        query,
        qparams.query.pagination.skip,
        qparams.query.pagination.skip*limit
    )
    response_converted = (
        [r for r in docs] if docs else []
    )
    return response_converted, count, schema

@log_with_args_mongo(level)
def get_cohort_with_id(self, qparams: RequestParams):
    collection = cohort.endpoint_name
    limit = qparams.query.pagination.limit
    query = apply_filters(self, {}, qparams.query.filters, collection, {}, "a")
    query = query_id(self, query, RequestAttributes.entry_id)
    schema = DefaultSchemas.COHORTS
    count = get_count(self, cohorts, query)
    docs = get_documents(self,
        cohorts,
        query,
        qparams.query.pagination.skip,
        qparams.query.pagination.skip*limit
    )
    response_converted = (
        [r for r in docs] if docs else []
    )
    return response_converted, count, schema