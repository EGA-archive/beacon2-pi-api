from typing import List, Union
import re
from beacon.request.parameters import AlphanumericFilter, OntologyFilter
from beacon.connections.omopcdm.utils import peek
from beacon.connections.omopcdm.__init__ import client
from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level

import aiosql
from pathlib import Path

CURIE_REGEX = r'^([a-zA-Z0-9]*):\/?[a-zA-Z0-9./]*$'

queries_file = Path(__file__).parent / "sql" / "basic_queries.sql"
filter_queries = aiosql.from_path(queries_file, "psycopg2")

@log_with_args(level)
def apply_filters(self, filtersGet: dict, filtersPost: List[dict], scope: str, granularity : str, limit : int = 10, skip : int = 0) -> dict:
    # Get and Post Filters as dict
    filters = []
    if filtersGet:
        LOG.debug("Get Query")
        listFilters= filtersGet["filters"].split(",")
        for filter in listFilters:
            # All Get Queries have include descendant terms as default
            filterDict = {"id":filter, "scope": scope, "includeDescendantTerms": "true"}
            filters.append(filterDict)
    elif filtersPost:
        LOG.debug("Post Query")
        filters = filtersPost
    else:
        return {}
    
    # Create query
    query = ''
    for filter in filters:
        # Alphanumeric filter
        if "value" in filter:
            filter = AlphanumericFilter(**filter)
            partial_query = apply_alphanumeric_filter(self, filter) # Only individuals
        # Ontology filters
        elif re.match(CURIE_REGEX, filter["id"]):
            ontFilter = OntologyFilter(**filter)
            if 'includeDescendantTerms' not in filter:
                ontFilter.include_descendant_terms = True
            elif filter['includeDescendantTerms'] == 'true':
                ontFilter.include_descendant_terms = True
            partial_query = apply_ontology_filter(self, ontFilter, scope) # Individuals or biosamples
        else:
            return query
        query += partial_query

    # Create final SQL queries per scope
    if scope == "biosamples":
        column = "specimen_id"
        table = "specimen"

    else:   # Individuals
        column = "person_id"
        table = "person"

    # Query different on granularity
    if granularity == "boolean":
        finalQuery = f""" 
        SELECT EXISTS (
            SELECT 1
            FROM cdm.{table} p
            WHERE true {query}
            );
        """
    elif granularity == "count":
        finalQuery = f"""
            SELECT COUNT(*)
                    FROM cdm.{table} p
                    WHERE true {query}
        """
    else:   # Record response
        finalQuery = f""" 
            SELECT {column}, 
                ( SELECT COUNT(*)
                    FROM cdm.{table} p
                    WHERE true {query}) AS totalCount
            FROM cdm.{table} p
            WHERE true {query}
            limit {limit}
            offset {skip};
        """
    return finalQuery

def search_descendants(concept_id: str) -> list:
    records = filter_queries.sql_get_descendants(client, concept_id=concept_id)
    l_descendants = set()
    for descendant in records:
        l_descendants.add(descendant[0])
    return l_descendants


def map_domains(domain_id: str) -> dict:
    # Domain_id : Table in OMOP
    # Maybe there is more than one mapping in the condition domain
    dictMapping = {
        # Individuals
        'Gender':['person','gender_concept_id'],
        'Race':['person','race_concept_id'],
        'Condition':['condition_occurrence','condition_concept_id'],
        'Measurement':['measurement','measurement_concept_id'],
        'Procedure':['procedure_occurrence','procedure_concept_id'],
        'Observation':['observation','observation_concept_id'],
        'Drug':['drug_exposure','drug_concept_id'],

        # Biosamples
        'Spec Disease Status':['specimen', 'disease_status_concept_id'],
        'Spec Anatomic Site':['specimen', 'anatomic_site_concept_id']
    }
    return dictMapping[domain_id]

