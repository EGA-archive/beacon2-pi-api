import logging, re
from typing import List, Optional
from decimal import Decimal
from sqlalchemy import select, func, bindparam, distinct, cast, String, case, or_, and_, literal, exists, extract, union_all
from sqlalchemy.sql import operators
from sqlalchemy.engine import Engine

from beacon.connections.postgresql_omop.conf import database_driver
from beacon.models.omop.connections.postgresql.utilities import RequestParams, DefaultSchemas, search_ontologies, basic_query, peek, search_ontologies_bio, MAX_LIMIT
import beacon.models.omop.connections.postgresql.mappings as mappings
from beacon.connections.postgresql_omop.__init__ import client
from beacon.connections.postgresql_omop import get_table

LOG = logging.getLogger(__name__)

###############################

def map_domains(domain_id):
    # Domain_id : Table in OMOP
    # Maybe there is more than one mapping in the condition domain
    dictMapping = {
        'Gender':{'person':'gender_concept_id'},
        'Race':{'person':'race_concept_id'},
        'Condition':{'condition_occurrence':'condition_concept_id'},
        'Measurement':{'measurement':'measurement_concept_id'},
        'Procedure':{'procedure_occurrence':'procedure_concept_id'},
        'Observation':{'observation':'observation_concept_id'},
        'Drug':{'drug_exposure':'drug_concept_id'}
    }
    return dictMapping[domain_id]

async def search_descendants(concept_id):
    vocab_conc_anc = get_table("concept_ancestor", schema="vocabularies")
    records = select(
        vocab_conc_anc.c.descendant_concept_id
    ).where(
        vocab_conc_anc.c.ancestor_concept_id == bindparam("concept_id"))
    
    async with client.connect() as conn:
        records = await conn.execute(records, {"concept_id": concept_id})

    l_descendants = set()
    for descendant in records:
        l_descendants.add(descendant[0])
    return l_descendants

def sql_filters_age(date, operator, value):
    cdm_person = get_table("person", schema="cdm")

    current_year = extract('year', func.current_date())
    current_month = extract('month', func.current_date())
    current_day = extract('day', func.current_date())

    birth_year = extract('year', cdm_person.c.birth_datetime)
    birth_month = extract('month', cdm_person.c.birth_datetime)
    birth_day = extract('day', cdm_person.c.birth_datetime)

    exact_age = (
        current_year - birth_year
        - case(
            (
                (current_month < birth_month) |
                ((current_month == birth_month) & (current_day < birth_day)),
                1
            ),
            else_=0
        )
    )

    # fallback if no birth_datetime
    approx_age = extract('year', date) - cdm_person.c.year_of_birth

    age_value = case(
        (cdm_person.c.birth_datetime != None, exact_age),
        else_=approx_age
    )

    return age_value.op(operator)(value)

