endpoint_name="images"
enable_endpoint=True
open_api_endpoints_definition=''
database='mongoEUCAIM' # The name must match the folder's name in connection that belongs to the desired database.

# Granularity accepted: boolean, count or record
granularity='record'

# Entry type configuration
id='imaging'
name=''
ontology_id=''
ontology_name=''
specification=''
description=''
defaultSchema_id=''
defaultSchema_name=''
defaultSchema_reference_to_schema_definition='https://raw.githubusercontent.com/EGA-archive/EUCAIM-Schema/refs/heads/main/ImagingMetadata.json'
defaultSchema_schema_version=''
aditionally_supported_schemas=[]
allow_queries_without_filters=True

# Map configuration
singleEntryUrl=True # True if your beacon enables endpoint images/{id}
