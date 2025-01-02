from beacon.request.parameters import RequestParams
from beacon.response.schemas import DefaultSchemas
from beacon.connections.omopcdm.__init__ import client
from beacon.logs.logs import log_with_args
from beacon.conf.conf import level
from typing import Optional
from beacon.connections.omopcdm.individuals import get_individuals
from beacon.connections.omopcdm.biosamples import get_biosamples, get_biosamples_with_person_id


import aiosql
from pathlib import Path
queries_file = Path(__file__).parent / "sql" / "cohorts.sql"
cohortQueries = aiosql.from_path(queries_file, "psycopg2")

def disease_criteria(cohortBasicInfo):
    if cohortBasicInfo['individuals']:
        diseases = cohortQueries.get_condition_per_person(client, person_ids = cohortBasicInfo['individuals'])
    else:
        diseases = cohortQueries.get_condition(client)

    list_diseases = []
    for disease in diseases:
        dict_disease = {"diseaseCode": {"label": disease[0],
                       "id": disease[1]}}
        list_diseases.append(dict_disease)

    return list_diseases

def location_criteria(cohortBasicInfo):
    if cohortBasicInfo['individuals']:
        locations = cohortQueries.get_location_per_person(client, person_ids = cohortBasicInfo['individuals'])
    else:
        locations = cohortQueries.get_location(client)

    list_locations = []
    for location in locations:
        dict_location = {"label": location[0],
                       "id": location[1]}
        list_locations.append(dict_location)

    return list_locations

def gender_criteria(cohortBasicInfo):
    if cohortBasicInfo['individuals']:
        genders = cohortQueries.get_gender_per_person(client, person_ids = cohortBasicInfo['individuals'])
    else:
        genders = cohortQueries.get_gender(client)
    list_genders = []

    for gender in genders:
        dict_gender = {"label": gender[0],
                       "id": gender[1]}
        list_genders.append(dict_gender)
    
    return list_genders

def cohort_data_types():
    return [{
            "id": "OGMS:0000015",
            "label": "clinical history"
        }]

def dataAvailabilityAndDistributionFunction(eventData):
    
    dict_distribution = {}
    count_ind = 0
    for event in eventData:
        count_ind += int(event[1])
        dict_distribution[str(event[0])] = event[1]

    if not dict_distribution:
        return {"availability": False}

    return {
        "availability": True,
        "availabilityCount":count_ind,
        "distribution":dict_distribution
    }

def createEvent(cohortBasicInfo):
    if cohortBasicInfo['individuals']:
        year_per_person = cohortQueries.get_year_of_birth_count_per_person(client, person_ids = cohortBasicInfo['individuals'])
        sex_per_person = cohortQueries.get_gender_count_per_person(client, person_ids = cohortBasicInfo['individuals'])
        disease_per_person = cohortQueries.get_condition_count_person(client, person_ids = cohortBasicInfo['individuals'])
        eventSize = len(cohortBasicInfo['individuals'])

    else:   # For all individuals
        year_per_person = cohortQueries.get_year_of_birth_count(client)
        sex_per_person = cohortQueries.get_gender_count(client)
        disease_per_person = cohortQueries.get_condition_count(client)
        eventSize = cohortQueries.get_cohort_count(client)

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


def create_cohort_model(cohortBasicInfo):

    if not cohortBasicInfo['individuals']:      # All database
        cohortSize = cohortQueries.get_cohort_count(client)
        min_age, max_age = cohortQueries.get_age_range(client)

    else:
        cohortSize = len(cohortBasicInfo['individuals'])
        min_age, max_age = cohortQueries.get_age_range_person(client, person_ids=cohortBasicInfo['individuals'])


    cohort = {
        'id': str(cohortBasicInfo['cohort']['id']),
        'name': cohortBasicInfo['cohort']['name'],
        'cohortDataTypes': cohort_data_types(),
        'cohortSize': cohortSize,
        # 'cohortType': cohort_type,
        'collectionEvents': [createEvent(cohortBasicInfo)],
        "inclusionCriteria": {
            'ageRange' : {
                "end": {
                    "iso8601duration": f"P{max_age}Y"
                },
                "start": {
                    "iso8601duration": f"P{min_age}Y"
                }
            },
            'genders': gender_criteria(cohortBasicInfo),
            'locations': location_criteria(cohortBasicInfo),
            'diseaseConditions':disease_criteria(cohortBasicInfo)
        }
    }
    return cohort

