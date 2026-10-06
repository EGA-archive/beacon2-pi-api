import logging
from datetime import date
from typing import Optional

from sqlalchemy import select, func, distinct, cast, String, Integer, desc

from beacon.models.omop.connections.postgresql.utilities import RequestParams, DefaultSchemas
from beacon.connections.postgresql_omop.__init__ import client
from beacon.connections.postgresql_omop import get_table
from beacon.models.omop.connections.postgresql.individuals import ind_base, get_the_individuals
from beacon.connections.postgresql_omop.conf import database_driver

LOG = logging.getLogger(__name__)

cohort_type = 'beacon-defined'

async def criteria(cohortBasicInfo):
    vocab_conc= get_table("concept", schema="vocabularies")
    cdm_cond_occ = get_table("condition_occurrence", schema="cdm")
    cdm_person = get_table("person", schema="cdm")
    cdm_location = get_table("location", schema="cdm")
    
    if cohortBasicInfo['individuals']:
        diseases = select(
            vocab_conc.c.concept_name.label('label'),
            func.concat(vocab_conc.c.vocabulary_id, ':', vocab_conc.c.concept_code).label('id')
        ).select_from(
            cdm_cond_occ
            .join(
                cdm_person,
                cdm_person.c.person_id == cdm_cond_occ.c.person_id
            )
            .join(
                vocab_conc,
                vocab_conc.c.concept_id == cdm_cond_occ.c.condition_concept_id
            )
        ).where(
            cdm_person.c.person_id.in_(cohortBasicInfo['individuals'])
        ).group_by(
            vocab_conc.c.concept_name, vocab_conc.c.vocabulary_id, vocab_conc.c.concept_code)
        
        locations = select(
            vocab_conc.c.concept_name.label('label'),
            func.concat(vocab_conc.c.vocabulary_id, ':', vocab_conc.c.concept_code).label('id')
        ).select_from(
            cdm_location
            .join(
                vocab_conc,
                vocab_conc.c.concept_id == cdm_location.c.country_concept_id)
            .join(
                cdm_person,
                cdm_person.c.location_id == cdm_location.c.location_id
            )
        ).where(
            cdm_person.c.person_id.in_(cohortBasicInfo['individuals'])
        ).group_by(
            vocab_conc.c.concept_name, vocab_conc.c.vocabulary_id, vocab_conc.c.concept_code)
        
        genders = select(
            vocab_conc.c.concept_name.label('label'),
            func.concat(vocab_conc.c.vocabulary_id, ':', vocab_conc.c.concept_code).label('id')
        ).select_from(
            cdm_person.join(
                vocab_conc,
                vocab_conc.c.concept_id == cdm_person.c.gender_concept_id)
        ).where(
            cdm_person.c.person_id.in_(cohortBasicInfo['individuals'])
        ).group_by(
            vocab_conc.c.concept_name, vocab_conc.c.vocabulary_id, vocab_conc.c.concept_code)
    else:
        diseases = select(
            vocab_conc.c.concept_name.label('label'),
            func.concat(vocab_conc.c.vocabulary_id, ':', vocab_conc.c.concept_code).label('id')
        ).select_from(
            cdm_cond_occ.join(
                vocab_conc,
                vocab_conc.c.concept_id == cdm_cond_occ.c.condition_concept_id
            )
        ).group_by(
            vocab_conc.c.concept_name, vocab_conc.c.vocabulary_id, vocab_conc.c.concept_code)
        
        locations = select(
            distinct(vocab_conc.c.concept_name).label('label'),
            func.concat(vocab_conc.c.vocabulary_id, ':', vocab_conc.c.concept_code).label('id')
        ).select_from(
            cdm_location.join(
                vocab_conc,
                vocab_conc.c.concept_id == cdm_location.c.country_concept_id)
        ).group_by(
            vocab_conc.c.concept_name, vocab_conc.c.vocabulary_id, vocab_conc.c.concept_code)
        
        genders = select(
            vocab_conc.c.concept_name.label('label'),
            func.concat(vocab_conc.c.vocabulary_id, ':', vocab_conc.c.concept_code).label('id')
        ).select_from(
            cdm_person.join(
                vocab_conc,
                vocab_conc.c.concept_id == cdm_person.c.gender_concept_id)
        ).group_by(
            vocab_conc.c.concept_name, vocab_conc.c.vocabulary_id, vocab_conc.c.concept_code)
        
    async with client.connect() as conn:
        diseases = await conn.execute(diseases)
        diseases = diseases.mappings().all()
        locations = await conn.execute(locations)
        locations = locations.mappings().all()
        genders = await conn.execute(genders)
        genders = genders.mappings().all() 
    
    list_diseases = []
    for disease in diseases:
        dict_disease = {"diseaseCode": {"label": disease["label"],
                       "id": disease["id"]}}
        list_diseases.append(dict_disease)

    list_locations = []
    for location in locations:
        dict_location = {"locationCode": {"label": location["label"],
                       "id": location["id"]}}
        list_locations.append(dict_location)

    list_genders = []
    for gender in genders:
        dict_gender = {"genderCode": {"label": gender["label"],
                       "id": gender["id"]}}
        list_genders.append(dict_gender)
    
    return list_diseases, list_locations, list_genders

