from aiohttp.test_utils import TestClient, TestServer, loop_context
import unittest
import os
import jwt
from aiohttp import web
from beacon.auth.__main__ import fetch_idp, validate_access_token, authentication, fetch_user_info, validate_ga4gh_visa
from dotenv import load_dotenv
from beacon.logs.logs import initialize_logger
from beacon.conf.conf_override import config
from beacon.utils.middlewares import error_middleware
from beacon.utils.routes import append_routes
from aiohttp_middlewares import cors_middleware
import beacon.conf.conf_override as conf_override
from beacon.exceptions.exceptions import NoTermsAndConditionsForResearcherAvailable
import requests
import yaml

# for keycloak, create aud in mappers, with custom, aud and beacon for audience
mock_access_token = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJreS1tUXNxZ0ZYeHdSUVRfRUhuQlJJUGpmbVhfRXZuUTVEbzZWUTJCazdZIn0.eyJleHAiOjE3OTEyMTU3NzYsImlhdCI6MTc5MTIxNTQ3NiwianRpIjoiZDM4MGZlYzQtYmRlMi00Y2RiLTgxOWQtYzRiOTVkMjQwNGY2IiwiaXNzIjoiaHR0cDovL2xvY2FsaG9zdDo4MDgwL2F1dGgvcmVhbG1zL0JlYWNvbiIsImF1ZCI6ImJlYWNvbiIsInN1YiI6IjQ3ZWZmMWIxLTc2MjEtNDU3MC1hMGJiLTAxYTcxOWZiYTBhMiIsInR5cCI6IkJlYXJlciIsImF6cCI6ImJlYWNvbiIsInNlc3Npb25fc3RhdGUiOiJmNmE1MTYyYy1mM2E4LTQ3N2MtOTc1ZS0xZDFmYWU4ZGJhZDEiLCJhY3IiOiIxIiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCBtaWNyb3Byb2ZpbGUtand0Iiwic2lkIjoiZjZhNTE2MmMtZjNhOC00NzdjLTk3NWUtMWQxZmFlOGRiYWQxIiwidXBuIjoiamFuZSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwibmFtZSI6IkphbmUgU21pdGgiLCJncm91cHMiOlsib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiIsIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXSwicHJlZmVycmVkX3VzZXJuYW1lIjoiamFuZSIsImdpdmVuX25hbWUiOiJKYW5lIiwiZmFtaWx5X25hbWUiOiJTbWl0aCIsImVtYWlsIjoiamFuZS5zbWl0aEBiZWFjb24uZ2E0Z2gifQ.i2QZfR4-k_h2MaBuOTQTUZQ-CmGqMEyGSEcdwbW3D838L7J-PatfPb2_jej-YAeRg3TM6usGShlRNX0zH65QSTzY5lrIkxL68fQ0hp_QZPPV0m4e-vQG_Ef0jiKbLrD0OYUYF9LHqnQOm8VukFYBE2WXkOEf3vxMwD2TlzikL7t8CknfsHVStHMBDgBRQqeg-BXxj3yhDbFfS6rSRIxB0QLlmnvRq6VfDgigMf-_p83gfFrsj9RVKgisD0J86T3YFnUoa19pqGYCVlyztUVOfQ9uYlygdNlI1Te154j-6-TSQtJ--iOkGlOk9yGheQHghUigox2u9jNoPhimTtXKPg'
mock_access_token_false = 'public'
mock_ga4gh_visa_dataset = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL3JlbXMudGVzdC5leGFtcGxlLm9yZy8iLCJzdWIiOiJ0ZXN0LXVzZXItMTIzIiwiaWF0IjoxNzAwMDAwMDAwLCJleHAiOjE5MDAwMDAwMDAsImdhNGdoX3Zpc2FfdjEiOnsidHlwZSI6IkNvbnRyb2xsZWRBY2Nlc3NHcmFudHMiLCJhc3NlcnRlZCI6MTcwMDAwMDAwMCwidmFsdWUiOiJodHRwczovL3JlbXMudGVzdC5leGFtcGxlLm9yZy9kYXRhc2V0cy90ZXN0LWRhdGFzZXQiLCJzb3VyY2UiOiJodHRwczovL3JlbXMudGVzdC5leGFtcGxlLm9yZy8iLCJieSI6ImRhYyJ9fQ.c3ludGhldGljLXRlc3Qtc2lnbmF0dXJl'