def create_dynamic_filter(filters):
    cdm_person = get_table("person", schema="cdm")
    cdm_cond_occ = get_table("condition_occurrence", schema="cdm")
    cdm_mesure = get_table("measurement", schema="cdm")
    cdm_proc_occ = get_table("procedure_occurrence", schema="cdm")
    cdm_obser = get_table("observation", schema="cdm")
    cdm_drug_exp = get_table("drug_exposure", schema="cdm")

    base_filter = {
        'demografic_filters': [],
        'condition_filters': [],
        'measurement_filters': [],
        'procedures_filters': [],
        'exposures_filters': [],
        'treatments_filters': [],
    }
    
    operator_map = {
                    '=': operators.eq,
                    '==': operators.eq,
                    '>': operators.gt,
                    '>=': operators.ge,
                    '<': operators.lt,
                    '<=': operators.le,
                    '!=': operators.ne,
                }

    for fltr in filters:
        table_map = fltr[0]
        concept_ids = fltr[1]
        operator = fltr[2]
        value = fltr[3]
        
        filter_type = 'Alphanumeric' if operator else 'Ontology'

        if 'person' in table_map:
            variable_name = table_map['person']
            column = cdm_person.c[variable_name]
            
            conditions = []
            for concept_id in concept_ids:
                condition = column == concept_id
                conditions.append(condition)

            expr = or_(*conditions)
            base_filter['demografic_filters'].append(expr)

        if 'condition_occurrence' in table_map:
            variable_name = table_map['condition_occurrence']
            
            if variable_name == 'Age':
                age_expr = sql_filters_age(cdm_cond_occ.c.condition_start_date, operator, value)
                condition_expr = age_expr
            
            else:
                column = cdm_cond_occ.c[variable_name]
                condition_expr = or_(*[column == x for x in concept_ids])
            
            exists_expr = exists(
                select(literal(1))
                .select_from(cdm_cond_occ)
                .where(
                    and_(
                        cdm_cond_occ.c.person_id == cdm_person.c.person_id,
                        condition_expr
                    )
                )
            )

            base_filter['condition_filters'].append(exists_expr)
        if 'measurement' in table_map:
            variable_name = table_map['measurement']
            
            if variable_name == 'Age':
                age_expr = sql_filters_age(cdm_mesure.c.measurement_date, operator, value)
                condition_expr = age_expr

            elif filter_type == 'Alphanumeric':
                op_func = operator_map.get(operator)
                if op_func is None:
                    raise ValueError(f"Unsupported operator: {operator}")
                column = cdm_mesure.c[variable_name]
                if operator in ['=', '==', '!=']:
                    compare_col = case(
                        (
                            cdm_mesure.c.value_as_number.isnot(None),
                            cast(cdm_mesure.c.value_as_number, String)
                        ),
                        (
                            cdm_mesure.c.value_as_concept_id.isnot(None),
                            cast(cdm_mesure.c.value_as_concept_id, String)
                        ),
                        else_=cast(
                            cdm_mesure.c.value_source_value,
                            String
                        )
                    )
                    compare_val = value
                else:
                    compare_col = cdm_mesure.c.value_as_number
                    compare_val = float(value)

                conditions = []
                for concept_id in concept_ids:
                    concept_condition = column == concept_id
                    value_condition = op_func(compare_col, compare_val)
                    conditions.append(and_(concept_condition, value_condition))

                condition_expr = or_(*conditions)

            else:
                column = cdm_mesure.c[variable_name]
                condition_expr = or_(*[column == x for x in concept_ids])

            exists_expr = exists(
                select(literal(1))
                .select_from(cdm_mesure)
                .where(
                    and_(
                        cdm_mesure.c.person_id == cdm_person.c.person_id,
                        condition_expr
                    )))

            base_filter['measurement_filters'].append(exists_expr)
        if 'procedure_occurrence' in table_map:
            variable_name = table_map['procedure_occurrence']

            if variable_name == 'Age':
                age_expr = sql_filters_age(cdm_proc_occ.c.procedure_date, operator, value)
                condition_expr = age_expr

            else:
                column = cdm_proc_occ.c[variable_name]
                condition_expr = or_(*[column == x for x in concept_ids])

            exists_expr = exists(
                select(literal(1))
                .select_from(cdm_proc_occ)
                .where(
                    and_(
                        cdm_proc_occ.c.person_id == cdm_person.c.person_id,
                        condition_expr
                    )))

            base_filter['procedures_filters'].append(exists_expr)

        if 'observation' in table_map:
            variable_name = table_map['observation']

            if variable_name == 'Age':
                age_expr = sql_filters_age(cdm_obser.c.observation_date, operator, value)
                condition_expr = age_expr
            
            elif filter_type == 'Alphanumeric':
                op_func = operator_map.get(operator)
                if op_func is None:
                    raise ValueError(f"Unsupported operator: {operator}")
                column = cdm_obser.c[variable_name]
                if operator in ['=', '==', '!=']:
                    compare_col = case(
                        (
                            cdm_obser.c.value_as_number.isnot(None),
                            cast(cdm_obser.c.value_as_number, String)
                        ),
                        (
                            cdm_obser.c.value_as_string.isnot(None),
                            cast(cdm_obser.c.value_as_string, String)
                        ),
                        else_=cast(
                            cdm_obser.c.value_as_concept_id,
                            String
                        )
                    )
                    compare_val = value
                else:
                    compare_col = cdm_obser.c.value_as_number
                    compare_val = float(value)
                
                conditions = []
                for concept_id in concept_ids:
                    concept_condition = column == concept_id
                    value_condition = op_func(compare_col, compare_val)
                    conditions.append(and_(concept_condition, value_condition))

                condition_expr = or_(*conditions)

            else:
                column = cdm_obser.c[variable_name]
                condition_expr = or_(*[column == x for x in concept_ids])

            exists_expr = exists(
                select(literal(1))
                .select_from(cdm_obser)
                .where(
                    and_(
                        cdm_obser.c.person_id == cdm_person.c.person_id,
                        condition_expr
                    )))

            base_filter['exposures_filters'].append(exists_expr)
            
        if 'drug_exposure' in table_map:
            variable_name = table_map['drug_exposure']

            if variable_name == 'Age':
                age_expr = sql_filters_age(cdm_drug_exp.c.drug_exposure_start_date, operator, value)
                condition_expr = age_expr
            
            elif filter_type == 'Alphanumeric':
                column = cdm_drug_exp.c[variable_name]
                value_as_number = cdm_drug_exp.c.quantity

                op_func = operator_map.get(operator)
                if op_func is None:
                    raise ValueError(f"Unsupported operator: {operator}")

                conditions = []
                for concept_id in concept_ids:
                    concept_condition = column == concept_id
                    value_condition = op_func(value_as_number, value)
                    conditions.append(and_(concept_condition, value_condition))

                condition_expr = or_(*conditions)

            else:
                column = cdm_drug_exp.c[variable_name]
                condition_expr = or_(*[column == x for x in concept_ids])

            exists_expr = exists(
                select(literal(1))
                .select_from(cdm_drug_exp)
                .where(
                    and_(
                        cdm_drug_exp.c.person_id == cdm_person.c.person_id,
                        condition_expr
                    )))

            base_filter['treatments_filters'].append(exists_expr)

    return base_filter

