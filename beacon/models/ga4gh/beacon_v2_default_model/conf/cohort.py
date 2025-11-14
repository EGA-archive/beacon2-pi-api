from beacon.connections.mongo.__init__ import cohorts

endpoint_name='cohorts' # Leave it blank ('') to deactivate the endpoint.
enable_endpoint=True
open_api_endpoints_definition='https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2/main/models/json/beacon-v2-default-model/cohorts/endpoints.json'
database='mongo' # The name must match the folder's name in connection that belongs to the desired database.
database_connection=cohorts

# Granularity accepted: boolean, count or record
granularity='record'

# Entry type info
id='cohort'
name='Cohort'
ontology_id='NCIT:C61512'
ontology_name='Cohort'
specification='Beacon v2.0.0'
description='A group of individuals, identified by a common characteristic. [ NCI ]'
defaultSchema_id='beacon-cohort-v2.0.0'
defaultSchema_name='Default schema for cohorts'
defaultSchema_reference_to_schema_definition='https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2/main/models/json/beacon-v2-default-model/cohorts/defaultSchema.json'
defaultSchema_schema_version='v2.0.0'
aditionally_supported_schemas=[]
allow_queries_without_filters=True

# Map configuration
singleEntryUrl=True # True if your beacon enables endpoint cohorts/{id}
analysis_lookup=True # True if your beacon enables endpoint cohorts/{id}/analyses
biosample_lookup=True # True if your beacon enables endpoint cohorts/{id}/biosamples
dataset_lookup=True # True if your beacon enables endpoint cohorts/{id}/datasets
genomicVariant_lookup=True # True if your beacon enables endpoint cohorts/{id}/g_variants
individual_lookup=True # True if your beacon enables endpoint cohorts/{id}/individuals
run_lookup=True # True if your beacon enables endpoint cohorts/{id}/runs