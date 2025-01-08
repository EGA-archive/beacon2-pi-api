import conf
import psycopg2

uri = "postgresql://{}:{}@{}:{}/{}".format(
    conf.database_user,
    conf.database_password,
    conf.database_host, # Ex: localhost
    conf.database_port, # Ex: 5432
    conf.database_name,
)

client = psycopg2.connect(uri)


# Create materialised view from the vocabulary used in the database
MaterialisedView = """
    -- Create a materialized view to store all relevant concept_ids
    DROP MATERIALIZED VIEW IF EXISTS search_ontologies_view;

    CREATE MATERIALIZED VIEW search_ontologies_view AS
    WITH relevant_concepts AS (
        -- Aggregate all concept_ids referenced in the data tables
        SELECT gender_concept_id as concept_id FROM cdm.person
        UNION
        SELECT race_concept_id as concept_id FROM cdm.person
        UNION
        SELECT condition_concept_id as concept_id FROM cdm.condition_occurrence
        UNION
        SELECT procedure_concept_id as concept_id FROM cdm.procedure_occurrence
        UNION
        SELECT measurement_concept_id as concept_id FROM cdm.measurement
        UNION
        SELECT unit_concept_id as concept_id FROM cdm.measurement
        UNION
        SELECT observation_concept_id as concept_id FROM cdm.observation
        UNION
        SELECT unit_concept_id as concept_id FROM cdm.observation
        UNION
        SELECT drug_concept_id as concept_id FROM cdm.drug_exposure
        UNION
        SELECT disease_status_concept_id as concept_id FROM cdm.specimen
        UNION
        SELECT anatomic_site_concept_id as concept_id FROM cdm.specimen
    )
    SELECT 
        DISTINCT c.concept_id,
        c.concept_name,
        c.vocabulary_id,
        c.concept_code
    FROM 
        vocabularies.concept c
    INNER JOIN 
        relevant_concepts rc
    ON 
        c.concept_id = rc.concept_id
    """

# Index vocabulary
indexQuery = """
    CREATE INDEX IF NOT EXISTS idx_concept_id ON search_ontologies_view (concept_id);
    """

# Query executor
def queryExecutor(query):
    cur = client.cursor()
    cur.execute(query)

# try:
#     queryExecutor(MaterialisedView)
#     queryExecutor(indexQuery)
#     print("Index and store procedure done")
# except:
#     print("Index and store procedure could not be created")
queryExecutor(MaterialisedView)
queryExecutor(indexQuery)
