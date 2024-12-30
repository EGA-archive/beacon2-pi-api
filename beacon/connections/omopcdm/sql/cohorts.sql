-- name: get_all_cohorts
-- Get all cohorts in database
SELECT cohort_definition_id, to_char(cohort_initiation_date, 'YYYY-MM-DD'),
    cohort_definition_name
FROM cdm.cohort_definition
ORDER BY cohort_definition_id

-- name: get_single_cohort
-- Get a cohort in database
SELECT cohort_definition_id, to_char(cohort_initiation_date, 'YYYY-MM-DD'),
    cohort_definition_name
FROM cdm.cohort_definition
where cohort_definition_id=:cohort_id

-- name: get_cohort_individuals
-- Get individuals from a cohort
SELECT subject_id
FROM cdm.cohort
where cohort_definition_id=:cohort_id
ORDER BY cohort_definition_id

-- name: get_cohort_individuals_limited
-- Get individuals from a cohort
SELECT subject_id
FROM cdm.cohort
where cohort_definition_id=:cohort_id
limit :limit

-- name: count_cohort_individuals$
-- Get individuals count
SELECT count(*)
FROM cdm.cohort
where cohort_definition_id = :cohort_id

-- name: get_cohort_count$
-- Get gender count
select count(*)
from cdm.person p

-- name: get_age_range^
-- Get age min-max
select min(date_part('year', age( now(), p.birth_datetime)))::int min_age, max(date_part('year', age( now(), p.birth_datetime)))::int max_age
from cdm.person p

-- name: get_age_range_person^
-- Get age min-max per person
select min(date_part('year', age( now(), p.birth_datetime)))::int min_age, max(date_part('year', age( now(), p.birth_datetime)))::int max_age
from cdm.person p
where p.person_id = ANY(:person_ids)

-- name: get_gender
-- Get gender
SELECT c.concept_name as label,
    c.vocabulary_id || ':' || c.concept_code as id
from cdm.person p
inner join vocabularies.concept c on c.concept_id = p.gender_concept_id
group by c.concept_name, c.vocabulary_id, c.concept_code

-- name: get_gender_per_person
-- Get gender per person
SELECT c.concept_name as label,
    c.vocabulary_id || ':' || c.concept_code as id
from cdm.person p
inner join vocabularies.concept c on c.concept_id = p.gender_concept_id
where p.person_id = ANY(:person_ids)
group by c.concept_name, c.vocabulary_id, c.concept_code

-- name: get_gender_count
-- Get gender count
select c.concept_name, count(*)
from cdm.person p
inner join vocabularies.concept c on c.concept_id = p.gender_concept_id
group by concept_name

-- name: get_gender_count_per_person
-- Get gender count
select c.concept_name, count(*)
from cdm.person p
inner join vocabularies.concept c on c.concept_id = p.gender_concept_id
where p.person_id = ANY(:person_ids)
group by concept_name

-- name: get_location
-- Get location
SELECT distinct c.concept_name as label,
    c.vocabulary_id || ':' || c.concept_code as id
from cdm.location p
inner join vocabularies.concept c on c.concept_id = p.country_concept_id
group by c.concept_name, c.vocabulary_id, c.concept_code

-- name: get_location_per_person
-- Get location
SELECT distinct c.concept_name as label,
    c.vocabulary_id || ':' || c.concept_code as id
from cdm.location l
inner join vocabularies.concept c on c.concept_id = l.country_concept_id
inner join cdm.person p on l.location_id = l.location_id
where p.person_id = ANY(:person_ids)
group by c.concept_name, c.vocabulary_id, c.concept_code

-- name: get_year_of_birth_count
-- Get year_of_birth count
select p.year_of_birth, count(*)
from cdm.person p
group by p.year_of_birth
order by year_of_birth

-- name: get_year_of_birth_count_per_person
-- Get year_of_birth count per person
select p.year_of_birth, count(*)
from cdm.person p
where p.person_id = ANY(:person_ids)
group by p.year_of_birth
order by year_of_birth

-- name: get_condition_count
-- Get condtion concept count
select  concept_name, count(distinct person_id) count_value
from cdm.condition_occurrence co
inner join vocabularies.concept c on c.concept_id = co.condition_concept_id
group by c.concept_code, c.vocabulary_id, concept_name
order by count_value desc

-- name: get_condition_count_person
-- Get condtion concept count per person
select  concept_name, count(distinct person_id) count_value
from cdm.condition_occurrence co
inner join vocabularies.concept c on c.concept_id = co.condition_concept_id
where person_id = ANY(:person_ids)
group by c.concept_code, c.vocabulary_id, concept_name
order by count_value desc

-- name: get_condition
-- Get condition
SELECT distinct c.concept_name as label,
    c.vocabulary_id || ':' || c.concept_code as id
from cdm.condition_occurrence p
inner join vocabularies.concept c on c.concept_id = p.condition_concept_id
group by c.concept_name, c.vocabulary_id, c.concept_code

-- name: get_condition_per_person
-- Get condition per person
SELECT distinct c.concept_name as label,
    c.vocabulary_id || ':' || c.concept_code as id
from cdm.condition_occurrence con
inner join vocabularies.concept c on c.concept_id = con.condition_concept_id
where person_id = ANY(:person_ids)
group by c.concept_name, c.vocabulary_id, c.concept_code

-- name: get_procedure_count
-- Get procedure concept count
select c.concept_code, c.vocabulary_id, concept_name, count(distinct person_id) count_value
from cdm.procedure_occurrence po
inner join vocabularies.concept c on c.concept_id = po.procedure_concept_id
group by c.concept_code, c.vocabulary_id, concept_name
order by count_value desc

-- name: get_drug_count
-- Get drug concept count
select c.concept_code, c.vocabulary_id, concept_name, count(distinct person_id) count_value
from cdm.drug_exposure de
inner join vocabularies.concept c on c.concept_id = de.drug_concept_id
group by c.concept_code, c.vocabulary_id, concept_name
order by count_value desc