def cohort_data_types():
    return [{
            "id": "OGMS:0000015",
            "label": "clinical history"
        }]

def dataAvailabilityAndDistributionFunction(eventData):
    dict_distribution = {}
    count_ind = 0
    for event in eventData:
        if "year_of_birth" in event and "count_1" in event:
            count_ind += int(event["count_1"])
            dict_distribution[str(event["year_of_birth"])] = event["count_1"]
        elif "concept_name" in event and "count_1" in event:
            count_ind += int(event["count_1"])
            dict_distribution[str(event["concept_name"])] = event["count_1"]
        elif "concept_name" in event and "count_value" in event:
            count_ind += int(event["count_value"])
            dict_distribution[str(event["concept_name"])] = event["count_value"]

    if not dict_distribution:
        return {"availability": False}

    return {
        "availability": True,
        "availabilityCount":count_ind,
        "distribution":dict_distribution
    }

async def createEvent(cohortBasicInfo):
    cdm_person = get_table("person", schema="cdm")
    vocab_conc= get_table("concept", schema="vocabularies")
    cdm_cond_occ = get_table("condition_occurrence", schema="cdm")
    
    if cohortBasicInfo['individuals']:
        year_per_person = select(
            cdm_person.c.year_of_birth,
            func.count("*")
        ).where(
            cdm_person.c.person_id.in_(cohortBasicInfo['individuals'])
        ).group_by(
            cdm_person.c.year_of_birth
        ).order_by(
            cdm_person.c.year_of_birth)

        sex_per_person = select(
            vocab_conc.c.concept_name,
            func.count("*")
        ).select_from(
            cdm_person.join(
                vocab_conc,
                vocab_conc.c.concept_id == cdm_person.c.gender_concept_id)
        ).where(
            cdm_person.c.person_id.in_(cohortBasicInfo['individuals'])
        ).group_by(
            vocab_conc.c.concept_name)
        
        disease_per_person = select(
            vocab_conc.c.concept_name,
            func.count(distinct(cdm_cond_occ.c.person_id)).label('count_value')
        ).select_from(
            cdm_cond_occ
            .join(
                vocab_conc,
                vocab_conc.c.concept_id == cdm_cond_occ.c.condition_concept_id
            )
            .join(
                cdm_person,
                cdm_person.c.person_id == cdm_cond_occ.c.person_id
            )
        ).where(
            cdm_person.c.person_id.in_(cohortBasicInfo['individuals'])
        ).group_by(
            vocab_conc.c.concept_name, vocab_conc.c.vocabulary_id, vocab_conc.c.concept_code
        ).order_by(
            desc("count_value"))
        
        eventSize = len(cohortBasicInfo['individuals'])

    else:
        year_per_person = select(
            cdm_person.c.year_of_birth,
            func.count("*")
        ).group_by(
            cdm_person.c.year_of_birth
        ).order_by(
            cdm_person.c.year_of_birth)
        
        sex_per_person = select(
            vocab_conc.c.concept_name,
            func.count("*")
        ).select_from(
            cdm_person.join(
                vocab_conc,
                vocab_conc.c.concept_id == cdm_person.c.gender_concept_id)
        ).group_by(
            vocab_conc.c.concept_name)
        
        disease_per_person = select(
            vocab_conc.c.concept_name,
            func.count(distinct(cdm_cond_occ.c.person_id)).label('count_value')
        ).select_from(
            cdm_cond_occ.join(
                vocab_conc,
                vocab_conc.c.concept_id == cdm_cond_occ.c.condition_concept_id
            )
        ).group_by(
            vocab_conc.c.concept_name, vocab_conc.c.vocabulary_id, vocab_conc.c.concept_code
        ).order_by(
            desc("count_value"))
        
        eventSize = select(func.count("*")).select_from(cdm_person)
        async with client.connect() as conn:
            result = await conn.execute(eventSize)
            eventSize = result.scalar_one()

    async with client.connect() as conn:
        year_per_person = await conn.execute(year_per_person)
        year_per_person = year_per_person.mappings().all()
        sex_per_person = await conn.execute(sex_per_person)
        sex_per_person = sex_per_person.mappings().all()
        disease_per_person = await conn.execute(disease_per_person)
        disease_per_person = disease_per_person.mappings().all()

    distributionAge = dataAvailabilityAndDistributionFunction(year_per_person)
    distributionSex = dataAvailabilityAndDistributionFunction(sex_per_person)
    distributionDiseases = dataAvailabilityAndDistributionFunction(disease_per_person)


    return {
        "eventAgeRange": {
            "availability": distributionAge['availability'],
            "availabilityCount": distributionAge['availabilityCount'],
            "distribution": {
                "year": distributionAge['distribution']
            }
        },
        "eventNum": 1,
        "eventDate": cohortBasicInfo['cohort']['date'],
        "eventGenders": {
            "availability": distributionSex['availability'],
            "availabilityCount": distributionSex['availabilityCount'],
            "distribution": {
                "genders": distributionSex['distribution']
            }
        },
        "eventDiseases": {
            "availability": distributionDiseases['availability'],
            "availabilityCount": distributionDiseases['availabilityCount'],
            "distribution": {
                "diseases": distributionDiseases['distribution']
            }
        },
        
        "eventSize": eventSize
        }
 
