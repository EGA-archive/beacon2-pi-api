from beacon.request.parameters import RequestParams
from beacon.response.schemas import DefaultSchemas
from beacon.connections.omopcdm.__init__ import client
from beacon.connections.omopcdm.utils import queryExecutor, search_ontologies
from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level
from beacon.connections.omopcdm.filters import apply_filters
from typing import Optional

import beacon.connections.omopcdm.mappings as mappings
from beacon.connections.omopcdm.biosamples import get_biosamples_with_person_id

import aiosql
from pathlib import Path
queries_file = Path(__file__).parent / "sql" / "individuals.sql"
individual_queries = aiosql.from_path(queries_file, "psycopg2")


def get_individual_info(offset: int=0, limit: int=10, person_id: str=None) -> list:
    if person_id == None:
        records = individual_queries.sql_get_individuals(client, offset=offset, limit=limit)
        if not records:
            return []
        listId = [str(record[0]) for record in records]
    else:
        records = individual_queries.sql_get_individual_id(client, person_id=person_id)
        if not records:
            return []
        listId = [str(records[0])]
    return listId

def get_individuals_person(listIds: list) -> dict:
    dict_person = {}
    for person_id in listIds:
        records = individual_queries.sql_get_person(client, person_id=person_id)
        listValues = []
        for record in records:
            listValues.append({"gender_concept_id" : record[0],
                                "race_concept_id" : record[1]})
        dict_person[person_id] = listValues
    return dict_person


def get_individuals_condition(listIds: list) -> dict:
    dict_condition = {}
    for person_id in listIds:
        records = individual_queries.sql_get_condition(client, person_id=person_id)
        listValues = []
        for record in records:
            if record[1] == None:
                ageOfOnset = "Not Available"
            else:
                ageOfOnset = f"P{record[1]}Y"
            listValues.append({"condition_concept_id" : record[0],
                               "condition_ageOfOnset" : ageOfOnset})
        dict_condition[person_id] = listValues

    return dict_condition

def get_individuals_procedure(listIds: list) -> dict:
    dict_procedure = {}
    for person_id in listIds:
        records = individual_queries.sql_get_procedure(client, person_id=person_id)
        listValues = []
        for record in records:
            if record[1] == "None":
                ageOfOnset = "Not Available"
            else:
                ageOfOnset = f"P{record[1]}Y"            
            listValues.append({"procedure_concept_id" : record[0],
                                "procedure_ageOfOnset" : ageOfOnset,
                                "procedure_date" : record[2]})
        dict_procedure[person_id] = listValues
    return dict_procedure        


def get_individuals_measures(listIds: list) -> dict:
    dict_measures = {}
    for person_id in listIds:
        records = individual_queries.sql_get_measure(client, person_id=person_id)
        listValues = []
        for record in records:
            if record[1] == "None":
                ageOfOnset = "Not Available"
            else:
                ageOfOnset = f"P{record[1]}Y"
            listValues.append({"measurement_concept_id" : record[0],
                                "measurement_ageOfOnset" : ageOfOnset,
                                "measurement_date" : record[2],
                                "unit_concept_id" : record[3],
                                "value_source_value" : record[4]})
        dict_measures[person_id] = listValues
    return dict_measures


def get_individuals_exposures(listIds: list) -> dict:
    dict_exposures = {}
    for person_id in listIds:
        records = individual_queries.sql_get_exposure(client, person_id=person_id)
        records_duration = individual_queries.sql_get_exposure_period(client, person_id=person_id)
        listValues = []
        for record in records:
            if record[1] == "None":
                ageOfOnset = "Not Available"
            else:
                ageOfOnset = f"P{record[1]}Y"
            if records_duration:
                records_duration = str(records_duration[0])
            else:
                records_duration = "Not Available"
            listValues.append({"observation_concept_id" : record[0],
                                "observation_ageOfOnset" : ageOfOnset,
                                "observation_date" : record[2],
                                "unit_concept_id" : record[3],
                                "duration": records_duration})
        dict_exposures[person_id] = listValues
    return dict_exposures

