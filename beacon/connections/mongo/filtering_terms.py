from beacon.connections.mongo.__init__ import filtering_terms
from beacon.connections.mongo.utils import get_count
from beacon.request.classes import RequestAttributes
from beacon.connections.mongo.utils import get_filtering_documents

def get_filtering_terms(self):
    try:
        query = {}
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
        return count, docs
    except Exception as e:
        self._error.handle_exception(e, None)
        raise