async def create_cohort_model(cohortBasicInfo):
    cdm_person = get_table("person", schema="cdm")
    individuals = cohortBasicInfo.get('individuals', [])
    def age_expression(birth_col):
        if "postgresql" in database_driver:
            return func.date_part(
                "year",
                func.age(func.current_date(), birth_col)
            )
        else:
            raise NotImplementedError("Unsupported database")

    age_expr = age_expression(cdm_person.c.birth_datetime)
    if not individuals:      # All database
        cohortSize = select(func.count("*")).select_from(cdm_person)
        age_query = select(
            cast(func.min(age_expr), Integer).label("min_age"),
            cast(func.max(age_expr), Integer).label("max_age"),
        )
        async with client.connect() as conn:
            cohortSize = await conn.execute(cohortSize)
            cohortSize = cohortSize.scalar_one() 
            age_result = await conn.execute(age_query)
            age_result = age_result.mappings().all()

    else:
        cohortSize = len(individuals)        
        age_query = select(
            cast(func.min(age_expr), Integer).label("min_age"),
            cast(func.max(age_expr), Integer).label("max_age"),
        ).where(
            cdm_person.c.person_id.in_(individuals)
        )        
        async with client.connect() as conn:
            age_result = await conn.execute(age_query)
            age_result = age_result.mappings().all()

    min_age_value = age_result[0]["min_age"]
    max_age_value = age_result[0]["max_age"]
    
    list_diseases, list_locations, list_genders = await criteria(cohortBasicInfo)
    
    cohort = {
        'id': str(cohortBasicInfo['cohort']['id']),
        'name': cohortBasicInfo['cohort']['name'],
        'cohortDataTypes': cohort_data_types(),
        'cohortSize': cohortSize,
        'cohortType': cohort_type,
        'collectionEvents': [await createEvent(cohortBasicInfo)],
        "inclusionCriteria": {
            'ageRange' : {
                "end": {
                    "iso8601duration": f"P{max_age_value}Y"
                },
                "start": {
                    "iso8601duration": f"P{min_age_value}Y"
                }
            },
            'genders': [item["genderCode"] for item in list_genders],
            'locations': [item["locationCode"] for item in list_locations],
            'diseaseConditions': [{'diseaseCode': item["diseaseCode"]} for item in list_diseases]
        }
    }
    return cohort

