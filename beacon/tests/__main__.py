from aiohttp.test_utils import TestClient, TestServer, loop_context
from aiohttp import web
from beacon.utils.middlewares import error_middleware
from beacon.__main__ import create_api
import json
import unittest
import beacon.conf.conf_override as conf_override
from beacon.permissions.tests import TestAuthZ
from beacon.auth.tests import TestAuthN
from aiohttp_middlewares import cors_middleware
from beacon.validator.configuration import check_configuration
import asyncio
from beacon.utils.routes import append_routes
from beacon.models.ga4gh.beacon_v2_default_model.connections.mongo.utils import import_analysis_confile, import_biosample_confile, import_genomicVariant_confile, import_individual_confile, import_run_confile, import_cohort_confile, import_dataset_confile
from beacon.models.EUCAIM.connections.mongo.utils import import_collections_confile, import_patients_confile
from unittest.mock import AsyncMock, patch
import asyncio
from beacon.utils.shutters import _graceful_shutdown, config_watcher, on_startup as on_start
from beacon.logs.logs import initialize_logger
from beacon.conf.conf_override import config
from unittest.mock import Mock
import tempfile
import os
from beacon.exceptions.exceptions import DatabaseIsDown
from beacon.views.health import HealthView

# Keeping the conf files loaded as dictionaries into variables
analysis = import_analysis_confile()
biosample = import_biosample_confile()
cohort = import_cohort_confile()
dataset = import_dataset_confile()
genomicVariant = import_genomicVariant_confile()
run = import_run_confile()
individual = import_individual_confile()
patients = import_patients_confile()
collections = import_collections_confile()

def create_app():
    """Method to mock an aiohttp app creation with the settings needed for testing"""
    LOG = initialize_logger(config.level)
    # Create the aiohttpp app object as if it is the real one
    app = web.Application(
        middlewares=[
            cors_middleware(origins=conf_override.config.cors_urls), error_middleware
        ]
    )
    # Adding variables needed to mock the app for testing
    app['logger'] = LOG
    app['pending_requests'] = set()
    app['shutting_down'] = False
    app['state'] = 'Running - healthy'
    app['exit_fn'] = Mock()
    app = append_routes(app=app)
    return app

