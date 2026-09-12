from beacon.logs.logs import log_with_args_mongo
from beacon.conf.conf_override import config
from beacon.connections.mongo.utils import get_count, get_documents, query_id, get_documents_for_cohorts, query_patientId
from beacon.connections.mongo.filters.filters import apply_filters
from beacon.connections.mongo.client import get_client
from beacon.response.classes import CollectionsResponse
from beacon.models.EUCAIM.connections.mongo.utils import get_non_collections_cross_query_attributes
from beacon.models.EUCAIM.connections.mongo.utils import import_patients_confile

@log_with_args_mongo(config.level)
def get_collections(self):
    client=get_client()

    collections=client['beacon'].collections

    # Find all the datasets in the mongo database.
    query = {}
    query = collections.find(query)
    return query

@log_with_args_mongo(config.level)
def get_full_collections(self):
    client=get_client()

    collections=client['beacon'].collections

    # Create the query syntax depending on it there is any entry id queried.
    if self.request_attributes.entry_id == None:
        query = {}
    else:
        query = {'id': self.request_attributes.entry_id}
    query = apply_filters(self, {}, self.request_attributes.qparams.query.filters, {}, None)
    query = collections.find(query, {"_id": 0})
    try:
        # Collect all the datasets found with the query performed.
        if self.request_attributes.qparams.query.requestParameters["datasets"] != []: # If there are datasets requested, then, query just for those datasets.
            response_converted = (
                [r for r in query if r["id"] in self.request_attributes.qparams.query.requestParameters["datasets"]] if query else []
            )
        else:
            response_converted = (
                [r for r in query] if query else []
            ) 
    except Exception:
        response_converted = (
            [r for r in query] if query else []
        )
    # Count how many datasets are to be returned in response.
    count = len(response_converted)
    return CollectionsResponse(docs=response_converted, count=count)

@log_with_args_mongo(config.level)
def get_list_of_datasets(self):
    # Get all the datasets to be returned in response and put them in a list.
    datasets = get_collections(self)
    beacon_datasets = [ r for r in datasets ]
    return beacon_datasets

@log_with_args_mongo(config.level)
def get_collections_with_id(self):
    client=get_client()
    collections=client['beacon'].collections
    limit = self.request_attributes.qparams.query.pagination.limit
    query={}
    # Include the id queried in the query.
    query = query_id(self, query, self.request_attributes.entry_id)
    # Count all the datasets to be returned in response.
    count = get_count(self, collections, query)
    # Find the datasets to be returned in response.
    docs = get_documents(self,
        collections,
        query,
        self.request_attributes.qparams.query.pagination.skip,
        self.request_attributes.qparams.query.pagination.skip*limit
    )
    response_converted = (
                [r for r in docs] if docs else []
            )
    return CollectionsResponse(docs=response_converted, count=count)

@log_with_args_mongo(config.level)
def get_cross_endpoint_collections(self):
    limit = self.request_attributes.qparams.query.pagination.limit
    # Process filters
    query = apply_filters(self, {}, self.request_attributes.qparams.query.filters, {}, "a")
    # Include the id queried in the query.
    patients = import_patients_confile()
    if self.request_attributes.pre_entry_type ==  patients["patients"]["endpoint_name"]:
        query = query_patientId(self, query, self.request_attributes.entry_id)
    else:
        query = query_id(self, query, self.request_attributes.entry_id)
    # Translate the ids that relate the two collection record types and get the records.
    mapping = get_non_collections_cross_query_attributes(self, self.request_attributes.entry_type, self.request_attributes.pre_entry_type)
    docs = get_documents_for_cohorts(self,
        mapping["secondary_collection"],
        query,
        0,
        0
    )
    final_query = {mapping["idq"]: {"$in": [doc[mapping["idq2"]] for doc in docs]}}
    docs = get_documents(self,
        self.request_attributes.mongo_collection,
        final_query,
        self.request_attributes.qparams.query.pagination.skip,
        self.request_attributes.qparams.query.pagination.skip*limit
    )
    # Count all the records to be returned in response.
    count = get_count(self, self.request_attributes.mongo_collection, final_query)
    response_converted = (
        [r for r in docs] if docs else []
    )
    return CollectionsResponse(docs=response_converted, count=count)
