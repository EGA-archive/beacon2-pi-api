from beacon.connections.mongo.__init__ import client
from beacon.connections.mongo.utils import get_count
from typing import Optional
from beacon.response.schemas import DefaultSchemas
from beacon.request.parameters import RequestParams
from beacon.connections.mongo.utils import get_filtering_documents
from beacon.exceptions.exceptions import raise_exception

def get_filtering_terms(self, qparams: RequestParams):
    try:
        query = {}
        schema = DefaultSchemas.FILTERINGTERMS
        count = get_count(self, client.beacon.filtering_terms, query)
        remove_id={'_id':0}
        docs = get_filtering_documents(
            self,
            client.beacon.filtering_terms,
            query,
            remove_id,
            qparams.query.pagination.skip,
            qparams.query.pagination.limit
        )
        return schema, count, docs
    except Exception as e:# pragma: no cover
        err = str(e)
        errcode=500
        raise_exception(err, errcode)