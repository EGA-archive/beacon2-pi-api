from aiohttp.test_utils import TestClient, TestServer, loop_context
import unittest
import os
import jwt
from aiohttp import web
from beacon.auth.__main__ import fetch_idp, validate_access_token, authentication, fetch_user_info
from dotenv import load_dotenv

# for keycloak, create aud in mappers, with custom, aud and beacon for audience
mock_access_token = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJreS1tUXNxZ0ZYeHdSUVRfRUhuQlJJUGpmbVhfRXZuUTVEbzZWUTJCazdZIn0.eyJleHAiOjE3NTk1MDY1NzEsImlhdCI6MTc1OTUwNjI3MSwianRpIjoiNzliNzkxNGQtMzVjZC00N2QyLWFkZTMtZDYwYjVhNjgzYjI0IiwiaXNzIjoiaHR0cHM6Ly9iZWFjb24tbmV0d29yay1kZW1vMi5lZ2EtYXJjaGl2ZS5vcmcvYXV0aC9yZWFsbXMvQmVhY29uIiwiYXVkIjoiYmVhY29uIiwic3ViIjoiNDdlZmYxYjEtNzYyMS00NTcwLWEwYmItMDFhNzE5ZmJhMGEyIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoiYmVhY29uIiwic2Vzc2lvbl9zdGF0ZSI6IjhiYThhNWQxLTNiNGEtNDI2NS1iMGY4LTYwZjE4NjQ3YTRkYyIsImFjciI6IjEiLCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIG1pY3JvcHJvZmlsZS1qd3QiLCJ1cG4iOiJqYW5lIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJuYW1lIjoiSmFuZSBTbWl0aCIsImdyb3VwcyI6WyJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIiwib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJqYW5lIiwiZ2l2ZW5fbmFtZSI6IkphbmUiLCJmYW1pbHlfbmFtZSI6IlNtaXRoIiwiZW1haWwiOiJqYW5lLnNtaXRoQGJlYWNvbi5nYTRnaCJ9.fJH_eO-cz5lkddjGXlPdaH5hwC0aenFJP8cAOJUGkph019wd8kAahgPJOFqd5JuDszUjCJRjKR3mvr63panNriyUnEANLSAwlPZI5KFkvK7Uk0DAOrXSoe4bjwZ1Snl0Nuluzs59stsly8jz80GPyHaS-Za2l73_pNcYQFlSd7doQ0e9FXnuNp9QW-5mZSQDmM0DZx7QHNLIS7mjAdJ79UY13r8w3p4jeeseBzE3oIkr6SSr58zK37wXS-rDZWXcRBRBUj3R5z1azihfD_9gvP4AADYK8govYoPd8lUcyUt9E1xf2SS8SbEYp6PTAVdgYh8mGdGh8Kw_Xdx9vVc9AA'
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
                load_dotenv("beacon/auth/idp_providers/lifescience.env", override=True)
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
                load_dotenv("beacon/auth/idp_providers/lifescience.env", override=True)
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
                load_dotenv("beacon/auth/idp_providers/lifescience.env", override=True)
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
                            load_dotenv("beacon/auth/idp_providers/lifescience.env", override=True)
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