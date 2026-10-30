from functools import lru_cache

from beacon.request.parameters import OntologyFilter
from beacon.request.classes import Similarity
from beacon.connections.mongo.utils import get_documents, choose_scope
from beacon.connections.mongo.client import get_client
from beacon.utils.modules import get_all_modules_connections_script
from beacon.connections.mongo import conf as mongo_conf
from beacon.exceptions.exceptions import InvalidRequest


@lru_cache(maxsize=32)
def get_cached_cross_query_modules():
    """Cache cross-query module discovery across requests."""
    return tuple(
        get_all_modules_connections_script(
            "filters.cross_queries.cross_query",
            "mongo",
        )
    )


def apply_ontology_filter(
    self,
    query: dict,
    filter: OntologyFilter,
    request_parameters: dict,
    dataset: str,
) -> dict:

    client = get_client()
    database = client[mongo_conf.database_name]

    synonyms_collection = database.synonyms
    similarities_collection = database.similarities
    filtering_terms_collection = database.filtering_terms

    final_term_list = []

    # ---------------------------------------------------------
    # 1. Resolve synonyms
    # ---------------------------------------------------------
    synonym_doc = get_documents(
        self,
        synonyms_collection,
        {"id": filter.id},
        0,
        1,
    )

    try:
        synonym_id = synonym_doc[0]["synonym"]
    except (IndexError, KeyError, TypeError):
        synonym_id = None

    if synonym_id is not None:
        final_term_list.append(synonym_id)

    # ---------------------------------------------------------
    # 2. Resolve the ontology scope
    # ---------------------------------------------------------
    try:
        scope = filter.scope
        scope=choose_scope(self, scope, filter)
    except Exception:
        if synonym_id is not None:
            filter.id=synonym_id
            scope = filter.scope
            scope=choose_scope(self, scope, filter)
        else:
            raise

    # ---------------------------------------------------------
    # 3. Resolve similarity terms
    # ---------------------------------------------------------
    similarity_fields = {
        Similarity.HIGH: "similarity_high",
        Similarity.MEDIUM: "similarity_medium",
        Similarity.LOW: "similarity_low",
    }

    if filter.similarity != Similarity.EXACT:
        similarity_field = similarity_fields.get(filter.similarity)

        if similarity_field is not None:
            similarity_doc = similarities_collection.find_one(
                {"id": filter.id},
                {
                    similarity_field: 1,
                    "_id": 0,
                },
            )

            if similarity_doc:
                similar_terms = similarity_doc.get(
                    similarity_field,
                    [],
                )

                if similar_terms is not None:
                    final_term_list = list(similar_terms)

    # ---------------------------------------------------------
    # 4. Include descendant terms
    # ---------------------------------------------------------
    if filter.includeDescendantTerms:
        ontology_id = filter.id.replace("\n", "")

        descendants_doc = similarities_collection.find_one(
            {"id": ontology_id},
            {
                "descendants": 1,
                "_id": 0,
            },
        )

        if descendants_doc:
            descendants = descendants_doc.get("descendants", [])

            if descendants:
                final_term_list.extend(descendants)

    # Include the requested term itself.
    final_term_list.append(filter.id)

    # Remove duplicate terms while preserving their order.
    final_term_list = list(dict.fromkeys(final_term_list))

    # ---------------------------------------------------------
    # 5. Resolve the filtering-term label
    # ---------------------------------------------------------
    filtering_term_query = {
        "$and": [
            {"id": filter.id},
            {"scopes": scope},
        ]
    }

    filtering_term_docs = get_documents(
        self,
        filtering_terms_collection,
        filtering_term_query,
        0,
        1,
    )

    if not filtering_term_docs:
        raise InvalidRequest(
            "No filtering-term label found for {} "
            "with scope {}.".format(filter.id, scope)
        )

    label = filtering_term_docs[0].get("label")

    if not label:
        raise InvalidRequest(
            "The filtering term {} has no label for scope {}.".format(
                filter.id,
                scope,
            )
        )

    # ---------------------------------------------------------
    # 6. Resolve the field/property to filter
    # ---------------------------------------------------------
    regex_query = {
        "$and": [
            {
                "id": {
                    "$regex": ":" + label,
                    "$options": "i",
                }
            },
            {"scopes": scope},
        ]
    }

    field_docs = get_documents(
        self,
        filtering_terms_collection,
        regex_query,
        0,
        1,
    )

    if not field_docs:
        raise InvalidRequest(
            "Unable to resolve the filtering-term field for "
            "{} with scope {}.".format(filter.id, scope)
        )

    field_id = field_docs[0].get("id")

    if not field_id or ":" not in field_id:
        raise InvalidRequest(
            "Invalid filtering-term field identifier: {}".format(
                field_id
            )
        )

    query_term = field_id.split(":", 1)[0] + ".id"

    # ---------------------------------------------------------
    # 7. Generate the ontology filter query
    # ---------------------------------------------------------
    if final_term_list:
        query = {
            "$or": [
                {query_term: term}
                for term in final_term_list
            ]
        }

    # ---------------------------------------------------------
    # 8. Apply cross-query modules
    # ---------------------------------------------------------
    for module in get_cached_cross_query_modules():
        query = module.cross_query(
            self,
            query,
            scope,
            request_parameters,
            dataset,
        )

    return query