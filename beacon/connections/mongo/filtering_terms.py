from beacon.connections.mongo.client import get_client
from beacon.connections.mongo.utils import get_filtering_documents
from beacon.response.classes import FilteringTermsResponse

def get_filtering_terms(self):
    client=get_client()
    filtering_terms=client['beacon'].filtering_terms
    query = {}
    #count = get_count(self, filtering_terms, query)
    remove_id={'_id':0}
    docs = get_filtering_documents(
        self,
        filtering_terms,
        query,
        remove_id,
        self.request_attributes.qparams.query.pagination.skip,
        self.request_attributes.qparams.query.pagination.limit
    )
    return FilteringTermsResponse(docs=docs)