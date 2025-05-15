endpoint_name='datasets'
open_api_endpoints_definition='https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2/main/models/json/beacon-v2-default-model/datasets/endpoints.json'

# Granularity accepted (if all False, endpoint will not be available)
boolean=True
count=True
record=True

# Entry type info
id='dataset'
name='Dataset'
ontology_id='NCIT:C47824'
ontology_name='Data set'
specification='Beacon v2.0.0'
description='A Dataset is a collection of records, like rows in a database or cards in a cardholder.'
defaultSchema_id='beacon-dataset-v2.0.0'
defaultSchema_name='Default schema for datasets'
defaultSchema_reference_to_schema_definition='https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2/main/models/json/beacon-v2-default-model/datasets/defaultSchema.json'
defaultSchema_schema_version='v2.0.0'
aditionally_supported_schemas=[]
allow_queries_without_filters=True

# Map configuration
singleEntryUrl=True # True if your beacon enables endpoint datasets/{id}
analysis_lookup=True # True if your beacon enables endpoint datasets/{id}/analyses
biosample_lookup=True # True if your beacon enables endpoint datasets/{id}/biosamples
cohort_lookup=True # True if your beacon enables endpoint datasets/{id}/datasets
genomicVariant_lookup=True # True if your beacon enables endpoint datasets/{id}/g_variants
individual_lookup=True # True if your beacon enables endpoint datasets/{id}/individuals
run_lookup=True # True if your beacon enables endpoint datasets/{id}/runs