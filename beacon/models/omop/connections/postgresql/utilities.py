import logging
import itertools
from sqlalchemy import select, func
from beacon.connections.postgresql_omop.__init__ import client
from beacon.connections.postgresql_omop import get_table

LOG = logging.getLogger(__name__)

MAX_LIMIT = 50


# Function to know if generator is empty
def peek(iterable):
    if isinstance(iterable, list):
        iterable = iter(iterable)
    try:
        first = next(iterable)
    except StopIteration:
        return None, []
    return first, itertools.chain([first], iterable)

async def basic_query(query):
    async with client.connect() as conn:
        result = await conn.execute(query)
        records = result.mappings().all()

    return records

# for individuals
async def search_ontology(concept_ids):
    vocab_conc= get_table("concept", schema="vocabularies")
    concept_ids = list(set([x for x in concept_ids if x != 0]))  # Remove 0 and duplicates

    if not concept_ids:
        return {}

    records = select(
        func.concat(vocab_conc.c.vocabulary_id, ':', vocab_conc.c.concept_code).label('id'),
        vocab_conc.c.concept_id.label('concept_id'),
        vocab_conc.c.concept_name.label('label')
    ).where(
        vocab_conc.c.concept_id.in_(concept_ids)
    )

    async with client.connect() as conn:
        result = await conn.execute(records)
        rows = result.mappings().all()
        records = {}

        for row in rows:
            ontology_id = row["id"]
            # Temporary change for CURIE validation
            if ontology_id == "UCUM:/min":
                ontology_id = "UCUM:1/min"
            if ontology_id == "UCUM:%":
                ontology_id = "UCUM:percent"

            records[row["concept_id"]] = {
                "id": ontology_id,
                "label": row["label"]
            }

    return records

def extract_concept_ids(data):
    """Recursively extract all concept_id integers from nested structure."""
    concept_ids = set()
    
    if isinstance(data, dict):
        for key, value in data.items():
            if "concept_id" in key and isinstance(value, int):
                concept_ids.add(value)
            elif isinstance(value, (dict, list)):
                concept_ids.update(extract_concept_ids(value))
    elif isinstance(data, list):
        for item in data:
            concept_ids.update(extract_concept_ids(item))

    return concept_ids

def resolve_concepts_in_data(data, cache):
    """Resolve concept_ids using pre-fetched cache."""
    if isinstance(data, dict):
        for key, value in data.items():
            if "concept_id" in key and isinstance(value, int):
                data[key] = cache.get(value, {'id': "None:No matching concept", 'label': "No matching concept"})
            elif isinstance(value, (dict, list)):
                resolve_concepts_in_data(value, cache)
    elif isinstance(data, list):
        for item in data:
            resolve_concepts_in_data(item, cache)
    return data

async def search_ontologies(data):
    concept_ids = extract_concept_ids(data)
    resolved_cache = await search_ontology(concept_ids)

    # Add default 'no match' for zero or not found
    resolved_cache[0] = {'id': "None:No matching concept", 'label': "No matching concept"}
    
    return resolve_concepts_in_data(data, resolved_cache)

# for biosamples
async def search_ontology2(concept_ids):
    vocab_conc= get_table("concept", schema="vocabularies")
    concept_ids = list(set([x for x in concept_ids if x != 0]))

    if not concept_ids:
        return {}

    records = select(
        func.concat(vocab_conc.c.vocabulary_id, ':', vocab_conc.c.concept_code).label('id'),
        vocab_conc.c.concept_id.label('concept_id'),
        vocab_conc.c.concept_name.label('label')
    ).where(
        vocab_conc.c.concept_id.in_(concept_ids)
    )

    async with client.connect() as conn:
        result = await conn.execute(records)
        rows = result.mappings().all()
        records = {
            row["concept_id"]: {
                "id": row["id"],
                "label": row["label"]
            } for row in rows
        }

    return records

def extract_concept_ids2(data):
    """Recursively extract all concept_id integers from nested structure."""
    concept_ids = set()
    
    if isinstance(data, dict):
        for key, value in data.items():
            if "concept_id" in key:
                try:
                    val = int(value)
                    concept_ids.add(val)
                except (ValueError, TypeError):
                    pass
            elif isinstance(value, (dict, list)):
                concept_ids.update(extract_concept_ids2(value))
    elif isinstance(data, list):
        for item in data:
            concept_ids.update(extract_concept_ids2(item))

    return concept_ids