def super_query_count(filters):
    cdm_person = get_table("person", schema="cdm")
    all_filters = []

    for key in [
        'demografic_filters',
        'condition_filters',
        'measurement_filters',
        'procedures_filters',
        'exposures_filters',
        'treatments_filters'
    ]:
        if key in filters and filters[key]:  
            values = filters.get(key)
            if not values:
                continue
            if not isinstance(values, list):
                values = [values]
            all_filters.extend(values)  
    
    query = select(
        func.count(distinct(cdm_person.c.person_id))
    ).where(
        and_(*all_filters)
    )

    return query

def super_query_get(filters, offset, limit):
    cdm_person = get_table("person", schema="cdm")
    all_filters = []

    for key in [
        'demografic_filters',
        'condition_filters',
        'measurement_filters',
        'procedures_filters',
        'exposures_filters',
        'treatments_filters'
    ]:
        if key in filters and filters[key]:  
            values = filters.get(key)
            if not values:
                continue
            if not isinstance(values, list):
                values = [values]
            all_filters.extend(values)  

    query = select(
        cdm_person.c.person_id
    ).where(
        and_(*all_filters)
    ).order_by(cdm_person.c.person_id).limit(limit).offset(offset)

    return query

def mapBeaconScopeToOMOP(scope):
    mappingDict = {'ageAtDisease':'condition_occurrence',
     'ageAtProcedure':'procedure_occurrence',
     'observationMoment':'measurement',
     'ageAtExposure':'observation',
     'ageAtTreatment':'drug_exposure'
     }
    scopeMapping = {mappingDict[scope]:'Age'}
    return scopeMapping

async def checkFilters(filtersDict, offset, limit, typeQuery):
    vocab_conc= get_table("concept", schema="vocabularies")
    listOfList = []
    dictTableMap = []
    for filter in filtersDict: 
        listConcept_id = set()
        operator = None
        value = None
        includeDescendantTerms = True
        typeFilter = 'Ontology'     # Default filter option
        # Check query
        # Parse query depend on POST/GET query
        if typeQuery == 'POST':
            if 'includeDescendantTerms' in filter:
                if filter['includeDescendantTerms'] == False:
                    includeDescendantTerms = False
            if 'operator' in filter:
                typeFilter = 'Alphanumeric'
                operator = filter['operator']
                value = filter['value']
                includeDescendantTerms = False
            if 'id' in filter:
                filterId = filter['id']
            else:
                return [], 0
            if filterId == 'ageOfOnset':
                # Convert scope to tableMap
                # listConcept_id empty
                typeFilter = "Age"
                listConcept_id = ['None']
                try:
                    scope = filter['scope']
                except:
                    print("You need an scope if you are using 'ageOfOnset'")

                try:
                    value = float(value)
                except (TypeError, ValueError):
                    return [], 0 
                
                if "condition" in scope:
                    filterId = 'ageAtDisease'
                elif "treatments" in scope:
                    filterId = 'ageAtTreatment'
                elif "procedure" in scope:
                    filterId = 'ageAtProcedure'
                elif "measurement" in scope:
                    filterId = 'observationMoment'
                elif "observation" in scope:
                    filterId = 'ageAtExposure'
                
                tableMap = mapBeaconScopeToOMOP(filterId)
                dictTableMap.append([tableMap, listConcept_id, operator, value])
                continue

        else: # If GET
            filterId = filter
        if typeFilter == "Ontology" or typeFilter == "Alphanumeric":
            if "HP" in filterId:
                vocabulary_id, concept_code = filterId.split('_')
                clean_concept = func.replace(vocab_conc.c.concept_code, 'HP_', '')
                clean_vocab = func.replace(vocab_conc.c.vocabulary_id, 'HPO', 'HP')
            
                records = select(
                    vocab_conc.c.concept_id, vocab_conc.c.domain_id
                ).where(
                    (clean_vocab == vocabulary_id) & (clean_concept == concept_code)
                )
                async with client.connect() as conn:
                    result = conn.execute(records, {"vocabulary_id": vocabulary_id, "concept_code": concept_code})                    
                    rows = result
                    rows = rows.mappings().all()
                    if "mssql" in database_driver:
                        result.close()
            
            elif "OMOP" in filterId: # change to 'elif' if the previous chunk is available
                vocabulary_id, concept_code = filterId.split(':')
                concept_id = int(concept_code)
                records = select(
                    vocab_conc.c.concept_id, vocab_conc.c.domain_id
                ).where(
                    (vocab_conc.c.concept_id == concept_id)
                ) 
                async with client.connect() as conn:
                    result = await conn.execute(records, {"vocabulary_id": vocabulary_id, "concept_code": concept_code})
                    rows = result
                    rows = rows.mappings().all()
                    if "mssql" in database_driver:
                        result.close() 
            else:
                vocabulary_id, concept_code = filterId.split(':')
                clean_concept = vocab_conc.c.concept_code
                clean_vocab = vocab_conc.c.vocabulary_id
                records = select(
                    vocab_conc.c.concept_id, vocab_conc.c.domain_id
                ).where(
                    (clean_vocab == vocabulary_id) & (clean_concept == concept_code)
                )
                async with client.connect() as conn:
                    result = await conn.execute(records, {"vocabulary_id": vocabulary_id, "concept_code": concept_code})                    
                    rows = result
                    rows = rows.mappings().all()
                    if "mssql" in database_driver:
                        result.close()                                     
            
            # Check if records is empty
            res = peek(rows)      
            if res is None:
                return [], 0
            __, records = res
            for record in records:
                original_concept_id = record['concept_id']
                domain_id = record['domain_id']
                listConcept_id.add(original_concept_id)
                # Look in which domains the concept_id belongs
                tableMap=map_domains(domain_id)
                if includeDescendantTerms:
                    # Import descendants of the concept_id
                    concept_ids= await search_descendants(original_concept_id)
                    # Concept_id and descendants in same set()
                    listConcept_id = listConcept_id.union(concept_ids)
            # if res[0] is None:
            #     LOG.warning(f"Filter not found: {filterId}")
            #     return [], 0, f"Filter not found: {filterId}"           
            dictTableMap.append([tableMap, listConcept_id, operator, value])
    base_filter = create_dynamic_filter(dictTableMap)
    query_count = super_query_count(base_filter)
    count_records = await basic_query(query_count)
    query_get = super_query_get(base_filter, offset, limit)
    records_get = await basic_query(query_get)
    listOfList = [record["person_id"] for record in records_get]

    return listOfList, count_records[0]["count_1"]

