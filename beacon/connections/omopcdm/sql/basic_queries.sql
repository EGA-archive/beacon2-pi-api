
-- name: sql_get_descendants
-- Get descendants from concept_id
SELECT descendant_concept_id
FROM vocabularies.concept_ancestor 
WHERE ancestor_concept_id = :concept_id

-- name: sql_get_concept_domain
-- Get OMOP concept_id and domain of the concept
SELECT concept_id, domain_id
FROM vocabularies.concept
WHERE vocabulary_id = :vocabulary_id and concept_code = :concept_code

-- name: sql_get_ontology^
-- Get ontology 
SELECT concept_name as label,
    vocabulary_id || ':' || concept_code as id
FROM vocabularies.concept 
WHERE concept_id = :concept_id
Limit 1

-- name: sql_get_ontology_view^
-- Get ontology in materialised view
SELECT concept_name as label,
    vocabulary_id || ':' || concept_code as id
FROM  search_ontologies_view
WHERE concept_id = :concept_id
Limit 1