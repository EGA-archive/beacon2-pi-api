import logging
import yaml
from beacon.exceptions.exceptions import FileNotFound

try:
    with open("beacon/conf/api_version.yml") as api_version_file:
        api_version_yaml = yaml.safe_load(api_version_file)
except Exception as e:
    raise FileNotFound('There are issues with the api_version.yml file. Check if it can be opened or if has any content')

level=logging.DEBUG
log_file=None
beacon_id = 'org.ega-archive.beacon-af-gdi-spain'  # ID of the Beacon
beacon_name = 'Allele Frequency Beacon GDI Spain'  # Name of the Beacon service
api_version = 'v2.2.0' # Version of the Beacon implementation
uri = 'https://beacon-af-spain-demo.ega-archive.org'
uri_subpath = '/api'
complete_url = uri + uri_subpath
environment = 'test'
description = r"Allele Frequency Beacon for GDI Spain."
version = api_version_yaml['api_version']
welcome_url = 'https://beacon.ega-archive.org/'
alternative_url = 'https://beacon.ega-archive.org/api'
create_datetime = '2021-11-29T12:00:00.000000Z'
update_datetime = ''
default_beacon_granularity = "record" # boolean, count or record
security_levels = ['PUBLIC', 'REGISTERED', 'CONTROLLED']
documentation_url = 'https://b2ri-documentation-demo.ega-archive.org/'
cors_urls = ["http://localhost:3003", "http://localhost:3000"]

# Service Info
ga4gh_service_type_group = 'org.ga4gh'
ga4gh_service_type_artifact = 'beacon'
ga4gh_service_type_version = '1.0'

# Organization info
org_id = 'EGA'  # Id of the organization
org_name = 'European Genome-Phenome Archive (EGA)'  # Full name
org_description = 'The European Genome-phenome Archive (EGA) is a service for permanent archiving and sharing of all types of personally identifiable genetic and phenotypic data resulting from biomedical research projects.'
org_adress = 'C/ Dr. Aiguader, 88, PRBB Building 08003 Barcelona, Spain'
org_welcome_url = 'https://ega-archive.org/'
org_contact_url = 'mailto:beacon.ega@crg.eu'
org_logo_url = 'https://legacy.ega-archive.org/images/logo.png'
org_info = ''

# Certificates
beacon_server_crt = ''
beacon_server_key = ''

# Query Budget
query_budget_per_user = False
query_budget_per_ip = False
query_budget_amount = 3
query_budget_time_in_seconds = 20
query_budget_database = 'mongo'
query_budget_db_name = 'beacon'
query_budget_table = 'budget'

# Query Rounding
imprecise_count=0 # If imprecise_count is 0, no modification of the count will be applied. If it's different than 0, count will always be this number when count is smaller than this number.
round_to_tens=False # If true, the rounding will be done to the immediate superior tenth if the imprecise_count is 0
round_to_hundreds=False # If true, the rounding will be done to the immediate superior hundredth if the imprecise_count is 0 and the round_to_tens is false