from aiohttp.test_utils import TestClient, TestServer, loop_context
import unittest
import os
import jwt
from aiohttp import web
from beacon.auth.__main__ import fetch_idp, validate_access_token, authentication, fetch_user_info
from dotenv import load_dotenv
import re
from beacon.logs.logs import LOG

# for keycloak, create aud in mappers, with custom, aud and beacon for audience
mock_access_token = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJreS1tUXNxZ0ZYeHdSUVRfRUhuQlJJUGpmbVhfRXZuUTVEbzZWUTJCazdZIn0.eyJleHAiOjE3NzAxMTEwNjcsImlhdCI6MTc3MDExMDc2NywianRpIjoiNWFjNWJkZTktZjBmMi00NDc3LWI3NzMtNjk1YzdkMjU4YTYyIiwiaXNzIjoiaHR0cDovL2xvY2FsaG9zdDo4MDgwL2F1dGgvcmVhbG1zL0JlYWNvbiIsImF1ZCI6ImJlYWNvbiIsInN1YiI6IjQ3ZWZmMWIxLTc2MjEtNDU3MC1hMGJiLTAxYTcxOWZiYTBhMiIsInR5cCI6IkJlYXJlciIsImF6cCI6ImJlYWNvbiIsInNlc3Npb25fc3RhdGUiOiI0MzY2OTljYy0xMjAzLTQ2ODMtYjVmNC02N2UxOThkNmExNjUiLCJhY3IiOiIxIiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCBtaWNyb3Byb2ZpbGUtand0Iiwic2lkIjoiNDM2Njk5Y2MtMTIwMy00NjgzLWI1ZjQtNjdlMTk4ZDZhMTY1IiwidXBuIjoiamFuZSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwibmFtZSI6IkphbmUgU21pdGgiLCJncm91cHMiOlsib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiIsIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXSwicHJlZmVycmVkX3VzZXJuYW1lIjoiamFuZSIsImdpdmVuX25hbWUiOiJKYW5lIiwiZmFtaWx5X25hbWUiOiJTbWl0aCIsImVtYWlsIjoiamFuZS5zbWl0aEBiZWFjb24uZ2E0Z2gifQ.Sk9XwP3aPC8WLV_a_-ekJbsNmdN9IIvIPyKaHdb_VwbHO1FtqDmjpSZ80S8jnuZEPkLgiBGMUupJdVAKHlMw77SEWt1ka8KInHJbIY3bMBqxHu13_qzsQnw1_Y-nQbAp5C0Q-Hwr1tFnzjoQho0jVhIvi0b3GdTczzWbVZFgIHX_ESoD8bgKfQQGZChFvPkPycKYFqwmC2-YuMPTgK_iKSWtUqe4WwoL7P1NNgo0yho0HxVymzm2vKDf2bww0-Qa_40IsNJUcFJ5IYBtZ3YUNUE2TeX7S97A7HLN0S-iIg6KY9niOY0mElj_-bcbvNDI3r1Xs0_4VfJ9it72YuJd2A'
mock_access_token_false = 'public'
#dummy test anonymous
#dummy test login
#add test coverage
#audit --> agafar informació molt específica que ens interessa guardar per sempre (de quins individuals ha obtingut resultats positius)

def create_test_app():
    app = web.Application()
    #app.on_startup.append(initialize)
    return app

