endpoint_name='biosamples' # Leave it blank ('') to deactivate the endpoint.
open_api_endpoints_definition='https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2/main/models/json/beacon-v2-default-model/biosamples/endpoints.json'
database='mongo' # The name must match the folder's name in connection that belongs to the desired database.

# Granularity accepted: boolean, count or record
granularity='record'

# Entry type info
id='biosample'
name='Biological Sample'
ontology_id='NCIT:C70699'
ontology_name='Biospecimen'
specification='Beacon v2.0.0'
description='Any material sample taken from a biological entity for testing, diagnostic, propagation, treatment or research purposes, including a sample obtained from a living organism or taken from the biological object after halting of all its life functions. Biospecimen can contain one or more components including but not limited to cellular molecules, cells, tissues, organs, body fluids, embryos, and body excretory products. [ NCI ]'
defaultSchema_id='beacon-biosample-v2.0.0'
defaultSchema_name='Default schema for a biological sample'
defaultSchema_reference_to_schema_definition='https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2/main/models/json/beacon-v2-default-model/biosamples/defaultSchema.json'
defaultSchema_schema_version='v2.0.0'
aditionally_supported_schemas=[]
allow_queries_without_filters=True

# Map configuration
singleEntryUrl=True # True if your beacon enables endpoint biosamples/{id}
analysis_lookup=True # True if your beacon enables endpoint biosamples/{id}/analyses
cohort_lookup=True # True if your beacon enables endpoint biosamples/{id}/cohorts
dataset_lookup=True # True if your beacon enables endpoint biosamples/{id}/datasets
genomicVariant_lookup=True # True if your beacon enables endpoint biosamples/{id}/g_variants
individual_lookup=True # True if your beacon enables endpoint biosamples/{id}/individuals
run_lookup=True # True if your beacon enables endpoint biosamples/{id}/runs