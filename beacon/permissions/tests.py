from aiohttp.test_utils import TestClient, TestServer, loop_context
import unittest
from aiohttp import web
from aiohttp.web import FileField
from aiohttp.web_request import Request
from .plugins import DummyPermissions as PermissionsProxy
from aiohttp.test_utils import make_mocked_request
from beacon.auth.tests import mock_access_token
from beacon.permissions.__main__ import authorization
from beacon.logs.logs import LOG
from unittest.mock import MagicMock
from beacon.request.classes import RequestAttributes
from beacon.permissions.utils import return_found_granularity_in_permissions

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
                RequestAttributes.entry_type_id='individual'
                datasets = await PermissionsProxy.get_permissions(self=PermissionsProxy, username='public', requested_datasets=[])
                list_datasets_names=[]
                for dataset in datasets:
                    list_datasets_names.append(dataset.dataset)
                tc = unittest.TestCase()
                tc.assertSetEqual(set(['test', 'test2', 'DemoDatasetBreast', 'CINECA_synthetic_cohort_EUROPE_UK1']),set(list_datasets_names))
            loop.run_until_complete(test_verify_public_datasets())
            loop.run_until_complete(client.close())
    def test_authZ_verify_registered_datasets(self):
        with loop_context() as loop:
            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_verify_registered_datasets():
                RequestAttributes.entry_type_id='individual'
                datasets = await PermissionsProxy.get_permissions(self=PermissionsProxy, username='dummy_user@example.com', requested_datasets=[])
                list_datasets_names=[]
                for dataset in datasets:
                    list_datasets_names.append(dataset.dataset)
                tc = unittest.TestCase()
                tc.assertSetEqual(set(['CINECA_synthetic_cohort_EUROPE_UK1', 'test2', 'test', 'DemoDatasetBreast']),set(list_datasets_names))
            loop.run_until_complete(test_verify_registered_datasets())
            loop.run_until_complete(client.close())
    def test_authZ_verify_controlled_datasets(self):
        with loop_context() as loop:
            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_verify_registered_datasets():
                RequestAttributes.entry_type_id='individual'
                datasets = await PermissionsProxy.get_permissions(self=PermissionsProxy, username='jane.smith@beacon.ga4gh', requested_datasets=[])
                list_datasets_names=[]
                for dataset in datasets:
                    list_datasets_names.append(dataset.dataset)
                tc = unittest.TestCase()
                tc.assertSetEqual(set(['AV_Dataset', 'test', 'test2', 'DemoDatasetBreast', 'CINECA_synthetic_cohort_EUROPE_UK1']),set(list_datasets_names))
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
                    raise web.HTTPUnauthorized()
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
                RequestAttributes.headers= headers
                username, list_visa_datasets = await authorization(self=MagicClass)
                assert username == 'jane.smith@beacon.ga4gh'
            loop.run_until_complete(test_authorization())
            loop.run_until_complete(client.close())
    def check_granularity_returned_is_correct(self):
        with loop_context() as loop:
            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            MagicClass = MagicMock(_id='hohoho')
            async def test_granularity_returned():
                RequestAttributes.entry_type_id = 'individual'
                returned_granularity = return_found_granularity_in_permissions(self=MagicClass,granularity_exceptions=[{"individual": "record"},{"biosample": "count"},{"analysis": "boolean"}], default_granularity=None)
                assert returned_granularity == 'record'
                RequestAttributes.entry_type_id = 'biosample'
                returned_granularity = return_found_granularity_in_permissions(self=MagicClass,granularity_exceptions=[{"individual": "record"},{"biosample": "count"},{"analysis": "boolean"}], default_granularity=None)
                assert returned_granularity == 'count'
                RequestAttributes.entry_type_id = 'analysis'
                returned_granularity = return_found_granularity_in_permissions(self=MagicClass,granularity_exceptions=[{"individual": "record"},{"biosample": "count"},{"analysis": "boolean"}], default_granularity=None)
                assert returned_granularity == 'boolean'
            loop.run_until_complete(test_granularity_returned())
            loop.run_until_complete(client.close())

if __name__ == '__main__':
    unittest.main()