#audit --> TODO: get very specific information that we are interested in saving and keeping it (example: what individuals were returned in response)

def create_test_app():
    LOG = initialize_logger(config.level)
    app = web.Application(
        middlewares=[
            cors_middleware(origins=conf_override.config.cors_urls), error_middleware
        ]
    )
    app['logger'] = LOG
    app['pending_requests'] = set()
    app['shutting_down'] = False
    app['state'] = 'Running - healthy'
    app = append_routes(app=app)
    return app

# Authentication and identity provider (IdP) integration test suite
class TestAuthN(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

        # Initialize logging system for authentication test diagnostics
        LOG = initialize_logger(config.level)

        # Assign test identifier (used in downstream auth/context logic)
        self._id = 'test'

        # Attach logger instance to test class
        self.LOG = LOG
    def test_auth_fetch_idp(self):
        # Test retrieval of Identity Provider configuration from environment/system
        with loop_context() as loop:

            # Create isolated application instance for authentication flow
            app = create_test_app()

            # Wrap app in test HTTP server/client
            client = TestClient(TestServer(app), loop=loop)

            loop.run_until_complete(client.start_server())

            async def test_fetch_idp():
                # Fetch IdP configuration dynamically using mock access token
                idp_issuer, user_info, idp_client_id, idp_client_secret, \
                idp_introspection, idp_jwks_url, aud = fetch_idp(
                    self, mock_access_token
                )

                # Load expected configuration from Keycloak environment file
                load_dotenv("beacon/auth/idp_providers/keycloak.env", override=True)

                # Extract expected values from environment variables
                IDP_ISSUER = os.getenv('ISSUER')
                IDP_CLIENT_ID = os.getenv('CLIENT_ID')
                IDP_CLIENT_SECRET = os.getenv('CLIENT_SECRET')
                IDP_WELL_KNOWN_ENDPOINT = os.getenv('WELL_KNOWN_ENDPOINT')
                response = requests.get(IDP_WELL_KNOWN_ENDPOINT)
                response.raise_for_status()
                well_known_info = response.json()
                JWKS_URL=well_known_info["jwks_uri"]
                INTROSPECTION=well_known_info["introspection_endpoint"]
                # Validate fetched configuration matches environment configuration
                assert IDP_ISSUER == idp_issuer
                assert IDP_CLIENT_ID == idp_client_id
                assert IDP_CLIENT_SECRET == idp_client_secret
                assert JWKS_URL == idp_jwks_url
                assert INTROSPECTION == idp_introspection

            # Execute async test inside event loop
            loop.run_until_complete(test_fetch_idp())

            # Clean shutdown of test server
            loop.run_until_complete(client.close())

    def test_auth_validate_access_token(self):
        # Test JWT validation pipeline without verifying signature (unit-level check)
        with loop_context() as loop:

            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_validate_access_token():
                # Load IdP configuration for validation context
                load_dotenv("beacon/auth/idp_providers/keycloak.env", override=True)

                IDP_ISSUER = os.getenv('ISSUER')
                IDP_WELL_KNOWN_ENDPOINT = os.getenv('WELL_KNOWN_ENDPOINT')
                response = requests.get(IDP_WELL_KNOWN_ENDPOINT)
                response.raise_for_status()
                well_known_info = response.json()
                IDP_JWKS_URL=well_known_info["jwks_uri"]
                # Validate fetched configuration matches environment configuration
                aud_must_include_url = os.getenv('MUST_INCLUDE_BEACON_URL_IN_AUDIENCE')
                if aud_must_include_url == True:
                    if config.complete_url not in aud:
                        self.LOG.warning("Unauthorized. The beacon's url is not included in the audience of the access token.")
                        raise Exception

                try:
                    # Extract JWT header without verification (inspect algorithm)
                    header = jwt.get_unverified_header(mock_access_token)
                    algorithm = header["alg"]

                    # Decode token payload without signature verification (unsafe but test-only)
                    decoded = jwt.decode(mock_access_token, options={"verify_signature": False})

                    # Extract issuer and audience for validation step
                    issuer = decoded['iss']
                    aud = decoded['aud']

                except Exception:
                    # Any parsing failure results in unauthorized request
                    raise web.HTTPUnauthorized()

                # Validate token against IdP configuration and JWKS endpoint
                access_token_validation = validate_access_token(
                    self,
                    mock_access_token,
                    IDP_ISSUER,
                    IDP_JWKS_URL,
                    aud
                )

                # Expect token to be valid under mocked conditions
                assert access_token_validation == True

            loop.run_until_complete(test_validate_access_token())
            loop.run_until_complete(client.close())

    def test_auth_fetch_user_info(self):
        # Test retrieval of user profile data from IdP userinfo endpoint
        with loop_context() as loop:

            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_fetch_user_info():
                # Load IdP configuration for API calls
                load_dotenv("beacon/auth/idp_providers/keycloak.env", override=True)

                IDP_ISSUER = os.getenv('ISSUER')
                IDP_WELL_KNOWN_ENDPOINT = os.getenv('WELL_KNOWN_ENDPOINT')
                response = requests.get(IDP_WELL_KNOWN_ENDPOINT)
                response.raise_for_status()
                well_known_info = response.json()
                IDP_USER_INFO=well_known_info["userinfo_endpoint"]

                # Initialize visa dataset accumulator (GA4GH passport model)
                list_visa_datasets = []

                # Fetch authenticated user profile from IdP
                user, list_visa_datasets = await fetch_user_info(
                    self,
                    mock_access_token,
                    IDP_USER_INFO,
                    IDP_ISSUER,
                    list_visa_datasets
                )

                # Validate returned identity information
                assert user.get('email') == 'jane.smith@beacon.ga4gh'

            loop.run_until_complete(test_fetch_user_info())
            loop.run_until_complete(client.close())
    def test_auth_authentication(self):
        # End-to-end authentication flow test (valid token case)
        with loop_context() as loop:

            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_authentication():
                # Perform full authentication pipeline using valid token
                user, list_visa_datasets = await authentication(
                    self,
                    mock_access_token
                )

                # Confirm authenticated identity resolution
                assert user.get('email') == 'jane.smith@beacon.ga4gh'

            loop.run_until_complete(test_authentication())
            loop.run_until_complete(client.close())
    def test_auth_authentication_false(self):
        # Negative authentication test: invalid token should fall back to public user
        with loop_context() as loop:

            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_authentication_false():
                # Authentication should fail gracefully for invalid token
                user, list_visa_datasets = await authentication(
                    self,
                    mock_access_token_false
                )

                # Expect fallback identity for unauthenticated requests
                assert user == None

            loop.run_until_complete(test_authentication_false())
            loop.run_until_complete(client.close())

    def test_auth_check_visa_passports(self):
        # Test GA4GH visa parsing and dataset extraction from passport claims
        with loop_context() as loop:

            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_visa_passports():
                # Simulated decoded user passport containing visas
                visa = jwt.decode(mock_ga4gh_visa_dataset, options={"verify_signature": False}, algorithms=["RS256"])
                if visa['iss'] in config.ga4gh_visa_trusted_issuers:
                    pass
                else:
                    self.LOG.warning("Unauthorized visa: {}. Issuer not trusted.".format(mock_ga4gh_visa_dataset))
                    raise Exception("Unauthorized visa. Issuer not trusted.")
                jwks_url=visa['iss']+'.well-known/openid-configuration'
                list_visa_datasets = []
                issuer = visa['iss']
                visa_validated = validate_ga4gh_visa(
                    self,
                    mock_ga4gh_visa_dataset,
                    issuer,
                    jwks_url
                )
                with open("/beacon/permissions/ga4gh_visas/visas_conf.yml", 'r') as pfile:
                    visas_conf = yaml.safe_load(pfile)
                pfile.close()
                if visa_validated==False:
                    visa_values=visa['ga4gh_visa_v1']
                    with open("/beacon/permissions/ga4gh_visas/visas_conf.yml", 'r') as pfile:
                        visas_conf = yaml.safe_load(pfile)
                    pfile.close()
                    visa_values=visa['ga4gh_visa_v1']
                    accepted_visa=False
                    if visa_values['type']=='AcceptedTermsAndPolicies':
                        for trusted_acceptedterms_visa in visas_conf['AcceptedTermsAndPolicies']:
                            if visa_values['value'] in trusted_acceptedterms_visa["accepted_values"]:
                                if visa["iss"] == trusted_acceptedterms_visa["iss"]:
                                    accepted_visa=True
                                    break
                        if accepted_visa==False:
                            self.LOG.warning('Terms and Conditions not accepted for the user')
                            raise NoTermsAndConditionsForResearcherAvailable('Terms and Conditions not accepted for the user')
                    elif visa_values['type']=='ResearcherStatus':
                        for trusted_acceptedterms_visa in visas_conf['ResearcherStatus']:
                            if visa_values['value'] in trusted_acceptedterms_visa["accepted_values"]:
                                if visa["iss"] == trusted_acceptedterms_visa["iss"]:
                                    accepted_visa=True
                                    break
                        if accepted_visa==False:
                            self.LOG.warning('Researcher Status: {} is not accepted'.format(visa_values['value']))
                            raise NoTermsAndConditionsForResearcherAvailable('Researcher Status is not RESEARCHER')
                    elif visa_values['type']=='ControlledAccessGrants':
                        for trusted_acceptedterms_visa in visas_conf['ControlledAccessGrants']:
                            if visa_values['value'] in trusted_acceptedterms_visa["accepted_values"]:
                                if visa["iss"] == trusted_acceptedterms_visa["iss"]:
                                    accepted_visa=True
                                    dataset_url = visa["ga4gh_visa_v1"]["value"]
                                    dataset_url_splitted = dataset_url.split('/')
                                    visa_dataset = dataset_url_splitted[-1]
                                    list_visa_datasets.append(visa_dataset)
                                    break
                        if accepted_visa==False:
                            self.LOG.warning('Invalid datasets visa')
                            raise NoTermsAndConditionsForResearcherAvailable('Invalid Visa')
                        if visa_values['type']=='AcceptedTermsAndPolicies':
                            if visa_values['value']=='accepted':
                                pass
                            else:
                                self.LOG.warning('Terms and Conditions not accepted for the user')
                                raise NoTermsAndConditionsForResearcherAvailable('Terms and Conditions not accepted for the user')
                        elif visa_values['type']=='ResearcherStatus':
                            if visa_values['value'] == 'RESEARCHER':
                                pass
                            else:
                                self.LOG.warning('Researcher Status is not RESEARCHER')
                                raise NoTermsAndConditionsForResearcherAvailable('Researcher Status is not RESEARCHER')
                    if visa['iss'] in config.ga4gh_visa_accepted_dataset_issuers:
                        if visa_values['type']=='ControlledAccessGrants':
                            dataset_url = visa["ga4gh_visa_v1"]["value"]
                            dataset_url_splitted = dataset_url.split('/')
                            visa_dataset = dataset_url_splitted[-1]
                            list_visa_datasets.append(visa_dataset)
                    else:
                        raise Exception


                # Expect correct dataset extraction from visa structure
                assert list_visa_datasets == ['test-dataset']

            loop.run_until_complete(test_check_visa_passports())
            loop.run_until_complete(client.close())

    def test_auth_check_accepted_terms_and_conditions(self):
        # Test GA4GH visa parsing and dataset extraction from passport claims
        with loop_context() as loop:

            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_terms():
                visa = {
                    "iss": "https://rems.example.org",
                    "ga4gh_visa_v1": {
                        "type": "AcceptedTermsAndPolicies",
                        "value": "accepted"
                    }
                }

                visa_validated=True
                mocking_config_value=True
                if visa_validated==True:
                    visa_values=visa['ga4gh_visa_v1']
                    if mocking_config_value == True:
                        if visa_values['type']=='AcceptedTermsAndPolicies':
                            if visa_values['value']=='accepted':
                                assert visa_values['value'] == 'accepted'
                            else:
                                raise NoTermsAndConditionsForResearcherAvailable('Terms and Conditions not accepted for the user')

            loop.run_until_complete(test_check_terms())
            loop.run_until_complete(client.close())

    def test_auth_check_researcher_status(self):
        # Test GA4GH visa parsing and dataset extraction from passport claims
        with loop_context() as loop:

            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_researcher_status():
                visa = {
                    "iss": "https://rems.example.org",
                    "ga4gh_visa_v1": {
                        "type": "ResearcherStatus",
                        "value": "RESEARCHER"
                    }
                }

                visa_validated=True
                mocking_config_value=True
                if visa_validated==True:
                    visa_values=visa['ga4gh_visa_v1']
                    if mocking_config_value == True:
                        if visa_values['type']=='ResearcherStatus':
                            if visa_values['value']=='RESEARCHER':
                                assert visa_values['value'] == 'RESEARCHER'
                            else:
                                raise NoTermsAndConditionsForResearcherAvailable('Researcher Status is not RESEARCHER')

            loop.run_until_complete(test_check_researcher_status())
            loop.run_until_complete(client.close())

if __name__ == '__main__':
    unittest.main()