async def filters(filtersDict, offset, limit):
    if type(filtersDict[0]) is dict:         # If filter is from Post
        listFilters, count = await checkFilters(filtersDict, offset, limit, 'POST')
    else:
        listFilters, count = await checkFilters(filtersDict, offset, limit, 'GET')

    return listFilters, count

################################

def format_query(listIds):
    list_format = []
    for person_id in listIds:
        dictId = {"id": str(person_id["person_id"])}
        
        if "gender_concept_id" in person_id:
            dictId["sex"] = person_id["gender_concept_id"]
        if "race_concept_id" in person_id:
            dictId["ethnicity"] = person_id["race_concept_id"]

        if "conditions" in person_id:
            dictId["diseases"] = [
                mappings.diseases_table_map(condition)
                for condition in person_id["conditions"]
                if isinstance(condition, dict) and "condition_concept_id" in condition]   
        if "procedures" in person_id:
            dictId["interventionsOrProcedures"] = [
                mappings.procedures_table_map(procedure)
                for procedure in person_id["procedures"]
                if isinstance(procedure, dict) and "procedure_concept_id" in procedure]
        if "measurements" in person_id:
            dictId["measures"] = [
                mappings.measures_table_map(measurement)
                for measurement in person_id["measurements"]
                if isinstance(measurement, dict) and "measurement_concept_id" in measurement]
        if "observations" in person_id:
            dictId["exposures"] = [
                mappings.exposures_table_map(observation)
                for observation in person_id["observations"]
                if isinstance(observation, dict) and "observation_concept_id" in observation]
        if "drugs" in person_id:
            dictId["treatments"] = [
                mappings.treatments_table_map(drug)
                for drug in person_id["drugs"]
                if isinstance(drug, dict) and "drug_concept_id" in drug]

        list_format.append(dictId)
    
    return list_format

def iso(data):
    def recurse(item):
        if isinstance(item, dict):
            for key, value in item.items():
                if key == 'iso8601duration' and isinstance(value, Decimal):
                    item[key] = f"P{value}Y"
                else:
                    recurse(value)
        elif isinstance(item, list):
            for elem in item:
                recurse(elem)

    recurse(data)
    return data

def ageOfOnset_func(birth_date, birth_year, event_date, label):
    return case((birth_date != None,
            func.extract('year', event_date) - func.extract('year', birth_date) - \
                case((or_(
                        func.extract('month', event_date) < func.extract('month', birth_date),
                        and_(
                            func.extract('month', event_date) == func.extract('month', birth_date),
                            func.extract('day', event_date) < func.extract('day', birth_date))
                        ),
                    literal(1)
                ), else_ = (
                    literal(0)
                ))
        ), else_=(
            func.extract('year', event_date) - birth_year
        )
    ).label(label)


###############################