class TestAuthN(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self._id = 'test'
    def test_auth_fetch_idp(self):
        with loop_context() as loop:
            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_fetch_idp():
                idp_issuer, user_info, idp_client_id, idp_client_secret, idp_introspection, idp_jwks_url, algorithm, aud = fetch_idp(self, mock_access_token)
                load_dotenv("beacon/auth/idp_providers/keycloak.env", override=True)
                IDP_ISSUER = os.getenv('ISSUER')
                IDP_CLIENT_ID = os.getenv('CLIENT_ID')
                IDP_CLIENT_SECRET = os.getenv('CLIENT_SECRET')
                IDP_USER_INFO = os.getenv('USER_INFO')
                IDP_INTROSPECTION = os.getenv('INTROSPECTION')
                IDP_JWKS_URL = os.getenv('JWKS_URL')
                assert IDP_ISSUER == idp_issuer
                assert IDP_CLIENT_ID == idp_client_id
                assert IDP_CLIENT_SECRET == idp_client_secret
                assert IDP_USER_INFO == user_info
                assert IDP_INTROSPECTION == idp_introspection
                assert IDP_JWKS_URL == idp_jwks_url
            loop.run_until_complete(test_fetch_idp())
            loop.run_until_complete(client.close())
    def test_auth_validate_access_token(self):
        with loop_context() as loop:
            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_validate_access_token():
                load_dotenv("beacon/auth/idp_providers/keycloak.env", override=True)
                IDP_ISSUER = os.getenv('ISSUER')
                IDP_CLIENT_ID = os.getenv('CLIENT_ID')
                IDP_CLIENT_SECRET = os.getenv('CLIENT_SECRET')
                IDP_USER_INFO = os.getenv('USER_INFO')
                IDP_INTROSPECTION = os.getenv('INTROSPECTION')
                IDP_JWKS_URL = os.getenv('JWKS_URL')
                try:
                    header = jwt.get_unverified_header(mock_access_token)
                    algorithm=header["alg"]
                    decoded = jwt.decode(mock_access_token, options={"verify_signature": False})
                    issuer = decoded['iss']
                    aud = decoded['aud']
                except Exception:
                    raise web.HTTPUnauthorized()
                access_token_validation = validate_access_token(self, mock_access_token, IDP_ISSUER, IDP_JWKS_URL, algorithm, aud)
                assert access_token_validation == True
            loop.run_until_complete(test_validate_access_token())
            loop.run_until_complete(client.close())
    def test_auth_fetch_user_info(self):
        with loop_context() as loop:
            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_fetch_user_info():
                load_dotenv("beacon/auth/idp_providers/keycloak.env", override=True)
                IDP_ISSUER = os.getenv('ISSUER')
                IDP_CLIENT_ID = os.getenv('CLIENT_ID')
                IDP_CLIENT_SECRET = os.getenv('CLIENT_SECRET')
                IDP_USER_INFO = os.getenv('USER_INFO')
                IDP_INTROSPECTION = os.getenv('INTROSPECTION')
                IDP_JWKS_URL = os.getenv('JWKS_URL')
                list_visa_datasets=[]
                user, list_visa_datasets = await fetch_user_info(self, mock_access_token, IDP_USER_INFO, IDP_ISSUER, list_visa_datasets)
                assert user.get('email') == 'jane.smith@beacon.ga4gh'
            loop.run_until_complete(test_fetch_user_info())
            loop.run_until_complete(client.close())
    def test_auth_authentication(self):
        with loop_context() as loop:
            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_authentication():
                user, list_visa_datasets = await authentication(self, mock_access_token)
                assert user.get('email') == 'jane.smith@beacon.ga4gh'
            loop.run_until_complete(test_authentication())
            loop.run_until_complete(client.close())
    def test_auth_authentication_false(self):
        with loop_context() as loop:
            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_authentication_false():
                user, list_visa_datasets = await authentication(self, mock_access_token_false)
                assert user == 'public'
            loop.run_until_complete(test_authentication_false())
            loop.run_until_complete(client.close())
    def test_auth_check_visa_passports(self):
        with loop_context() as loop:
            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_visa_passports():
                user={}
                user['ga4gh_passport_v1']=['visa']
                visa_datasets = user['ga4gh_passport_v1']
                list_visa_datasets=[]
                if visa_datasets is not None:
                    for visa_dataset in visa_datasets:
                        try:
                            visa = {}
                            load_dotenv("beacon/auth/idp_providers/keycloak.env", override=True)
                            IDP_ISSUER = os.getenv('ISSUER')
                            visa['iss']=IDP_ISSUER
                            visa["ga4gh_visa_v1"]={}
                            visa["ga4gh_visa_v1"]["value"]='visa/dataset'
                            if visa['iss']==IDP_ISSUER:
                                pass
                            else:
                                raise web.HTTPUnauthorized('invalid visa token')
                            dataset_url = visa["ga4gh_visa_v1"]["value"]
                            dataset_url_splitted = dataset_url.split('/')
                            visa_dataset = dataset_url_splitted[-1]
                            list_visa_datasets.append(visa_dataset)
                        except Exception:
                            visa_dataset = None
                assert list_visa_datasets == ['dataset']
            loop.run_until_complete(test_check_visa_passports())
            loop.run_until_complete(client.close())

if __name__ == '__main__':
    unittest.main()