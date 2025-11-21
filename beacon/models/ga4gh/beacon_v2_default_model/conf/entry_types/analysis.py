from beacon.connections.mongo.__init__ import analyses

endpoint_name="analyses"
enable_endpoint=True
open_api_endpoints_definition='https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2/main/models/json/beacon-v2-default-model/analyses/endpoints.json'
database='mongo' # The name must match the folder's name in connection that belongs to the desired database.
database_connection=analyses

# Granularity accepted: boolean, count or record
granularity='record'

# Entry type configuration
id='analysis'
name='Bioinformatics analysis'
ontology_id='edam:operation_2945'
ontology_name='Analysis'
specification='Beacon v2.0.0'
description='Apply analytical methods to existing data of a specific type.'
defaultSchema_id='beacon-analysis-v2.0.0'
defaultSchema_name='Default schema for a bioinformatics analysis'
defaultSchema_reference_to_schema_definition='https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2/main/models/json/beacon-v2-default-model/analyses/defaultSchema.json'
defaultSchema_schema_version='v2.0.0'
aditionally_supported_schemas=[]
allow_queries_without_filters=True

# Map configuration
singleEntryUrl=True # True if your beacon enables endpoint analyses/{id}
biosample_lookup=True # True if your beacon enables endpoint analyses/{id}/biosamples
cohort_lookup=True # True if your beacon enables endpoint analyses/{id}/cohorts
dataset_lookup=True # True if your beacon enables endpoint analyses/{id}/datasets
genomicVariant_lookup=True # True if your beacon enables endpoint analyses/{id}/g_variants
individual_lookup=True # True if your beacon enables endpoint analyses/{id}/individuals
# TODO: afegir noms de urls pels lookups amb la variable example: individual_lookup_url=""
run_lookup=True # True if your beacon enables endpoint analyses/{id}/runs