class TestMain(unittest.TestCase):
    def test_main_check_slash_endpoint_is_working(self):
        # Create an isolated event loop for this test case
        with loop_context() as loop:
            # Initialize application and test HTTP client/server
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)

            # Start the test server
            loop.run_until_complete(client.start_server())

            async def test_check_slash_endpoint_is_working():
                # Call root "/" (or configured subpath root)
                resp = await client.get(conf_override.config.uri_subpath + "")

                # Basic availability check: endpoint should respond OK
                assert resp.status == 200

            # Run async test logic inside event loop
            loop.run_until_complete(test_check_slash_endpoint_is_working())

            # Cleanly close client/server after test
            loop.run_until_complete(client.close())


    def test_main_check_post_slash_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_post_slash_endpoint_is_working():
                # Validate POST request is also accepted at root endpoint
                resp = await client.post(conf_override.config.uri_subpath + "")
                assert resp.status == 200

            loop.run_until_complete(test_check_post_slash_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_info_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_info_endpoint_is_working():
                # Query service info endpoint
                resp = await client.get(conf_override.config.uri_subpath + "/info")

                # Ensure endpoint responds successfully
                assert resp.status == 200

                # Parse JSON payload
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate top-level structure exists
                self.assertIn("response", responsedict)
                self.assertIn("meta", responsedict)

                # Validate required response metadata fields
                self.assertIn("id", responsedict["response"])
                self.assertIn("name", responsedict["response"])
                self.assertIn("apiVersion", responsedict["response"])
                self.assertIn("environment", responsedict["response"])
                self.assertIn("organization", responsedict["response"])

                # Validate nested organization structure
                self.assertIn("id", responsedict["response"]["organization"])
                self.assertIn("name", responsedict["response"]["organization"])

            loop.run_until_complete(test_check_info_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_post_info_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_post_info_endpoint_is_working():
                # Same endpoint behavior tested using POST method
                resp = await client.post(conf_override.config.uri_subpath + "/info")
                assert resp.status == 200

                # Parse and validate structure consistency
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                self.assertIn("response", responsedict)
                self.assertIn("meta", responsedict)

                self.assertIn("id", responsedict["response"])
                self.assertIn("name", responsedict["response"])
                self.assertIn("apiVersion", responsedict["response"])
                self.assertIn("environment", responsedict["response"])
                self.assertIn("organization", responsedict["response"])

                self.assertIn("id", responsedict["response"]["organization"])
                self.assertIn("name", responsedict["response"]["organization"])

            loop.run_until_complete(test_check_post_info_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_service_info_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_service_info_endpoint_is_working():
                # Service-info endpoint provides static service metadata
                resp = await client.get(conf_override.config.uri_subpath + "/service-info")
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate required service-info fields
                self.assertIn("name", responsedict)
                self.assertIn("type", responsedict)
                self.assertIn("id", responsedict)
                self.assertIn("description", responsedict)
                self.assertIn("organization", responsedict)
                self.assertIn("contactUrl", responsedict)
                self.assertIn("documentationUrl", responsedict)
                self.assertIn("createdAt", responsedict)
                self.assertIn("environment", responsedict)
                self.assertIn("version", responsedict)

            loop.run_until_complete(test_check_service_info_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_post_service_info_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_post_service_info_endpoint_is_working():
                # POST variant of service-info endpoint
                resp = await client.post(conf_override.config.uri_subpath + "/service-info")
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Ensure identical schema expectations as GET
                self.assertIn("name", responsedict)
                self.assertIn("type", responsedict)
                self.assertIn("id", responsedict)
                self.assertIn("description", responsedict)
                self.assertIn("organization", responsedict)
                self.assertIn("contactUrl", responsedict)
                self.assertIn("documentationUrl", responsedict)
                self.assertIn("createdAt", responsedict)
                self.assertIn("environment", responsedict)
                self.assertIn("version", responsedict)

            loop.run_until_complete(test_check_post_service_info_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_entry_types_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_entry_types_endpoint_is_working():
                # Entry types endpoint exposes supported biological/data entity types
                resp = await client.get(conf_override.config.uri_subpath + "/entry_types")
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate response structure
                self.assertIn("response", responsedict)
                self.assertIn("meta", responsedict)

                entry_types = responsedict["response"]["entryTypes"]

                # Validate expected domain entities exist
                self.assertIn("analysis", entry_types)
                self.assertIn("biosample", entry_types)
                self.assertIn("cohort", entry_types)
                self.assertIn("dataset", entry_types)
                self.assertIn("genomicVariant", entry_types)
                self.assertIn("run", entry_types)
                self.assertIn("individual", entry_types)

            loop.run_until_complete(test_check_entry_types_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_post_entry_types_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_post_entry_types_endpoint_is_working():
                # POST variant should behave identically to GET
                resp = await client.post(conf_override.config.uri_subpath + "/entry_types")
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                self.assertIn("response", responsedict)
                self.assertIn("meta", responsedict)

                entry_types = responsedict["response"]["entryTypes"]

                self.assertIn("analysis", entry_types)
                self.assertIn("biosample", entry_types)
                self.assertIn("cohort", entry_types)
                self.assertIn("dataset", entry_types)
                self.assertIn("genomicVariant", entry_types)
                self.assertIn("run", entry_types)
                self.assertIn("individual", entry_types)

            loop.run_until_complete(test_check_post_entry_types_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_configuration_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_configuration_endpoint_is_working():
                # Configuration endpoint exposes API schema + metadata
                resp = await client.get(conf_override.config.uri_subpath + "/configuration")
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate main response structure
                self.assertIn("response", responsedict)
                self.assertIn("meta", responsedict)

                # Validate configuration schema metadata
                self.assertIn("entryTypes", responsedict["response"])
                self.assertIn("maturityAttributes", responsedict["response"])
                self.assertIn("securityAttributes", responsedict["response"])
                self.assertIn("$schema", responsedict["response"])

                # Validate meta information completeness
                self.assertIn("apiVersion", responsedict["meta"])
                self.assertIn("beaconId", responsedict["meta"])
                self.assertIn("returnedSchemas", responsedict["meta"])

                entry_types = responsedict["response"]["entryTypes"]

                # Ensure all expected entry types are supported
                self.assertIn("analysis", entry_types)
                self.assertIn("biosample", entry_types)
                self.assertIn("cohort", entry_types)
                self.assertIn("dataset", entry_types)
                self.assertIn("genomicVariant", entry_types)
                self.assertIn("run", entry_types)
                self.assertIn("individual", entry_types)

            loop.run_until_complete(test_check_configuration_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_post_configuration_endpoint_is_working(self):
        with loop_context() as loop:
            # Create application instance and attach async test client
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)

            # Start HTTP test server
            loop.run_until_complete(client.start_server())

            async def test_check_post_configuration_endpoint_is_working():
                # POST request to configuration endpoint (mirrors GET behavior)
                resp = await client.post(conf_override.config.uri_subpath + "/configuration")
                assert resp.status == 200

                # Parse JSON response
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate core response structure exists
                self.assertIn("response", responsedict)
                self.assertIn("meta", responsedict)

                # Validate configuration schema components
                self.assertIn("entryTypes", responsedict["response"])
                self.assertIn("maturityAttributes", responsedict["response"])
                self.assertIn("securityAttributes", responsedict["response"])
                self.assertIn("$schema", responsedict["response"])

                # Validate metadata completeness
                self.assertIn("apiVersion", responsedict["meta"])
                self.assertIn("beaconId", responsedict["meta"])
                self.assertIn("returnedSchemas", responsedict["meta"])

                # Validate supported biological entry types
                self.assertIn("analysis", responsedict["response"]["entryTypes"])
                self.assertIn("biosample", responsedict["response"]["entryTypes"])
                self.assertIn("cohort", responsedict["response"]["entryTypes"])
                self.assertIn("dataset", responsedict["response"]["entryTypes"])
                self.assertIn("genomicVariant", responsedict["response"]["entryTypes"])
                self.assertIn("run", responsedict["response"]["entryTypes"])
                self.assertIn("individual", responsedict["response"]["entryTypes"])

            # Execute async test inside event loop
            loop.run_until_complete(test_check_post_configuration_endpoint_is_working())

            # Clean shutdown of test client
            loop.run_until_complete(client.close())


    def test_main_check_map_endpoint_is_working(self):
        with loop_context() as loop:
            # Setup app + test server
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_map_endpoint_is_working():
                # Map endpoint exposes available endpoint sets in the API
                resp = await client.get(conf_override.config.uri_subpath + "/map")
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate metadata consistency
                self.assertIn("apiVersion", responsedict["meta"])
                self.assertIn("beaconId", responsedict["meta"])
                self.assertIn("returnedSchemas", responsedict["meta"])

                # Validate endpoint set mapping for each entity type
                self.assertIn("analysis", responsedict["response"]["endpointSets"])
                self.assertIn("biosample", responsedict["response"]["endpointSets"])
                self.assertIn("cohort", responsedict["response"]["endpointSets"])
                self.assertIn("dataset", responsedict["response"]["endpointSets"])
                self.assertIn("genomicVariant", responsedict["response"]["endpointSets"])
                self.assertIn("run", responsedict["response"]["endpointSets"])
                self.assertIn("individual", responsedict["response"]["endpointSets"])

            loop.run_until_complete(test_check_map_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_post_map_endpoint_is_working(self):
        with loop_context() as loop:
            # Initialize test environment
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_post_map_endpoint_is_working():
                # POST variant of /map endpoint (should match GET behavior)
                resp = await client.post(conf_override.config.uri_subpath + "/map")
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate shared metadata fields
                self.assertIn("apiVersion", responsedict["meta"])
                self.assertIn("beaconId", responsedict["meta"])
                self.assertIn("returnedSchemas", responsedict["meta"])

                # Validate endpoint mapping consistency
                self.assertIn("analysis", responsedict["response"]["endpointSets"])
                self.assertIn("biosample", responsedict["response"]["endpointSets"])
                self.assertIn("cohort", responsedict["response"]["endpointSets"])
                self.assertIn("dataset", responsedict["response"]["endpointSets"])
                self.assertIn("genomicVariant", responsedict["response"]["endpointSets"])
                self.assertIn("run", responsedict["response"]["endpointSets"])
                self.assertIn("individual", responsedict["response"]["endpointSets"])

            loop.run_until_complete(test_check_post_map_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_filtering_terms_endpoint_is_working(self):
        with loop_context() as loop:
            # Setup server and client
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_filtering_terms_endpoint_is_working():
                # Filtering terms endpoint provides allowed query filters
                resp = await client.get(conf_override.config.uri_subpath + "/filtering_terms")
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate metadata section
                self.assertIn("apiVersion", responsedict["meta"])
                self.assertIn("beaconId", responsedict["meta"])
                self.assertIn("returnedSchemas", responsedict["meta"])

                # Validate filtering configuration payload
                self.assertIn("filteringTerms", responsedict["response"])
                self.assertIn("resources", responsedict["response"])

            loop.run_until_complete(test_check_filtering_terms_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_post_filtering_terms_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_post_filtering_terms_endpoint_is_working():
                # POST variant of filtering terms endpoint
                resp = await client.post(conf_override.config.uri_subpath + "/filtering_terms")
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Same structure expected for POST
                self.assertIn("apiVersion", responsedict["meta"])
                self.assertIn("beaconId", responsedict["meta"])
                self.assertIn("returnedSchemas", responsedict["meta"])
                self.assertIn("filteringTerms", responsedict["response"])
                self.assertIn("resources", responsedict["response"])

            loop.run_until_complete(test_check_post_filtering_terms_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_datasets_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_datasets_endpoint_is_working():
                # Dynamic dataset endpoint name + testMode flag
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    dataset["dataset"]["endpoint_name"] + "?testMode=true"
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate metadata for dataset query
                self.assertIn("apiVersion", responsedict["meta"])
                self.assertIn("beaconId", responsedict["meta"])
                self.assertIn("returnedSchemas", responsedict["meta"])
                self.assertIn("receivedRequestSummary", responsedict["meta"])
                self.assertIn("returnedGranularity", responsedict["meta"])
                self.assertIn("testMode", responsedict["meta"])

                # Validate response payload
                self.assertIn("collections", responsedict["response"])
                self.assertIn("responseSummary", responsedict)

                # Ensure dataset existence flag is correctly set
                assert responsedict["responseSummary"]["exists"] is True

            loop.run_until_complete(test_check_datasets_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_post_datasets_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_post_datasets_endpoint_is_working():
                # POST variant of dataset endpoint
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    dataset["dataset"]["endpoint_name"]
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate dataset response metadata
                self.assertIn("apiVersion", responsedict["meta"])
                self.assertIn("beaconId", responsedict["meta"])
                self.assertIn("returnedSchemas", responsedict["meta"])
                self.assertIn("receivedRequestSummary", responsedict["meta"])
                self.assertIn("returnedGranularity", responsedict["meta"])
                self.assertIn("testMode", responsedict["meta"])

                # Validate dataset payload
                self.assertIn("collections", responsedict["response"])
                self.assertIn("responseSummary", responsedict)

                assert responsedict["responseSummary"]["exists"] is True

            loop.run_until_complete(test_check_post_datasets_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_datasets_endpoint_with_count_granularity_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_datasets_endpoint_count_is_working():
                # Request dataset with count granularity
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    dataset["dataset"]["endpoint_name"] +
                    "?testMode=true&requestedGranularity=count"
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate metadata consistency
                self.assertIn("returnedGranularity", responsedict["meta"])

                # Count mode should include totals but not full collections
                self.assertNotIn("collections", responsedict)

                # Ensure numeric summary is present
                self.assertIn("numTotalResults", responsedict["responseSummary"])

                assert responsedict["responseSummary"]["exists"] is True

            loop.run_until_complete(test_check_datasets_endpoint_count_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_datasets_endpoint_with_boolean_granularity_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_datasets_endpoint_boolean_is_working():
                # Boolean granularity only checks existence (no counts)
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    dataset["dataset"]["endpoint_name"] +
                    "?testMode=true&requestedGranularity=boolean"
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate structure for boolean response
                self.assertIn("returnedGranularity", responsedict["meta"])
                self.assertNotIn("collections", responsedict)

                # Boolean mode should NOT include counts
                self.assertNotIn("numTotalResults", responsedict["responseSummary"])

                assert responsedict["responseSummary"]["exists"] is True

            loop.run_until_complete(test_check_datasets_endpoint_boolean_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_g_variants_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_g_variants_endpoint_is_working():
                # Genomic variants endpoint (dynamic endpoint name)
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"]
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate metadata completeness
                self.assertIn("apiVersion", responsedict["meta"])
                self.assertIn("beaconId", responsedict["meta"])
                self.assertIn("returnedSchemas", responsedict["meta"])
                self.assertIn("receivedRequestSummary", responsedict["meta"])
                self.assertIn("returnedGranularity", responsedict["meta"])
                self.assertIn("testMode", responsedict["meta"])

                # Validate response structure for genomic results
                self.assertIn("resultSets", responsedict["response"])
                self.assertIn("responseSummary", responsedict)

                # Ensure dataset actually reports existence
                assert responsedict["responseSummary"]["exists"] is True

            loop.run_until_complete(test_check_g_variants_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_analyses_with_limit_endpoint_is_working(self):
        with loop_context() as loop:
            # Initialize app + async test server
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_analyses_with_limit_endpoint_is_working():
                # Query analyses endpoint with pagination + record-level granularity
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    analysis["analysis"]["endpoint_name"] +
                    "?limit=200&skip=0&requestedGranularity=record"
                )
                assert resp.status == 200

                # Parse JSON response payload
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate standard API metadata contract
                self.assertIn("apiVersion", responsedict["meta"])
                self.assertIn("beaconId", responsedict["meta"])
                self.assertIn("returnedSchemas", responsedict["meta"])
                self.assertIn("receivedRequestSummary", responsedict["meta"])
                self.assertIn("returnedGranularity", responsedict["meta"])
                self.assertIn("testMode", responsedict["meta"])

                # Validate response structure for record-level query
                self.assertIn("resultSets", responsedict["response"])
                self.assertIn("responseSummary", responsedict)

                # Ensure dataset exists in system
                assert responsedict["responseSummary"]["exists"] is True

            loop.run_until_complete(test_check_analyses_with_limit_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_analyses_endpoint_is_working(self):
        with loop_context() as loop:
            # Standard analyses endpoint (no filters)
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_analyses_endpoint_is_working():
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    analysis["analysis"]["endpoint_name"]
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate API contract consistency
                self.assertIn("apiVersion", responsedict["meta"])
                self.assertIn("beaconId", responsedict["meta"])
                self.assertIn("returnedSchemas", responsedict["meta"])
                self.assertIn("receivedRequestSummary", responsedict["meta"])
                self.assertIn("returnedGranularity", responsedict["meta"])
                self.assertIn("testMode", responsedict["meta"])

                # Validate response container
                self.assertIn("resultSets", responsedict["response"])
                self.assertIn("responseSummary", responsedict)

                assert responsedict["responseSummary"]["exists"] is True

            loop.run_until_complete(test_check_analyses_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_analyses_with_id_endpoint_is_working(self):
        with loop_context() as loop:
            # Query a specific analysis by ID
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_analyses_with_id_endpoint_is_working():
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    analysis["analysis"]["endpoint_name"] +
                    "/EGA-testing"
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Specific ID should return exactly one matching result
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_analyses_with_id_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_analyses_g_variants_endpoint_is_working(self):
        with loop_context() as loop:
            # Test analysis filtered by genomic variants
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_analyses_g_variants_endpoint_is_working():
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    analysis["analysis"]["endpoint_name"] +
                    "/EGA-testing/" +
                    genomicVariant["genomicVariant"]["endpoint_name"]
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect multiple matches for variant-linked analyses
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 10

            loop.run_until_complete(test_check_analyses_g_variants_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_analyses_runs_endpoint_is_working(self):
        with loop_context() as loop:
            # Test analysis filtered by sequencing run
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_analyses_runs_endpoint_is_working():
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    analysis["analysis"]["endpoint_name"] +
                    "/EGA-testing/" +
                    run["run"]["endpoint_name"]
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect single matching result for run association
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_analyses_runs_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_analyses_individuals_endpoint_is_working(self):
        with loop_context() as loop:
            # Test analysis filtered by individual subject
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_analyses_individuals_endpoint_is_working():
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    analysis["analysis"]["endpoint_name"] +
                    "/EGA-testing/" +
                    individual["individual"]["endpoint_name"]
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Ensure correct linkage between analysis and individual
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_analyses_individuals_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_analyses_datasets_endpoint_is_working(self):
        with loop_context() as loop:
            # Test analysis filtered by dataset association
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_analyses_individuals_endpoint_is_working():
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    analysis["analysis"]["endpoint_name"] +
                    "/EGA-testing/" +
                    dataset["dataset"]["endpoint_name"]
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Ensure dataset linkage is valid
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_analyses_individuals_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_analyses_cohorts_endpoint_is_working(self):
        with loop_context() as loop:
            # Test analysis filtered by cohort association
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_analyses_individuals_endpoint_is_working():
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    analysis["analysis"]["endpoint_name"] +
                    "/EGA-testing/" +
                    cohort["cohort"]["endpoint_name"]
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Cohort linkage should return single expected match
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_analyses_individuals_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_analyses_biosamples_endpoint_is_working(self):
        with loop_context() as loop:
            # Test analysis filtered by biosample association
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_analyses_biosmples_endpoint_is_working():
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    analysis["analysis"]["endpoint_name"] +
                    "/EGA-testing/" +
                    biosample["biosample"]["endpoint_name"]
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Biosample association validation
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_analyses_biosmples_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_biosamples_endpoint_is_working(self):
        with loop_context() as loop:
            # Basic biosamples listing endpoint
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_biosamples_endpoint_is_working():
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    biosample["biosample"]["endpoint_name"]
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Standard API response validation
                self.assertIn("apiVersion", responsedict["meta"])
                self.assertIn("beaconId", responsedict["meta"])
                self.assertIn("returnedSchemas", responsedict["meta"])
                self.assertIn("receivedRequestSummary", responsedict["meta"])
                self.assertIn("returnedGranularity", responsedict["meta"])
                self.assertIn("testMode", responsedict["meta"])

                self.assertIn("resultSets", responsedict["response"])
                self.assertIn("responseSummary", responsedict)

                assert responsedict["responseSummary"]["exists"] is True

            loop.run_until_complete(test_check_biosamples_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_biosamples_with_limit_endpoint_is_working(self):
        with loop_context() as loop:
            # Biosample endpoint with pagination limit
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_biosamples_with_limit_endpoint_is_working():
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    biosample["biosample"]["endpoint_name"] + "?limit=200"
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate paginated response structure
                self.assertIn("apiVersion", responsedict["meta"])
                self.assertIn("beaconId", responsedict["meta"])
                self.assertIn("returnedSchemas", responsedict["meta"])
                self.assertIn("receivedRequestSummary", responsedict["meta"])
                self.assertIn("returnedGranularity", responsedict["meta"])
                self.assertIn("testMode", responsedict["meta"])

                self.assertIn("resultSets", responsedict["response"])
                self.assertIn("responseSummary", responsedict)

                assert responsedict["responseSummary"]["exists"] is True

            loop.run_until_complete(test_check_biosamples_with_limit_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_biosamples_with_id_endpoint_is_working(self):
        with loop_context() as loop:
            # Biosample lookup by specific ID
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_biosamples_with_id_endpoint_is_working():
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    biosample["biosample"]["endpoint_name"] + "/SAMPLE3"
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # ID lookup should return exactly one match
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_biosamples_with_id_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_biosamples_g_variants_endpoint_is_working(self):
        with loop_context() as loop:
            # Setup application and async test client
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)

            # Start test server before making requests
            loop.run_until_complete(client.start_server())

            async def test_check_biosamples_g_variants_endpoint_is_working():
                # Query biosamples filtered by genomic variants
                # URL pattern: /biosamples/{id}/{genomicVariant}
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    biosample["biosample"]["endpoint_name"] +
                    "/SAMPLE3/" +
                    genomicVariant["genomicVariant"]["endpoint_name"]
                )
                assert resp.status == 200

                # Parse response payload
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Verify existence of matching records and expected cardinality
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 10

            loop.run_until_complete(test_check_biosamples_g_variants_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_biosamples_runs_endpoint_is_working(self):
        with loop_context() as loop:
            # Biosample filtered by sequencing run association
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_biosamples_runs_endpoint_is_working():
                # /biosamples/{id}/runs endpoint test
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    biosample["biosample"]["endpoint_name"] +
                    "/SAMPLE1/" +
                    run["run"]["endpoint_name"]
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect single biosample-run relationship match
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_biosamples_runs_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_biosamples_datasets_endpoint_is_working(self):
        with loop_context() as loop:
            # Biosample filtered by dataset linkage
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_biosamples_runs_endpoint_is_working():
                # NOTE: dataset association endpoint tested here
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    biosample["biosample"]["endpoint_name"] +
                    "/SAMPLE1/" +
                    dataset["dataset"]["endpoint_name"]
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate dataset-biosample relationship exists
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_biosamples_runs_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_biosamples_cohorts_endpoint_is_working(self):
        with loop_context() as loop:
            # Biosample filtered by cohort membership
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_biosamples_runs_endpoint_is_working():
                # Cohort filtering applied to biosample endpoint
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    biosample["biosample"]["endpoint_name"] +
                    "/SAMPLE1/" +
                    cohort["cohort"]["endpoint_name"]
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Ensure biosample belongs to expected cohort
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_biosamples_runs_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_biosamples_analyses_endpoint_is_working(self):
        with loop_context() as loop:
            # Biosample linked to analysis results
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_biosamples_analyses_endpoint_is_working():
                # /biosamples/{id}/analyses relationship query
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    biosample["biosample"]["endpoint_name"] +
                    "/SAMPLE1/" +
                    analysis["analysis"]["endpoint_name"]
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate analysis linkage correctness
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_biosamples_analyses_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_individuals_endpoint_is_working(self):
        with loop_context() as loop:
            # Individual endpoint with test mode enabled
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_individuals_endpoint_is_working():
                # testMode ensures deterministic or mocked response behavior
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    individual["individual"]["endpoint_name"] +
                    "?testMode=true"
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                from beacon.utils.handovers import handover_1

                # Validate external handover links returned by API
                assert responsedict["response"]["resultSets"][0]["resultsHandovers"] == [handover_1]

            loop.run_until_complete(test_check_individuals_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_individuals_with_limit_endpoint_is_working(self):
        with loop_context() as loop:
            # Individuals endpoint with pagination limit
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_individuals_with_limit_endpoint_is_working():
                # Limit controls number of returned individuals
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    individual["individual"]["endpoint_name"] +
                    "?limit=200"
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Standard API contract validation
                self.assertIn("apiVersion", responsedict["meta"])
                self.assertIn("beaconId", responsedict["meta"])
                self.assertIn("returnedSchemas", responsedict["meta"])
                self.assertIn("receivedRequestSummary", responsedict["meta"])
                self.assertIn("returnedGranularity", responsedict["meta"])
                self.assertIn("testMode", responsedict["meta"])

                self.assertIn("resultSets", responsedict["response"])
                self.assertIn("responseSummary", responsedict)

                assert responsedict["responseSummary"]["exists"] is True

            loop.run_until_complete(test_check_individuals_with_limit_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_individuals_with_id_endpoint_is_working(self):
        with loop_context() as loop:
            # Direct lookup of individual by identifier
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_individuals_with_id_endpoint_is_working():
                # ID-based lookup should return single deterministic result
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    individual["individual"]["endpoint_name"] +
                    "/SAMPLE2"
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Ensure uniqueness of returned entity
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_individuals_with_id_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_individuals_g_variants_endpoint_is_working(self):
        with loop_context() as loop:
            # Individuals filtered by genomic variants
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_individuals_g_variants_endpoint_is_working():
                # Variant-linked individuals query
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    individual["individual"]["endpoint_name"] +
                    "/SAMPLE2/" +
                    genomicVariant["genomicVariant"]["endpoint_name"]
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect multiple matches for variant association
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 10

            loop.run_until_complete(test_check_individuals_g_variants_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_individuals_biosamples_endpoint_is_working(self):
        with loop_context() as loop:
            # Individuals filtered by biosample linkage
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_individuals_biosamples_endpoint_is_working():
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    individual["individual"]["endpoint_name"] +
                    "/SAMPLE2/" +
                    biosample["biosample"]["endpoint_name"]
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate biosample-individual relationship
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_individuals_biosamples_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_individuals_datasets_endpoint_is_working(self):
        with loop_context() as loop:
            # Individuals filtered by dataset association
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_individuals_biosamples_endpoint_is_working():
                # Dataset linkage for individual
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    individual["individual"]["endpoint_name"] +
                    "/SAMPLE2/" +
                    dataset["dataset"]["endpoint_name"]
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Ensure dataset association is correct
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_individuals_biosamples_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_individuals_cohorts_endpoint_is_working(self):
        with loop_context() as loop:
            # Individuals filtered by cohort membership
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_individuals_biosamples_endpoint_is_working():
                # Cohort relationship validation
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    individual["individual"]["endpoint_name"] +
                    "/SAMPLE2/" +
                    cohort["cohort"]["endpoint_name"]
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Cohort membership correctness check
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_individuals_biosamples_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_runs_endpoint_is_working(self):
        with loop_context() as loop:
            # Base runs endpoint (no filters)
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_runs_endpoint_is_working():
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    run["run"]["endpoint_name"]
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Standard API structure validation for runs
                self.assertIn("apiVersion", responsedict["meta"])
                self.assertIn("beaconId", responsedict["meta"])
                self.assertIn("returnedSchemas", responsedict["meta"])
                self.assertIn("receivedRequestSummary", responsedict["meta"])
                self.assertIn("returnedGranularity", responsedict["meta"])
                self.assertIn("testMode", responsedict["meta"])

                self.assertIn("resultSets", responsedict["response"])
                self.assertIn("responseSummary", responsedict)

                # Ensure data existence flag is set correctly
                assert responsedict["responseSummary"]["exists"] is True

            loop.run_until_complete(test_check_runs_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_runs_with_limit_endpoint_is_working(self):
        with loop_context() as loop:
            # Setup application and async test client
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)

            # Start test server before sending requests
            loop.run_until_complete(client.start_server())

            async def test_check_runs_with_limit_endpoint_is_working():
                # Query runs endpoint with pagination (limit=200)
                # This verifies that the API correctly supports bounded result sets
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    run["run"]["endpoint_name"] +
                    "?limit=200"
                )
                assert resp.status == 200

                # Parse JSON response
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate API contract metadata for paginated response
                self.assertIn("apiVersion", responsedict["meta"])
                self.assertIn("beaconId", responsedict["meta"])
                self.assertIn("returnedSchemas", responsedict["meta"])
                self.assertIn("receivedRequestSummary", responsedict["meta"])
                self.assertIn("returnedGranularity", responsedict["meta"])
                self.assertIn("testMode", responsedict["meta"])

                # Ensure response structure includes expected payload containers
                self.assertIn("resultSets", responsedict["response"])
                self.assertIn("responseSummary", responsedict)

                # Confirm that at least one result exists for query
                assert responsedict["responseSummary"]["exists"] is True

            loop.run_until_complete(test_check_runs_with_limit_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_runs_with_id_endpoint_is_working(self):
        with loop_context() as loop:
            # Direct lookup of a run by its unique identifier
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)

            loop.run_until_complete(client.start_server())

            async def test_check_runs_with_id_endpoint_is_working():
                # Endpoint: /runs/{run_id}
                # Ensures deterministic lookup of a single run record
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    run["run"]["endpoint_name"] +
                    "/EGA-testing"
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # ID-based query must return exactly one matching run
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_runs_with_id_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_runs_g_variants_endpoint_is_working(self):
        with loop_context() as loop:
            # Runs filtered by genomic variant association
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)

            loop.run_until_complete(client.start_server())

            async def test_check_runs_g_variants_endpoint_is_working():
                # Endpoint pattern: /runs/{run_id}/{genomicVariant}
                # Tests cross-entity filtering between runs and variants
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    run["run"]["endpoint_name"] +
                    "/EGA-testing/" +
                    genomicVariant["genomicVariant"]["endpoint_name"]
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect multiple linked results for variant association
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 10

            loop.run_until_complete(test_check_runs_g_variants_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_runs_analyses_endpoint_is_working(self):
        with loop_context() as loop:
            # Runs filtered by analysis relationship
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)

            loop.run_until_complete(client.start_server())

            async def test_check_runs_analyses_endpoint_is_working():
                # Query: run linked to analysis entity
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    run["run"]["endpoint_name"] +
                    "/EGA-testing/" +
                    analysis["analysis"]["endpoint_name"]
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate one-to-one or single expected linkage
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_runs_analyses_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_runs_datasets_endpoint_is_working(self):
        with loop_context() as loop:
            # Runs filtered by dataset association
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)

            loop.run_until_complete(client.start_server())

            async def test_check_runs_analyses_endpoint_is_working():
                # NOTE: dataset filtering applied to run endpoint
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    run["run"]["endpoint_name"] +
                    "/EGA-testing/" +
                    dataset["dataset"]["endpoint_name"]
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate dataset-run relationship exists
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_runs_analyses_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_runs_cohorts_endpoint_is_working(self):
        with loop_context() as loop:
            # Runs filtered by cohort membership
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)

            loop.run_until_complete(client.start_server())

            async def test_check_runs_analyses_endpoint_is_working():
                # Cohort-based filtering for sequencing runs
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    run["run"]["endpoint_name"] +
                    "/EGA-testing/" +
                    cohort["cohort"]["endpoint_name"]
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Cohort association should yield expected single result
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_runs_analyses_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_runs_biosamples_endpoint_is_working(self):
        with loop_context() as loop:
            # Runs filtered by biosample association
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)

            loop.run_until_complete(client.start_server())

            async def test_check_runs_biosamples_endpoint_is_working():
                # Cross-entity query: run → biosample linkage
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    run["run"]["endpoint_name"] +
                    "/EGA-testing/" +
                    biosample["biosample"]["endpoint_name"]
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate biosample linkage correctness
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_runs_biosamples_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_runs_individuals_endpoint_is_working(self):
        with loop_context() as loop:
            # Runs filtered by individual subject
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)

            loop.run_until_complete(client.start_server())

            async def test_check_runs_individuals_endpoint_is_working():
                # Validate run → individual relationship mapping
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    run["run"]["endpoint_name"] +
                    "/EGA-testing/" +
                    individual["individual"]["endpoint_name"]
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect one linked individual-run association
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_runs_individuals_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_cohorts_endpoint_is_working(self):
        with loop_context() as loop:
            # Base cohorts listing endpoint
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)

            loop.run_until_complete(client.start_server())

            async def test_check_cohorts_endpoint_is_working():
                # Retrieve cohort collection metadata
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    cohort["cohort"]["endpoint_name"]
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Standard API response contract validation
                self.assertIn("apiVersion", responsedict["meta"])
                self.assertIn("beaconId", responsedict["meta"])
                self.assertIn("returnedSchemas", responsedict["meta"])
                self.assertIn("receivedRequestSummary", responsedict["meta"])
                self.assertIn("returnedGranularity", responsedict["meta"])
                self.assertIn("testMode", responsedict["meta"])

                self.assertIn("collections", responsedict["response"])
                self.assertIn("responseSummary", responsedict)

                assert responsedict["responseSummary"]["exists"] is True

            loop.run_until_complete(test_check_cohorts_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_cohorts_endpoint_with_count_granularity_is_working(self):
        with loop_context() as loop:
            # Cohort endpoint tested with count granularity mode
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)

            loop.run_until_complete(client.start_server())

            async def test_check_cohorts_endpoint_count_is_working():
                # NOTE: request currently points to dataset endpoint (likely reused test pattern)
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    dataset["dataset"]["endpoint_name"] +
                    "?testMode=true&requestedGranularity=count"
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate metadata for count-based response
                self.assertIn("apiVersion", responsedict["meta"])
                self.assertIn("beaconId", responsedict["meta"])
                self.assertIn("returnedSchemas", responsedict["meta"])
                self.assertIn("receivedRequestSummary", responsedict["meta"])
                self.assertIn("returnedGranularity", responsedict["meta"])
                self.assertIn("testMode", responsedict["meta"])

                # Count mode should not return full collections
                self.assertNotIn("collections", responsedict)
                self.assertIn("responseSummary", responsedict)

                # Count response must include total results
                self.assertIn("numTotalResults", responsedict["responseSummary"])

                assert responsedict["responseSummary"]["exists"] is True

            loop.run_until_complete(test_check_cohorts_endpoint_count_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_cohorts_endpoint_with_boolean_granularity_is_working(self):
        # Create isolated async event loop context for the test
        with loop_context() as loop:
            # Initialize application under test
            app = create_app()

            # Create async HTTP test client bound to event loop
            client = TestClient(TestServer(app), loop=loop)

            # Start server before making requests
            loop.run_until_complete(client.start_server())

            async def test_check_cohorts_endpoint_boolean_is_working():
                # Request cohort endpoint using BOOLEAN granularity
                # Boolean granularity means only existence info is returned
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    dataset["dataset"]["endpoint_name"] +
                    "?testMode=true&requestedGranularity=boolean"
                )

                # Ensure HTTP request succeeded
                assert resp.status == 200

                # Read response body as text
                responsetext = await resp.text()

                # Parse JSON payload into dictionary
                responsedict = json.loads(responsetext)

                # Validate required API metadata fields are present
                self.assertIn("apiVersion", responsedict["meta"])
                self.assertIn("beaconId", responsedict["meta"])
                self.assertIn("returnedSchemas", responsedict["meta"])
                self.assertIn("receivedRequestSummary", responsedict["meta"])
                self.assertIn("returnedGranularity", responsedict["meta"])
                self.assertIn("testMode", responsedict["meta"])

                # Boolean mode should NOT include full dataset collections
                self.assertNotIn("collections", responsedict)

                # Response must still include summary object
                self.assertIn("responseSummary", responsedict)

                # Boolean granularity should not include numeric result counts
                self.assertNotIn("numTotalResults", responsedict["responseSummary"])

                # Primary contract check: existence flag must be true
                assert responsedict["responseSummary"]["exists"] is True

            # Execute async test function inside event loop
            loop.run_until_complete(test_check_cohorts_endpoint_boolean_is_working())

            # Clean up client and close connections
            loop.run_until_complete(client.close())


    def test_main_check_cohorts_with_limit_endpoint_is_working(self):
        # Test cohort listing endpoint with pagination limit applied
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)

            # Start test server
            loop.run_until_complete(client.start_server())

            async def test_check_cohorts_with_limit_endpoint_is_working():
                # Query cohort endpoint with limit=200 for pagination testing
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    cohort["cohort"]["endpoint_name"] +
                    "?limit=200"
                )

                # Ensure successful response
                assert resp.status == 200

                # Extract response body
                responsetext = await resp.text()

                # Convert JSON response to dict
                responsedict = json.loads(responsetext)

                # Validate API metadata consistency for list response
                self.assertIn("apiVersion", responsedict["meta"])
                self.assertIn("beaconId", responsedict["meta"])
                self.assertIn("returnedSchemas", responsedict["meta"])
                self.assertIn("receivedRequestSummary", responsedict["meta"])
                self.assertIn("returnedGranularity", responsedict["meta"])
                self.assertIn("testMode", responsedict["meta"])

                # Collections must be present in list-style endpoint
                self.assertIn("collections", responsedict["response"])

                # Response summary must always exist
                self.assertIn("responseSummary", responsedict)

                # Existence flag confirms dataset contains cohorts
                assert responsedict["responseSummary"]["exists"] is True

            loop.run_until_complete(test_check_cohorts_with_limit_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_cohorts_with_id_endpoint_is_working(self):
        # Test retrieval of a single cohort by identifier
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)

            loop.run_until_complete(client.start_server())

            async def test_check_cohorts_with_id_endpoint_is_working():
                # Fetch specific cohort using hardcoded test ID
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    cohort["cohort"]["endpoint_name"] +
                    "/EGA-testing"
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # ID-based lookup must return exactly one entity
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_cohorts_with_id_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_cohorts_runs_endpoint_is_working(self):
        # Test cohort filtered by run association
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)

            loop.run_until_complete(client.start_server())

            async def test_check_cohorts_runs_endpoint_is_working():
                # Query cohort-run relationship endpoint
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    cohort["cohort"]["endpoint_name"] +
                    "/EGA-testing/" +
                    run["run"]["endpoint_name"]
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect one linked run for cohort
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_cohorts_runs_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_cohorts_biosamples_endpoint_is_working(self):
        # Test cohort → biosample relationship query
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)

            loop.run_until_complete(client.start_server())

            async def test_check_cohorts_biosamples_endpoint_is_working():
                # Fetch biosamples belonging to cohort
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    cohort["cohort"]["endpoint_name"] +
                    "/EGA-testing/" +
                    biosample["biosample"]["endpoint_name"]
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Cohort is expected to contain multiple biosamples
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 20

            loop.run_until_complete(test_check_cohorts_biosamples_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_cohorts_analyses_endpoint_is_working(self):
        # Test cohort → analysis relationship endpoint
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)

            loop.run_until_complete(client.start_server())

            async def test_check_cohorts_analyses_endpoint_is_working():
                # Retrieve analyses associated with cohort
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    cohort["cohort"]["endpoint_name"] +
                    "/EGA-testing/" +
                    analysis["analysis"]["endpoint_name"]
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect single analysis match
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_cohorts_analyses_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_cohorts_individuals_endpoint_is_working(self):
        # Test cohort → individuals relationship mapping
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)

            loop.run_until_complete(client.start_server())

            async def test_check_cohorts_inividuals_endpoint_is_working():
                # Retrieve individuals belonging to cohort
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    cohort["cohort"]["endpoint_name"] +
                    "/EGA-testing/" +
                    individual["individual"]["endpoint_name"]
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Cohort expected to contain multiple individuals
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 20

            loop.run_until_complete(test_check_cohorts_inividuals_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_cohorts_g_variants_endpoint_is_working(self):
        # Test cohort → genomic variants aggregation endpoint
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)

            loop.run_until_complete(client.start_server())

            async def test_check_cohorts_g_variants_endpoint_is_working():
                # Query variants associated with cohort
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    cohort["cohort"]["endpoint_name"] +
                    "/EGA-testing/" +
                    genomicVariant["genomicVariant"]["endpoint_name"]
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Cohort aggregation returns higher variant count
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 41

            loop.run_until_complete(test_check_cohorts_g_variants_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_datasets_with_id_endpoint_is_working(self):
        with loop_context() as loop:
            # Standard dataset endpoint setup
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)

            # Start server before issuing requests
            loop.run_until_complete(client.start_server())

            async def test_check_datasets_with_id_endpoint_is_working():
                # Request a specific dataset by ID ("test")
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    dataset["dataset"]["endpoint_name"] + "/test"
                )

                assert resp.status == 200

                # Parse JSON response payload
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Ensure dataset exists and only one result is returned
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_datasets_with_id_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_datasets_runs_endpoint_is_working(self):
        with loop_context() as loop:
            # Dataset → run relationship endpoint validation
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)

            loop.run_until_complete(client.start_server())

            async def test_check_datasets_runs_endpoint_is_working():
                # Query runs associated with dataset using nested path
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    dataset["dataset"]["endpoint_name"] + "/test/" +
                    run["run"]["endpoint_name"]
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate dataset-run linkage exists and is singular
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_datasets_runs_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_datasets_g_variants_2_endpoint_is_working(self):
        with loop_context() as loop:
            # Dataset → genomic variants relationship test
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)

            loop.run_until_complete(client.start_server())

            async def test_check_datasets_g_variants_endpoint_is_working():
                # Query variants linked to dataset (nested relationship endpoint)
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    dataset["dataset"]["endpoint_name"] + "/test/" +
                    genomicVariant["genomicVariant"]["endpoint_name"]
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect multiple variant matches in dataset scope
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 41

            loop.run_until_complete(test_check_datasets_g_variants_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_datasets_biosamples_endpoint_is_working(self):
        with loop_context() as loop:
            # Initialize application and async test client
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)

            # Start test server before issuing requests
            loop.run_until_complete(client.start_server())

            async def test_check_datasets_biosamples_endpoint_is_working():
                # Query biosamples linked to a dataset (dataset → biosample relationship)
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    dataset["dataset"]["endpoint_name"] + "/test/" +
                    biosample["biosample"]["endpoint_name"]
                )

                assert resp.status == 200

                # Parse JSON response
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect dataset has multiple biosamples (aggregation-level relationship)
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 20

            loop.run_until_complete(test_check_datasets_biosamples_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_datasets_analyses_endpoint_is_working(self):
        with loop_context() as loop:
            # Dataset → analyses relationship endpoint validation
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)

            loop.run_until_complete(client.start_server())

            async def test_check_datasets_analyses_endpoint_is_working():
                # Query analyses associated with dataset
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    dataset["dataset"]["endpoint_name"] + "/test/" +
                    analysis["analysis"]["endpoint_name"]
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect single linked analysis result
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_datasets_analyses_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_datasets_individuals_endpoint_is_working(self):
        with loop_context() as loop:
            # Dataset → individuals relationship test
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)

            loop.run_until_complete(client.start_server())

            async def test_check_datasets_individuals_endpoint_is_working():
                # Query individuals associated with dataset
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    dataset["dataset"]["endpoint_name"] + "/test/" +
                    individual["individual"]["endpoint_name"]
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect multiple individuals linked to dataset
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 20

            loop.run_until_complete(test_check_datasets_individuals_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_g_variants_with_limit_endpoint_is_working(self):
        with loop_context() as loop:
            # Genomic variants collection endpoint with pagination support
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)

            loop.run_until_complete(client.start_server())

            async def test_check_g_variants_with_limit_endpoint_is_working():
                # Request genomic variants with pagination limit
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] +
                    "?limit=200"
                )

                assert resp.status == 200

            loop.run_until_complete(test_check_g_variants_with_limit_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_g_variants_with_id_endpoint_is_working(self):
        with loop_context() as loop:
            # Specific genomic variant lookup by hash-like identifier
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)

            loop.run_until_complete(client.start_server())

            async def test_check_g_variants_with_id_endpoint_is_working():
                # Query single genomic variant by unique ID (hash)
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] +
                    "/c4143367c9ecad58cbf87b08c11288149e801a70f71a5e114a8476607fe163a1"
                )

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Ensure only one result is returned for unique variant
                assert responsedict["responseSummary"]["numTotalResults"] == 1
                assert resp.status == 200

            loop.run_until_complete(test_check_g_variants_with_id_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_g_variants_runs_endpoint_is_working(self):
        with loop_context() as loop:
            # Genomic variant → run linkage test
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)

            loop.run_until_complete(client.start_server())

            async def test_check_g_variants_runs_endpoint_is_working():
                # Query runs associated with a genomic variant
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] +
                    "/c4143367c9ecad58cbf87b08c11288149e801a70f71a5e114a8476607fe163a1/" +
                    run["run"]["endpoint_name"]
                )

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                assert responsedict["responseSummary"]["numTotalResults"] == 1
                assert resp.status == 200

            loop.run_until_complete(test_check_g_variants_runs_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_biosamples_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_g_variants_biosamples_endpoint_is_working():
                # Query biosamples linked to a specific genomic variant (reverse lookup relationship)
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] +
                    "/c4143367c9ecad58cbf87b08c11288149e801a70f71a5e114a8476607fe163a1/" +
                    biosample["biosample"]["endpoint_name"]
                )

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect multiple biosamples associated with this variant
                assert responsedict["responseSummary"]["numTotalResults"] == 15
                assert resp.status == 200

            loop.run_until_complete(test_check_g_variants_biosamples_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_analyses_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_g_variants_analyses_endpoint_is_working():
                # Query analyses linked to a specific genomic variant
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] +
                    "/c4143367c9ecad58cbf87b08c11288149e801a70f71a5e114a8476607fe163a1/" +
                    analysis["analysis"]["endpoint_name"]
                )

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect exactly one analysis linked to this variant
                assert responsedict["responseSummary"]["numTotalResults"] == 1
                assert resp.status == 200

            loop.run_until_complete(test_check_g_variants_analyses_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_individuals_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_g_variants_individuals_endpoint_is_working():
                # Query individuals carrying or associated with a genomic variant
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] +
                    "/c4143367c9ecad58cbf87b08c11288149e801a70f71a5e114a8476607fe163a1/" +
                    individual["individual"]["endpoint_name"]
                )

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect variant appears in multiple individuals
                assert responsedict["responseSummary"]["numTotalResults"] == 15
                assert resp.status == 200

            loop.run_until_complete(test_check_g_variants_individuals_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_datasets_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_g_variants_datasets_endpoint_is_working():
                # Query datasets containing a specific genomic variant
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] +
                    "/c4143367c9ecad58cbf87b08c11288149e801a70f71a5e114a8476607fe163a1/" +
                    dataset["dataset"]["endpoint_name"]
                )

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect single dataset association for this variant
                assert responsedict["responseSummary"]["numTotalResults"] == 1
                assert resp.status == 200

            loop.run_until_complete(test_check_g_variants_datasets_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_cohorts_endpoint_is_working(self):
        with loop_context() as loop:
            # Initialize app and async test client
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_g_variants_cohorts_endpoint_is_working():
                # Query cohorts associated with a specific genomic variant
                # This tests reverse relationship: variant → cohort mapping
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] +
                    "/c4143367c9ecad58cbf87b08c11288149e801a70f71a5e114a8476607fe163a1/" +
                    cohort["cohort"]["endpoint_name"]
                )

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect a single cohort association for this variant
                assert responsedict["responseSummary"]["numTotalResults"] == 1
                assert resp.status == 200

            loop.run_until_complete(test_check_g_variants_cohorts_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_g_variants_endpoint_NONE_resultSetResponse_is_working(self):
        with loop_context() as loop:
            # Test filtering result set output (NONE = suppress resultSet details)
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_g_variants_endpoint_NONE_resultSetResponse_is_working():
                # includeResultsetResponses=NONE should suppress detailed result sets
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] +
                    "?includeResultsetResponses=NONE&testMode=True"
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate minimal response structure still exists
                self.assertIn("apiVersion", responsedict["meta"])
                self.assertIn("beaconId", responsedict["meta"])
                self.assertIn("returnedSchemas", responsedict["meta"])
                self.assertIn("receivedRequestSummary", responsedict["meta"])
                self.assertIn("returnedGranularity", responsedict["meta"])
                self.assertIn("testMode", responsedict["meta"])
                self.assertIn("responseSummary", responsedict)

                # Variant exists despite no resultSet payload being included
                assert responsedict["responseSummary"]["exists"] is True

            loop.run_until_complete(test_check_g_variants_endpoint_NONE_resultSetResponse_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_g_variants_endpoint_MISS_resultSetResponse_is_working(self):
        with loop_context() as loop:
            # MISS mode simulates "no match found"
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_g_variants_endpoint_MISS_resultSetResponse_is_working():
                # includeResultsetResponses=MISS forces a non-match scenario
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] +
                    "?includeResultsetResponses=MISS&testMode=True"
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Full response structure still validated even when no match exists
                self.assertIn("apiVersion", responsedict["meta"])
                self.assertIn("beaconId", responsedict["meta"])
                self.assertIn("returnedSchemas", responsedict["meta"])
                self.assertIn("receivedRequestSummary", responsedict["meta"])
                self.assertIn("returnedGranularity", responsedict["meta"])
                self.assertIn("testMode", responsedict["meta"])
                self.assertIn("resultSets", responsedict["response"])
                self.assertIn("responseSummary", responsedict)

                # Explicitly expect no matching variant
                assert responsedict["responseSummary"]["exists"] is False

            loop.run_until_complete(test_check_g_variants_endpoint_MISS_resultSetResponse_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_g_variants_endpoint_ALL_resultSetResponse_is_working(self):
        with loop_context() as loop:
            # ALL mode returns full resultSet detail information
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_g_variants_endpoint_ALL_resultSetResponse_is_working():
                # includeResultsetResponses=ALL returns full backend result sets
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] +
                    "?includeResultsetResponses=ALL&testMode=True"
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Ensure full response schema is preserved
                self.assertIn("apiVersion", responsedict["meta"])
                self.assertIn("beaconId", responsedict["meta"])
                self.assertIn("returnedSchemas", responsedict["meta"])
                self.assertIn("receivedRequestSummary", responsedict["meta"])
                self.assertIn("returnedGranularity", responsedict["meta"])
                self.assertIn("testMode", responsedict["meta"])
                self.assertIn("resultSets", responsedict["response"])
                self.assertIn("responseSummary", responsedict)

                # Variant should exist when full result sets are included
                assert responsedict["responseSummary"]["exists"] is True

            loop.run_until_complete(test_check_g_variants_endpoint_ALL_resultSetResponse_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_sequence_query(self):
        with loop_context() as loop:
            # Create application instance for testing
            app = create_app()

            # Wrap app in async test client bound to event loop
            client = TestClient(TestServer(app), loop=loop)

            # Start the test server before making requests
            loop.run_until_complete(client.start_server())

            async def test_check_g_variants_endpoint_with_parameters_is_working():
                # Query genomic variants using explicit sequence-based filters
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] +
                    "?start=43045703&referenceName=17&assemblyId=GRCh37"
                    "&referenceBases=G&alternateBases=A&testMode=True"
                )

                # Ensure request succeeded
                assert resp.status == 200

                # Parse JSON response payload
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect exactly one matching variant for this query
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            # Execute async test inside event loop
            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())

            # Cleanly close client/server resources
            loop.run_until_complete(client.close())


    def test_main_check_g_variants_sequence_query_gives_0_results(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_g_variants_endpoint_with_parameters_is_working():
                # Same query structure, but with mismatching alternate allele
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] +
                    "?start=43045703&referenceName=17&assemblyId=GRCh37"
                    "&referenceBases=G&alternateBases=C&testMode=True"
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect no matching records for invalid allele combination
                assert responsedict["responseSummary"]["exists"] == False

            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_g_variants_range_query(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_g_variants_endpoint_with_parameters_is_working():
                # Range-based query over genomic coordinates
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] +
                    "?start=343675&referenceName=2&assemblyId=GRCh37&end=345681&testMode=True"
                )

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                assert responsedict["responseSummary"]["numTotalResults"] == 6
                assert resp.status == 200

            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_g_variants_range_query_with_chr(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_g_variants_endpoint_with_parameters_is_working():
                # Same range query but chromosome prefixed with 'chr'
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] +
                    "?start=343675&referenceName=chr2&assemblyId=GRCh37&end=345681&testMode=True"
                )

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                assert responsedict["responseSummary"]["numTotalResults"] == 6
                assert resp.status == 200

            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_g_variants_geneId_query(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_g_variants_endpoint_with_parameters_is_working():
                # Gene-based filtering (e.g., BRCA1)
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] +
                    "?geneId=BRCA1&testMode=True"
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_g_variants_bracket_query(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_g_variants_endpoint_with_parameters_is_working():
                # Multi-value range query using comma-separated intervals
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] +
                    "?start=43045703,43045704&end=43045704,43045705"
                    "&referenceName=17&assemblyId=GRCh37&testMode=True"
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_g_variants_genomic_allele_query(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_g_variants_endpoint_with_parameters_is_working():
                # HGVS-like allele query using short form genomic notation
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] +
                    "?genomicAlleleShortForm=NC_000008.10:g.467881_467885delinsA&testMode=True"
                )

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                assert responsedict["responseSummary"]["numTotalResults"] == 1
                assert resp.status == 200

            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_aminoacidChange_query(self):
        with loop_context() as loop:
            # Initialize application under test
            app = create_app()

            # Wrap app in async test client tied to event loop
            client = TestClient(TestServer(app), loop=loop)

            # Start server before executing HTTP requests
            loop.run_until_complete(client.start_server())

            async def test_check_g_variants_endpoint_with_parameters_is_working():
                # Query using amino acid change + gene filter
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] +
                    "?aminoacidChange=Pro1856Ser&geneId=BRCA1&testMode=True"
                )

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect exactly one match for this protein-level variant query
                assert responsedict["responseSummary"]["numTotalResults"] == 1

                # Validate successful request
                assert resp.status == 200

            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_post_cross_query_individuals_g_variants_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_post_cross_query_g_variants_individuals_is_working():
                # Cross-entity POST query: genomic variants filtered by individuals
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            # Filter on individual ontology term
                            "filters": [{"id": "NCIT:C16576", "scope": "individual"}],

                            # Only include matching result sets
                            "includeResultsetResponses": "HIT",

                            # Pagination controls
                            "pagination": {"skip": 0, "limit": 10},

                            # Enable test mode for deterministic behavior
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect aggregated cross-query result size
                assert responsedict["responseSummary"]["numTotalResults"] == 40

            loop.run_until_complete(test_check_post_cross_query_g_variants_individuals_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_post_cross_query_individuals_biosamples_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_post_cross_query_biosamples_individuals_is_working():
                # Cross-query: biosamples filtered by individual-level ontology term
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    biosample["biosample"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [{"id": "NCIT:C16576", "scope": "individual"}],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect biosample results for matching individuals
                assert responsedict["responseSummary"]["numTotalResults"] == 20
                assert resp.status == 200

            loop.run_until_complete(test_check_post_cross_query_biosamples_individuals_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_request_parameters_fail(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_request_parameters_fail():
                # Invalid parameter name ("star" instead of "start") should trigger 400
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] +
                    "?star=12448"
                )

                assert resp.status == 400

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate error response structure
                self.assertIn("apiVersion", responsedict["meta"])
                self.assertIn("beaconId", responsedict["meta"])
                self.assertIn("returnedSchemas", responsedict["meta"])
                self.assertIn("receivedRequestSummary", responsedict["meta"])
                self.assertIn("returnedGranularity", responsedict["meta"])
                self.assertIn("testMode", responsedict["meta"])

                self.assertIn("error", responsedict)
                self.assertIn("errorCode", responsedict["error"])
                self.assertIn("errorMessage", responsedict["error"])

                # Ensure correct HTTP error mapping
                assert responsedict["error"]["errorCode"] == 400

            loop.run_until_complete(test_check_request_parameters_fail())
            loop.run_until_complete(client.close())


    def test_main_check_wrong_combination_request_parameters(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_wrong_combination_request_parameters():
                # Missing required parameter combination should trigger validation error
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] +
                    "?start=12448"
                )

                assert resp.status == 400

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Ensure structured error response is returned
                self.assertIn("error", responsedict)
                self.assertIn("errorCode", responsedict["error"])
                self.assertIn("errorMessage", responsedict["error"])
                assert responsedict["error"]["errorCode"] == 400

            loop.run_until_complete(test_wrong_combination_request_parameters())
            loop.run_until_complete(client.close())


    def test_main_check_datasets_g_variants_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_datasets_g_variants_endpoint_is_working():
                # Dataset-filtered genomic variant query
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] +
                    "?datasets=test"
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect dataset-filtered result count
                assert responsedict["responseSummary"]["numTotalResults"] == 41

            loop.run_until_complete(test_check_datasets_g_variants_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_alphanumeric_equal_query_is_working(self):
        with loop_context() as loop:
            # Initialize application for test execution
            app = create_app()

            # Wrap app in async HTTP test client
            client = TestClient(TestServer(app), loop=loop)

            # Start server before sending requests
            loop.run_until_complete(client.start_server())

            async def test_check_alphanumeric_equal_query_is_working():
                # Equality filter on alphanumeric field (ethnicity = European)
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    individual["individual"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "ethnicity",
                                    "operator": "=",
                                    "value": "European",
                                    "scope": "individual"
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect deterministic match count for exact filter
                assert responsedict["responseSummary"]["numTotalResults"] == 20

            loop.run_until_complete(test_check_alphanumeric_equal_query_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_alphanumeric_like_query_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_alphanumeric_like_query_is_working():
                # LIKE-style pattern matching using wildcard %
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    individual["individual"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "ethnicity",
                                    "operator": "=",
                                    "value": "%pean%",
                                    "scope": "individual"
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Pattern match should still resolve to same dataset subset
                assert responsedict["responseSummary"]["numTotalResults"] == 20

            loop.run_until_complete(test_check_alphanumeric_like_query_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_alphanumeric_not_like_query_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_alphanumeric_not_like_query_is_working():
                # NOT LIKE-style filter using negation operator
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    individual["individual"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "ethnicity",
                                    "operator": "!",
                                    "value": "%uropean%",
                                    "scope": "individual"
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect no matching records due to exclusion filter
                assert responsedict["responseSummary"]["exists"] == False

            loop.run_until_complete(test_check_alphanumeric_not_like_query_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_alphanumeric_not_query_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_alphanumeric_not_query_is_working():
                # Direct NOT equality filter (exclude exact match)
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    individual["individual"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "ethnicity",
                                    "operator": "!",
                                    "value": "European",
                                    "scope": "individual"
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # No matching individuals expected
                assert responsedict["responseSummary"]["exists"] == False

            loop.run_until_complete(test_check_alphanumeric_not_query_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_iso8601duration_gt_query_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_iso8601duration_gt_query_is_working():
                # Numeric comparison on ISO8601 duration-like field (age at exposure)
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    individual["individual"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "exposures.ageAtExposure.iso8601duration",
                                    "operator": ">",
                                    "value": "31"
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect deterministic count of matching exposures above threshold
                assert responsedict["responseSummary"]["numTotalResults"] == 20

            loop.run_until_complete(test_check_iso8601duration_gt_query_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_iso8601duration_ls_query_is_working(self):
        with loop_context() as loop:
            # Create application instance and test client bound to event loop
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_iso8601duration_ls_query_is_working():
                # Query individuals endpoint filtering by ISO8601 duration (less-than operator)
                # This checks that ageAtExposure.iso8601duration < 33 returns expected matches
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" + individual["individual"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "exposures.ageAtExposure.iso8601duration",
                                    "operator": "<",
                                    "value": "33"
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                # Ensure request succeeded and results exist
                assert resp.status == 200
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate that matching individuals exist and count is as expected
                assert responsedict["responseSummary"]["exists"] == True
                assert responsedict["responseSummary"]["numTotalResults"] == 20

            loop.run_until_complete(test_check_iso8601duration_ls_query_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_iso8601duration_eq_query_is_working(self):
        with loop_context() as loop:
            # Setup test server and client
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_iso8601duration_eq_query_is_working():
                # Equality filter on ISO8601 duration field (ageAtExposure == 34)
                # Expected to return no matches in test dataset
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" + individual["individual"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "exposures.ageAtExposure.iso8601duration",
                                    "operator": "=",
                                    "value": "34"
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                # Validate successful request but no matching results
                assert resp.status == 200
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)
                assert responsedict["responseSummary"]["exists"] == False

            loop.run_until_complete(test_check_iso8601duration_eq_query_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_measurement_value_query_is_working(self):
        with loop_context() as loop:
            # Initialize test server/client for measurement-based filtering
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_measurement_value_query_is_working():
                # Numeric comparison query on an individual-level attribute
                # Tests operator ">" on a measurement-like field
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" + individual["individual"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "anatomical entity",
                                    "operator": ">",
                                    "value": "44",
                                    "scope": "individual"
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                # Confirm valid response and expected result count
                assert resp.status == 200
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)
                assert responsedict["responseSummary"]["numTotalResults"] == 20

            loop.run_until_complete(test_check_measurement_value_query_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_measurement_value_query_does_not_find_results(self):
        with loop_context() as loop:
            # Setup server/client for negative numeric filter test case
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_measurement_value_query_does_not_find_results():
                # Same measurement field but stricter threshold (> 50)
                # Expected to return no matches
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" + individual["individual"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "anatomical entity",
                                    "operator": ">",
                                    "value": "50",
                                    "scope": "individual"
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                # Validate that query executes but returns no matches
                assert resp.status == 200
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)
                assert responsedict["responseSummary"]["exists"] == False

            loop.run_until_complete(test_check_measurement_value_query_does_not_find_results())
            loop.run_until_complete(client.close())
    def test_main_check_custom_query_is_working(self):
        with loop_context() as loop:
            # Initialize app and async test client
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_custom_query_is_working():
                # Custom structured filter query on biosample endpoint
                # Tests domain-specific filter syntax: sampleOriginType:ovary
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" + biosample["biosample"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {"id": "sampleOriginType:ovary"}
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                # Only verifying request success (no payload validation here)
                assert resp.status == 200

            loop.run_until_complete(test_check_custom_query_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_range_query_with_variant_min_and_max_lengths_is_working(self):
        with loop_context() as loop:
            # Range query with additional constraints on variant size (min/max length)
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_range_query_with_variant_min_and_max_lengths_working():
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" + genomicVariant["genomicVariant"]["endpoint_name"] +
                    "?start=343675&referenceName=2&assemblyId=GRCh37&end=345681"
                    "&variantMinLength=0&variantMaxLength=10&testMode=true"
                )

                # Ensures filtering by structural variant length constraints works correctly
                assert resp.status == 200
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)
                assert responsedict["responseSummary"]["numTotalResults"] == 2

            loop.run_until_complete(test_check_range_query_with_variant_min_and_max_lengths_working())
            loop.run_until_complete(client.close())


    def test_main_check_filters_as_request_parameter_working(self):
        with loop_context() as loop:
            # Tests legacy/simple query style using filters passed as request parameter
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_filters_as_request_parameter_working():
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" + individual["individual"]["endpoint_name"] +
                    "?filters=NCIT:C16576&testMode=true"
                )

                # Validates filter parsing from query string instead of JSON body
                assert resp.status == 200
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)
                assert responsedict["responseSummary"]["numTotalResults"] == 20

            loop.run_until_complete(test_check_filters_as_request_parameter_working())
            loop.run_until_complete(client.close())


    def test_main_check_datasets_list_query_is_working(self):
        with loop_context() as loop:
            # Query uses requestParameters.datasets to restrict dataset scope
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_datasets_list_query_is_working():
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" + individual["individual"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "requestParameters": {
                                "datasets": ["test"]
                            },
                            "filters": [],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 101},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                # Ensures dataset-scoped filtering does not break result aggregation
                assert resp.status == 200
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)
                assert responsedict["responseSummary"]["numTotalResults"] == 20

            loop.run_until_complete(test_check_datasets_list_query_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_range_query_with_variant_assemblyId_GRCh37_is_working(self):
        with loop_context() as loop:
            # Explicit assembly selection (GRCh37 genome build)
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_range_query_with_variant_assemblyId_GRCh37_working():
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" + genomicVariant["genomicVariant"]["endpoint_name"] +
                    "?start=343675&referenceName=2&assemblyId=GRCh37&end=345681&testMode=True"
                )

                # Confirms correct mapping of genomic coordinates under GRCh37
                assert resp.status == 200
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)
                assert responsedict["responseSummary"]["numTotalResults"] == 6

            loop.run_until_complete(test_check_range_query_with_variant_assemblyId_GRCh37_working())
            loop.run_until_complete(client.close())


    def test_main_check_range_query_with_variant_assemblyId_NCBI36_is_working(self):
        with loop_context() as loop:
            # Negative case: unsupported/older assembly (NCBI36)
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_range_query_with_variant_assemblyId_NCBI36_working():
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" + genomicVariant["genomicVariant"]["endpoint_name"] +
                    "?start=343675&referenceName=2&assemblyId=NCBI36&end=345681&testMode=True"
                )

                # Expected behavior: no results found for this assembly
                assert resp.status == 200
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)
                assert responsedict["responseSummary"]["exists"] == False

            loop.run_until_complete(test_check_range_query_with_variant_assemblyId_NCBI36_working())
            loop.run_until_complete(client.close())


    def test_main_check_NONE_count_query_is_working(self):
        with loop_context() as loop:
            # Test for COUNT granularity with minimal response payload (NONE resultset info)
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_NONE_count_query_is_working():
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" + individual["individual"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "ethnicity",
                                    "operator": "=",
                                    "value": "European",
                                    "scope": "individual"
                                }
                            ],
                            "includeResultsetResponses": "NONE",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "count"
                        }
                    }
                )

                # Ensures response respects COUNT granularity and omits detailed result sets
                assert resp.status == 200
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                assert responsedict["meta"]["returnedGranularity"] == "count"
                assert responsedict["meta"]["receivedRequestSummary"]["includeResultsetResponses"] == "NONE"

            loop.run_until_complete(test_check_NONE_count_query_is_working())
            loop.run_until_complete(client.close())


    def test_individuals_variants_with_heterozygosity(self):
        with loop_context() as loop:
            # Cross-entity query: genomicVariant → individual with genotype constraint
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_heterozygosity():
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] +
                    "/f640486e9e025466848eadc64622f213e4cc9bec534b8a68554fe4d4d0682a28/" +
                    individual["individual"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {"id": "GENO:0000458"}  # heterozygous genotype ontology term
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                # Validates genotype-based filtering across variant-individual relationship
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)
                assert responsedict["responseSummary"]["numTotalResults"] == 7
                assert resp.status == 200

            loop.run_until_complete(test_check_heterozygosity())
            loop.run_until_complete(client.close())
    def test_individuals_variants_with_homozygosity(self):
        with loop_context() as loop:
            # Setup async test environment for variant → individual cross-query
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_homozygosity():
                # Query linking a specific genomic variant to individuals with homozygous genotype
                # GENO:0000136 represents homozygous state
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] +
                    "/b215f7a084c83adfc2d4908ea69ce96ebbbff2ac0fbbb2bdd847858268b43610/" +
                    individual["individual"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [{"id": "GENO:0000136"}],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                # Validate successful response and expected homozygous match count
                assert resp.status == 200
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)
                assert responsedict["responseSummary"]["numTotalResults"] == 3

            loop.run_until_complete(test_check_homozygosity())
            loop.run_until_complete(client.close())


    def test_individuals_variants_with_filter(self):
        with loop_context() as loop:
            # Cross-query variant → individual using phenotype-like filter (NCIT ontology)
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_individuals_variants():
                # Filter scoped to individual entity using NCIT:C16576 term
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] +
                    "/f640486e9e025466848eadc64622f213e4cc9bec534b8a68554fe4d4d0682a28/" +
                    individual["individual"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {"id": "NCIT:C16576", "scope": "individual"}
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                # Ensure filter correctly narrows down individual-linked variant results
                assert resp.status == 200
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)
                assert responsedict["responseSummary"]["numTotalResults"] == 16

            loop.run_until_complete(test_check_individuals_variants())
            loop.run_until_complete(client.close())


    def test_analyses_variants_with_heterozygosity(self):
        with loop_context() as loop:
            # Variant → analysis relationship query using heterozygous genotype filter
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_heterozygosity():
                # GENO:0000458 represents heterozygous genotype in ontology
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] +
                    "/f640486e9e025466848eadc64622f213e4cc9bec534b8a68554fe4d4d0682a28/" +
                    analysis["analysis"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [{"id": "GENO:0000458"}],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                # Validate heterozygous variant appears in exactly one analysis result
                assert resp.status == 200
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_heterozygosity())
            loop.run_until_complete(client.close())


    def test_analyses_variants_with_homozygosity(self):
        with loop_context() as loop:
            # Variant → analysis query using homozygous genotype filter
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_homozygosity():
                # GENO:0000136 = homozygous genotype filter
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] +
                    "/b215f7a084c83adfc2d4908ea69ce96ebbbff2ac0fbbb2bdd847858268b43610/" +
                    analysis["analysis"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [{"id": "GENO:0000136"}],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                # Ensure homozygous variant is linked to exactly one analysis record
                assert resp.status == 200
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_homozygosity())
            loop.run_until_complete(client.close())


    def test_analyses_variants_with_filter(self):
        with loop_context() as loop:
            # Generic phenotype/individual-scoped filter applied to analysis-level query
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_analyses_variants():
                # Filter using NCIT ontology term scoped to individual context
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] +
                    "/f640486e9e025466848eadc64622f213e4cc9bec534b8a68554fe4d4d0682a28/" +
                    analysis["analysis"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {"id": "NCIT:C16576", "scope": "individual"}
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                # Ensure analysis-level filtering returns expected single match
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)
                assert responsedict["responseSummary"]["numTotalResults"] == 1
                assert resp.status == 200

            loop.run_until_complete(test_check_analyses_variants())
            loop.run_until_complete(client.close())
    def test_biosamples_variants_with_heterozygosity(self):
        # Create an event loop context for running async test code
        with loop_context() as loop:
            app = create_app()  # Initialize the application under test

            # Wrap the app in a test server and HTTP client
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_heterozygosity():
                # Query genomicVariant endpoint with a biosample-related nested route
                # This tests heterozygous genotype filtering (GENO:0000458)
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] + "/" +
                    "f640486e9e025466848eadc64622f213e4cc9bec534b8a68554fe4d4d0682a28/" +
                    biosample["biosample"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [{"id": "GENO:0000458"}],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate that heterozygous variants exist in biosample context
                assert responsedict["responseSummary"]["numTotalResults"] == 7

            loop.run_until_complete(test_check_heterozygosity())
            loop.run_until_complete(client.close())


    def test_biosamples_variants_with_homozygosity(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_homozygosity():
                # Same endpoint pattern but testing homozygous genotype filter
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] + "/" +
                    "b215f7a084c83adfc2d4908ea69ce96ebbbff2ac0fbbb2bdd847858268b43610/" +
                    biosample["biosample"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [{"id": "GENO:0000136"}],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect fewer results than heterozygosity case
                assert responsedict["responseSummary"]["numTotalResults"] == 3

            loop.run_until_complete(test_check_homozygosity())
            loop.run_until_complete(client.close())


    def test_biosamples_variants_with_filter(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_biosamples_variants():
                # Cross-entity filtering: individual-linked variants in biosample context
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] + "/" +
                    "c18249a2d7a303fb0551a4e86f43f5d830ba9182c88029e35697c87ebcb98546/" +
                    biosample["biosample"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {"id": "NCIT:C16576", "scope": "individual"}
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate filtered biosample-linked variant results
                assert responsedict["responseSummary"]["numTotalResults"] == 7

            loop.run_until_complete(test_check_biosamples_variants())
            loop.run_until_complete(client.close())


    def test_runs_variants_with_heterozygosity(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_heterozygosity():
                # Same heterozygosity concept, but at RUN level entity
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] + "/" +
                    "f640486e9e025466848eadc64622f213e4cc9bec534b8a68554fe4d4d0682a28/" +
                    run["run"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [{"id": "GENO:0000458"}],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_heterozygosity())
            loop.run_until_complete(client.close())


    def test_runs_variants_with_homozygosity(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_homozygosity():
                # RUN-level homozygous variant filtering
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] + "/" +
                    "b215f7a084c83adfc2d4908ea69ce96ebbbff2ac0fbbb2bdd847858268b43610/" +
                    run["run"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [{"id": "GENO:0000136"}],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_homozygosity())
            loop.run_until_complete(client.close())
    def test_runs_variants_with_filter(self):
        with loop_context() as loop:
            app = create_app()  # Initialize application under test
            client = TestClient(TestServer(app), loop=loop)

            # Start test server before executing requests
            loop.run_until_complete(client.start_server())

            async def test_check_runs_variants():
                # Query genomic variants linked to a specific RUN entity
                # Filter targets individuals within run context (NCIT:C16576)
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] + "/" +
                    "f640486e9e025466848eadc64622f213e4cc9bec534b8a68554fe4d4d0682a28/" +
                    run["run"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [{"id": "NCIT:C16576", "scope": "individual"}],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect a single matching variant in this run context
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_runs_variants())
            loop.run_until_complete(client.close())


    def test_variants_with_run_filter(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_runs_variants():
                # Query genomic variants directly with RUN-scoped filter
                # This tests filtering variants by run-associated ontology term
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [{"id": "GENEPIO:0001966", "scope": "run"}],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect multiple variants matching run-based filtering
                assert responsedict["responseSummary"]["numTotalResults"] == 21

            loop.run_until_complete(test_check_runs_variants())
            loop.run_until_complete(client.close())


    def test_individuals_with_run_filter(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_runs_variants():
                # Individual endpoint filtered by RUN-level ontology term
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    individual["individual"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [{"id": "GENEPIO:0001966", "scope": "run"}],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect a single individual matching run filter
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_runs_variants())
            loop.run_until_complete(client.close())


    def test_analyses_with_run_filter(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_runs_variants():
                # Analysis endpoint filtered by RUN-associated ontology term
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    analysis["analysis"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [{"id": "GENEPIO:0001966", "scope": "run"}],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect one analysis linked via run filter
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_runs_variants())
            loop.run_until_complete(client.close())


    def test_biosamples_with_run_filter(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_runs_variants():
                # Biosample endpoint filtered through RUN-level relationship
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    biosample["biosample"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [{"id": "GENEPIO:0001966", "scope": "run"}],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect biosamples associated with run filter
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_runs_variants())
            loop.run_until_complete(client.close())


    def test_variants_with_biosample_filter(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_runs_variants():
                # Variant query filtered by biosample-level ontology term
                # Tests cross-entity filtering (biosample → variant mapping)
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [{"id": "EFO:0009655", "scope": "biosample"}],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect multiple variants associated with biosample condition
                assert responsedict["responseSummary"]["numTotalResults"] == 40

            loop.run_until_complete(test_check_runs_variants())
            loop.run_until_complete(client.close())
    def test_individuals_with_biosample_filter(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_runs_variants():
                # POST request filtering individuals via a biosample-level ontology term (EFO)
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    individual["individual"]["endpoint_name"],
                    json={
                        "meta": {
                            "apiVersion": "2.0"
                        },
                        "query": {
                            "filters": [
                                {"id": "EFO:0009655", "scope": "biosample"}
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {
                                "skip": 0,
                                "limit": 10
                            },
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect 20 individuals linked to biosamples matching this filter
                assert responsedict["responseSummary"]["numTotalResults"] == 20

            loop.run_until_complete(test_check_runs_variants())
            loop.run_until_complete(client.close())


    def test_analyses_with_biosample_filter(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_runs_variants():
                # Same biosample ontology filter applied to analyses endpoint
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    analysis["analysis"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {"id": "EFO:0009655", "scope": "biosample"}
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect a single matching analysis record
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_runs_variants())
            loop.run_until_complete(client.close())


    def test_runs_with_biosample_filter(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_runs_variants():
                # Apply biosample ontology filter directly to run-level endpoint
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    run["run"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {"id": "EFO:0009655", "scope": "biosample"}
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect one matching run
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_runs_variants())
            loop.run_until_complete(client.close())


    def test_analyses_with_request_parameters(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_geneId_individual_filter():
                # Mix of filters + requestParameters (geneId) applied to analysis endpoint
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    analysis["analysis"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {"id": "NCIT:C16576", "scope": "individual"}
                            ],
                            "requestParameters": {"geneId": "SDF4"},
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": False,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect one matching result combining filter + geneId parameter
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_geneId_individual_filter())
            loop.run_until_complete(client.close())


    def test_runs_with_request_parameters(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_geneId_individual_filter():
                # Same requestParameters (geneId) test but on run endpoint
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    run["run"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {"id": "NCIT:C16576", "scope": "individual"}
                            ],
                            "requestParameters": {"geneId": "SDF4"},
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": False,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect one run matching gene + individual filter combination
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_geneId_individual_filter())
            loop.run_until_complete(client.close())


    def test_biosamples_with_request_parameters(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_geneId_individual_filter():
                # Biosample endpoint using both filter + geneId request parameter
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    biosample["biosample"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {"id": "NCIT:C16576", "scope": "individual"}
                            ],
                            "requestParameters": {"geneId": "SDF4"},
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": False,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect 17 biosample-level results
                assert responsedict["responseSummary"]["numTotalResults"] == 17

            loop.run_until_complete(test_check_geneId_individual_filter())
            loop.run_until_complete(client.close())
    def test_individuals_with_request_parameters(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_geneId_individual_filter():
                # Biosample endpoint is queried with an individual-scoped filter + geneId request parameter
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    biosample["biosample"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {"id": "NCIT:C16576", "scope": "individual"}
                            ],
                            # Additional constraint applied at request-parameter level
                            "requestParameters": {"geneId": "SDF4"},
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": False,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect biosamples matching both individual filter + geneId constraint
                assert responsedict["responseSummary"]["numTotalResults"] == 17

            loop.run_until_complete(test_check_geneId_individual_filter())
            loop.run_until_complete(client.close())


    def test_biosamples_with_request_parameters_fails(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_geneId_individual_filter():
                # Same structure as previous test, but geneId now yields no matching biosamples
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    biosample["biosample"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {"id": "NCIT:C16576", "scope": "individual"}
                            ],
                            # Different geneId expected to return no results
                            "requestParameters": {"geneId": "TP53"},
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": False,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Existence flag is expected to be false when no matching records exist
                assert responsedict["responseSummary"]["exists"] == False

            loop.run_until_complete(test_check_geneId_individual_filter())
            loop.run_until_complete(client.close())


    def test_biosamples_with_request_parameters_2(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_runs_variants():
                # Variant-like requestParameters are applied at biosample endpoint
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    biosample["biosample"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "requestParameters": {
                                "alternateBases": "A",
                                "referenceBases": "G",
                                "start": [43045703],
                                "referenceName": "17",
                                "assemblyId": "GRCh37"
                            },
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect filtered biosample results matching genomic constraints
                assert responsedict["responseSummary"]["numTotalResults"] == 15

            loop.run_until_complete(test_check_runs_variants())
            loop.run_until_complete(client.close())


    def test_analyses_with_request_parameters_2(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_runs_variants():
                # Same variant-style requestParameters applied to analysis endpoint
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    analysis["analysis"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "requestParameters": {
                                "alternateBases": "A",
                                "referenceBases": "G",
                                "start": [43045703],
                                "referenceName": "17",
                                "assemblyId": "GRCh37"
                            },
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Analysis endpoint should return a single matching result
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_runs_variants())
            loop.run_until_complete(client.close())


    def test_variants_with_request_parameters(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_variants():
                # Direct genomicVariant endpoint query using requestParameters instead of query string
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "requestParameters": {
                                "alternateBases": "A",
                                "referenceBases": "G",
                                "start": [43045703],
                                "referenceName": "17",
                                "assemblyId": "GRCh37"
                            },
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # One exact variant match expected
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_variants())
            loop.run_until_complete(client.close())


    def test_main_check_g_variants_sequence_query_fails(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_g_variants_endpoint_with_parameters_is_working():
                # Invalid combination of parameters in query string (sequence + alleles conflict)
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] +
                    "?start=43045703&referenceName=17&referenceBases=G&alternateBases=A&testMode=True"
                )

                assert resp.status == 400
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Error response should explicitly indicate a bad request
                assert responsedict["error"]["errorCode"] == 400

            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_range_query_fails(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_g_variants_endpoint_with_parameters_is_working():
                # Invalid genomic range query (missing proper combination or inconsistent coordinates)
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] +
                    "?start=345675&referenceName=2&end=345681&testMode=True"
                )

                assert resp.status == 400
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # API should reject malformed range query
                assert responsedict["error"]["errorCode"] == 400

            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_g_variants_bracket_query_fails(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_g_variants_endpoint_with_parameters_is_working():
                # Invalid multi-value range query using comma-separated coordinates
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] +
                    "?start=43045703,43045704&end=43045704,43045705&referenceName=17&testMode=True"
                )

                assert resp.status == 400
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # API enforces strict parameter formatting rules
                assert responsedict["error"]["errorCode"] == 400

            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_test_mode_fails(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_g_variants_endpoint_with_parameters_is_working():
                # Invalid testMode value (expects boolean, receives numeric)
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] +
                    "?start=43045703,43045704&end=43045704,43045705&referenceName=17&assemblyId=GRCh37&testMode=3"
                )

                assert resp.status == 400
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validation error due to incorrect type for testMode
                assert responsedict["error"]["errorCode"] == 400

            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())


    def test_descendant_terms(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_runs_variants():
                # Ontology-based filtering with descendant expansion enabled
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    individual["individual"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "MONDO:0004975",
                                    "scope": "individual",
                                    "includeDescendantTerms": True
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect expanded ontology query to return multiple matched individuals
                assert responsedict["responseSummary"]["numTotalResults"] == 20

            loop.run_until_complete(test_check_runs_variants())
            loop.run_until_complete(client.close())


    def test_main_check_g_variants_range_query_chrX(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_g_variants_endpoint_with_parameters_is_working():
                # Chromosome X range query (genomic interval search)
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] +
                    "?start=31120923&referenceName=X&assemblyId=GRCh37&end=31121924&testMode=true"
                )

                assert resp.status == 200
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect exactly one matching variant in this genomic region
                assert responsedict["responseSummary"]["exists"] == True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_g_variants_sequence_query_chrX(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_g_variants_endpoint_with_parameters_is_working():
                # Chromosome X sequence-level variant query (SNV match)
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] +
                    "?start=31121923&referenceName=X&assemblyId=GRCh37&referenceBases=T&alternateBases=C&testMode=true"
                )

                assert resp.status == 200
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Exact allele match expected
                assert responsedict["responseSummary"]["exists"] == True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_g_variants_range_sequence_chrY(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_g_variants_endpoint_with_parameters_is_working():
                # Chromosome Y allele-based query (male-specific chromosome region)
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] +
                    "?start=14191773&referenceBases=A&alternateBases=G&assemblyId=GRCh37&referenceName=Y"
                )

                assert resp.status == 200
                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Single variant expected in Y chromosome region
                assert responsedict["responseSummary"]["exists"] == True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_limit_query_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_limit_query_is_working():
                # Pagination limit test for dataset-controlled query
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    individual["individual"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "requestParameters": {"datasets": ["test"]},
                            "filters": [],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 15},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Ensure pagination limit is respected at result set level
                assert len(responsedict["response"]["resultSets"][0]["results"]) == 15
                assert resp.status == 200

            loop.run_until_complete(test_check_limit_query_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_record_resultSet_query_is_working(self):
        # Create async loop context for test isolation
        with loop_context() as loop:
            app = create_app()  # Initialize application instance
            client = TestClient(TestServer(app), loop=loop)  # Wrap app in test server/client
            loop.run_until_complete(client.start_server())  # Start async test server

            # Define async test coroutine
            async def test_check_record_resultSet_query_is_working():
                # Send POST request with record-level granularity
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" + individual["individual"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},  
                        # API version metadata
                        "query": {
                            "requestParameters": {
                                "datasets": ["test"]  
                                # Dataset under test
                            },
                            "filters": [],  
                            # No filters applied
                            "includeResultsetResponses": "HIT",  
                            # Return full result set
                            "pagination": {
                                "skip": 0,
                                "limit": 10  
                                # Expect 10 results
                            },
                            "testMode": True,  
                            # Enable deterministic test behavior
                            "requestedGranularity": "record"  
                            # Return full records
                        }
                    }
                )
                # Raw HTTP response body
                responsetext = await resp.text()  
                # Parse JSON response
                responsedict = json.loads(responsetext)  

                # Validate number of returned records
                assert len(responsedict["response"]["resultSets"][0]["results"]) == 10
                # Ensure HTTP success
                assert resp.status == 200

            # Execute async test
            loop.run_until_complete(test_check_record_resultSet_query_is_working())
            loop.run_until_complete(client.close())  # Clean up client connection


    def test_main_check_count_resultSet_query_is_working(self):
        # Setup isolated event loop for test
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_count_resultSet_query_is_working():
                # Request count-level granularity instead of full records
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" + individual["individual"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "requestParameters": {"datasets": ["test"]},
                            "filters": [],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            # Only counts returned
                            "requestedGranularity": "count"  
                        }
                    }
                )

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Ensure no full results are returned in count mode
                assert responsedict["response"]["resultSets"][0].get("results") is None
                # Validate total results count
                assert responsedict["responseSummary"]["numTotalResults"] == 20
                assert responsedict["response"]["resultSets"][0]["resultsCount"] == 20
                assert resp.status == 200

            loop.run_until_complete(test_check_count_resultSet_query_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_boolean_resultSet_query_is_working(self):
        # Boolean granularity test setup
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_boolean_resultSet_query_is_working():
                # Boolean query: checks existence only
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" + individual["individual"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "requestParameters": {"datasets": ["test"]},
                            "filters": [],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "boolean"
                        }
                    }
                )

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Boolean response should not include records or counts
                assert responsedict["response"]["resultSets"][0].get("results") is None
                assert responsedict["response"]["resultSets"][0].get("resultsCount") is None
                # Existence flag must be true
                assert responsedict["response"]["resultSets"][0]["exists"] is True
                assert resp.status == 200

            loop.run_until_complete(test_check_boolean_resultSet_query_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_boolean_query_is_working(self):
        # Boolean query with no response payload expected
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_boolean_query_is_working():
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" + individual["individual"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "requestParameters": {"datasets": ["test"]},
                            "filters": [],
                            # No result set returned
                            "includeResultsetResponses": "NONE",  
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "boolean"
                        }
                    }
                )

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Full response body should be omitted
                assert responsedict.get("response") is None
                # Summary should still confirm existence
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"].get("numTotalResults") is None
                assert resp.status == 200

            loop.run_until_complete(test_check_boolean_query_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_counts_query_is_working(self):
        # Count-only query without resultset payload
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_counts_query_is_working():
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" + individual["individual"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "requestParameters": {"datasets": ["test"]},
                            "filters": [],
                            "includeResultsetResponses": "NONE",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "count"
                        }
                    }
                )

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # No resultset returned, only summary metadata
                assert responsedict.get("response") is None
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 20
                assert resp.status == 200

            loop.run_until_complete(test_check_counts_query_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_requestedSchemas(self):
        # Setup isolated async loop for request lifecycle testing
        with loop_context() as loop:
            app = create_app()  # Initialize application under test
            client = TestClient(TestServer(app), loop=loop)  # Wrap app in test HTTP client
            loop.run_until_complete(client.start_server())  # Start test server

            async def test_check_requestedSchemas():
                # Request with explicit schema negotiation in metadata
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" + individual["individual"]["endpoint_name"],
                    json={
                        "meta": {
                            "apiVersion": "2.0",
                            "requestedSchemas": [
                                # Schema version hint
                                {"schema": "beacon-individual-v2.0.0"}  
                            ]
                        },
                        "query": {
                            "requestParameters": {"datasets": ["test"]},
                            "filters": [],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                             # Only existence check expected
                            "requestedGranularity": "boolean" 
                        }
                    }
                )

                # Ensure request succeeded
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate that schema request still returns existence info
                assert responsedict["responseSummary"]["exists"] is True

            loop.run_until_complete(test_check_requestedSchemas())
            loop.run_until_complete(client.close())


    def test_main_check_404_not_found_error(self):
        # Verify API correctly handles invalid endpoints
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_404_not_found_error():
                # Request to a non-existent endpoint should return 404
                resp = await client.post(conf_override.config.uri_subpath + "/impossibleendpoint")

                assert resp.status == 404  # Ensure correct HTTP error code

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate error payload structure
                assert responsedict["error"]["errorMessage"] == "Not found"
                assert responsedict["error"]["errorCode"] == 404

            loop.run_until_complete(test_check_404_not_found_error())
            loop.run_until_complete(client.close())


    def test_main_check_400_bad_request(self):
        # Validate query parameter validation errors
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_400_bad_request():
                # Invalid query parameter intentionally introduced (typo in testMode)
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    individual["individual"]["endpoint_name"] + '?testMod=true'
                )
                # Expect bad request response
                assert resp.status == 400 

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate error code is properly returned
                assert responsedict["error"]["errorCode"] == 400

            loop.run_until_complete(test_check_400_bad_request())
            loop.run_until_complete(client.close())


    def test_main_check_biosamples_g_variants_sequence_query(self):
        # Test biosample endpoint with genomic sequence query parameters
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_biosamples_endpoint_with_parameters_is_working():
                # GET request using genomic coordinate filters
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    biosample["biosample"]["endpoint_name"] +
                    "?start=43045703&referenceName=17&assemblyId=GRCh37"
                    "&referenceBases=G&alternateBases=A&testMode=True"
                )
                # Ensure endpoint responds successfully
                assert resp.status == 200  

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate existence of matching biosamples
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 15

            loop.run_until_complete(test_check_biosamples_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_post_individuals_with_filter_is_working(self):
        # Validate POST request with filter-based query on genomic variant endpoint
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_post_individuals_with_filter_is_working():
                # Query with ontology-based filter applied to individuals
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                # Disease/phenotype filter
                                {"id": "NCIT:C16576", "scope": "individual"}  
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )
                # Ensure valid response
                assert resp.status == 200  

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate filtered results exist and match expected count
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 40

            loop.run_until_complete(test_check_post_individuals_with_filter_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_cross_query_individuals_g_variants_with_filter_is_working(self):
        # Test cross-entity filtering: Individuals queried via GenomicVariation scope
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_cross_query_individuals_g_variants_with_filter_is_working():
                # Query individuals using genomic variation filter (cross-domain query)
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    individual["individual"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {"id": "ENSGLOSSARY:0000150", "scope": "genomicVariation"}
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200  # Ensure endpoint responds successfully

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Verify cross-query returns expected matching individuals
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 19

            loop.run_until_complete(test_check_cross_query_individuals_g_variants_with_filter_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_cross_query_analyses_g_variants_with_filter_is_working(self):
        # Cross-query: Analyses endpoint filtered by genomic variation
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_cross_query_analyses_g_variants_with_filter_is_working():
                # Apply genomicVariation scope filter on analyses endpoint
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    analysis["analysis"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {"id": "ENSGLOSSARY:0000150", "scope": "genomicVariation"}
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200  # Validate successful query execution

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Analyses endpoint should return a small number of matches
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_cross_query_analyses_g_variants_with_filter_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_cross_query_biosamples_g_variants_with_filter_is_working(self):
        # Cross-query: Biosamples filtered by genomic variation scope
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_cross_query_biosamples_g_variants_with_filter_is_working():
                # Query biosamples using genomic variation filter
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    biosample["biosample"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {"id": "ENSGLOSSARY:0000150", "scope": "genomicVariation"}
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate biosample matches for genomic variation query
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 19

            loop.run_until_complete(test_check_cross_query_biosamples_g_variants_with_filter_is_working())
            loop.run_until_complete(client.close())


    def test_individuals_with_request_parameters_and_filters(self):
        # Combined query: filters + genomic request parameters in same request
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_individuals_with_request_parameters_and_filters():
                # Query individuals using both variant filters and genomic coordinates
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    individual["individual"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {"id": "NCIT:C16576", "scope": "individual"}
                            ],
                            "requestParameters": {
                                "alternateBases": "A",
                                "referenceBases": "G",
                                "start": [43045703],
                                "referenceName": "17",
                                "assemblyId": "GRCh37"
                            },
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Ensure combined filtering + coordinate query works correctly
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 15

            loop.run_until_complete(test_check_individuals_with_request_parameters_and_filters())
            loop.run_until_complete(client.close())


    def test_main_check_no_dataset_found(self):
        # Validate behavior when requesting a non-existent dataset
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_check_no_dataset_found():
                # Query dataset that does not exist in system
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"] +
                    "?datasets=no_dataset"
                )
                # API still responds successfully
                assert resp.status == 200  

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # No dataset should result in empty logical match
                assert responsedict["responseSummary"]["exists"] is False

            loop.run_until_complete(test_check_check_no_dataset_found())
            loop.run_until_complete(client.close())


    def test_main_get_double_filters(self):
        # Validate handling of multiple filters passed via query string
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_get_double_filters():
                # Multiple comma-separated ontology filters applied
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    individual["individual"]["endpoint_name"] +
                    "?filters=NCIT:C16576,NCIT:C16731"
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Ensure combined filters still return valid matches
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 20

            loop.run_until_complete(test_check_get_double_filters())
            loop.run_until_complete(client.close())


    def test_main_check_configuration_validation(self):
        # Validate system configuration initialization logic
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_configuration():
                # Initialize logger and run configuration validation
                LOG = initialize_logger(config.level)
                check_configuration(LOG=LOG)

            # Execute configuration check (no HTTP request involved)
            loop.run_until_complete(test_check_configuration())
            loop.run_until_complete(client.close())
    def test_individuals_with_request_parameters_empty_fails(self):
        # Test that empty requestParameters object triggers validation error
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_individuals_with_request_parameters_empty_fails():
                # Send request with empty requestParameters (invalid state)
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    individual["individual"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "requestParameters": {},  # Empty object should fail validation
                            "filters": [{"id": "NCIT:C16576", "scope": "individual"}],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 400  # Expect validation error

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Ensure correct validation error message is returned
                assert "set of meta/query parameters" in responsedict["error"]["errorMessage"]
                assert responsedict["error"]["errorCode"] == 400

            loop.run_until_complete(test_check_individuals_with_request_parameters_empty_fails())
            loop.run_until_complete(client.close())


    def test_main_check_measurement_value_query_is_not_working_with_query_string_filters(self):
        # Test conflict between query string filters and JSON body filters
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_measurement_value_query_is_not_working():
                # Mixing query string filters with body filters should fail
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    individual["individual"]["endpoint_name"] +
                    '?filters=NCIT:C16576&limit=5&skip=0',
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "anatomical entity",
                                    "operator": ">",
                                    "value": "44",
                                    "scope": "individual"
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 400  # Conflict expected

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Ensure conflict error message is returned
                assert "two parameters conflict from string" in responsedict["error"]["errorMessage"]

            loop.run_until_complete(test_check_measurement_value_query_is_not_working())
            loop.run_until_complete(client.close())


    def test_main_check_measurement_value_query_is_working_with_query_string_filters(self):
        # Test valid usage of measurement value query without conflicting filters
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_measurement_value_query_is_working():
                # Valid request using skip in query string only
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    individual["individual"]["endpoint_name"] + '?skip=0',
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "anatomical entity",
                                    "operator": ">",
                                    "value": "44",
                                    "scope": "individual"
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200  # Valid request should succeed

            loop.run_until_complete(test_check_measurement_value_query_is_working())
            loop.run_until_complete(client.close())


    def test_individuals_with_request_parameters_with_query_string(self):
        # Test mixing query string parameters with requestParameters payload
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_runs_variants():
                # Query string provides alternateBases while body provides genomic coordinates
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    individual["individual"]["endpoint_name"] +
                    '?alternateBases=A',
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "requestParameters": {
                                "referenceBases": "G",
                                "start": [43045703],
                                "referenceName": "17",
                                "assemblyId": "GRCh37"
                            },
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )
                # Ensure successful hybrid query handling
                assert resp.status == 200  

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate expected match results from variant query
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 15

            loop.run_until_complete(test_check_runs_variants())
            loop.run_until_complete(client.close())
    def test_individuals_with_request_parameters_with_query_string_parsing_datasets(self):
        # Test parsing of multiple coordinate values passed via query string
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_runs_variants():
                # Query string includes multiple end positions combined with requestParameters
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    individual["individual"]["endpoint_name"] +
                    '?end=43045704,43045705',
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "requestParameters": {
                                "start": [43045703, 43045704],  
                                # Multiple start positions
                                "referenceName": "17",
                                "assemblyId": "GRCh37"
                            },
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )
                # Ensure successful hybrid query execution
                assert resp.status == 200  

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate expected existence and result count
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 15

            loop.run_until_complete(test_check_runs_variants())
            loop.run_until_complete(client.close())


    def test_main_check_measurement_value_query_is_not_working_with_query_string_includeResultsetResponses(self):
        # Test conflict between includeResultsetResponses in query string and body
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_measurement_value_query_is_not_working():
                # includeResultsetResponses mismatch between URL and body should fail
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    individual["individual"]["endpoint_name"] +
                    '?includeResultsetResponses=MISS',
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "anatomical entity",
                                    "operator": ">",
                                    "value": "44",
                                    "scope": "individual"
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )
                # Conflict expected due to parameter mismatch
                assert resp.status == 400  

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Ensure correct conflict error is returned
                assert "two parameters conflict from string" in responsedict["error"]["errorMessage"]

            loop.run_until_complete(test_check_measurement_value_query_is_not_working())
            loop.run_until_complete(client.close())


    def test_similarity_high(self):
        # Test ontology similarity expansion at HIGH level
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_similarity_high():
                # Filter uses high similarity threshold for ontology term expansion
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    individual["individual"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "MONDO:0004975",
                                    "scope": "individual",
                                    # Strict similarity expansion
                                    "similarity": "high"  
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )
                # Ensure valid query execution
                assert resp.status == 200  

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # High similarity still returns expanded matches
                assert responsedict["responseSummary"]["numTotalResults"] == 20

            loop.run_until_complete(test_check_similarity_high())
            loop.run_until_complete(client.close())


    def test_similarity_medium(self):
        # Test ontology similarity expansion at MEDIUM level
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_similarity_medium():
                # Medium similarity allows moderate ontology expansion
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    individual["individual"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "MONDO:0004975",
                                    "scope": "individual",
                                    "similarity": "medium"
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Medium similarity yields same expected match count
                assert responsedict["responseSummary"]["numTotalResults"] == 20

            loop.run_until_complete(test_check_similarity_medium())
            loop.run_until_complete(client.close())


    def test_similarity_low(self):
        # Test ontology similarity expansion at LOW level (broadest expansion)
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_similarity_low():
                # Low similarity allows most permissive ontology expansion
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    individual["individual"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "MONDO:0004975",
                                    "scope": "individual",
                                    "similarity": "low"
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Low similarity still returns same aggregate match count in this dataset
                assert responsedict["responseSummary"]["numTotalResults"] == 20

            loop.run_until_complete(test_check_similarity_low())
            loop.run_until_complete(client.close())
    def test_synonyms(self):
        # Test synonym expansion for ontology term filtering
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_synonyms():
                # Query using disease ontology term expected to expand via synonyms
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    individual["individual"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {"id": "DOID:1485", "scope": "individual"}
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200  # Ensure valid request execution

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Synonym expansion should increase matched result set
                assert responsedict["responseSummary"]["numTotalResults"] == 20

            loop.run_until_complete(test_check_synonyms())
            loop.run_until_complete(client.close())


    def test_main_check_analyses_with_requestedSchemas_is_working(self):
        # Validate schema negotiation for analyses endpoint via query string
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_analyses_with_with_requestedSchemas_is_working():
                # Request specific schema version via query parameter
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    analysis["analysis"]["endpoint_name"] +
                    "?requestedSchemas=beacon-analysis-v2.0.0&testMode=true"
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Ensure schema-filtered request still returns valid entity
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_analyses_with_with_requestedSchemas_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_post_cross_query_analyses_individuals_is_working(self):
        # Cross-query: individuals filtered by analysis attributes (valid case)
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_post_cross_query_analyses_individuals_is_working():
                # Filter individuals by analysis tool (GATK4.0 expected to exist)
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    individual["individual"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "variantCaller",
                                    "operator": "=",
                                    "value": "GATK4.0",
                                    "scope": "analysis"
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expected single match for this analysis filter
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_post_cross_query_analyses_individuals_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_post_cross_query_analyses_individuals_is_not_working(self):
        # Cross-query negative case: analysis filter that should not match individuals
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_post_cross_query_analyses_individuals_is_not_working():
                # Filter uses non-existent analysis tool version (GATK3.0)
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    individual["individual"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "variantCaller",
                                    "operator": "=",
                                    "value": "GATK3.0",
                                    "scope": "analysis"
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # No matches expected for unsupported analysis filter
                assert responsedict["responseSummary"]["exists"] is False

            loop.run_until_complete(test_check_post_cross_query_analyses_individuals_is_not_working())
            loop.run_until_complete(client.close())


    def test_main_check_post_cross_query_analyses_g_variants_is_working(self):
        # Cross-query: genomic variants filtered by analysis metadata (positive case)
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_post_cross_query_analyses_g_variants_is_working():
                # Analysis filter applied to genomicVariant endpoint (GATK4.0 expected)
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "variantCaller",
                                    "operator": "=",
                                    "value": "GATK4.0",
                                    "scope": "analysis"
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 0},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect full dataset match for this analysis filter
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 21

            loop.run_until_complete(test_check_post_cross_query_analyses_g_variants_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_post_cross_query_analyses_g_variants_is_not_working(self):
        # Cross-query negative case: genomicVariant filtered by unsupported analysis value
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_post_cross_query_analyses_g_variants_is_not_working():
                # Analysis filter uses unsupported tool version (GATK3.0)
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "variantCaller",
                                    "operator": "=",
                                    "value": "GATK3.0",
                                    "scope": "analysis"
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # No matches expected for invalid analysis filter
                assert responsedict["responseSummary"]["exists"] is False

            loop.run_until_complete(test_check_post_cross_query_analyses_g_variants_is_not_working())
            loop.run_until_complete(client.close())
    def test_main_check_post_cross_query_analyses_runs_is_working(self):
        # Cross-query: Runs endpoint filtered by analysis metadata (valid case)
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_post_cross_query_analyses_runs_is_working():
                # Query runs using analysis filter (GATK4.0 expected to match)
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    run["run"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "variantCaller",
                                    "operator": "=",
                                    "value": "GATK4.0",
                                    "scope": "analysis"
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200  # Ensure successful response

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect exactly one matching run for this analysis filter
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_post_cross_query_analyses_runs_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_post_cross_query_analyses_runs_is_not_working(self):
        # Cross-query negative case: analysis filter should not match genomicVariant
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_post_cross_query_analyses_runs_is_not_working():
                # Invalid analysis value (GATK3.0) expected to return no results
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "variantCaller",
                                    "operator": "=",
                                    "value": "GATK3.0",
                                    "scope": "analysis"
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # No matches expected for unsupported analysis tool version
                assert responsedict["responseSummary"]["exists"] is False

            loop.run_until_complete(test_check_post_cross_query_analyses_runs_is_not_working())
            loop.run_until_complete(client.close())


    def test_main_check_post_cross_query_analyses_biosamples_is_working(self):
        # Cross-query: Biosamples filtered by analysis metadata (valid case)
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_post_cross_query_analyses_biosamples_is_working():
                # Analysis filter applied to biosample endpoint
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    biosample["biosample"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "variantCaller",
                                    "operator": "=",
                                    "value": "GATK4.0",
                                    "scope": "analysis"
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect single matching biosample for this analysis filter
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_post_cross_query_analyses_biosamples_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_post_cross_query_biosamples_analyses_is_not_working(self):
        # Cross-query negative case: biosamples filtered by unsupported analysis value
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_post_cross_query_analyses_biosamples_is_not_working():
                # GATK3.0 expected to return no biosample matches
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    biosample["biosample"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "variantCaller",
                                    "operator": "=",
                                    "value": "GATK3.0",
                                    "scope": "analysis"
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # No match expected for invalid analysis filter
                assert responsedict["responseSummary"]["exists"] is False

            loop.run_until_complete(test_check_post_cross_query_analyses_biosamples_is_not_working())
            loop.run_until_complete(client.close())


    def test_main_check_post_cross_query_individuals_g_variants_is_not_working(self):
        # Cross-query negative case: individual endpoint with incorrect scope mapping
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_post_cross_query_individuals_g_variants_is_not_working():
                # Mis-scoped filter (individual scope incorrectly used for anatomical entity)
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "anatomical entity",
                                    "operator": "=",
                                    "value": "GATK3.0",
                                    "scope": "individual"
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # No results expected due to invalid scope mapping
                assert responsedict["responseSummary"]["exists"] is False

            loop.run_until_complete(test_check_post_cross_query_individuals_g_variants_is_not_working())
            loop.run_until_complete(client.close())


    def test_main_check_post_cross_query_individuals_runs_is_not_working(self):
        # Cross-query negative case: run endpoint with invalid individual-scoped filter
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_post_cross_query_individuals_runs_is_not_working():
                # Incorrect scope usage expected to yield no matches
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    run["run"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "anatomical entity",
                                    "operator": "=",
                                    "value": "GATK3.0",
                                    "scope": "individual"
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # No matches expected due to incorrect filter scope
                assert responsedict["responseSummary"]["exists"] is False

            loop.run_until_complete(test_check_post_cross_query_individuals_runs_is_not_working())
            loop.run_until_complete(client.close())
    def test_main_check_post_cross_query_runs_individuals_is_not_working(self):
        # Cross-query negative case: run-scoped filter incorrectly applied to individuals
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_post_cross_query_runs_individuals_is_not_working():
                # Run-level attribute (librarySource) incorrectly queried in individual context
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    individual["individual"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "librarySource",
                                    "operator": "=",
                                    "value": "GATK3.0",
                                    "scope": "run"
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200  # Request still executes successfully

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # No matches expected due to invalid cross-entity scope usage
                assert responsedict["responseSummary"]["exists"] is False

            loop.run_until_complete(test_check_post_cross_query_runs_individuals_is_not_working())
            loop.run_until_complete(client.close())


    def test_main_check_post_cross_query_g_variants_runs_is_not_working(self):
        # Cross-query negative case: run filter applied to genomicVariant endpoint
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_post_cross_query_runs_g_variants_is_not_working():
                # Invalid run-scoped filter applied to genomicVariant endpoint
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "librarySource",
                                    "operator": "=",
                                    "value": "GATK3.0",
                                    "scope": "run"
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect no results due to invalid scope mapping
                assert responsedict["responseSummary"]["exists"] is False

            loop.run_until_complete(test_check_post_cross_query_runs_g_variants_is_not_working())
            loop.run_until_complete(client.close())


    def test_main_check_post_cross_query_biosamples_runs_is_not_working(self):
        # Cross-query negative case: run-scoped filter applied to biosamples endpoint
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_post_cross_query_runs_biosamples_is_not_working():
                # Run-level attribute incorrectly applied to biosample entity
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    biosample["biosample"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "librarySource",
                                    "operator": "=",
                                    "value": "GATK3.0",
                                    "scope": "run"
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # No matches expected due to invalid cross-entity filtering
                assert responsedict["responseSummary"]["exists"] is False

            loop.run_until_complete(test_check_post_cross_query_runs_biosamples_is_not_working())
            loop.run_until_complete(client.close())


    def test_main_check_post_cross_query_runs_analyses_is_not_working(self):
        # Cross-query negative case: run filter applied to analyses endpoint
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_post_cross_query_runs_analyses_is_not_working():
                # Invalid run-scoped filter applied to analysis entity
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    analysis["analysis"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "librarySource",
                                    "operator": "=",
                                    "value": "GATK3.0",
                                    "scope": "run"
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # No matches expected due to invalid scope usage
                assert responsedict["responseSummary"]["exists"] is False

            loop.run_until_complete(test_check_post_cross_query_runs_analyses_is_not_working())
            loop.run_until_complete(client.close())


    def test_main_check_post_cross_query_biosamples_individuals_is_not_working(self):
        # Cross-query negative case: biosample-scoped filter incorrectly applied to individuals
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_post_cross_query_biosamples_individuals_is_not_working():
                # Biosample field used in individual context (invalid mapping)
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    individual["individual"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "measurements.assayCode",
                                    "operator": "=",
                                    "value": "GATK3.0",
                                    "scope": "biosample"
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # No results expected due to invalid cross-entity filter scope
                assert responsedict["responseSummary"]["exists"] is False

            loop.run_until_complete(test_check_post_cross_query_biosamples_individuals_is_not_working())
            loop.run_until_complete(client.close())


    def test_main_check_post_cross_query_g_variants_biosamples_is_not_working(self):
        # Cross-query negative case: biosample filter applied to genomicVariant endpoint
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_post_cross_query_biosamples_g_variants_is_not_working():
                # Biosample attribute incorrectly used in genomicVariant query
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    genomicVariant["genomicVariant"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "measurements.assayCode",
                                    "operator": "=",
                                    "value": "GATK3.0",
                                    "scope": "biosample"
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # No matches expected due to incorrect scope mapping
                assert responsedict["responseSummary"]["exists"] is False

            loop.run_until_complete(test_check_post_cross_query_biosamples_g_variants_is_not_working())
            loop.run_until_complete(client.close())
    def test_main_check_post_cross_query_runs_biosamples_is_not_working(self):
        # Cross-query negative case: biosample-scoped filter incorrectly applied to runs endpoint
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_post_cross_query_runs_biosamples_is_not_working():
                # Biosample field applied to run entity (invalid cross-entity scope usage)
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    run["run"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "measurements.assayCode",
                                    "operator": "=",
                                    "value": "GATK3.0",
                                    "scope": "biosample"
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200  # Request succeeds even if filter does not match

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # No matches expected due to incorrect scope mapping
                assert responsedict["responseSummary"]["exists"] is False

            loop.run_until_complete(test_check_post_cross_query_runs_biosamples_is_not_working())
            loop.run_until_complete(client.close())


    def test_main_check_post_cross_query_analyses_biosamples_is_not_working(self):
        # Cross-query negative case: biosample filter applied to analyses endpoint
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_post_cross_query_biosamples_analyses_is_not_working():
                # Invalid biosample-scoped filter applied to analysis entity
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    analysis["analysis"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "measurements.assayCode",
                                    "operator": "=",
                                    "value": "GATK3.0",
                                    "scope": "biosample"
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # No results expected due to invalid cross-entity filter scope
                assert responsedict["responseSummary"]["exists"] is False

            loop.run_until_complete(test_check_post_cross_query_biosamples_analyses_is_not_working())
            loop.run_until_complete(client.close())


    def test_main_check_cohorts_datasets_cross_query_is_working(self):
        # Cross-query: cohorts endpoint joined with dataset identifier
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_cohorts_datasets_cross_query_is_working():
                # Fetch cohort data for specific dataset context
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    cohort["cohort"]["endpoint_name"] +
                    "/EGA-testing/" +
                    dataset["dataset"]["endpoint_name"]
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect single matching cross-linked cohort-dataset result
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_cohorts_datasets_cross_query_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_datasets_cohorts_cross_query_is_working(self):
        # Cross-query: dataset endpoint joined with cohort identifier
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_datasets_cohorts_cross_query_is_working():
                # Reverse direction cohort-dataset relationship query
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    dataset["dataset"]["endpoint_name"] +
                    "/test/" +
                    cohort["cohort"]["endpoint_name"]
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect single matching cross-linked dataset-cohort result
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_datasets_cohorts_cross_query_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_iso8601duration_gt_query_is_working_with_iso_value(self):
        # Query using ISO 8601 duration comparison operator (> threshold filtering)
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_iso8601duration_gt_query_is_working():
                # Filter exposures older than 31 years (P31Y ISO 8601 duration)
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    individual["individual"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "exposures.ageAtExposure.iso8601duration",
                                    "operator": ">",
                                    "value": "P31Y"
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expected deterministic result count for duration-based filter
                assert responsedict["responseSummary"]["numTotalResults"] == 20

            loop.run_until_complete(test_check_iso8601duration_gt_query_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_individuals_endpoint_is_removing_dataset(self):
        # Validate dataset exclusion behavior in individuals endpoint (testMode)
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_individuals_endpoint_is_removing_dataset():
                # Ensure dataset filtering is applied correctly in test mode
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    individual["individual"]["endpoint_name"] +
                    "?testMode=true"
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect fixed number of results in dataset-filtered environment
                assert responsedict["responseSummary"]["numTotalResults"] == 20

            loop.run_until_complete(test_check_individuals_endpoint_is_removing_dataset())
            loop.run_until_complete(client.close())


    def test_main_check_patients_endpoint_is_working(self):
        # Basic validation of patients endpoint availability
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_patients_endpoint_is_working():
                # Simple GET request to patients endpoint in test mode
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    patients["patients"]["endpoint_name"] +
                    "?testMode=true"
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

            loop.run_until_complete(test_check_patients_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_patients_with_limit_endpoint_is_working(self):
        # Patients endpoint with pagination limit validation
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_patients_with_limit_endpoint_is_working():
                # Validate response structure when limit parameter is applied
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    patients["patients"]["endpoint_name"] +
                    "?limit=200"
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Validate required metadata fields exist in response
                self.assertIn("apiVersion", responsedict["meta"])
                self.assertIn("beaconId", responsedict["meta"])
                self.assertIn("returnedSchemas", responsedict["meta"])
                self.assertIn("receivedRequestSummary", responsedict["meta"])
                self.assertIn("returnedGranularity", responsedict["meta"])
                self.assertIn("testMode", responsedict["meta"])

                # Validate response structure integrity
                self.assertIn("resultSets", responsedict["response"])
                self.assertIn("responseSummary", responsedict)

                assert responsedict["responseSummary"]["exists"] is True

            loop.run_until_complete(test_check_patients_with_limit_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_datasets_with_limit_endpoint_is_working(self):
            with loop_context() as loop:
                app = create_app()
                client = TestClient(TestServer(app), loop=loop)
                loop.run_until_complete(client.start_server())
                async def test_check_datasets_with_limit_endpoint_is_working():
                    resp = await client.get(conf_override.config.uri_subpath+"/"+dataset["dataset"]["endpoint_name"]+"?limit=200")
                    assert resp.status == 200
                    responsetext=await resp.text()
                    responsedict=json.loads(responsetext)
                    self.assertIn("apiVersion",responsedict["meta"])
                    self.assertIn("beaconId",responsedict["meta"])
                    self.assertIn("returnedSchemas",responsedict["meta"])
                    self.assertIn("receivedRequestSummary",responsedict["meta"])
                    self.assertIn("returnedGranularity",responsedict["meta"])
                    self.assertIn("testMode",responsedict["meta"])
                    self.assertIn("collections",responsedict["response"])
                    self.assertIn("responseSummary",responsedict)
                    assert responsedict["responseSummary"]["exists"] == True
                loop.run_until_complete(test_check_datasets_with_limit_endpoint_is_working())
                loop.run_until_complete(client.close())
    def test_main_check_patients_with_id_endpoint_is_working(self):
        # Validate retrieval of a specific patient by ID
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_patients_with_id_endpoint_is_working():
                # Fetch single patient record by identifier
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    patients["patients"]["endpoint_name"] +
                    "/subject003"
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect exactly one patient match
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_patients_with_id_endpoint_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_patients_collections_endpoint_is_working(self):
        # Validate patient-to-collection relationship endpoint
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_patients_collections_endpoint_is_working():
                # Retrieve collections associated with a specific patient
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    patients["patients"]["endpoint_name"] +
                    "/subject003/" +
                    collections["collections"]["endpoint_name"]
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect exactly one linked collection result
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_patients_collections_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_post_collections_with_filter_is_working(self):
        # Test POST collections endpoint with multiple patient-scoped filters
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_post_patients_with_filter_is_working():
                # Complex filter set including numeric comparison and multiple identifiers
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    collections["collections"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {"id": "EUCAIM:IMG1000026", "scope": "patients"},
                                {"id": "EUCAIM:BP1000270", "scope": "patients"},
                                {"id": "EUCAIM:CLIN1000060", "scope": "patients"},
                                {"id": "EUCAIM:IMG1000047", "scope": "patients"},
                                {
                                    "id": "imageStudy.disease.tumorMetadata.PSA",
                                    "operator": "<",
                                    "value": 2,
                                    "scope": "patients"
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200  # Successful query execution

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect exactly one matching collection result
                assert responsedict["responseSummary"]["exists"] is True
                assert responsedict["responseSummary"]["numTotalResults"] == 1

            loop.run_until_complete(test_check_post_patients_with_filter_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_post_cross_query_cohort_individuals_is_working(self):
        # Cross-query: cohort filter applied to individuals endpoint (valid case)
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_post_cross_query_cohort_individuals_is_working():
                # Cohort-scoped ontology filter applied to individuals
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    individual["individual"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {"id": "OGMS:0000015", "scope": "cohort"}
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # At least one matching individual expected
                assert responsedict["responseSummary"]["exists"] is True

            loop.run_until_complete(test_check_post_cross_query_cohort_individuals_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_post_cross_query_analysis_datasets_is_working(self):
        # Cross-query: analysis filter applied to dataset endpoint
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_post_cross_query_analysis_datasets_is_working():
                # Analysis metadata (variantCaller) used in dataset context
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    dataset["dataset"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "variantCaller",
                                    "operator": "=",
                                    "value": "GATK4.0",
                                    "scope": "analysis"
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Expect dataset match from linked analysis metadata
                assert responsedict["responseSummary"]["exists"] is True

            loop.run_until_complete(test_check_post_cross_query_analysis_datasets_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_post_cross_query_analysis_cohorts_is_working(self):
        # Cross-query: analysis filter applied to cohort endpoint
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_post_cross_query_analysis_cohorts_is_working():
                # Analysis-level metadata used to filter cohort results
                resp = await client.post(
                    conf_override.config.uri_subpath + "/" +
                    cohort["cohort"]["endpoint_name"],
                    json={
                        "meta": {"apiVersion": "2.0"},
                        "query": {
                            "filters": [
                                {
                                    "id": "variantCaller",
                                    "operator": "=",
                                    "value": "GATK4.0",
                                    "scope": "analysis"
                                }
                            ],
                            "includeResultsetResponses": "HIT",
                            "pagination": {"skip": 0, "limit": 10},
                            "testMode": True,
                            "requestedGranularity": "record"
                        }
                    }
                )

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # At least one cohort expected to match
                assert responsedict["responseSummary"]["exists"] is True

            loop.run_until_complete(test_check_post_cross_query_analysis_cohorts_is_working())
            loop.run_until_complete(client.close())


    def test_main_check_health_endpoint(self):
        # Health endpoint basic availability check
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_health_endpoint():
                # Simple GET health check for service status
                resp = await client.get(conf_override.config.uri_subpath + "/health")

                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Service should report healthy state
                assert responsedict["state"] == "Running - healthy"

            loop.run_until_complete(test_check_health_endpoint())
            loop.run_until_complete(client.close())


    def test_main_check_health_endpoint_draining(self):
        # Health endpoint state transition test (healthy -> draining)
        with loop_context() as loop:
            app = create_app()

            # Register startup hook for state transition behavior
            app.on_startup.append(on_start)

            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            pause_event = asyncio.Event()

            async def test_draining_state(self):
                # Simulated application state and logger setup
                app = {
                    'logger': initialize_logger(config.level),
                    'state': 'Running - healthy',
                    'pending_requests': []
                }

                new_initial_times = {}

                # Create temporary file to trigger config watcher
                with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as tmp:
                    path = tmp.name

                paths_to_restart = [path]
                exit_called = {'called': False}

                # Fake exit handler to capture shutdown trigger
                def fake_exit(code):
                    exit_called['called'] = True

                # Start config watcher task
                task = asyncio.create_task(
                    config_watcher(
                        app,
                        new_initial_times,
                        paths_to_restart,
                        exit_fn=fake_exit,
                        sleep_interval=0.1
                    )
                )

                await asyncio.sleep(0.2)

                # Trigger file change to simulate config update
                with open(path, "a") as f:
                    f.write("# test change\n")
                os.utime(path, None)

                await task

                # Expect state transition to draining mode
                assert app['state'] == 'Draining'

                # Expect shutdown signal to be triggered
                assert exit_called['called'] is True

                # Cleanup temp file
                os.remove(path)

            loop.run_until_complete(test_draining_state(self))
            loop.run_until_complete(client.close())
class AsyncTest(unittest.IsolatedAsyncioTestCase):

    # Starts a background API server using asyncio and waits briefly for it to initialize.
    async def test_main_create_api(self):

        async def server_running_in_background():
            # Launch API server on port 5051 and keep it running indefinitely
            server = await asyncio.run(await create_api(5051))
            await server.serve_forever()

        # Run the server task in the background
        server_task = asyncio.create_task(server_running_in_background())

        # Give the server time to start before test ends
        await asyncio.sleep(2)


class TestShutdown(unittest.IsolatedAsyncioTestCase):

    # Creates a minimal mock application state used for shutdown tests
    def make_app(self):
        app = {}
        app['pending_requests'] = set()
        app['shutting_down'] = False
        app['state'] = 'Running - healthy'
        return app

    # Helper to execute a coroutine while triggering a shutdown signal
    async def trigger_shutdown(self, coro, stop_event):
        task = asyncio.create_task(coro)
        await asyncio.sleep(0)
        stop_event.set()
        await task
        return task

    # Verifies graceful shutdown when there are no pending requests
    async def test_shutdown_no_pending(self):
        app = self.make_app()
        runner = AsyncMock()
        logger = AsyncMock()
        stop_event = asyncio.Event()

        await self.trigger_shutdown(
            _graceful_shutdown(app, logger, runner, stop_event),
            stop_event
        )

        self.assertTrue(app['shutting_down'])
        self.assertEqual(app['state'], 'Shutting down')
        runner.cleanup.assert_awaited_once()

    # Verifies shutdown completes correctly when a short task is pending
    async def test_shutdown_with_pending_success(self):
        app = self.make_app()

        async def short_task():
            await asyncio.sleep(0.01)

        t = asyncio.create_task(short_task())
        app['pending_requests'].add(t)

        runner = AsyncMock()
        logger = AsyncMock()
        stop_event = asyncio.Event()

        await self.trigger_shutdown(
            _graceful_shutdown(app, logger, runner, stop_event),
            stop_event
        )

        self.assertTrue(t.done())
        runner.cleanup.assert_awaited_once()

    # Ensures timeout logic forces shutdown when tasks take too long
    async def test_shutdown_timeout(self):
        app = self.make_app()

        async def long_task():
            await asyncio.sleep(10)

        t = asyncio.create_task(long_task())
        app['pending_requests'].add(t)

        runner = AsyncMock()
        logger = AsyncMock()
        stop_event = asyncio.Event()

        original_timeout = config.pending_requests_timeout_in_seconds
        config.pending_requests_timeout_in_seconds = 0.01

        try:
            await self.trigger_shutdown(
                _graceful_shutdown(app, logger, runner, stop_event),
                stop_event
            )
        finally:
            config.pending_requests_timeout_in_seconds = original_timeout

        logger.warning.assert_any_call("Timeout reached, forcing shutdown")
        runner.cleanup.assert_awaited_once()

    # Verifies behavior when a pending task raises an exception
    async def test_shutdown_pending_exception(self):
        app = self.make_app()

        async def failing_task():
            raise RuntimeError("boom")

        t = asyncio.create_task(failing_task())
        app['pending_requests'].add(t)

        runner = AsyncMock()
        logger = AsyncMock()
        stop_event = asyncio.Event()

        await self.trigger_shutdown(
            _graceful_shutdown(app, logger, runner, stop_event),
            stop_event
        )

        self.assertTrue(t.done())
        runner.cleanup.assert_awaited_once()

    # Ensures multiple pending tasks are all awaited and completed
    async def test_shutdown_multiple_pending(self):
        app = self.make_app()

        async def task1():
            await asyncio.sleep(0.01)

        async def task2():
            await asyncio.sleep(0.02)

        tasks = [
            asyncio.create_task(task1()),
            asyncio.create_task(task2())
        ]

        app['pending_requests'].update(tasks)

        runner = AsyncMock()
        logger = AsyncMock()
        stop_event = asyncio.Event()

        await self.trigger_shutdown(
            _graceful_shutdown(app, logger, runner, stop_event),
            stop_event
        )

        self.assertTrue(all(t.done() for t in tasks))
        runner.cleanup.assert_awaited_once()


class TestHealthHandler(unittest.IsolatedAsyncioTestCase):

    # Simulates a database failure scenario and checks degraded health response
    async def test_database_down(self):
        app = {
            'state': 'Running - healthy',
            'pending_requests': set(),
            'logger': initialize_logger(config.level)
        }

        request = AsyncMock()
        request.app = app

        handler = HealthView(request)

        # Patch health handler to simulate database failure
        @patch("beacon.views.health.HealthView.handler")
        def test_risky_function_raises(self, mock_risky):
            mock_risky.side_effect = DatabaseIsDown('mongo')

            response = handler.handler()

            self.assertEqual(response.status, 200)

            body = response.text
            self.assertIn("Running - degraded", body)
            self.assertIn("database is down", body)

            self.assertEqual(app['state'], 'Running - degraded')




if __name__ == '__main__':
    unittest.main()