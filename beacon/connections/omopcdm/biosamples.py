from beacon.request.parameters import RequestParams
from beacon.response.schemas import DefaultSchemas
from beacon.connections.omopcdm.__init__ import client
from beacon.connections.omopcdm.utils import queryExecutor, search_ontologies
from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level
from beacon.connections.omopcdm.filters import apply_filters
from typing import Optional

import aiosql
from pathlib import Path
queries_file = Path(__file__).parent / "sql" / "biosamples.sql"
biosamples_queries = aiosql.from_path(queries_file, "psycopg2")

def get_biosample_info(offset=0, limit=10, biosample_id=None):
    if biosample_id == None:
        records = biosamples_queries.sql_get_biosamples(client, offset=offset, limit=limit)
        if not records:
            return []
        listId = [str(record[0]) for record in records]
    else:
        records = biosamples_queries.sql_get_biosample_id(client, specimen_id=biosample_id)
        if not records:
            return []
        listId = [str(records[0])]
    return listId

def get_specimens(listIds):
    dict_specimens = {}
    for biosample_id in listIds:
        records = biosamples_queries.sql_get_specimen(client, specimen_id = biosample_id)
        listValues = []
        for record in records:
            listValues.append({'person_id': record[0],
                               'disease_status_concept_id': record[1],
                               'anatomic_site_concept_id': record[2],
                               'specimen_date': record[3],
                               'specimen_moment': record[4]})
        dict_specimens[biosample_id] = listValues
    return dict_specimens

def format_query(listIds, specimens):

    list_format = []
    for biosample_id in listIds:
        dict_biosample_id =  { 
            "id": str(biosample_id),
            "individualId": str(specimens[biosample_id][0]["person_id"]),
            "biosampleStatus": {
                "id":  specimens[biosample_id][0]["disease_status_concept_id"]["id"],
                "label": specimens[biosample_id][0]["disease_status_concept_id"]["label"]
            },
            "sampleOriginType": {
                "id" : specimens[biosample_id][0]["anatomic_site_concept_id"]["id"],
                "label" : specimens[biosample_id][0]["anatomic_site_concept_id"]["label"]
            },
            "collectionMoment": specimens[biosample_id][0]["specimen_date"],
            "collectionDate": specimens[biosample_id][0]["specimen_moment"],
            "info": {}
            }
        list_format.append(dict_biosample_id)
    return list_format


def retrieveRecords(listIds: list) -> list:
    specimens = get_specimens(listIds)

    specimens = search_ontologies(specimens)

    docs = format_query(listIds, specimens)

    return docs

@log_with_args(level)
def get_biosamples(self, entry_id: Optional[str], qparams: RequestParams, dataset: str):
    scope = 'biosamples'
    include = qparams.query.include_resultset_responses # Always HIT responses
    schema = DefaultSchemas.BIOSAMPLES
    limit = qparams.query.pagination.limit
    skip = qparams.query.pagination.skip
    if limit > 50 or limit == 0:
        limit = 50
    granularity = qparams.query.requested_granularity   # record, count, boolean

    # If filters
    if qparams.query.filters or "filters" in qparams.query.request_parameters:
        query = apply_filters(self,
                      qparams.query.request_parameters, 
                      qparams.query.filters, 
                      scope,
                      granularity,
                      limit, 
                      skip)
        # Run query
        resultQuery = queryExecutor(query)
    else:   # Get All individuals
        listIds = get_biosample_info(skip, limit, entry_id)    # List with all Ids
        countIds = biosamples_queries.get_count_specimen(client)   # Count individuals
        if countIds ==0:
            resultQuery = []
        else:
            resultQuery = [(countIds, listId) for listId in listIds ]

    LOG.debug(f"Final query {resultQuery}")
    if not resultQuery:
        return schema, 0, 0, {}, dataset
    # Different response depending the granularity
    if granularity == "boolean":
        return schema, 1, 1, {}, dataset
    elif granularity == "count":
        return schema, resultQuery[0][0], resultQuery[0][0], {}, dataset
    # Record response
    count = resultQuery[0][0]
    listIds = [str(record[1]) for record in resultQuery]
    docs = retrieveRecords(listIds)

    return schema, count, count, docs, dataset

@log_with_args(level)
def get_biosample_with_id(self, entry_id: Optional[str], qparams: RequestParams, dataset: str):
    include = qparams.query.include_resultset_responses
    schema = DefaultSchemas.BIOSAMPLES

    # Search Id
    listIds = get_biosample_info(person_id=entry_id)
    if not listIds:
        return schema, 0, 0, {}, dataset

    docs = retrieveRecords(listIds)

    return schema, 1, 1, docs, dataset

# Function to get all the biosamples from an individual id
def get_biosamples_with_person_id(person_id: Optional[str], qparams: RequestParams):

    schema = DefaultSchemas.BIOSAMPLES
    specimens = biosamples_queries.get_specimen_by_person_id(client, person_id=person_id)
    listSpecimenIds = [specimen[0] for specimen in specimens ]
    if not listSpecimenIds:
        return 0, {}
    docs = retrieveRecords(listSpecimenIds)
    return  len(listSpecimenIds), docs