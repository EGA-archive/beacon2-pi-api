
-- name: sql_get_individuals
-- Get individuals
SELECT person_id
FROM cdm.person
LIMIT :limit
OFFSET :offset

-- name: cohort_individuals
-- Get individuals
SELECT subject_id as person_id
FROM cdm.cohort
where cohort_definition_id = :cohort_id
LIMIT :limit
OFFSET :offset

-- name: count_cohort_individuals$
-- Get individuals count
SELECT count(*)
FROM cdm.cohort
where cohort_definition_id = :cohort_id

-- name: count_individuals$
-- Get individuals count
SELECT count(*)
FROM cdm.person

-- name: sql_get_individual_id^
-- Get individual by id
SELECT DISTINCT person_id
FROM cdm.person
WHERE person_id = :person_id

-- name: sql_get_person
-- Get gender and race by id
SELECT gender_concept_id, race_concept_id
FROM cdm.person
WHERE person_id = :person_id

-- name: sql_get_condition
-- Get condition properties by id
SELECT condition_concept_id,
    CASE
        WHEN birth_datetime IS NOT NULL THEN extract(Year from age(condition_start_date, birth_datetime)) 
        ELSE extract(Year from condition_start_date) - year_of_birth
	END AS condition_ageOfOnset
FROM cdm.person as p,
    cdm.condition_occurrence as c
WHERE p.person_id = :person_id and p.person_id = c.person_id;

-- name: sql_get_procedure
-- Get procedure properties by id
SELECT procedure_concept_id,
    CASE
        WHEN birth_datetime IS NOT NULL THEN extract(Year from age(procedure_date, birth_datetime)) 
        ELSE extract(Year from procedure_date) - year_of_birth
	END AS procedure_ageOfOnset,
    to_char(procedure_date, 'YYYY-MM-DD')
FROM cdm.person as p,
    cdm.procedure_occurrence as c
WHERE p.person_id = :person_id and p.person_id=c.person_id

-- name: sql_get_measure
-- Get measure properties by id
Select measurement_concept_id,
    CASE
        WHEN birth_datetime IS NOT NULL THEN extract(Year from age(measurement_date, birth_datetime)) 
        ELSE extract(Year from measurement_date) - year_of_birth
	END AS measurement_ageOfOnset,
    to_char(measurement_date, 'YYYY-MM-DD'),
    unit_concept_id,
    value_source_value
FROM cdm.person as p,
    cdm.measurement c
WHERE p.person_id = :person_id and p.person_id=c.person_id

-- name: sql_get_exposure
-- Get exposure properties by id
Select observation_concept_id,
    CASE
        WHEN birth_datetime IS NOT NULL THEN extract(Year from age(observation_date, birth_datetime)) 
        ELSE extract(Year from observation_date) - year_of_birth
	END AS observation_ageOfOnset,
    to_char(observation_date, 'YYYY-MM-DD'),
    unit_concept_id
FROM cdm.person as p,
    cdm.observation c
WHERE p.person_id = :person_id and p.person_id=c.person_id

-- name: sql_get_exposure_period^
-- Get exposure duration by id
SELECT 
    concat(
        'P', 
        extract(years from age(observation_period_end_date, observation_period_start_date)), 
        'Y', 
        extract(months from age(observation_period_end_date, observation_period_start_date)), 
        'M', 
        extract(days from age(observation_period_end_date, observation_period_start_date)), 
        'D'
    ) as duration
FROM cdm.observation_period c
WHERE c.person_id = :person_id

-- name: sql_get_treatment
-- Get treatment properties by id
SELECT drug_concept_id,
    CASE
        WHEN birth_datetime IS NOT NULL THEN extract(Year from age(drug_exposure_start_date, birth_datetime)) 
        ELSE extract(Year from drug_exposure_start_date) - year_of_birth
	END AS drug_exposure_ageOfOnset
FROM cdm.person as p,
    cdm.drug_exposure as c
WHERE p.person_id = :person_id and p.person_id = c.person_id;

-- name: sql_filtering_terms_race_gender
-- Get all the race and gender filtering terms for individual
select distinct CONCAT(vocabulary_id,':',concept_code) as uri, c.concept_name
from vocabularies.concept as c
join cdm.person as p on p.race_concept_id=c.concept_id or p.gender_concept_id=c.concept_id

-- name: sql_filtering_terms_condition
-- Get all the condition_occurrence filtering terms for individual
select distinct CONCAT(vocabulary_id,':',concept_code) as uri, c.concept_name
from vocabularies.concept as c
join cdm.condition_occurrence as con on con.condition_concept_id=c.concept_id

-- name: sql_filtering_terms_measurement
-- Get all the measurement filtering terms for individual
select distinct CONCAT(vocabulary_id,':',concept_code) as uri, c.concept_name
from vocabularies.concept as c
join cdm.measurement as con on con.measurement_concept_id=c.concept_id

-- name: sql_filtering_terms_procedure
-- Get all the procedure_occurrence filtering terms for individual
select distinct CONCAT(vocabulary_id,':',concept_code) as uri, c.concept_name
from vocabularies.concept as c
join cdm.procedure_occurrence as con on con.procedure_concept_id=c.concept_id

-- name: sql_filtering_terms_observation
-- Get all the observation filtering terms for individual
select distinct CONCAT(vocabulary_id,':',concept_code) as uri, c.concept_name
from vocabularies.concept as c
join cdm.observation as con on con.observation_concept_id=c.concept_id

-- name: sql_filtering_terms_drug_exposure
-- Get all the drug exposure filtering terms for individual
select distinct CONCAT(vocabulary_id,':',concept_code) as uri, c.concept_name
from vocabularies.concept as c
join cdm.drug_exposure as con on con.drug_concept_id=c.concept_id
