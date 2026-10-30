from pymongo.cursor import Cursor
from beacon.connections.mongo.client import get_client
from pymongo.collection import Collection
from beacon.logs.logs import log_with_args_mongo
from beacon.conf.conf_override import config
from beacon.exceptions.exceptions import InvalidRequest
from beacon.response.classes import SingleDatasetResponse
from beacon.models.ga4gh.beacon_v2_default_model.connections.mongo.utils import import_genomicVariant_confile
from beacon.connections.mongo import conf as mongo_conf

@log_with_args_mongo(config.level)
def query_id(self, query: dict, document_id) -> dict:
    query["id"] = document_id
    return query

@log_with_args_mongo(config.level)
def query_variantInternalId(self, query: dict, document_id) -> dict:
    query["_id"] = document_id
    return query

@log_with_args_mongo(config.level)
def query_patientId(self, query: dict, document_id) -> dict:
    query["patientId"] = document_id
    return query


@log_with_args_mongo(config.level)
def join_query(
    self,
    mongo_collection,
    query: dict,
    original_id: str,
    dataset: str,
):
    mongo_query = query.copy()

    if dataset is not None:
        existing_and = mongo_query.get("$and", [])
        mongo_query["$and"] = [
            *existing_and,
            {"datasetId": dataset},
        ]

    projection = {"_id": 0, original_id: 1}

    return mongo_collection.find(
        mongo_query,
        projection,
        max_time_ms=100_000,
    )

@log_with_args_mongo(config.level)
def get_documents(self, collection: Collection, query: dict, skip: int, limit: int) -> Cursor:
    return collection.find(query,{"_id": 0, "datasetId": 0}).skip(skip).limit(limit).max_time_ms(100 * 1000)

@log_with_args_mongo(config.level)
def get_documents_for_cohorts(self, collection: Collection, query: dict, skip: int, limit: int) -> Cursor:
    return collection.find(query,{"_id": 0}).skip(skip).limit(limit).max_time_ms(100 * 1000)

@log_with_args_mongo(config.level)
def get_count(self, collection: Collection, query: dict) -> int:
    client=get_client()
    counts_=client[mongo_conf.database_name].counts
    if not query:
        return collection.estimated_document_count()
    else:
        counts=counts_.find({"id": str(query), "collection": str(collection)})
        try:
            counts=list(counts)
            if counts == []:
                total_counts=collection.count_documents(query)
                insert_dict={}
                insert_dict['id']=str(query)
                insert_dict['num_results']=total_counts
                insert_dict['collection']=str(collection)
                insert_total=counts_.insert_one(insert_dict)
            else:
                total_counts=counts[0]["num_results"]
        except Exception as e:
            self.LOG.warning(f"get_count failed, result not cached")
            total_counts=0
        return total_counts

@log_with_args_mongo(config.level)
def get_docs_by_response_type(self, include: str, query: dict, dataset: SingleDatasetResponse, limit: int, skip: int):
    if include == 'ALL':
        query_count=query
        query_count["$or"]=[]
        queryid={}
        queryid['datasetId']=dataset.dataset
        query_count["$or"].append(queryid)
        if query_count["$or"]!=[]:
            dataset_count = get_count(self, self.request_attributes.mongo_collection, query_count)
            docs = get_documents(
                self,
                self.request_attributes.mongo_collection,
                query_count,
                skip*limit,
                limit
            )
            docs=list(docs)
    elif include == 'MISS':
        query_count=query
        query_count["$or"]=[]
        queryid={}
        queryid['datasetId']=dataset.dataset
        query_count["$or"].append(queryid)
        if query_count["$or"]!=[]:
            dataset_count = get_count(self, self.request_attributes.mongo_collection, query_count)
            docs = get_documents(
                self,
                self.request_attributes.mongo_collection,
                query_count,
                skip*limit,
                limit
            )
            docs=list(docs)
        else:
            dataset_count=0
            dataset.exists=False
        if dataset_count !=0:
            return dataset
    else:
        query_count=query
        query_count["$or"]=[]
        queryid={}
        queryid['datasetId']=dataset.dataset
        query_count["$or"].append(queryid)
        if query_count["$or"]!=[]:
            dataset_count = get_count(self, self.request_attributes.mongo_collection, query_count)
            if dataset_count == 0:
                docs = []
            else:
                docs = get_documents(
                    self,
                    self.request_attributes.mongo_collection,
                    query_count,
                    skip*limit,
                    limit
                )
                docs=list(docs)
        else:
            dataset_count=0
            dataset.exists=False
        if dataset_count==0:
            return dataset
    if dataset_count > 0:
        dataset.exists=True
    dataset.dataset_count=dataset_count
    dataset.docs=docs
    return dataset

@log_with_args_mongo(config.level)
def get_filtering_documents(self, collection: Collection, query: dict, remove_id: dict,skip: int, limit: int) -> Cursor:
    # Get the docs by removing the unwanted id
    return collection.find(query,remove_id).skip(skip).limit(limit).max_time_ms(100 * 1000)

from functools import lru_cache


@lru_cache(maxsize=4096)
def _get_filtering_term_scopes(term_id):
    """Cache filtering-term scopes to avoid repeated MongoDB reads."""
    client = get_client()
    filtering_terms = client[mongo_conf.database_name].filtering_terms

    doc = filtering_terms.find_one(
        {"id": term_id},
        {"_id": 0, "scopes": 1},
    )

    if doc is None:
        return None

    return tuple(doc.get("scopes") or ())


@lru_cache(maxsize=1)
def _get_genomic_variant_endpoint():
    """Cache the genomic variant endpoint configuration."""
    return import_genomicVariant_confile()["genomicVariant"]["endpoint_name"]


@log_with_args_mongo(config.level)
def choose_scope(self, scope, filter):
    term_id = filter.id

    # Retrieve cached scopes, or query MongoDB on the first request.
    scopes = _get_filtering_term_scopes(term_id)

    # If the filtering term does not exist, preserve the validation error.
    if scopes is None:
        raise InvalidRequest(
            "The filtering term: {} is not a valid filtering term.".format(
                term_id
            )
        )

    genomic_variant_endpoint = _get_genomic_variant_endpoint()
    entry_type = self.request_attributes.entry_type

    # If no scope was requested, infer it from the term and endpoint.
    if scope is None:
        if not scopes:
            # Internal zygosity terms do not have a scope.
            if term_id in ("GENO:0000136", "GENO:0000458"):
                return None

            if entry_type == genomic_variant_endpoint:
                return "genomicVariation"

            return entry_type[:-1]

        # Prefer a scope compatible with the requested endpoint.
        for scoped in scopes:
            if (
                str(scoped) + "s" == entry_type
                and entry_type != genomic_variant_endpoint
            ):
                return str(scoped)

            if (
                str(scoped) == "genomicVariation"
                and entry_type == genomic_variant_endpoint
            ):
                return str(scoped)

        # If exactly one scope is available, infer it.
        if len(scopes) == 1:
            return scopes[0]

        raise InvalidRequest(
            "Look at filtering terms endpoint and select a scope "
            "from one of the available scope values for this filtering "
            "term: {}".format(term_id)
        )

    # If a scope was explicitly requested, validate it.
    if scope in scopes:
        return scope

    raise InvalidRequest(
        "Scope requested in filtering term does not match any of its "
        "possible scopes. Look at filtering terms endpoint to know "
        "which scopes you can select for this filtering term: {}".format(
            term_id
        )
    )