async def ind_base(entry_id: Optional[str] = None, qparams: RequestParams = RequestParams()):
    cdm_person = get_table("person", schema="cdm")
    cdm_cond_occ = get_table("condition_occurrence", schema="cdm")
    cdm_proc_occ = get_table("procedure_occurrence", schema="cdm")
    cdm_drug_exp = get_table("drug_exposure", schema="cdm")
    cdm_mesure = get_table("measurement", schema="cdm")
    cdm_obser = get_table("observation", schema="cdm")
    cdm_obser_per = get_table("observation_period", schema="cdm")

    def normalize_ids(entry_id):
        if entry_id is None:
            return None
        if isinstance(entry_id, list):
            return [int(x) for x in entry_id]
        return [int(entry_id)]
    entry_id = normalize_ids(entry_id)

    ids_subquery = union_all(
        *[select(literal(v).label("person_id")) for v in entry_id]
    ).subquery()
    
    # Step 0: function for date formatting TODO: add more options if needed
    def format_date(column, fmt='YYYY-MM-DD'):
        if "postgresql" in database_driver:
            return func.to_char(column, fmt)
        elif 'mysql' in database_driver:
            mysql_fmt = fmt.replace('YYYY', '%Y').replace('MM', '%m').replace('DD', '%d')
            return func.date_format(column, mysql_fmt)
        elif "denodo" in database_driver:
            denodo_fmt = fmt.replace('YYYY', 'yyyy').replace('DD', 'dd')
            return func.formatdate(denodo_fmt, column)
        elif "mssql" in database_driver:
            mssql_fmt = (
                fmt.replace('YYYY', 'yyyy')
                .replace('MM', 'MM')
                .replace('DD', 'dd')
            )
            return func.format(column, mssql_fmt)
        else:
            # fallback: cast to string (ISO format)
            return cast(column, String)
       
    async with client.connect() as conn:
        # Step 1: Get base person_id data
        if "denodo" in database_driver:
            base_query = select(
                    cdm_person.c.person_id,
                    cdm_person.c.gender_concept_id,
                    cdm_person.c.race_concept_id,
            )
            if entry_id is not None:
                base_query = base_query.select_from(
                    cdm_person.join(ids_subquery, cdm_person.c.person_id == ids_subquery.c.person_id)
                )
        else:
            base_query = select(
                cdm_person.c.person_id,
                cdm_person.c.gender_concept_id,
                cdm_person.c.race_concept_id,
            ).where(cdm_person.c.person_id.in_(entry_id))

            
        base_result = await conn.execute(base_query)
        rows = base_result.mappings().all()

        individuals = {row["person_id"]: dict(row) | {
            "conditions": [], "procedures": [], "measurements": [], "observations": [], "drugs": []
        } for row in rows}

        person_ids = list(individuals.keys())
        
        ids_subquery = union_all(
            *[select(literal(v).label("person_id")) for v in person_ids]
        ).subquery()

        # Step 2: Fetch and append conditions
        if "denodo" in database_driver:
            cond_query = select(
                cdm_cond_occ.c.person_id,
                cdm_cond_occ.c.condition_concept_id,
                ageOfOnset_func(cdm_person.c.birth_datetime, cdm_person.c.year_of_birth, cdm_cond_occ.c.condition_start_date, 'condition_ageOfOnset')
            ).select_from(
                cdm_cond_occ
                .join(cdm_person, cdm_cond_occ.c.person_id == cdm_person.c.person_id)
                .join(ids_subquery, cdm_cond_occ.c.person_id == ids_subquery.c.person_id)
            )
        else:
            cond_query = select(
                cdm_cond_occ.c.person_id,
                cdm_cond_occ.c.condition_concept_id,
                ageOfOnset_func(cdm_person.c.birth_datetime, cdm_person.c.year_of_birth, cdm_cond_occ.c.condition_start_date, 'condition_ageOfOnset')
            ).select_from(
                cdm_cond_occ
                .join(cdm_person, cdm_cond_occ.c.person_id == cdm_person.c.person_id)
            ).where(
               cdm_cond_occ.c.person_id.in_(person_ids)
            )

        result = await conn.execute(cond_query, {"limit": qparams.query.pagination.limit, "offset": qparams.query.pagination.skip, "entry_id": entry_id})
        rows = result.mappings().all()
        for row in rows:
            individuals[row["person_id"]]["conditions"].append(dict(row))

        # Step 3: Fetch and append procedures
        if "denodo" in database_driver:
            proc_query = select(
                cdm_proc_occ.c.person_id,
                cdm_proc_occ.c.procedure_concept_id,
                format_date(cdm_proc_occ.c.procedure_date).label("procedure_date"),
                ageOfOnset_func(cdm_person.c.birth_datetime, cdm_person.c.year_of_birth, cdm_proc_occ.c.procedure_date, 'procedure_ageOfOnset')
            ).select_from(
                cdm_proc_occ
                .join(cdm_person, cdm_proc_occ.c.person_id == cdm_person.c.person_id)
                .join(ids_subquery, cdm_proc_occ.c.person_id == ids_subquery.c.person_id)
            )
        else:
            proc_query = select(
                cdm_proc_occ.c.person_id,
                cdm_proc_occ.c.procedure_concept_id,
                format_date(cdm_proc_occ.c.procedure_date).label("procedure_date"),
                ageOfOnset_func(cdm_person.c.birth_datetime, cdm_person.c.year_of_birth, cdm_proc_occ.c.procedure_date, 'procedure_ageOfOnset')
            ).select_from(
                cdm_proc_occ
                .join(cdm_person, cdm_proc_occ.c.person_id == cdm_person.c.person_id)
            ).where(
               cdm_proc_occ.c.person_id.in_(person_ids))

        result = await conn.execute(proc_query, {"limit": qparams.query.pagination.limit, "offset": qparams.query.pagination.skip, "entry_id": entry_id})
        rows = result.mappings().all()
        for row in rows:
            individuals[row["person_id"]]["procedures"].append(dict(row))

        # Step 4: Fetch and append measurements
        if "denodo" in database_driver:    
            meas_query = select(
                cdm_mesure.c.person_id,
                cdm_mesure.c.measurement_concept_id,
                format_date(cdm_mesure.c.measurement_date).label("measurement_date"),
                ageOfOnset_func(cdm_person.c.birth_datetime, cdm_person.c.year_of_birth, cdm_mesure.c.measurement_date, 'measurement_ageOfOnset'),
                cdm_mesure.c.unit_concept_id, cdm_mesure.c.value_source_value
            ).select_from(
                cdm_mesure
                .join(cdm_person, cdm_mesure.c.person_id == cdm_person.c.person_id)
                .join(ids_subquery, cdm_mesure.c.person_id == ids_subquery.c.person_id)
            )
        else:
            meas_query = select(
                cdm_mesure.c.person_id,
                cdm_mesure.c.measurement_concept_id,
                format_date(cdm_mesure.c.measurement_date).label("measurement_date"),
                ageOfOnset_func(cdm_person.c.birth_datetime, cdm_person.c.year_of_birth, cdm_mesure.c.measurement_date, 'measurement_ageOfOnset'),
                cdm_mesure.c.unit_concept_id, cdm_mesure.c.value_source_value
            ).select_from(
                cdm_mesure
                .join(cdm_person, cdm_mesure.c.person_id == cdm_person.c.person_id)
            ).where(
                cdm_mesure.c.person_id.in_(person_ids))

        result = await conn.execute(meas_query, {"limit": qparams.query.pagination.limit, "offset": qparams.query.pagination.skip, "entry_id": entry_id})
        rows = result.mappings().all()
        for row in rows:
            individuals[row["person_id"]]["measurements"].append(dict(row))

        # Step 5: Fetch and append observations
        if "denodo" in database_driver: 
            obs_query = select(
                cdm_obser.c.person_id,
                cdm_obser.c.observation_concept_id,
                format_date(cdm_obser.c.observation_date).label("observation_date"),
                ageOfOnset_func(cdm_person.c.birth_datetime, cdm_person.c.year_of_birth, cdm_obser.c.observation_date, 'observation_ageOfOnset'),
                cdm_obser.c.unit_concept_id
            ).select_from(
                cdm_obser
                .join(cdm_person, cdm_obser.c.person_id == cdm_person.c.person_id)
                .join(ids_subquery, cdm_obser.c.person_id == ids_subquery.c.person_id)
            )
        else:
            obs_query = select(
                cdm_obser.c.person_id,
                cdm_obser.c.observation_concept_id,
                format_date(cdm_obser.c.observation_date).label("observation_date"),
                ageOfOnset_func(cdm_person.c.birth_datetime, cdm_person.c.year_of_birth, cdm_obser.c.observation_date, 'observation_ageOfOnset'),
                cdm_obser.c.unit_concept_id
            ).select_from(
                cdm_obser
                .join(cdm_person, cdm_obser.c.person_id == cdm_person.c.person_id)
            ).where(
                cdm_obser.c.person_id.in_(person_ids))

        result = await conn.execute(obs_query, {"limit": qparams.query.pagination.limit, "offset": qparams.query.pagination.skip, "entry_id": entry_id})
        rows = result.mappings().all()
        for row in rows:
            individuals[row["person_id"]]["observations"].append(dict(row))

        if "denodo" in database_driver: 
            duration_query = select(
                cdm_obser_per.c.person_id,
                func.concat(
                    'P',
                    func.extract('year', cdm_obser_per.c.observation_period_end_date) - func.extract('year', cdm_obser_per.c.observation_period_start_date),
                    'Y',
                    func.extract('month', cdm_obser_per.c.observation_period_end_date) - func.extract('month', cdm_obser_per.c.observation_period_start_date),
                    'M',
                    func.extract('day', cdm_obser_per.c.observation_period_end_date) - func.extract('day', cdm_obser_per.c.observation_period_start_date),
                    'D'
                ).label('duration')
            ).select_from(
                cdm_obser_per.join(ids_subquery,cdm_obser_per.c.person_id == ids_subquery.c.person_id)
            )
        else:
            duration_query = select(
                cdm_obser_per.c.person_id,
                func.concat(
                    'P',
                    func.extract('year', cdm_obser_per.c.observation_period_end_date) - func.extract('year', cdm_obser_per.c.observation_period_start_date),
                    'Y',
                    func.extract('month', cdm_obser_per.c.observation_period_end_date) - func.extract('month', cdm_obser_per.c.observation_period_start_date),
                    'M',
                    func.extract('day', cdm_obser_per.c.observation_period_end_date) - func.extract('day', cdm_obser_per.c.observation_period_start_date),
                    'D'
                ).label('duration')
            ).where(
                cdm_obser_per.c.person_id.in_(person_ids))

        result = await conn.execute(duration_query, {"limit": qparams.query.pagination.limit, "offset": qparams.query.pagination.skip, "entry_id": entry_id})
        records_duration = result.mappings().all()
        duration_map = {row["person_id"]: row["duration"] for row in records_duration}
        for person_id, data in individuals.items():
            duration = duration_map.get(person_id, "Not Available")
            for obs in data["observations"]:
                obs["duration"] = duration

        # Step 6: Fetch and append drug exposures
        if "denodo" in database_driver: 
            drug_query = select(
                cdm_drug_exp.c.person_id,
                cdm_drug_exp.c.drug_concept_id,
                ageOfOnset_func(cdm_person.c.birth_datetime, cdm_person.c.year_of_birth, cdm_drug_exp.c.drug_exposure_start_date, 'drug_exposure_ageOfOnset')
            ).select_from(
                cdm_drug_exp
                .join(cdm_person, cdm_drug_exp.c.person_id == cdm_person.c.person_id)
                .join(ids_subquery, cdm_drug_exp.c.person_id == ids_subquery.c.person_id)
            )
        else:
            drug_query = select(
                cdm_drug_exp.c.person_id,
                cdm_drug_exp.c.drug_concept_id,
                ageOfOnset_func(cdm_person.c.birth_datetime, cdm_person.c.year_of_birth, cdm_drug_exp.c.drug_exposure_start_date, 'drug_exposure_ageOfOnset')
            ).select_from(
                cdm_drug_exp
                .join(cdm_person, cdm_drug_exp.c.person_id == cdm_person.c.person_id)
            ).where(
                cdm_drug_exp.c.person_id.in_(person_ids))
        
        result = await conn.execute(drug_query, {"limit": qparams.query.pagination.limit, "offset": qparams.query.pagination.skip, "entry_id": entry_id})
        rows = result.mappings().all()
        for row in rows:
            individuals[row["person_id"]]["drugs"].append(dict(row)) 
    
    docs = list(individuals.values())
    docs = await search_ontologies(docs)

    return docs