def get_individuals_treatments(listIds: list) -> dict:
    dict_treatments = {}
    for person_id in listIds:
        records = individual_queries.sql_get_treatment(client, person_id=person_id)
        listValues = []
        for record in records:
            if record[1] == "None":
                ageOfOnset = "Not Available"
            else:
                ageOfOnset = f"P{record[1]}Y"
            listValues.append({"drugExposure_concept_id" : record[0],
                                "drugExposure_ageOfOnset" : ageOfOnset})
        dict_treatments[person_id] = listValues
    return dict_treatments 


def format_query(listIds: list, dictPerson: dict, dictCondition: dict, dictProcedures: dict, dictMeasures: dict, dictExposures: dict, dictTreatments: dict)-> list:
    list_format = []
    for person_id in listIds:
        dictId = {"id":person_id}
        if any("gender_concept_id" in d for d in dictPerson[person_id]):
            dictId["sex"] = dictPerson[person_id][0]["gender_concept_id"]
        if any("race_concept_id" in d for d in dictPerson[person_id]):
            dictId["ethnicity"] = dictPerson[person_id][0]["race_concept_id"]
        if any("condition_concept_id" in d for d in dictCondition[person_id]):
            dictId["diseases"] = list(map(mappings.diseases_table_map, dictCondition[person_id]))
        if any("procedure_concept_id" in d for d in dictProcedures[person_id]):
            dictId["interventionsOrProcedures"] = list(map(mappings.procedures_table_map, dictProcedures[person_id]))
        if any("measurement_concept_id" in d for d in dictMeasures[person_id]):
            dictId["measures"] = list(map(mappings.measures_table_map, dictMeasures[person_id]))
        if any("observation_concept_id" in d for d in dictExposures[person_id]):
            dictId["exposures"] = list(map(mappings.exposures_table_map, dictExposures[person_id]))
        if any("drugExposure_concept_id" in d for d in dictTreatments[person_id]):
            dictId["treatments"] = list(map(mappings.treatments_table_map, dictTreatments[person_id]))
        list_format.append(dictId)
    return list_format

def retrieveRecords(listIds: list) -> list:
    dictPerson = get_individuals_person(listIds)        # List with Id, sex, ethnicity
    dictCondition = get_individuals_condition(listIds)  # List with al the diseases per Id
    dictProcedures = get_individuals_procedure(listIds)
    dictMeasures = get_individuals_measures(listIds)
    dictExposures = get_individuals_exposures(listIds)
    dictTreatments = get_individuals_treatments(listIds)

    dictPerson = search_ontologies(dictPerson)
    dictCondition = search_ontologies(dictCondition)
    dictProcedures = search_ontologies(dictProcedures)
    dictMeasures = search_ontologies(dictMeasures)
    dictExposures = search_ontologies(dictExposures)
    dictTreatments = search_ontologies(dictTreatments)

    docs = format_query(listIds, dictPerson, dictCondition, dictProcedures, dictMeasures, dictExposures, dictTreatments)

    return docs

@log_with_args(level)
def get_individuals(self, entry_id: Optional[str], qparams: RequestParams, dataset: str):

    include = qparams.query.include_resultset_responses # Always HIT responses
    scope = "individuals"
    schema = DefaultSchemas.INDIVIDUALS
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
        listIds = get_individual_info(skip, limit, entry_id)    # List with all Ids
        countIds = individual_queries.count_individuals(client)   # Count individuals
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
def get_individual_with_id(self, entry_id: Optional[str], qparams: RequestParams, dataset: str):
    schema = DefaultSchemas.INDIVIDUALS
    include = qparams.query.include_resultset_responses
    
    # Search Id
    listIds = get_individual_info(person_id=entry_id)
    if not listIds:
        return schema, 0, 0, {}, dataset

    docs = retrieveRecords(listIds)

    return schema, 1, 1, docs, dataset

# OMOP CDM do not work with variants
@log_with_args(level)
def get_variants_of_individual(self, entry_id: Optional[str], qparams: RequestParams, dataset: str):
    schema = DefaultSchemas.GENOMICVARIATIONS

    return schema, 0, 0, {}, dataset

@log_with_args(level)
def get_biosamples_of_individual(self, entry_id: Optional[str], qparams: RequestParams, dataset: str):
    
    schema = DefaultSchemas.BIOSAMPLES

    count, docs = get_biosamples_with_person_id(entry_id, qparams)
    
    return schema, count, count, docs, dataset