def resolve_concepts_in_data2(data, cache):
    """Resolve concept_ids using pre-fetched cache."""
    if isinstance(data, dict):
        for key, value in data.items():
            if "concept_id" in key:
                try:
                    val = int(value)
                    data[key] = cache.get(val, {'id': "None:No matching concept", 'label': "No matching concept"})
                except (ValueError, TypeError):
                    data[key] = {'id': "None:No matching concept", 'label': "No matching concept"}
            elif isinstance(value, (dict, list)):
                resolve_concepts_in_data2(value, cache)
    elif isinstance(data, list):
        for item in data:
            resolve_concepts_in_data2(item, cache)
    return data

async def search_ontologies_bio(data):
    concept_ids = extract_concept_ids2(data)
    resolved_cache = await search_ontology2(concept_ids)

    # Add default 'no match' for zero or not found
    resolved_cache[0] = {'id': "None:No matching concept", 'label': "No matching concept"}
    
    return resolve_concepts_in_data2(data, resolved_cache)


###################################################
from typing_extensions import Self
from pydantic import BaseModel
from strenum import StrEnum
from typing import List
from beacon.conf import conf_default
from humps.main import camelize
from aiohttp.web_request import Request

class CamelModel(BaseModel):
    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True


class IncludeResultsetResponses(StrEnum):
    ALL = "ALL",
    HIT = "HIT",
    MISS = "MISS",
    NONE = "NONE"
    

class Granularity(StrEnum):
    BOOLEAN = "boolean",
    COUNT = "count",
    RECORD = "record"


class Pagination(CamelModel):
    skip: int = 0
    limit: int = 10


class RequestMeta(CamelModel):
    requested_schemas: List[str] = []
    api_version: str = conf_default.api_version


class RequestQuery(CamelModel):
    filters: List[dict] = []
    include_resultset_responses: IncludeResultsetResponses = IncludeResultsetResponses.HIT
    pagination: Pagination = Pagination()
    request_parameters: dict = {}
    test_mode: bool = False
    requested_granularity: Granularity = Granularity(conf_default.default_beacon_granularity)


class RequestParams(CamelModel):
    meta: RequestMeta = RequestMeta()
    query: RequestQuery = RequestQuery()
    
    def from_request(self, request: Request) -> Self: 
        if request.method != "POST" or not request.has_body or not request.can_read_body:
            for k, v in request.query.items():
                if k == "requestedSchema":
                    self.meta.requested_schemas = [v]
                elif k == "skip":
                    self.query.pagination.skip = int(v)
                elif k == "limit":
                    self.query.pagination.limit = int(v)
                elif k == "includeResultsetResponses":
                    self.query.include_resultset_responses = IncludeResultsetResponses(v)
                elif k == "filters":
                    self.query.filters.append(v)                 
                else:
                    self.query.request_parameters[k] = v
        return self

    def summary(self):
        list_of_filters=[]
        if len(self.query.filters) == 0:        # No filters
            pass
        elif type(self.query.filters[0]) is dict:    # POST filters
            for item in self.query.filters:
                for k,v in item.items():
                    list_of_filters.append(v)
        else:                                   # GET filters
            for item in self.query.filters:
                list_of_filters.append(item)

        #LOG.info(list_of_filters)
        return {
            "apiVersion": self.meta.api_version,
            "requestedSchemas": self.meta.requested_schemas,
            "filters": list_of_filters,
            "requestParameters": self.query.request_parameters,
            "includeResultsetResponses": self.query.include_resultset_responses,
            "pagination": self.query.pagination.dict(),
            "requestedGranularity": self.query.requested_granularity,
            "testMode": self.query.test_mode
        }

###################################################
from enum import Enum


class DefaultSchemas(Enum):
    BIOSAMPLES = {"entityType": "biosample", "schema": "beacon-dataset-v2.0.0"}
    COHORTS = {"entityType": "cohort", "schema": "beacon-cohort-v2.0.0"}
    INDIVIDUALS = {"entityType": "individual", "schema": "beacon-individual-v2.0.0"}
    FILTERINGTERMS = {"entityType": "filteringterms", "schema": "beacon-dataset-v2.0.0"}


###################################################