async def get_the_individuals(entry_id: Optional[str] = None, qparams: RequestParams = RequestParams()):
    cdm_person = get_table("person", schema="cdm")
    orig_entry_id = entry_id
    
    if qparams.query.pagination.limit == 0:
        qparams.query.pagination.limit = MAX_LIMIT
    if not qparams.query.pagination.limit:
        qparams.query.pagination.limit = 10
       
    async with client.connect() as conn:
        # Handle filters
        if qparams.query.filters:
            listIds, count_ids = await filters(qparams.query.filters,
                                        offset=qparams.query.pagination.skip,
                                        limit=qparams.query.pagination.limit)
            if count_ids == 0:
                return DefaultSchemas.INDIVIDUALS, 0, []
            entry_id = listIds
        else:
            # Default: get first 10 person_ids if no filters or entry_id
            if entry_id is None:
                default_query = select(cdm_person.c.person_id).order_by(cdm_person.c.person_id).limit(qparams.query.pagination.limit).offset(qparams.query.pagination.skip)
                result = await conn.execute(default_query)
                entry_id = result.scalars().all()
            elif not isinstance(entry_id, list):
                entry_id = [entry_id]

        docs = await ind_base(entry_id, qparams=qparams)

        if qparams.query.filters:
            counter = count_ids
        elif orig_entry_id is None:
            counter_query = select(func.count('*')).select_from(cdm_person)
            result = await conn.execute(counter_query)
            counter = result.scalar_one() 
        else:
            counter = len(docs)
        
    docs = format_query(docs)
    docs = iso(docs)
    
    return DefaultSchemas.INDIVIDUALS, counter, docs