async def search_cohorts(cohort_id=None, is_all=False):
    cdm_cohort_def = get_table("cohort_definition", schema="cdm")
    cdm_cohort = get_table("cohort", schema="cdm")
    list_cohorts = []
    
    # If fetching all cohorts or including the "All patients" cohort
    if is_all or cohort_id is None:
        # Add "All patients" cohort entry
        dict_cohort = {'id': '0', 'date': date.today().isoformat(), 'name': "All patients"}
        individuals = []
        list_cohorts.append({'cohort': dict_cohort, 'individuals': individuals})
        
        # If cohort_id is None, fetch all cohorts from DB
        if cohort_id is None:
            cohorts_stmt = select(
                cdm_cohort_def.c.cohort_definition_id, 
                cdm_cohort_def.c.cohort_definition_name, 
                cast(cdm_cohort_def.c.cohort_initiation_date, String)
            ).order_by(cdm_cohort_def.c.cohort_definition_id)
            
            async with client.connect() as conn:
                cohorts = await conn.execute(cohorts_stmt)

                for cohort in cohorts:
                    dict_cohort = {'id': str(cohort[0]), 'date': cohort[2], 'name': cohort[1]}
                    stmt = select(cdm_cohort.c.subject_id
                    ).where(
                        cdm_cohort.c.cohort_definition_id == cohort[0]
                    ).order_by(
                        cdm_cohort.c.cohort_definition_id)
                    result_individuals = await conn.execute(stmt)
                    rows = result_individuals.mappings().all()
                    individuals = [row["subject_id"] for row in rows]
                    list_cohorts.append({'cohort': dict_cohort, 'individuals': individuals})
            return list_cohorts
    
    # If specific cohort_id provided
    if cohort_id is not None and not is_all:
        # Special case for '0' = All patients
        if int(cohort_id)==0:
            dict_cohort = {'id': '0', 'date': date.today().isoformat(), 'name': "All patients"}
            individuals = []
            return {'cohort': dict_cohort, 'individuals': individuals}
        
        cohorts_stmt = select(
            cdm_cohort_def.c.cohort_definition_id,
            cdm_cohort_def.c.cohort_definition_name,
            cast(cdm_cohort_def.c.cohort_initiation_date, String)
        ).where(cdm_cohort_def.c.cohort_definition_id.in_([cohort_id]))
        
        async with client.connect() as conn:
            cohorts = await conn.execute(cohorts_stmt)
            
            for cohort in cohorts:
                dict_cohort = {'id': str(cohort[0]), 'date': cohort[2], 'name': cohort[1]}
                stmt = select(cdm_cohort.c.subject_id).where(
                    cdm_cohort.c.cohort_definition_id == cohort[0]
                )
                result_individuals = await conn.execute(stmt)
                rows = result_individuals.mappings().all()
                individuals = [row["subject_id"] for row in rows]
                return {'cohort': dict_cohort, 'individuals': individuals}
    
    return list_cohorts

async def get_cohorts(entry_id: Optional[str]=None, qparams: RequestParams=None):   
    schema = DefaultSchemas.COHORTS
    list_cohorts = await search_cohorts()
    count = len(list_cohorts)
    docs = []
    for cohort in list_cohorts:
        docs.append(await create_cohort_model(cohort))
    return schema, count, docs


async def get_cohort_with_id(entry_id: Optional[str], qparams: RequestParams=None):
    entry_id = int(entry_id)
    schema = DefaultSchemas.COHORTS
    count = 1
    cohortBasicInfo = await search_cohorts(entry_id)
    docs = [await create_cohort_model(cohortBasicInfo)]
    return schema, count, docs

async def get_cohort_individuals(cohort_id, offset=0, limit=10):
    cdm_cohort = get_table("cohort", schema="cdm")
    async with client.connect() as conn:
        list_ids = select(
            cdm_cohort.c.subject_id.label('person_id')
        ).where(
            cdm_cohort.c.cohort_definition_id == cohort_id)
    
        list_ids = await conn.execute(list_ids)
        list_ids = list_ids.mappings().all()
        
    list_ids = [row.person_id for row in list_ids]
    ids = await ind_base(list_ids)
    
    async with client.connect() as conn:
        count_ids = select(func.count("*")).select_from(cdm_cohort
        ).where(
            cdm_cohort.c.cohort_definition_id == cohort_id)

        count_ids = await conn.execute(count_ids)
        count_ids = count_ids.scalar_one() 
        
    return DefaultSchemas.INDIVIDUALS, count_ids, ids


async def get_individuals_of_cohort(cohort_id: Optional[str], qparams: RequestParams):
    cohort_id = int(cohort_id)
    if cohort_id == '0':
        print('all individuals')
        ind = await get_the_individuals(qparams=qparams)
        return ind
    else:
        coh_ind = await get_cohort_individuals(cohort_id, 
                                  offset=qparams.query.pagination.skip,
                                  limit=qparams.query.pagination.limit)
        return coh_ind
