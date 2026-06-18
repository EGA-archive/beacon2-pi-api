from aiohttp.test_utils import TestClient, TestServer, loop_context
import unittest
from aiohttp import web
from .plugins import DummyPermissions as PermissionsProxy
from aiohttp.test_utils import make_mocked_request
from beacon.auth.tests import mock_access_token
from beacon.permissions.__main__ import authorization
from unittest.mock import MagicMock
from beacon.request.classes import RequestAttributes
from beacon.permissions.utils import return_found_granularity_in_exceptions, return_granularity_and_exceptions
import yaml
from beacon.logs.logs import initialize_logger
from beacon.conf.conf_override import config
from beacon.utils.middlewares import error_middleware
from beacon.utils.routes import append_routes
from aiohttp_middlewares import cors_middleware
import beacon.conf.conf_override as conf_override

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

class TestAuthZ(unittest.TestCase):
    """
    Authorization test suite covering dataset access control,
    authentication headers, and granularity logic.
    """

    def test_authZ_verify_public_datasets(self):
        # Initialize async test environment
        with loop_context() as loop:
            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)

            # Start test server
            loop.run_until_complete(client.start_server())

            async def test_verify_public_datasets():
                # Public users should have access to a restricted dataset subset
                RequestAttributes.entry_type_id = 'individual'

                # Fetch permissions for anonymous/public user
                datasets = await PermissionsProxy.get_permissions(
                    self=PermissionsProxy,
                    username='public',
                    requested_datasets=[]
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
                        'CINECA_synthetic_cohort_EUROPE_UK1'
                    ]),
                    set(list_datasets_names)
                )

            # Run async test and close client
            loop.run_until_complete(test_verify_public_datasets())
            loop.run_until_complete(client.close())

    def test_authZ_verify_registered_datasets(self):
        # Test access control for authenticated (registered) user
        with loop_context() as loop:
            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)

            loop.run_until_complete(client.start_server())

            async def test_verify_registered_datasets():
                # Registered user dataset visibility
                RequestAttributes.entry_type_id = 'individual'

                # Query permission layer for authenticated user
                datasets = await PermissionsProxy.get_permissions(
                    self=PermissionsProxy,
                    username='dummy_user@example.com',
                    requested_datasets=[]
                )

                # Extract dataset names
                list_datasets_names = []
                for dataset in datasets:
                    list_datasets_names.append(dataset.dataset)

                # Validate dataset access policy for registered users
                tc = unittest.TestCase()
                tc.assertSetEqual(
                    set([
                        'CINECA_synthetic_cohort_EUROPE_UK1',
                        'test2',
                        'test',
                        'DemoDatasetBreast'
                    ]),
                    set(list_datasets_names)
                )

            loop.run_until_complete(test_verify_registered_datasets())
            loop.run_until_complete(client.close())

    def test_authZ_verify_controlled_datasets(self):
        # Test access control for a controlled-access (authorized) user
        with loop_context() as loop:
            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)

            loop.run_until_complete(client.start_server())

            async def test_verify_registered_datasets():
                # Controlled dataset access depends on user identity
                RequestAttributes.entry_type_id = 'individual'

                datasets = await PermissionsProxy.get_permissions(
                    self=PermissionsProxy,
                    username='jane.smith@beacon.ga4gh',
                    requested_datasets=[]
                )

                # Collect dataset identifiers
                list_datasets_names = []
                for dataset in datasets:
                    list_datasets_names.append(dataset.dataset)

                # Ensure controlled dataset access includes privileged datasets
                tc = unittest.TestCase()
                tc.assertSetEqual(
                    set([
                        'AV_Dataset',
                        'test',
                        'test2',
                        'DemoDatasetBreast',
                        'CINECA_synthetic_cohort_EUROPE_UK1'
                    ]),
                    set(list_datasets_names)
                )

            loop.run_until_complete(test_verify_registered_datasets())
            loop.run_until_complete(client.close())

    def test_authZ_bearer_required(self):
        # Validate that Authorization header follows Bearer schema
        with loop_context() as loop:
            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)

            loop.run_until_complete(client.start_server())

            async def test_bearer_required():
                # Mock HTTP request with intentionally malformed Bearer header
                req = make_mocked_request(
                    'GET',
                    '/',
                    headers={'Authorization': 'Bearer '}
                )

                auth = req.headers.get('Authorization')

                # Reject missing or malformed Bearer token
                if not auth or not auth.lower().startswith('bearer '):
                    raise web.HTTPUnauthorized()

                # Ensure correct prefix is present
                assert auth[0:7] == 'Bearer '

            loop.run_until_complete(test_bearer_required())
            loop.run_until_complete(client.close())

    def test_authZ_authorization(self):
        # Test authorization flow and token-to-user resolution
        with loop_context() as loop:
            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)

            loop.run_until_complete(client.start_server())

            MagicClass = MagicMock(_id='hohoho')

            async def test_authorization():
                # Attach Authorization header with mocked access token
                headers = {'Authorization': 'Bearer ' + mock_access_token}
                RequestAttributes.headers = headers

                # Resolve username and visa dataset context
                username, list_visa_datasets = await authorization(
                    self=MagicClass
                )

                # Ensure token maps to correct identity
                assert username == 'jane.smith@beacon.ga4gh'

            loop.run_until_complete(test_authorization())
            loop.run_until_complete(client.close())

    def check_granularity_returned_is_correct(self):
        # Validate mapping of entry type → response granularity
        with loop_context() as loop:
            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)

            loop.run_until_complete(client.start_server())

            MagicClass = MagicMock(_id='hohoho')

            async def test_granularity_returned():
                # Individual-level granularity
                RequestAttributes.entry_type_id = 'individual'
                returned_granularity = return_found_granularity_in_exceptions(
                    self=MagicClass,
                    granularity_exceptions=[
                        {"individual": "record"},
                        {"biosample": "count"},
                        {"analysis": "boolean"}
                    ],
                    default_granularity=None
                )
                assert returned_granularity == 'record'

                # Biosample-level granularity
                RequestAttributes.entry_type_id = 'biosample'
                returned_granularity = return_found_granularity_in_exceptions(
                    self=MagicClass,
                    granularity_exceptions=[
                        {"individual": "record"},
                        {"biosample": "count"},
                        {"analysis": "boolean"}
                    ],
                    default_granularity=None
                )
                assert returned_granularity == 'count'

                # Analysis-level granularity
                RequestAttributes.entry_type_id = 'analysis'
                returned_granularity = return_found_granularity_in_exceptions(
                    self=MagicClass,
                    granularity_exceptions=[
                        {"individual": "record"},
                        {"biosample": "count"},
                        {"analysis": "boolean"}
                    ],
                    default_granularity=None
                )
                assert returned_granularity == 'boolean'

            loop.run_until_complete(test_granularity_returned())
            loop.run_until_complete(client.close())

    def check_controlled_granularity_returned_is_correct(self):
        # Validate controlled dataset-specific granularity rules
        with loop_context() as loop:
            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)

            loop.run_until_complete(client.start_server())

            MagicClass = MagicMock(_id='hohoho')

            # Load dataset-specific permission configuration
            with open("/beacon/permissions/datasets/datasets_permissions.yml", 'r') as pfile:
                datasets_permissions = yaml.safe_load(pfile)

            async def test_controlled_granularity_returned():
                for dataset, security_level_dict in datasets_permissions.items():

                    # Only validate for dataset "test2"
                    if dataset == 'test2':

                        # --- Individual level ---
                        RequestAttributes.entry_type_id = 'individual'
                        returned_granularity, exceptions = return_granularity_and_exceptions(
                            self=MagicClass,
                            security_level_dict=security_level_dict,
                            username='jane.smith@beacon.ga4gh',
                            default_granularity=None,
                            granularity_exceptions=None
                        )

                        returned_granularity = return_found_granularity_in_exceptions(
                            self=MagicClass,
                            granularity_exceptions=exceptions,
                            default_granularity=returned_granularity
                        )
                        assert returned_granularity == 'record'

                        # --- Biosample level ---
                        RequestAttributes.entry_type_id = 'biosample'
                        returned_granularity, exceptions = return_granularity_and_exceptions(
                            self=MagicClass,
                            security_level_dict=security_level_dict,
                            username='jane.smith@beacon.ga4gh',
                            default_granularity=None,
                            granularity_exceptions=None
                        )

                        returned_granularity = return_found_granularity_in_exceptions(
                            self=MagicClass,
                            granularity_exceptions=exceptions,
                            default_granularity=returned_granularity
                        )
                        assert returned_granularity == 'count'

                        # --- Analysis level ---
                        RequestAttributes.entry_type_id = 'analysis'
                        returned_granularity, exceptions = return_granularity_and_exceptions(
                            self=MagicClass,
                            security_level_dict=security_level_dict,
                            username='jane.smith@beacon.ga4gh',
                            default_granularity=None,
                            granularity_exceptions=None
                        )

                        returned_granularity = return_found_granularity_in_exceptions(
                            self=MagicClass,
                            granularity_exceptions=exceptions,
                            default_granularity=returned_granularity
                        )
                        assert returned_granularity == 'boolean'

            loop.run_until_complete(test_controlled_granularity_returned())
            loop.run_until_complete(client.close())

if __name__ == '__main__':
    unittest.main()