###########

def format_query_bio(biosamples):
    list_format = []
    for sample in biosamples:
        dict_biosample =  { 
            "id": str(sample.get("specimen_id", "")),
            "individualId": str(sample.get("person_id", "")),
            "biosampleStatus": {
                "id": sample["disease_status_concept_id"]["id"],
                "label": sample["disease_status_concept_id"]["label"]
            },
            "sampleOriginType": {
                "id" : sample["anatomic_site_concept_id"]["id"],
                "label" : sample["anatomic_site_concept_id"]["label"]
            },
            "collectionMoment": sample.get("specimen_date", ""),
            "collectionDate": sample.get("specimen_datetime", ""),
            "info": {}
            }
        list_format.append(dict_biosample)
    return list_format

def get_biosamples_of_individual(entry_id: Optional[str], qparams: RequestParams = RequestParams()):
    with client.connect() as conn:
        specimens = select(distinct(cdm_specimen.c.specimen_id)).where(cdm_specimen.c.person_id == entry_id)
        specimens = conn.execute(specimens).fetchall()
        listSpecimens = [specimen[0] for specimen in specimens ]
        count = len(listSpecimens)

        for biosample_id in listSpecimens:
            records = select(
                cdm_specimen.c.person_id, 
                cdm_specimen.c.disease_status_concept_id, 
                cdm_specimen.c.anatomic_site_concept_id, 
                cast(cdm_specimen.c.specimen_date, String), 
                cast(cdm_specimen.c.specimen_datetime, String)
            ).where(
                cdm_specimen.c.specimen_id == biosample_id)
        records = conn.execute(records).fetchall()

    listValues = []
    for record in records:
        listValues.append({'specimen_id': biosample_id,
                            'person_id': record[0],
                            'disease_status_concept_id': record[1],
                            'anatomic_site_concept_id': record[2],
                            'specimen_date': record[3],
                            'specimen_datetime': record[4]})

    docs = search_ontologies_bio(listValues)
    docs = format_query_bio(docs)

    return DefaultSchemas.BIOSAMPLES, count, docs

