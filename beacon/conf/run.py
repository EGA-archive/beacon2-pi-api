endpoint_name='runs' # Leave it blank ('') to deactivate the endpoint.
enable_endpoint=True
open_api_endpoints_definition='https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2/main/models/json/beacon-v2-default-model/runs/endpoints.json'
database='mongo' # The name must match the folder's name in connection that belongs to the desired database.

# Granularity accepted: boolean, count or record
granularity='record'

# Entry type info
id='run'
name='Sequencing run'
ontology_id='NCIT:C148088'
ontology_name='Sequencing run'
specification='Beacon v2.0.0'
description='The valid and completed operation of a high-throughput sequencing instrument for a single sequencing process. [ NCI ]'
defaultSchema_id='beacon-run-v2.0.0'
defaultSchema_name='Default schema for a sequencing run'
defaultSchema_reference_to_schema_definition='https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2/main/models/json/beacon-v2-default-model/runs/defaultSchema.json'
defaultSchema_schema_version='v2.0.0'
aditionally_supported_schemas=[]
allow_queries_without_filters=True

# Map configuration
singleEntryUrl=True # True if your beacon enables endpoint runs/{id}
analysis_lookup=True # True if your beacon enables endpoint runs/{id}/analyses
biosample_lookup=True # True if your beacon enables endpoint runs/{id}/biosamples
dataset_lookup=True # True if your beacon enables endpoint runs/{id}/datasets
genomicVariant_lookup=True # True if your beacon enables endpoint runs/{id}/g_variants
individual_lookup=True # True if your beacon enables endpoint runs/{id}/individuals
cohort_lookup=True # True if your beacon enables endpoint runs/{id}/cohorts