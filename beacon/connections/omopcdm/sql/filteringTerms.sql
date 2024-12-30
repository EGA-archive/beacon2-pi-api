
--Individuals--

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

--Biosamples--

-- name: sql_filtering_terms_biosample
-- Get all the observation filtering terms for individual
select distinct CONCAT(vocabulary_id,':',concept_code) as uri, c.concept_name
from vocabularies.concept as c
join cdm.specimen as con
    on con.disease_status_concept_id=c.concept_id or con.anatomic_site_concept_id=c.concept_id