###########

def get_filtering_terms_of_individual(entry_id: Optional[str], qparams: RequestParams):
    conn = client.connect()

    sql_filtering_terms_race_gender = select(
        distinct(func.concat(vocab_conc.c.vocabulary_id, vocab_conc.c.concept_code).label('uri')),
        vocab_conc.c.concept_id,
        vocab_conc.c.concept_name
    ).select_from(
        vocab_conc.join(
            cdm_person,
            (cdm_person.c.race_concept_id == vocab_conc.c.concept_id) |
            (cdm_person.c.gender_concept_id == vocab_conc.c.concept_id)))
        
    sql_filtering_terms_condition = select(
        distinct(func.concat(vocab_conc.c.vocabulary_id, vocab_conc.c.concept_code).label('uri')),
        vocab_conc.c.concept_id,
        vocab_conc.c.concept_name
    ).select_from(
        vocab_conc.join(
            cdm_cond_occ,
            (cdm_cond_occ.c.condition_concept_id == vocab_conc.c.concept_id)))

    sql_filtering_terms_measurement = select(
        distinct(func.concat(vocab_conc.c.vocabulary_id, vocab_conc.c.concept_code).label('uri')),
        vocab_conc.c.concept_id,
        vocab_conc.c.concept_name
    ).select_from(
        vocab_conc.join(
            cdm_mesure,
            (cdm_mesure.c.measurement_concept_id == vocab_conc.c.concept_id)))

    sql_filtering_terms_procedure = select(
        distinct(func.concat(vocab_conc.c.vocabulary_id, vocab_conc.c.concept_code).label('uri')),
        vocab_conc.c.concept_id,
        vocab_conc.c.concept_name
    ).select_from(
        vocab_conc.join(
            cdm_proc_occ,
            (cdm_proc_occ.c.procedure_concept_id == vocab_conc.c.concept_id)))

    sql_filtering_terms_observation = select(
        distinct(func.concat(vocab_conc.c.vocabulary_id, vocab_conc.c.concept_code).label('uri')),
        vocab_conc.c.concept_id,
        vocab_conc.c.concept_name
    ).select_from(
        vocab_conc.join(
            cdm_obser,
            (cdm_obser.c.observation_concept_id == vocab_conc.c.concept_id)))

    sql_filtering_terms_drug_exposure = select(
        distinct(func.concat(vocab_conc.c.vocabulary_id, vocab_conc.c.concept_code).label('uri')),
        vocab_conc.c.concept_id,
        vocab_conc.c.concept_name
    ).select_from(
        vocab_conc.join(
            cdm_drug_exp,
            (cdm_drug_exp.c.drug_concept_id == vocab_conc.c.concept_id)))
    
    sql_filtering_terms_race_gender = conn.execute(sql_filtering_terms_race_gender)
    sql_filtering_terms_condition = conn.execute(sql_filtering_terms_condition)
    sql_filtering_terms_measurement = conn.execute(sql_filtering_terms_measurement)
    sql_filtering_terms_procedure = conn.execute(sql_filtering_terms_procedure)
    sql_filtering_terms_observation = conn.execute(sql_filtering_terms_observation)
    sql_filtering_terms_drug_exposure = conn.execute(sql_filtering_terms_drug_exposure)

    l_sql_filters = [sql_filtering_terms_race_gender,
                    sql_filtering_terms_condition,
                    sql_filtering_terms_measurement,
                    sql_filtering_terms_procedure,
                    sql_filtering_terms_observation,
                    sql_filtering_terms_drug_exposure]
    l_indFilters = []
    for ind_filters in l_sql_filters:
        for filters in ind_filters:
            if filters[0].endswith("OMOP generated"):
                continue
            dict_filter = {"id":filters[0],"omop_id":filters[1],"label":filters[2],"scopes":["individual"],"type":"ontology"}
            l_indFilters.append(dict_filter)
    
    conn.close()

    return DefaultSchemas.FILTERINGTERMS, len(l_indFilters), l_indFilters