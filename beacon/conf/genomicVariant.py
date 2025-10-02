endpoint_name='g_variants' # Leave it blank ('') to deactivate the endpoint.
enable_endpoint=True
open_api_endpoints_definition='https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2/main/models/json/beacon-v2-default-model/genomicVariations/endpoints.json'
database='mongo' # The name must match the folder's name in connection that belongs to the desired database.

# Granularity accepted: boolean, count or record
granularity='record'

# Entry type info
id='genomicVariant'
name='Genomic Variants'
ontology_id='SO:0000735'
ontology_name='sequence_location'
specification='Beacon v2.0.0'
description='The location of a sequence.'
defaultSchema_id='beacon-g_variant-v2.0.0'
defaultSchema_name='Default schema for a genomic variation'
defaultSchema_reference_to_schema_definition='https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2/main/models/json/beacon-v2-default-model/genomicVariations/defaultSchema.json'
defaultSchema_schema_version='v2.0.0'
aditionally_supported_schemas=[]
allow_queries_without_filters=True

# Map configuration
singleEntryUrl=True # True if your beacon enables endpoint g_variants/{id}
analysis_lookup=True # True if your beacon enables endpoint g_variants/{id}/analyses
biosample_lookup=True # True if your beacon enables endpoint g_variants/{id}/biosamples
dataset_lookup=True # True if your beacon enables endpoint g_variants/{id}/datasets
cohort_lookup=True # True if your beacon enables endpoint g_variants/{id}/cohorts
individual_lookup=True # True if your beacon enables endpoint g_variants/{id}/individuals
run_lookup=True # True if your beacon enables endpoint g_variants/{id}/runs