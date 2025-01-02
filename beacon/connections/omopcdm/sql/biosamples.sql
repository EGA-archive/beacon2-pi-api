
-- name: sql_get_biosamples
-- Get biosamples
SELECT specimen_id
FROM cdm.specimen
LIMIT :limit
OFFSET :offset

-- name: sql_get_biosample_id^
-- Get biosample by id
SELECT DISTINCT specimen_id
FROM cdm.specimen
WHERE specimen_id = :specimen_id

-- name: get_count_specimen$
-- Get specimen count
SELECT count(*)
FROM cdm.specimen

-- name: sql_get_specimen
-- Get gender and race by id
SELECT person_id, disease_status_concept_id, anatomic_site_concept_id,
    specimen_date::text, specimen_datetime::text
FROM cdm.specimen
WHERE specimen_id = :specimen_id

-- name: get_specimen_by_person_id
-- Get specimen id by person id
SELECT distinct specimen_id
FROM cdm.specimen
WHERE person_id in :person_id