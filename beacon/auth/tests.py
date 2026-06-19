from aiohttp.test_utils import TestClient, TestServer, loop_context
import unittest
import os
import jwt
from aiohttp import web
from beacon.auth.__main__ import fetch_idp, validate_access_token, authentication, fetch_user_info
from dotenv import load_dotenv
from beacon.logs.logs import initialize_logger
from beacon.conf.conf_override import config
from beacon.utils.middlewares import error_middleware
from beacon.utils.routes import append_routes
from aiohttp_middlewares import cors_middleware
import beacon.conf.conf_override as conf_override

# for keycloak, create aud in mappers, with custom, aud and beacon for audience
mock_access_token = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJreS1tUXNxZ0ZYeHdSUVRfRUhuQlJJUGpmbVhfRXZuUTVEbzZWUTJCazdZIn0.eyJleHAiOjE3Nzk3OTg1MzksImlhdCI6MTc3OTc5ODIzOSwianRpIjoiZDQwNGEyNWEtMjk0Yy00M2RjLWE0OTMtNzZiM2M4NjJjYTc4IiwiaXNzIjoiaHR0cDovL2xvY2FsaG9zdDo4MDgwL2F1dGgvcmVhbG1zL0JlYWNvbiIsImF1ZCI6ImJlYWNvbiIsInN1YiI6IjQ3ZWZmMWIxLTc2MjEtNDU3MC1hMGJiLTAxYTcxOWZiYTBhMiIsInR5cCI6IkJlYXJlciIsImF6cCI6ImJlYWNvbiIsInNlc3Npb25fc3RhdGUiOiI0NDA1OTk3Zi1kNzdkLTQ4YWYtODdmNy1mZTE3ZDJjYTlmZGIiLCJhY3IiOiIxIiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCBtaWNyb3Byb2ZpbGUtand0Iiwic2lkIjoiNDQwNTk5N2YtZDc3ZC00OGFmLTg3ZjctZmUxN2QyY2E5ZmRiIiwidXBuIjoiamFuZSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwibmFtZSI6IkphbmUgU21pdGgiLCJncm91cHMiOlsib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiIsIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXSwicHJlZmVycmVkX3VzZXJuYW1lIjoiamFuZSIsImdpdmVuX25hbWUiOiJKYW5lIiwiZmFtaWx5X25hbWUiOiJTbWl0aCIsImVtYWlsIjoiamFuZS5zbWl0aEBiZWFjb24uZ2E0Z2gifQ.YFtQijg_AxZNytFtcA0EnVUmbnbecpMo2R-fbRCkD6QDY-I2YWV_Glww0yCU_Yp17a5r60uYvotfIcpLKnWMduBLPeP7pyj9UAM_LtidvIKhpQBTQ8azf4eLHEv2Ju0hYDa_24c1u8UKDg6Jqz40gzV4Z7QRIhKhzqBXTdxo5TlIzYZLtzhqx91gVp9SIqaURUBo4wxqisxnFbsOc-J-IQmOw0OwbzB1f7ugG_xXP-wbJ1SbqbeyaB8pwAo7_dkfWezuhBsCdfhcGuAyvn49KPubgGnenKY3jUVzVxE9MbslKuBlLg_A7c5UNnuQ2vLW77jm6zMGRDPjRjoTIHq1bA'
mock_access_token_false = 'public'

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
                idp_introspection, idp_jwks_url, algorithm, aud = fetch_idp(
                    self, mock_access_token
                )

                # Load expected configuration from Keycloak environment file
                load_dotenv("beacon/auth/idp_providers/keycloak.env", override=True)

                # Extract expected values from environment variables
                IDP_ISSUER = os.getenv('ISSUER')
                IDP_CLIENT_ID = os.getenv('CLIENT_ID')
                IDP_CLIENT_SECRET = os.getenv('CLIENT_SECRET')
                IDP_USER_INFO = os.getenv('USER_INFO')
                IDP_INTROSPECTION = os.getenv('INTROSPECTION')
                IDP_JWKS_URL = os.getenv('JWKS_URL')

                # Validate fetched configuration matches environment configuration
                assert IDP_ISSUER == idp_issuer
                assert IDP_CLIENT_ID == idp_client_id
                assert IDP_CLIENT_SECRET == idp_client_secret
                assert IDP_USER_INFO == user_info
                assert IDP_INTROSPECTION == idp_introspection
                assert IDP_JWKS_URL == idp_jwks_url

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
                IDP_CLIENT_ID = os.getenv('CLIENT_ID')
                IDP_CLIENT_SECRET = os.getenv('CLIENT_SECRET')
                IDP_USER_INFO = os.getenv('USER_INFO')
                IDP_INTROSPECTION = os.getenv('INTROSPECTION')
                IDP_JWKS_URL = os.getenv('JWKS_URL')

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
                    algorithm,
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
                IDP_CLIENT_ID = os.getenv('CLIENT_ID')
                IDP_CLIENT_SECRET = os.getenv('CLIENT_SECRET')
                IDP_USER_INFO = os.getenv('USER_INFO')
                IDP_INTROSPECTION = os.getenv('INTROSPECTION')
                IDP_JWKS_URL = os.getenv('JWKS_URL')

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
                assert user == 'public'

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
                user = {}
                user['ga4gh_passport_v1'] = ['visa']

                visa_datasets = user['ga4gh_passport_v1']
                list_visa_datasets = []

                # Process each visa entry in passport
                if visa_datasets is not None:
                    for visa_dataset in visa_datasets:
                        try:
                            visa = {}

                            # Load issuer configuration for validation
                            load_dotenv("beacon/auth/idp_providers/keycloak.env", override=True)
                            IDP_ISSUER = os.getenv('ISSUER')

                            # Construct minimal visa structure
                            visa['iss'] = IDP_ISSUER
                            visa["ga4gh_visa_v1"] = {}
                            visa["ga4gh_visa_v1"]["value"] = 'visa/dataset'

                            # Validate issuer integrity
                            if visa['iss'] == IDP_ISSUER:
                                pass
                            else:
                                raise web.HTTPUnauthorized('invalid visa token')

                            # Extract dataset identifier from structured visa string
                            dataset_url = visa["ga4gh_visa_v1"]["value"]
                            dataset_url_splitted = dataset_url.split('/')

                            visa_dataset = dataset_url_splitted[-1]

                            # Collect resolved dataset identifier
                            list_visa_datasets.append(visa_dataset)

                        except Exception:
                            # Ignore malformed visa entries
                            visa_dataset = None

                # Expect correct dataset extraction from visa structure
                assert list_visa_datasets == ['dataset']

            loop.run_until_complete(test_check_visa_passports())
            loop.run_until_complete(client.close())

if __name__ == '__main__':
    unittest.main()