def search_cohorts(isAll):
    list_cohorts = []
    if isAll:
        dict_cohort = {'id': '0', 'date': '', 'name':"All patients"}
        list_cohorts.append({'cohort':dict_cohort,'individuals': []})

    cohorts=cohortQueries.get_all_cohorts(client)
    for cohort in cohorts:
        dict_cohort = {'id': cohort[0], 'date': cohort[1],
                       'name':cohort[2]}
        individuals=[ind[0] for ind in cohortQueries.get_cohort_individuals(client, cohort_id=cohort[0])]

        list_cohorts.append({'cohort':dict_cohort, 'individuals': individuals})
    return list_cohorts

@log_with_args(level)
def get_cohorts(self, entry_id: Optional[str], qparams: RequestParams):

    schema = DefaultSchemas.COHORTS

    list_cohorts = search_cohorts(isAll=True)
    count = len(list_cohorts)
    docs = []
    for cohort in list_cohorts:
        docs.append(create_cohort_model(cohort))


    response_converted = (
        [r for r in docs] if docs else []
    )
    return response_converted, count, schema

def search_single_cohort(cohort_id):
    if int(cohort_id)==0:
        dict_cohort = {'id': '0', 'date': '',
                       'name':"All patients"}
        individuals=[]
        return {'cohort':dict_cohort, 'individuals': individuals}
    
    cohorts=cohortQueries.get_single_cohort(client, cohort_id=cohort_id)
    for cohort in cohorts:
        dict_cohort = {'id': str(cohort[0]), 'date': cohort[1],
                       'name':cohort[2]}
        individuals=[ind[0] for ind in cohortQueries.get_cohort_individuals(client, cohort_id=cohort[0])]

    return {'cohort':dict_cohort, 'individuals': individuals}


@log_with_args(level)
def get_cohort_with_id(self, entry_id: Optional[str], qparams: RequestParams):
    schema = DefaultSchemas.COHORTS
    cohortBasicInfo = search_single_cohort(entry_id)
    print(cohortBasicInfo)
    docs = [create_cohort_model(cohortBasicInfo)]

    response_converted = (
        [r for r in docs] if docs else []
    )
    return response_converted, 1, schema

@log_with_args(level)
def get_individuals_of_cohort(self, entry_id: Optional[str], qparams: RequestParams, dataset: str):
    schema = DefaultSchemas.INDIVIDUALS
    limit = qparams.query.pagination.limit
    if entry_id == '0':
        return get_individuals(self, None, qparams, dataset)
    
    records = cohortQueries.get_cohort_individuals_limited(client,
                            limit=limit,
                            cohort_id=entry_id)                 # List with all Ids
    listIds = [record[0] for record in records]

    return get_individuals(self, listIds, qparams, dataset)

@log_with_args(level)
def get_biosamples_of_cohort(self, entry_id: Optional[str], qparams: RequestParams, dataset: str):
    schema = DefaultSchemas.BIOSAMPLES

    limit = qparams.query.pagination.limit
    if entry_id == '0':
        return get_biosamples(self, None, qparams, dataset)
    
    listIndividualIds = cohortQueries.get_cohort_individuals_limited(client,
                            limit=limit,
                            cohort_id=entry_id)                 # List with all Ids
    count, records= get_biosamples_with_person_id(listIndividualIds, qparams)
    return schema, count, count, records, dataset