import logging
import yaml
from beacon.exceptions.exceptions import raise_exception

try:
    with open("beacon/conf/api_version.yml") as api_version_file:
        api_version_yaml = yaml.safe_load(api_version_file)
except Exception as e:# pragma: no cover
    err = str(e)
    errcode=500
    raise_exception(err, errcode)

level=logging.NOTSET
log_file=None
beacon_id = 'org.ega-archive.ega-beacon'  # ID of the Beacon
beacon_name = 'EGA Beacon'  # Name of the Beacon service
api_version = 'v2.0.0' # Version of the Beacon implementation
uri = 'https://af-ega-beacon-demo.ega-archive.org/api/'
environment = 'prod'
description = r"This beacon is based on the European Genome-Phenome Archive datasets."
version = api_version_yaml['api_version']
welcome_url = 'https://beacon.ega-archive.org/'
alternative_url = 'https://beacon.ega-archive.org/api'
create_datetime = '2021-11-29T12:00:00.000000'
update_datetime = ''
max_beacon_granularity = "record" # boolean, count or record
security_levels = ['PUBLIC', 'REGISTERED', 'CONTROLLED']
documentation_url = 'https://b2ri-documentation-demo.ega-archive.org/'
alphanumeric_terms = ['libraryStrategy', 'molecularAttributes.geneIds', 'diseases.ageOfOnset.iso8601duration', 'molecularAttributes.aminoacidChanges','phenotypicFeatures.onset.iso8601duration', 'exposures.ageAtExposure.iso8601duration', 'treatments.ageAtOnset.iso8601duration']
cors_urls = ["http://localhost:3000","https://cancer-beacon-demo.ega-archive.org", "https://beacon-network-demo2.ega-archive.org", "https://beacon.ega-archive.org", "https://beacon-network-test.ega-archive.org", "https://af-beacon.ega-archive.org", "https://beacon-cancer-registry-test.ega-archive.org", "https://global-beacon-network.ega-archive.org"]
test_datasetId="synthetic_usecases_4beacon_testingV3"

# Service Info
ga4gh_service_type_group = 'org.ga4gh'
ga4gh_service_type_artifact = 'beacon'
ga4gh_service_type_version = '1.0'

# Organization info
org_id = 'EGA'  # Id of the organization
org_name = 'European Genome-Phenome Archive (EGA)'  # Full name
org_description = ('The European Genome-phenome Archive (EGA) '
                   'is a service for permanent archiving and sharing '
                   'of all types of personally identifiable genetic '
                   'and phenotypic data resulting from biomedical research projects.')
org_adress = ('C/ Dr. Aiguader, 88'
              'PRBB Building'
              '08003 Barcelona, Spain')
org_welcome_url = 'https://ega-archive.org/'
org_contact_url = 'mailto:beacon.ega@crg.eu'
org_logo_url = 'https://static.ega-archive.org/img/logo.png'
org_info = ''

beacon_server_crt = ''
beacon_server_key = ''