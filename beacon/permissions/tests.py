from aiohttp.test_utils import TestClient, TestServer, loop_context
import unittest
from aiohttp import web
from aiohttp.web import FileField
from aiohttp.web_request import Request
from .plugins import DummyPermissions as PermissionsProxy
from aiohttp.test_utils import make_mocked_request
from beacon.auth.tests import mock_access_token
from beacon.permissions.__main__ import authorization
from unittest.mock import MagicMock

#dummy test anonymous
#dummy test login
#add test coverage
#audit --> agafar informació molt específica que ens interessa guardar per sempre (de quins individuals ha obtingut resultats positius)

def create_test_app():
    app = web.Application()
    #app.on_startup.append(initialize)
    return app

class TestAuthZ(unittest.TestCase):
    def test_authZ_verify_public_datasets(self):
        with loop_context() as loop:
            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_verify_public_datasets():
                datasets = await PermissionsProxy.get(self=PermissionsProxy, username='public', requested_datasets=[])
                tc = unittest.TestCase()
                tc.assertSetEqual(set(['synthetic_usecases_4beacon_testingV3']),set(datasets))
            loop.run_until_complete(test_verify_public_datasets())
            loop.run_until_complete(client.close())
    def test_authZ_verify_registered_datasets(self):
        with loop_context() as loop:
            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_verify_registered_datasets():
                datasets = await PermissionsProxy.get(self=PermissionsProxy, username='dummy_user', requested_datasets=[])
                tc = unittest.TestCase()
                tc.assertSetEqual(set(['CINECA_synthetic_cohort_EUROPE_UK1', 'AV_Dataset', 'synthetic_usecases_4beacon_testingV3']),set(datasets))
            loop.run_until_complete(test_verify_registered_datasets())
            loop.run_until_complete(client.close())
    def test_authZ_bearer_required(self):
        with loop_context() as loop:
            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_bearer_required():
                req = make_mocked_request('GET', '/', headers={'Authorization': 'Bearer '})
                auth = req.headers.get('Authorization')
                if not auth or not auth.lower().startswith('bearer '):
                    raise web.HTTPUnauthorized()# pragma: no cover
                assert auth[0:7] == 'Bearer '
            loop.run_until_complete(test_bearer_required())
            loop.run_until_complete(client.close())
    def test_authZ_authorization(self):
        with loop_context() as loop:
            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            MagicClass = MagicMock(_id='hohoho')
            async def test_authorization():
                headers={'Authorization': 'Bearer ' + mock_access_token}
                req = make_mocked_request('GET', '/', headers=headers)
                username, list_visa_datasets = await authorization(self=MagicClass, request=req, headers=headers)
                assert username == 'jane'
            loop.run_until_complete(test_authorization())
            loop.run_until_complete(client.close())

if __name__ == '__main__':
    unittest.main()# pragma: no cover