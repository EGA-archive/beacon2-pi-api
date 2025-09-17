from beacon.connections.mongo.__init__ import client, dbname, filtering_terms
from beacon.connections.mongo.utils import get_count
from typing import Optional
from beacon.response.schemas import DefaultSchemas
from beacon.request.classes import RequestAttributes
from beacon.connections.mongo.utils import get_filtering_documents
from beacon.request.classes import ErrorClass

def get_filtering_terms(self):
    try:
        query = {}
        schema = DefaultSchemas.FILTERINGTERMS
        count = get_count(self, filtering_terms, query)
        remove_id={'_id':0}
        docs = get_filtering_documents(
            self,
            filtering_terms,
            query,
            remove_id,
            RequestAttributes.qparams.query.pagination.skip,
            RequestAttributes.qparams.query.pagination.limit
        )
        return schema, count, docs
    except Exception as e:# pragma: no cover
        ErrorClass.error_code=500
        ErrorClass.error_message=str(e)
        raise