@log_with_args(level)
def filter_to_OMOP_vocabulary(self, filter: Union[OntologyFilter, AlphanumericFilter]):
    listConcept_id = set() # Set to store Concept id + Possible descendant terms
    vocabulary_id, concept_code = filter.id.split(':')
    records = filter_queries.sql_get_concept_domain(client,
                                                        vocabulary_id=vocabulary_id,
                                                        concept_code=concept_code)
    # Check if records is empty
    res = peek(records)
    if res is None:
        return [], 0
    _, records = res
    for record in records:
        original_concept_id = record[0]
        domain_id = record[1]
    listConcept_id.add(original_concept_id)
    # Look in which domains the concept_id belongs
    tableMap=map_domains(domain_id)
    if type(filter) == OntologyFilter:
        if filter.include_descendant_terms:
            # Import descendants of the concept_id
            concept_ids= search_descendants(original_concept_id)
            # Concept_id and descendants in same set()
            listConcept_id = listConcept_id.union(concept_ids)
    return listConcept_id, tableMap 

@log_with_args(level)
def format_value(self, value: Union[str, List[int]]) -> Union[List[int], str, int, float]:
    if isinstance(value, list):
        return value# pragma: no cover
    elif isinstance(value, int):
        return value# pragma: no cover
    
    elif value.isnumeric():
        if float(value).is_integer():
            return int(value)
        else:
            return float(value)# pragma: no cover
    
    else:
        return value


@log_with_args(level)
def apply_alphanumeric_filter(self,  filter: AlphanumericFilter) -> str:
    scope = filter.scope

    formatted_value = format_value(self, filter.value)

    # # If value is string
    # if isinstance(formatted_value,str):
    #     if filter.id in conf.alphanumeric_terms:
    #         filter.id = filter.id# pragma: no cover
    #     else:
    #         filter.id = filter.id + '.' + 'label'        
    # else:
    #     # Age Alphanumeric filters
    if (filter.id == 'ageOfOnset' or
        filter.id == 'ageAtProcedure' or
        filter.id == 'observationMoment' or
        filter.id == 'ageAtExposure'):
        listConcept_id = ['None']
        if filter.id == 'ageOfOnset':
            try:
                scope = filter['scope']
            except:
                print("You need an scope if you are using 'ageOfOnset', try 'disease' or 'treatments'")
            if "disease" in scope:
                filter.id = 'ageAtDisease'
            elif "treatments" in scope:
                filter.id = 'ageAtTreatment'
        mappingDict = {
            'ageAtDisease': ['condition_occurrence', 'condition_start_date'],
            'ageAtProcedure': ['procedure_occurrence', 'procedure_date'],
            'observationMoment': ['measurement', 'measurement_date'],
            'ageAtExposure': ['observation', 'observation_date'],
            'ageAtTreatment': ['drug_exposure', 'drug_exposure_start_date']
            }
        LOG.debug(f"scope {scope}")
        LOG.debug(f"mappingDict[filter.id][0] {mappingDict[filter.id][0]}")

        # Create filter
        query = f"""
            and exists (
                select 1
                from cdm.{mappingDict[filter.id][0]} tab
                where p.person_id = tab.person_id
                and (
                CASE
                    WHEN birth_datetime IS NOT NULL THEN extract(Year from age({mappingDict[filter.id][1]}, birth_datetime)) {filter.operator} {filter.value} 
                    ELSE (extract(Year from {mappingDict[filter.id][1]}) - year_of_birth)  {filter.operator} {filter.value}
                END )
                )
                """
    # Other alphanumeric filters with integers
    else:
        conceptId, tableMap = filter_to_OMOP_vocabulary(self, filter)
        LOG.debug(tableMap)
        query = f"""
            and exists (
                select 1
                from cdm.{tableMap[0]} tab
                where p.person_id = tab.person_id
                and (
                {tableMap[1]} = {''.join(map(str, conceptId))} and value_as_number {filter.operator} {filter.value})
                )
                """
    return query


@log_with_args(level)
def apply_ontology_filter(self, filter: OntologyFilter, scope: str) -> str:
    setConceptId, tableMap = filter_to_OMOP_vocabulary(self, filter)
    LOG.debug(tableMap)
    listConceptId = []
    for conceptId in setConceptId:
        listConceptId.append(tableMap[1] + ' = ' + str(conceptId))
    partialQuery = ' or '.join(listConceptId)
    if scope == "biosamples":
        partialQuery = f"and ({partialQuery})"
        return partialQuery
    elif scope == "individuals":
        query = f"""
                    and exists (
                        select 1
                        from cdm.{tableMap[0]} tab
                        where p.person_id = tab.person_id
                        and ({partialQuery})
                        )
                """
        return query