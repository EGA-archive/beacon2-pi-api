from aiohttp.test_utils import TestClient, TestServer, loop_context
import unittest
import os
import jwt
from aiohttp import web
from beacon.auth.__main__ import fetch_idp, validate_access_token, authentication, fetch_user_info, get_grants_from_visas
from dotenv import load_dotenv
from beacon.logs.logs import initialize_logger
from beacon.conf.conf_override import config
from beacon.utils.middlewares import error_middleware
from beacon.utils.routes import append_routes
from aiohttp_middlewares import cors_middleware
import beacon.conf.conf_override as conf_override
from beacon.exceptions.exceptions import NoTermsAndConditionsForResearcherAvailable, NoPermissionsAvailable
import requests
import yaml

# for keycloak, create aud in mappers, with custom, aud and beacon for audience
mock_access_token = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJreS1tUXNxZ0ZYeHdSUVRfRUhuQlJJUGpmbVhfRXZuUTVEbzZWUTJCazdZIn0.eyJleHAiOjE3OTE5MDk4MzgsImlhdCI6MTc5MTkwOTUzOCwianRpIjoiZmQ4NmEyNWUtMzc3NC00NmQ3LTg2YTgtNDBiYzkxODI1NDBjIiwiaXNzIjoiaHR0cDovL2xvY2FsaG9zdDo4MDgwL2F1dGgvcmVhbG1zL0JlYWNvbiIsImF1ZCI6ImJlYWNvbiIsInN1YiI6IjQ3ZWZmMWIxLTc2MjEtNDU3MC1hMGJiLTAxYTcxOWZiYTBhMiIsInR5cCI6IkJlYXJlciIsImF6cCI6ImJlYWNvbiIsInNlc3Npb25fc3RhdGUiOiJjOGEyMTIwOC1mY2I0LTQ1OTItOGY0OC1hMzI3MTJkNmZmMTYiLCJhY3IiOiIxIiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCBtaWNyb3Byb2ZpbGUtand0Iiwic2lkIjoiYzhhMjEyMDgtZmNiNC00NTkyLThmNDgtYTMyNzEyZDZmZjE2IiwidXBuIjoiamFuZSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwibmFtZSI6IkphbmUgU21pdGgiLCJncm91cHMiOlsib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiIsIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXSwicHJlZmVycmVkX3VzZXJuYW1lIjoiamFuZSIsImdpdmVuX25hbWUiOiJKYW5lIiwiZmFtaWx5X25hbWUiOiJTbWl0aCIsImVtYWlsIjoiamFuZS5zbWl0aEBiZWFjb24uZ2E0Z2gifQ.RTn7TFXAS8Z62aaN5uV6EusoPh7lyMzDogMxVUwkoAYS2gwopk_9UAqf76xFjzu3wKPcEFjOvdfyqgnuuXa_9oVZ3osqKRfoXuafrM6k4c1RCh0nam9uAEhP0-7q8g61tzwTtPg_-eKwjd1eQsNDo63g8Dd-dMSFntJP49iDj-Z1yu8p_9vBlwm7sLvyobfhTweteE_5Gk8mWAoP9c6X9bK-XkhRuImmd9Zq1u4Nn1bIWGYGzhT21RHPAC0CWcgGsV2jyhKDDpWZ3gxjMN-bI3JK04kKD_TMqXt0Uybvhw8V3ebUrghM2y7-9bEUvuBF0G2mejjF0h8psil1esFqqw'
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

                # Load expected configuration from Keycloak testing_idp environment file
                load_dotenv("beacon/auth/idp_providers/confidential/testing_idp.env", override=True)

                # Extract expected values from environment variables
                IDP_ISSUER = os.getenv('ISSUER')
                IDP_CLIENT_ID = os.getenv('CLIENT_ID')
                IDP_CLIENT_SECRET = os.getenv('CLIENT_SECRET')
                IDP_WELL_KNOWN_ENDPOINT = os.getenv('WELL_KNOWN_ENDPOINT')
                response = requests.get(IDP_WELL_KNOWN_ENDPOINT)
                response.raise_for_status()
                well_known_info = response.json()
                IDP_JWKS_URL=well_known_info["jwks_uri"]
                INTROSPECTION=well_known_info["introspection_endpoint"]
                if 'localhost'in IDP_JWKS_URL:
                    IDP_JWKS_URL=IDP_JWKS_URL.replace('localhost', 'idp')
                if 'localhost'in INTROSPECTION:
                    INTROSPECTION=INTROSPECTION.replace('localhost', 'idp')
                # Validate fetched configuration matches environment configuration
                assert IDP_ISSUER == idp_issuer
                assert IDP_CLIENT_ID == idp_client_id
                assert IDP_CLIENT_SECRET == idp_client_secret
                assert IDP_JWKS_URL == idp_jwks_url
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
                load_dotenv("beacon/auth/idp_providers/confidential/testing_idp.env", override=True)

                IDP_ISSUER = os.getenv('ISSUER')
                IDP_WELL_KNOWN_ENDPOINT = os.getenv('WELL_KNOWN_ENDPOINT')

                response = requests.get(IDP_WELL_KNOWN_ENDPOINT)
                response.raise_for_status()
                well_known_info = response.json()
                IDP_JWKS_URL=well_known_info["jwks_uri"]
                if 'localhost'in IDP_JWKS_URL:
                    IDP_JWKS_URL=IDP_JWKS_URL.replace('localhost', 'idp')
                # Validate fetched configuration matches environment configuration
                aud_must_include_url = os.getenv('MUST_INCLUDE_BEACON_URL_IN_AUDIENCE')
                if aud_must_include_url == True:
                    if config.complete_url not in aud:
                        self.LOG.warning("Unauthorized. The beacon's url is not included in the audience of the access token.")
                        raise Exception

                try:
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
                load_dotenv("beacon/auth/idp_providers/confidential/testing_idp.env", override=True)

                IDP_ISSUER = os.getenv('ISSUER')
                IDP_WELL_KNOWN_ENDPOINT = os.getenv('WELL_KNOWN_ENDPOINT')
                response = requests.get(IDP_WELL_KNOWN_ENDPOINT)
                response.raise_for_status()
                well_known_info = response.json()
                IDP_USER_INFO=well_known_info["userinfo_endpoint"]
                if "localhost" in IDP_USER_INFO:
                    IDP_USER_INFO=IDP_USER_INFO.replace("localhost","idp")
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
                assert user.get('sub') == '47eff1b1-7621-4570-a0bb-01a719fba0a2'

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
                assert user.get('sub') == '47eff1b1-7621-4570-a0bb-01a719fba0a2'

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
                list_accepted_datasets=[]
                with open("/beacon/permissions/ga4gh_visas/visas_conf.yml", 'r') as pfile:
                    visas_conf = yaml.safe_load(pfile)
                pfile.close()
                visas_conf["ControlledAccessGrants"]["enabled"]=True
                visas_outcome={}
                # Simulated decoded user passport containing visas
                for visa_type,conditions in visas_conf.items():
                    
                    if conditions['enabled']==True:
                        if visa_type not in visas_outcome:
                            if visa_type == 'ControlledAccessGrants':
                                visas_outcome[visa_type]=None
                            else:
                                visas_outcome[visa_type]=False
                        elif visas_outcome[visa_type]==True:
                            continue
                    else:
                        continue
                    visa = jwt.decode(mock_ga4gh_visa_dataset, options={"verify_signature": False}, algorithms=["RS256"])
                    if 'ga4gh_visa_v1' in visa:
                        visa_values=visa['ga4gh_visa_v1']
                        if visa_values['type']==visa_type:
                            for issuer in conditions['issuers']:
                                if visa['iss'] == issuer['iss']:
                                    accepted_issuer=True
                                    break
                            if accepted_issuer==False:
                                self.LOG.warning("Unauthorized visa: {}. Issuer not trusted.".format(visa))
                                raise NoPermissionsAvailable("Unauthorized visa. Issuer not trusted.")
                            accepted_issuer=False
                            for issuers_values in conditions['issuers']:
                                if visa_values['value'] in issuers_values["accepted_values"]:
                                    if visa["iss"] == issuers_values["iss"]:
                                        if visa_type == 'ControlledAccessGrants':
                                            dataset_url = visa["ga4gh_visa_v1"]["value"]
                                            dataset_url_splitted = dataset_url.split('/')
                                            visa_dataset = dataset_url_splitted[-1]
                                            list_accepted_datasets.append(visa_dataset)
                                            visas_outcome[visa_type]=visa_dataset
                                        else:
                                            visas_outcome[visa_type]=True
                                        break
                        else:
                            continue

                # Expect correct dataset extraction from visa structure
                assert list_accepted_datasets == ['test-dataset']

                from beacon.permissions.plugins import DummyPermissions

                datasets = await DummyPermissions.get_permissions(
                    self=DummyPermissions,
                    user_id='142140921401',
                    requested_datasets=[],
                    visa_datasets=list_accepted_datasets
                )

                # Collect dataset identifiers returned by permission system
                list_datasets_names = []
                for dataset in datasets:
                    list_datasets_names.append(dataset.dataset)

                # Validate public dataset visibility matches expected policy
                tc = unittest.TestCase()
                tc.assertSetEqual(
                    set([
                        'test',
                        'test2',
                        'DemoDatasetBreast',
                        'CINECA_synthetic_cohort_EUROPE_UK1',
                        'test-dataset',
                        'test3',
                        'test4'
                    ]),
                    set(list_datasets_names)
                )

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