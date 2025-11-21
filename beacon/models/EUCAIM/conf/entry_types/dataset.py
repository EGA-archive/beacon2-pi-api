from beacon.connections.mongo.__init__ import datasets

endpoint_name='image_datasets' # Leave it blank ('') to deactivate the endpoint.
enable_endpoint=True
open_api_endpoints_definition='https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2/main/models/json/beacon-v2-default-model/datasets/endpoints.json'
database='mongo' # The name must match the folder's name in connection that belongs to the desired database.
database_connection=datasets

# Granularity accepted: boolean, count or record
granularity='record'

# Entry type info
id='dataset'
name='Dataset'
ontology_id='NCIT:C47824'
ontology_name='Data set'
specification=''
description='A Dataset is a collection of records, like rows in a database or cards in a cardholder.'
defaultSchema_id='EUCAIM-dataset-v0.0.1'
defaultSchema_name='Default schema for datasets'
defaultSchema_reference_to_schema_definition='https://raw.githubusercontent.com/ga4gh-beacon/beacon-v2/main/models/json/beacon-v2-default-model/datasets/defaultSchema.json'
defaultSchema_schema_version=''
aditionally_supported_schemas=[]
allow_queries_without_filters=True

# Map configuration
singleEntryUrl=True # True if your beacon enables endpoint datasets/{id}