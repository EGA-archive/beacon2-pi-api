endpoint_name='individuals' # Leave it blank ('') to deactivate the endpoint.
enable_endpoint=True
open_api_endpoints_definition='https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2/main/models/json/beacon-v2-default-model/individuals/endpoints.json'
database='mongo' # The name must match the folder's name in connection that belongs to the desired database.

# Granularity accepted: boolean, count or record
granularity='record'

# Entry type info
id='individual'
name='Individual'
ontology_id='NCIT:C25190'
ontology_name='Person'
specification='Beacon v2.0.0'
description='A human being. It could be a Patient, a Tissue Donor, a Participant, a Human Study Subject, etc.'
defaultSchema_id='beacon-individual-v2.2.0'
defaultSchema_name='Default schema for an individual'
defaultSchema_reference_to_schema_definition='https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2/main/models/json/beacon-v2-default-model/individuals/defaultSchema.json'
defaultSchema_schema_version='v2.0.0'
aditionally_supported_schemas=[]
allow_queries_without_filters=True

# Map configuration
singleEntryUrl=True # True if your beacon enables endpoint individuals/{id}
analysis_lookup=True # True if your beacon enables endpoint individuals/{id}/analyses
biosample_lookup=True # True if your beacon enables endpoint individuals/{id}/biosamples
dataset_lookup=True # True if your beacon enables endpoint individuals/{id}/datasets
genomicVariant_lookup=True # True if your beacon enables endpoint individuals/{id}/g_variants
cohort_lookup=True # True if your beacon enables endpoint individuals/{id}/cohorts
run_lookup=True # True if your beacon enables endpoint individuals/{id}/runs