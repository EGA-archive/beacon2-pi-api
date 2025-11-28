from beacon.connections.mongo.__init__ import analyses

endpoint_name="diseases"
enable_endpoint=True
open_api_endpoints_definition=''
database='mongo' # The name must match the folder's name in connection that belongs to the desired database.
database_connection=analyses

# Granularity accepted: boolean, count or record
granularity='record'

# Entry type configuration
id='disease'
name=''
ontology_id='EFO:0000408'
ontology_name='Disease'
specification=''
description=''
defaultSchema_id='EUCAIM-disease_v0.0.1'
defaultSchema_name=''
defaultSchema_reference_to_schema_definition='https://raw.githubusercontent.com/EGA-archive/EUCAIM-Schema/refs/heads/main/DiseaseMetadata.json'
defaultSchema_schema_version=''
aditionally_supported_schemas=[]
allow_queries_without_filters=True

# Map configuration
singleEntryUrl=True # True if your beacon enables endpoint images/{id}