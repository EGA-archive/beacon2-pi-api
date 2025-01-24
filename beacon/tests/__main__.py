
from aiohttp.test_utils import TestClient, TestServer, loop_context
from aiohttp import web
from beacon.__main__ import Collection, Resultset, Info, ServiceInfo, Map, Configuration, FilteringTerms, EntryTypes
import json
import unittest
from beacon.permissions.tests import TestAuthZ
from beacon.validator.tests import TestValidator
from beacon.auth.tests import TestAuthN
#from beacon.request.tests import TestRequest
from beacon.tests.wrong_service_info import service_info_wrong
from aiohttp.test_utils import make_mocked_request
from beacon.response.catalog import build_beacon_error_response
from bson import json_util
from beacon.logs.logs import LOG
from beacon.connections.mongo.filters import cross_query, apply_filters
from beacon.connections.mongo.g_variants import get_analyses_of_variant
from unittest.mock import MagicMock
from beacon.request.parameters import RequestMeta, RequestQuery, Pagination, RequestParams

def create_app():
    app = web.Application()
    #app.on_startup.append(initialize)
    app.add_routes([web.view('/api', Info)])
    app.add_routes([web.view('/api/info', Info)])
    app.add_routes([web.view('/api/entry_types', EntryTypes)])
    app.add_routes([web.view('/api/service-info', ServiceInfo)])
    app.add_routes([web.view('/api/configuration', Configuration)])
    app.add_routes([web.view('/api/map', Map)])
    app.add_routes([web.view('/api/filtering_terms', FilteringTerms)])
    app.add_routes([web.view('/api/datasets', Collection)])
    app.add_routes([web.view('/api/datasets/{id}', Collection)])
    app.add_routes([web.view('/api/datasets/{id}/g_variants', Resultset)])
    app.add_routes([web.view('/api/datasets/{id}/biosamples', Resultset)])
    app.add_routes([web.view('/api/datasets/{id}/analyses', Resultset)])
    app.add_routes([web.view('/api/datasets/{id}/runs', Resultset)])
    app.add_routes([web.view('/api/datasets/{id}/individuals', Resultset)])
    app.add_routes([web.view('/api/cohorts', Collection)])
    app.add_routes([web.view('/api/cohorts/{id}', Collection)])
    app.add_routes([web.view('/api/cohorts/{id}/individuals', Resultset)])
    app.add_routes([web.view('/api/cohorts/{id}/g_variants', Resultset)])
    app.add_routes([web.view('/api/cohorts/{id}/biosamples', Resultset)])
    app.add_routes([web.view('/api/cohorts/{id}/analyses', Resultset)])
    app.add_routes([web.view('/api/cohorts/{id}/runs', Resultset)])
    app.add_routes([web.view('/api/g_variants', Resultset)])
    app.add_routes([web.view('/api/g_variants/{id}', Resultset)])
    app.add_routes([web.view('/api/g_variants/{id}/analyses', Resultset)])
    app.add_routes([web.view('/api/g_variants/{id}/biosamples', Resultset)])
    app.add_routes([web.view('/api/g_variants/{id}/individuals', Resultset)])
    app.add_routes([web.view('/api/g_variants/{id}/runs', Resultset)])
    app.add_routes([web.view('/api/individuals', Resultset)])
    app.add_routes([web.view('/api/individuals/{id}', Resultset)])
    app.add_routes([web.view('/api/individuals/{id}/g_variants', Resultset)])
    app.add_routes([web.view('/api/individuals/{id}/biosamples', Resultset)])
    app.add_routes([web.view('/api/analyses', Resultset)])
    app.add_routes([web.view('/api/analyses/{id}', Resultset)])
    app.add_routes([web.view('/api/analyses/{id}/g_variants', Resultset)])
    app.add_routes([web.view('/api/biosamples', Resultset)])
    app.add_routes([web.view('/api/biosamples/{id}', Resultset)])
    app.add_routes([web.view('/api/biosamples/{id}/g_variants', Resultset)])
    app.add_routes([web.view('/api/biosamples/{id}/analyses', Resultset)])
    app.add_routes([web.view('/api/biosamples/{id}/runs', Resultset)])
    app.add_routes([web.view('/api/runs', Resultset)])
    app.add_routes([web.view('/api/runs/{id}', Resultset)])
    app.add_routes([web.view('/api/runs/{id}/analyses', Resultset)])
    app.add_routes([web.view('/api/runs/{id}/g_variants', Resultset)])
    return app

class TestMain(unittest.TestCase):
    def test_main_check_slash_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_slash_endpoint_is_working():
                resp = await client.get("/api")
                assert resp.status == 200
            loop.run_until_complete(test_check_slash_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_post_slash_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_post_slash_endpoint_is_working():
                resp = await client.post("/api")
                assert resp.status == 200
            loop.run_until_complete(test_check_post_slash_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_info_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_info_endpoint_is_working():
                resp = await client.get("/api/info")
                assert resp.status == 200
            loop.run_until_complete(test_check_info_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_post_info_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_post_info_endpoint_is_working():
                resp = await client.post("/api/info")
                assert resp.status == 200
            loop.run_until_complete(test_check_post_info_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_service_info_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_service_info_endpoint_is_working():
                resp = await client.get("/api/service-info")
                assert resp.status == 200
            loop.run_until_complete(test_check_service_info_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_post_service_info_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_post_service_info_endpoint_is_working():
                resp = await client.post("/api/service-info")
                assert resp.status == 200
            loop.run_until_complete(test_check_post_service_info_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_entry_types_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_entry_types_endpoint_is_working():
                resp = await client.get("/api/entry_types")
                assert resp.status == 200
            loop.run_until_complete(test_check_entry_types_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_post_entry_types_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_post_entry_types_endpoint_is_working():
                resp = await client.post("/api/entry_types")
                assert resp.status == 200
            loop.run_until_complete(test_check_post_entry_types_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_configuration_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_endpoint_is_working():
                resp = await client.get("/api/configuration")
                assert resp.status == 200
            loop.run_until_complete(test_check_configuration_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_post_configuration_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_post_configuration_endpoint_is_working():
                resp = await client.post("/api/configuration")
                assert resp.status == 200
            loop.run_until_complete(test_check_post_configuration_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_map_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_map_endpoint_is_working():
                resp = await client.get("/api/map")
                assert resp.status == 200
            loop.run_until_complete(test_check_map_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_post_map_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_post_map_endpoint_is_working():
                resp = await client.post("/api/map")
                assert resp.status == 200
            loop.run_until_complete(test_check_post_map_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_filtering_terms_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_filtering_terms_endpoint_is_working():
                resp = await client.get("/api/filtering_terms")
                assert resp.status == 200
            loop.run_until_complete(test_check_filtering_terms_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_post_filtering_terms_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_post_filtering_terms_endpoint_is_working():
                resp = await client.post("/api/filtering_terms")
                assert resp.status == 200
            loop.run_until_complete(test_check_post_filtering_terms_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_datasets_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_datasets_endpoint_is_working():
                resp = await client.get("/api/datasets")
                assert resp.status == 200
            loop.run_until_complete(test_check_datasets_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_post_datasets_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_post_datasets_endpoint_is_working():
                resp = await client.post("/api/datasets")
                assert resp.status == 200
            loop.run_until_complete(test_check_post_datasets_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_endpoint_is_working():
                resp = await client.get("/api/g_variants")
                assert resp.status == 200
            loop.run_until_complete(test_check_g_variants_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_analyses_with_limit_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_analyses_with_limit_endpoint_is_working():
                resp = await client.get("/api/analyses?limit=200")
                assert resp.status == 200
            loop.run_until_complete(test_check_analyses_with_limit_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_analyses_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_analyses_endpoint_is_working():
                resp = await client.get("/api/analyses")
                assert resp.status == 200
            loop.run_until_complete(test_check_analyses_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_analyses_with_id_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_analyses_with_id_endpoint_is_working():
                resp = await client.get("/api/analyses/EGA-testing")
                assert resp.status == 200
            loop.run_until_complete(test_check_analyses_with_id_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_analyses_g_variants_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_analyses_g_variants_endpoint_is_working():
                resp = await client.get("/api/analyses/EGA-testing/g_variants")
                assert resp.status == 200
            loop.run_until_complete(test_check_analyses_g_variants_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_biosamples_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_biosamples_endpoint_is_working():
                resp = await client.get("/api/biosamples")
                assert resp.status == 200
            loop.run_until_complete(test_check_biosamples_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_biosamples_with_limit_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_biosamples_with_limit_endpoint_is_working():
                resp = await client.get("/api/biosamples?limit=200")
                assert resp.status == 200
            loop.run_until_complete(test_check_biosamples_with_limit_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_biosamples_with_id_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_biosamples_with_id_endpoint_is_working():
                resp = await client.get("/api/biosamples/SAMPLE3")
                assert resp.status == 200
            loop.run_until_complete(test_check_biosamples_with_id_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_biosamples_g_variants_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_biosamples_g_variants_endpoint_is_working():
                resp = await client.get("/api/biosamples/SAMPLE3/g_variants")
                assert resp.status == 200
            loop.run_until_complete(test_check_biosamples_g_variants_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_biosamples_runs_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_biosamples_runs_endpoint_is_working():
                resp = await client.get("/api/biosamples/SAMPLE1/runs")
                assert resp.status == 200
            loop.run_until_complete(test_check_biosamples_runs_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_biosamples_analyses_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_biosamples_analyses_endpoint_is_working():
                resp = await client.get("/api/biosamples/SAMPLE1/analyses")
                assert resp.status == 200
            loop.run_until_complete(test_check_biosamples_analyses_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_individuals_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_individuals_endpoint_is_working():
                resp = await client.get("/api/individuals")
                assert resp.status == 200
            loop.run_until_complete(test_check_individuals_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_individuals_with_limit_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_individuals_with_limit_endpoint_is_working():
                resp = await client.get("/api/individuals?limit=200")
                assert resp.status == 200
            loop.run_until_complete(test_check_individuals_with_limit_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_individuals_with_id_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_individuals_with_id_endpoint_is_working():
                resp = await client.get("/api/individuals/SAMPLE2")
                assert resp.status == 200
            loop.run_until_complete(test_check_individuals_with_id_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_individuals_g_variants_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_individuals_g_variants_endpoint_is_working():
                resp = await client.get("/api/individuals/SAMPLE2/g_variants")
                assert resp.status == 200
            loop.run_until_complete(test_check_individuals_g_variants_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_individuals_biosamples_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_individuals_biosamples_endpoint_is_working():
                resp = await client.get("/api/individuals/SAMPLE2/biosamples")
                assert resp.status == 200
            loop.run_until_complete(test_check_individuals_biosamples_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_runs_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_runs_endpoint_is_working():
                resp = await client.get("/api/runs")
                assert resp.status == 200
            loop.run_until_complete(test_check_runs_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_runs_with_limit_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_runs_with_limit_endpoint_is_working():
                resp = await client.get("/api/runs?limit=200")
                assert resp.status == 200
            loop.run_until_complete(test_check_runs_with_limit_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_runs_with_id_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_runs_with_id_endpoint_is_working():
                resp = await client.get("/api/runs/EGA-testing")
                assert resp.status == 200
            loop.run_until_complete(test_check_runs_with_id_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_runs_g_variants_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_runs_g_variants_endpoint_is_working():
                resp = await client.get("/api/runs/EGA-testing/g_variants")
                assert resp.status == 200
            loop.run_until_complete(test_check_runs_g_variants_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_runs_analyses_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_runs_analyses_endpoint_is_working():
                resp = await client.get("/api/runs/EGA-testing/analyses")
                assert resp.status == 200
            loop.run_until_complete(test_check_runs_analyses_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_cohorts_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_cohorts_endpoint_is_working():
                resp = await client.get("/api/cohorts")
                assert resp.status == 200
            loop.run_until_complete(test_check_cohorts_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_cohorts_with_limit_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_cohorts_with_limit_endpoint_is_working():
                resp = await client.get("/api/cohorts?limit=200")
                assert resp.status == 200
            loop.run_until_complete(test_check_cohorts_with_limit_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_cohorts_with_id_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_cohorts_with_id_endpoint_is_working():
                resp = await client.get("/api/cohorts/EGA-testing")
                assert resp.status == 200
            loop.run_until_complete(test_check_cohorts_with_id_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_cohorts_runs_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_cohorts_runs_endpoint_is_working():
                resp = await client.get("/api/cohorts/EGA-testing/runs")
                assert resp.status == 200
            loop.run_until_complete(test_check_cohorts_runs_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_cohorts_biosamples_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_cohorts_biosamples_endpoint_is_working():
                resp = await client.get("/api/cohorts/EGA-testing/biosamples")
                assert resp.status == 200
            loop.run_until_complete(test_check_cohorts_biosamples_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_cohorts_analyses_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_cohorts_analyses_endpoint_is_working():
                resp = await client.get("/api/cohorts/EGA-testing/analyses")
                assert resp.status == 200
            loop.run_until_complete(test_check_cohorts_analyses_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_cohorts_individuals_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_cohorts_inividuals_endpoint_is_working():
                resp = await client.get("/api/cohorts/EGA-testing/individuals")
                assert resp.status == 200
            loop.run_until_complete(test_check_cohorts_inividuals_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_cohorts_g_variants_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_cohorts_g_variants_endpoint_is_working():
                resp = await client.get("/api/cohorts/EGA-testing/g_variants")
                assert resp.status == 200
            loop.run_until_complete(test_check_cohorts_g_variants_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_datasets_with_limit_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_datasets_with_limit_endpoint_is_working():
                resp = await client.get("/api/datasets?limit=200")
                assert resp.status == 200
            loop.run_until_complete(test_check_datasets_with_limit_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_datasets_with_id_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_datasets_with_id_endpoint_is_working():
                resp = await client.get("/api/datasets/synthetic_usecases_4beacon_testingV3")
                assert resp.status == 200
            loop.run_until_complete(test_check_datasets_with_id_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_datasets_runs_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_datasets_runs_endpoint_is_working():
                resp = await client.get("/api/datasets/synthetic_usecases_4beacon_testingV3/runs")
                assert resp.status == 200
            loop.run_until_complete(test_check_datasets_runs_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_datasets_g_variants_2_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_datasets_g_variants_endpoint_is_working():
                resp = await client.get("/api/datasets/synthetic_usecases_4beacon_testingV3/g_variants")
                assert resp.status == 200
            loop.run_until_complete(test_check_datasets_g_variants_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_datasets_biosamples_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_datasets_biosamples_endpoint_is_working():
                resp = await client.get("/api/datasets/synthetic_usecases_4beacon_testingV3/biosamples")
                assert resp.status == 200
            loop.run_until_complete(test_check_datasets_biosamples_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_datasets_analyses_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_datasets_analyses_endpoint_is_working():
                resp = await client.get("/api/datasets/synthetic_usecases_4beacon_testingV3/analyses")
                assert resp.status == 200
            loop.run_until_complete(test_check_datasets_analyses_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_datasets_individuals_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_datasets_inividuals_endpoint_is_working():
                resp = await client.get("/api/datasets/synthetic_usecases_4beacon_testingV3/individuals")
                assert resp.status == 200
            loop.run_until_complete(test_check_datasets_inividuals_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_with_limit_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_with_limit_endpoint_is_working():
                resp = await client.get("/api/g_variants?limit=200")
                assert resp.status == 200
            loop.run_until_complete(test_check_g_variants_with_limit_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_with_id_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_with_id_endpoint_is_working():
                resp = await client.get("/api/g_variants/beffb86a-d809-11ef-bdb1-0242ac130002:G:A")
                assert resp.status == 200
            loop.run_until_complete(test_check_g_variants_with_id_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_runs_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_runs_endpoint_is_working():
                resp = await client.get("/api/g_variants/beffb86a-d809-11ef-bdb1-0242ac130002:G:A/runs")
                assert resp.status == 200
            loop.run_until_complete(test_check_g_variants_runs_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_biosamples_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_biosamples_endpoint_is_working():
                resp = await client.get("/api/g_variants/beffb86a-d809-11ef-bdb1-0242ac130002:G:A/biosamples")
                assert resp.status == 200
            loop.run_until_complete(test_check_g_variants_biosamples_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_analyses_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_analyses_endpoint_is_working():
                resp = await client.get("/api/g_variants/beffb86a-d809-11ef-bdb1-0242ac130002:G:A/analyses")
                assert resp.status == 200
            loop.run_until_complete(test_check_g_variants_analyses_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_individuals_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_inividuals_endpoint_is_working():
                resp = await client.get("/api/g_variants/beffb86a-d809-11ef-bdb1-0242ac130002:G:A/individuals")
                assert resp.status == 200
            loop.run_until_complete(test_check_g_variants_inividuals_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_endpoint_NONE_resultSetResponse_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_endpoint_NONE_resultSetResponse_is_working():
                resp = await client.get("/api/g_variants?includeResultsetResponses=NONE")
                assert resp.status == 200
            loop.run_until_complete(test_check_g_variants_endpoint_NONE_resultSetResponse_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_endpoint_MISS_resultSetResponse_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_endpoint_MISS_resultSetResponse_is_working():
                resp = await client.get("/api/g_variants?includeResultsetResponses=MISS")
                assert resp.status == 200
            loop.run_until_complete(test_check_g_variants_endpoint_MISS_resultSetResponse_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_endpoint_ALL_resultSetResponse_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_endpoint_ALL_resultSetResponse_is_working():
                resp = await client.get("/api/g_variants?includeResultsetResponses=ALL")
                assert resp.status == 200
            loop.run_until_complete(test_check_g_variants_endpoint_ALL_resultSetResponse_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_sequence_query(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_endpoint_with_parameters_is_working():
                resp = await client.get("/api/g_variants?start=43045703&referenceName=17&assemblyId=GRCh38&referenceBases=G&alternateBases=A")
                assert resp.status == 200
            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_range_query(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_endpoint_with_parameters_is_working():
                resp = await client.get("/api/g_variants?start=345675&referenceName=2&assemblyId=GRCh38&end=345681")
                assert resp.status == 200
            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_geneId_query(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_endpoint_with_parameters_is_working():
                resp = await client.get("/api/g_variants?geneId=BRCA1")
                assert resp.status == 200
            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_bracket_query(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_endpoint_with_parameters_is_working():
                resp = await client.get("/api/g_variants?start=43045703,43045704&end=43045704,43045705&referenceName=17&assemblyId=GRCh38")
                assert resp.status == 200
            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_genomic_allele_query(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_endpoint_with_parameters_is_working():
                resp = await client.get("/api/g_variants?genomicAlleleShortForm=NC_000017.11:g.43045703G>A")
                assert resp.status == 200
            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_aminoacidChange_query(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_endpoint_with_parameters_is_working():
                resp = await client.get("/api/g_variants?aminoacidChange=Pro1856Ser&geneId=BRCA1")
                assert resp.status == 200
            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_post_cross_query_individuals_g_variants_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_post_cross_query_g_variants_individuals_is_working():
                resp = await client.post("/api/g_variants", json={"meta": {
                    "apiVersion": "2.0"
                },
                "query": { "requestParameters": {        },
                    "filters": [
            {"id":"NCIT:C16576", "scope":"individual"}],
                    "includeResultsetResponses": "HIT",
                    "pagination": {
                        "skip": 0,
                        "limit": 10
                    },
                    "testMode": True,
                    "requestedGranularity": "record"
                }
                })
                assert resp.status == 200
            loop.run_until_complete(test_check_post_cross_query_g_variants_individuals_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_post_cross_query_individuals_biosamples_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_post_cross_query_biosamples_individuals_is_working():
                resp = await client.post("/api/biosamples", json={"meta": {
                    "apiVersion": "2.0"
                },
                "query": { "requestParameters": {        },
                    "filters": [
            {"id":"NCIT:C16576", "scope":"individual"}],
                    "includeResultsetResponses": "HIT",
                    "pagination": {
                        "skip": 0,
                        "limit": 10
                    },
                    "testMode": True,
                    "requestedGranularity": "record"
                }
                })
                responsetext=await resp.text()
                responsedict=json.loads(responsetext)
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
                resp = await client.get("/api/g_variants?star=12448")
                assert resp.status == 400
            loop.run_until_complete(test_check_request_parameters_fail())
            loop.run_until_complete(client.close())# pragma: no cover
    def test_main_check_wrong_combination_request_parameters(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_wrong_combination_request_parameters():
                resp = await client.get("/api/g_variants?start=12448")
                assert resp.status == 400
            loop.run_until_complete(test_wrong_combination_request_parameters())
            loop.run_until_complete(client.close())# pragma: no cover
    def test_main_check_datasets_g_variants_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_datasets_g_variants_endpoint_is_working():
                resp = await client.get("/api/g_variants?datasets=synthetic_usecases_4beacon_testingV3")
                assert resp.status == 200
            loop.run_until_complete(test_check_datasets_g_variants_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_cross_query_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_cross_query_is_working():
                MagicClass = MagicMock(_id='hohoho')
                resp = cross_query(MagicClass, {'$or': [{'ethnicity.id': 'NCIT:C43851'}]}, 'individual', 'biosamples', {}, 'synthetic_usecases_4beacon_testingV3')
                assert resp != {}
            loop.run_until_complete(test_check_cross_query_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_cross_query_3_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_cross_query_3_is_working():
                MagicClass = MagicMock(_id='hohoho')
                resp = cross_query(MagicClass, {'$or': [{'ethnicity.id': 'NCIT:C43851'}]}, 'individual', 'g_variants', {}, 'synthetic_usecases_4beacon_testingV3')
                assert resp != {}
            loop.run_until_complete(test_check_cross_query_3_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_cross_query_7_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_cross_query_7_is_working():
                MagicClass = MagicMock(_id='hohoho')
                resp = cross_query(MagicClass, {'$or': [{'platformModel.id': 'OBI:0002048'}]}, 'run', 'individuals', {}, 'synthetic_usecases_4beacon_testingV3')
                assert resp != {}
            loop.run_until_complete(test_check_cross_query_7_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_cross_query_8_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_cross_query_8_is_working():
                MagicClass = MagicMock(_id='hohoho')
                resp = cross_query(MagicClass, {'$or': [{'platformModel.id': 'OBI:0002048'}]}, 'run', 'biosamples', {}, 'synthetic_usecases_4beacon_testingV3')
                assert resp != {}
            loop.run_until_complete(test_check_cross_query_8_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_cross_query_9_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_cross_query_9_is_working():
                MagicClass = MagicMock(_id='hohoho')
                resp = cross_query(MagicClass, {'$or': [{'platformModel.id': 'OBI:0002048'}]}, 'run', 'g_variants', {}, 'synthetic_usecases_4beacon_testingV3')
                assert resp != {}
            loop.run_until_complete(test_check_cross_query_9_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_alphanumeric_equal_query_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_alphanumeric_equal_query_is_working():
                resp = await client.post("/api/individuals", json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": { "requestParameters": {        },
                    "filters": [
            {"id": "ethnicity",
                    "operator": "=",
                    "value": "European",
            "scope":"individual"}],
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
            loop.run_until_complete(test_check_alphanumeric_equal_query_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_alphanumeric_like_query_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_alphanumeric_like_query_is_working():
                resp = await client.post("/api/individuals", json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": { "requestParameters": {        },
                    "filters": [
            {"id": "ethnicity",
                    "operator": "=",
                    "value": "%pean%",
            "scope":"individual"}],
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
            loop.run_until_complete(test_check_alphanumeric_like_query_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_alphanumeric_not_like_query_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_alphanumeric_not_like_query_is_working():
                resp = await client.post("/api/individuals", json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": { "requestParameters": {        },
                    "filters": [
            {"id": "ethnicity",
                    "operator": "!",
                    "value": "%uropean%",
            "scope":"individual"}],
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
            loop.run_until_complete(test_check_alphanumeric_not_like_query_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_alphanumeric_not_query_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_alphanumeric_not_query_is_working():
                resp = await client.post("/api/individuals", json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": { "requestParameters": {        },
                    "filters": [
            {"id": "ethnicity",
                    "operator": "!",
                    "value": "European",
            "scope":"individual"}],
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
            loop.run_until_complete(test_check_alphanumeric_not_query_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_iso8601duration_gt_query_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_iso8601duration_gt_query_is_working():
                resp = await client.post("/api/individuals", json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": { "requestParameters": {        },
                    "filters": [
            {"id": "exposures.ageAtExposure.iso8601duration",
                    "operator": ">",
                    "value": "31",
            "scope":"individual"}],
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
            loop.run_until_complete(test_check_iso8601duration_gt_query_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_iso8601duration_ls_query_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_iso8601duration_ls_query_is_working():
                resp = await client.post("/api/individuals", json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": { "requestParameters": {        },
                    "filters": [
            {"id": "exposures.ageAtExposure.iso8601duration",
                    "operator": "<",
                    "value": "33",
            "scope":"individual"}],
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
            loop.run_until_complete(test_check_iso8601duration_ls_query_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_iso8601duration_eq_query_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_iso8601duration_eq_query_is_working():
                resp = await client.post("/api/individuals", json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": { "requestParameters": {        },
                    "filters": [
            {"id": "exposures.ageAtExposure.iso8601duration",
                    "operator": "=",
                    "value": "34",
            "scope":"individual"}],
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
            loop.run_until_complete(test_check_iso8601duration_eq_query_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_measurement_value_query_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_measurement_value_query_is_working():
                resp = await client.post("/api/individuals", json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": { "requestParameters": {        },
                    "filters": [
                            {
                        "id": "anatomical entity",
                        "operator": ">",
                        "value": "44"
                    }, 
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
            loop.run_until_complete(test_check_measurement_value_query_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_custom_query_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_custom_query_is_working():
                resp = await client.post("/api/biosamples", json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": { "requestParameters": {        },
                    "filters": [
                            {
                        "id": "sampleOriginType:ovary"
                    } 
                , 
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
            loop.run_until_complete(test_check_custom_query_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_range_query_with_variant_min_and_max_lengths_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_range_query_with_variant_min_and_max_lengths_working():
                resp = await client.get("/api/g_variants?start=345675&referenceName=2&assemblyId=GRCh38&end=345681&variantMinLength=0&variantMaxLength=10&testMode=true")
                assert resp.status == 200
            loop.run_until_complete(test_check_range_query_with_variant_min_and_max_lengths_working())
            loop.run_until_complete(client.close())
    def test_main_check_filters_as_request_parameter_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_filters_as_request_parameter_working():
                resp = await client.get("/api/individuals?filters=NCIT:C16576&testMode=true")
                assert resp.status == 200
            loop.run_until_complete(test_check_filters_as_request_parameter_working())
            loop.run_until_complete(client.close())
    def test_main_check_datasets_list_query_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_datasets_list_query_is_working():
                resp = await client.post("/api/individuals", json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": { "requestParameters": {
                "datasets": ["synthetic_usecases_4beacon_testingV3"]
                },
                    "filters": [                ],
                    "includeResultsetResponses": "HIT",
                    "pagination": {
                        "skip": 0,
                        "limit": 101
                    },
                    "testMode": True,
                    "requestedGranularity": "record"
                }
            }
            )

                assert resp.status == 200
            loop.run_until_complete(test_check_datasets_list_query_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_range_query_with_variant_assemblyId_GRCh38_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_range_query_with_variant_assemblyId_GRCh38_working():
                resp = await client.get("/api/g_variants?start=16050074&end=16050075&assemblyId=GRCh38&referenceName=22")
                assert resp.status == 200
            loop.run_until_complete(test_check_range_query_with_variant_assemblyId_GRCh38_working())
            loop.run_until_complete(client.close())
    def test_main_check_range_query_with_variant_assemblyId_GRCh37_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_range_query_with_variant_assemblyId_GRCh37_working():
                resp = await client.get("/api/g_variants?start=16050074&end=16050075&assemblyId=GRCh37&referenceName=22")
                assert resp.status == 200
            loop.run_until_complete(test_check_range_query_with_variant_assemblyId_GRCh37_working())
            loop.run_until_complete(client.close())
    def test_main_check_range_query_with_variant_assemblyId_NCBI36_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_range_query_with_variant_assemblyId_NCBI36_working():
                resp = await client.get("/api/g_variants?start=16050074&end=16050075&assemblyId=NCBI36&referenceName=22")
                assert resp.status == 200
            loop.run_until_complete(test_check_range_query_with_variant_assemblyId_NCBI36_working())
            loop.run_until_complete(client.close())
    def test_main_check_NONE_count_query_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_NONE_count_query_is_working():
                resp = await client.post("/api/individuals", json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": { "requestParameters": {        },
                    "filters": [
            {"id": "ethnicity",
                    "operator": "=",
                    "value": "European",
            "scope":"individual"}],
                    "includeResultsetResponses": "NONE",
                    "pagination": {
                        "skip": 0,
                        "limit": 10
                    },
                    "testMode": True,
                    "requestedGranularity": "count"
                }
            }
            )

                assert resp.status == 200
            loop.run_until_complete(test_check_NONE_count_query_is_working())
            loop.run_until_complete(client.close())
    def test_individuals_variants_with_heterozygosity(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_heterozygosity():
                resp = await client.post("/api/g_variants/beffb86a-d809-11ef-bdb1-0242ac130002:G:A/individuals", json={
                    "meta": {
                        "apiVersion": "2.0"
                    },
                    "query":{ "requestParameters": {
                    
                        },
                        "filters": [
                {"id":"GENO:0000458"}],
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
            loop.run_until_complete(test_check_heterozygosity())
            loop.run_until_complete(client.close())
    def test_individuals_variants_with_homozygosity(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_homozygosity():
                resp = await client.post("/api/g_variants/beffb86a-d809-11ef-bdb1-0242ac130002:G:A/individuals", json={
                    "meta": {
                        "apiVersion": "2.0"
                    },
                    "query":{ "requestParameters": {
                    
                        },
                        "filters": [
                {"id":"GENO:0000136"}],
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
            loop.run_until_complete(test_check_homozygosity())
            loop.run_until_complete(client.close())
    def test_individuals_variants_with_filter(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_individuals_variants():
                resp = await client.post("/api/g_variants/beffb86a-d809-11ef-bdb1-0242ac130002:G:A/individuals", json={
                    "meta": {
                        "apiVersion": "2.0"
                    },
                    "query":{ "requestParameters": {
                    
                        },
                        "filters": [ {"id": "NCIT:C16576", "scope": "individual"}
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
            loop.run_until_complete(test_check_individuals_variants())
            loop.run_until_complete(client.close())
    def test_analyses_variants_with_heterozygosity(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_heterozygosity():
                resp = await client.post("/api/g_variants/beffb86a-d809-11ef-bdb1-0242ac130002:G:A/analyses", json={
                    "meta": {
                        "apiVersion": "2.0"
                    },
                    "query":{ "requestParameters": {
                    
                        },
                        "filters": [
                {"id":"GENO:0000458"}],
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
            loop.run_until_complete(test_check_heterozygosity())
            loop.run_until_complete(client.close())
    def test_analyses_variants_with_homozygosity(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_homozygosity():
                resp = await client.post("/api/g_variants/beffb86a-d809-11ef-bdb1-0242ac130002:G:A/analyses", json={
                    "meta": {
                        "apiVersion": "2.0"
                    },
                    "query":{ "requestParameters": {
                    
                        },
                        "filters": [
                {"id":"GENO:0000136"}],
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
            loop.run_until_complete(test_check_homozygosity())
            loop.run_until_complete(client.close())
    def test_analyses_variants_with_filter(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_analyses_variants():
                resp = await client.post("/api/g_variants/beffb86a-d809-11ef-bdb1-0242ac130002:G:A/analyses", json={
                    "meta": {
                        "apiVersion": "2.0"
                    },
                    "query":{ "requestParameters": {
                    
                        },
                        "filters": [ {"id": "NCIT:C16576", "scope": "individual"}
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
            loop.run_until_complete(test_check_analyses_variants())
            loop.run_until_complete(client.close())
    def test_biosamples_variants_with_heterozygosity(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_heterozygosity():
                resp = await client.post("/api/g_variants/beffb86a-d809-11ef-bdb1-0242ac130002:G:A/biosamples", json={
                    "meta": {
                        "apiVersion": "2.0"
                    },
                    "query":{ "requestParameters": {
                    
                        },
                        "filters": [
                {"id":"GENO:0000458"}],
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
            loop.run_until_complete(test_check_heterozygosity())
            loop.run_until_complete(client.close())
    def test_biosamples_variants_with_homozygosity(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_homozygosity():
                resp = await client.post("/api/g_variants/beffb86a-d809-11ef-bdb1-0242ac130002:G:A/biosamples", json={
                    "meta": {
                        "apiVersion": "2.0"
                    },
                    "query":{ "requestParameters": {
                    
                        },
                        "filters": [
                {"id":"GENO:0000136"}],
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
            loop.run_until_complete(test_check_homozygosity())
            loop.run_until_complete(client.close())
    def test_biosamples_variants_with_filter(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_biosamples_variants():
                resp = await client.post("/api/g_variants/beffb86a-d809-11ef-bdb1-0242ac130002:G:A/biosamples", json={
                    "meta": {
                        "apiVersion": "2.0"
                    },
                    "query":{ "requestParameters": {
                    
                        },
                        "filters": [ {"id": "NCIT:C16576", "scope": "individual"}
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
            loop.run_until_complete(test_check_biosamples_variants())
            loop.run_until_complete(client.close())
    def test_runs_variants_with_heterozygosity(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_heterozygosity():
                resp = await client.post("/api/g_variants/beffb86a-d809-11ef-bdb1-0242ac130002:G:A/runs", json={
                    "meta": {
                        "apiVersion": "2.0"
                    },
                    "query":{ "requestParameters": {
                    
                        },
                        "filters": [
                {"id":"GENO:0000458"}],
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
            loop.run_until_complete(test_check_heterozygosity())
            loop.run_until_complete(client.close())
    def test_runs_variants_with_homozygosity(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_homozygosity():
                resp = await client.post("/api/g_variants/beffb86a-d809-11ef-bdb1-0242ac130002:G:A/runs", json={
                    "meta": {
                        "apiVersion": "2.0"
                    },
                    "query":{ "requestParameters": {
                    
                        },
                        "filters": [
                {"id":"GENO:0000136"}],
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
            loop.run_until_complete(test_check_homozygosity())
            loop.run_until_complete(client.close())
    def test_runs_variants_with_filter(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_runs_variants():
                resp = await client.post("/api/g_variants/beffb86a-d809-11ef-bdb1-0242ac130002:G:A/runs", json={
                    "meta": {
                        "apiVersion": "2.0"
                    },
                    "query":{ "requestParameters": {
                    
                        },
                        "filters": [ {"id": "NCIT:C16576", "scope": "individual"}
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
            loop.run_until_complete(test_check_runs_variants())
            loop.run_until_complete(client.close())
    def test_individuals_with_variant_filter(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_individuals_variants():
                resp = await client.post("/api/individuals", json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": { "requestParameters": {        },
                    "filters": [
            {"id":"ENSGLOSSARY:0000150", "scope":"genomicVariation"}],
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
            loop.run_until_complete(test_check_individuals_variants())
            loop.run_until_complete(client.close())
    def test_biosamples_with_variant_filter(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_biosamples_variants():
                resp = await client.post("/api/biosamples", json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": { "requestParameters": {        },
                    "filters": [
            {"id":"ENSGLOSSARY:0000150", "scope":"genomicVariation"}],
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
            loop.run_until_complete(test_check_biosamples_variants())
            loop.run_until_complete(client.close())
    def test_analyses_with_variant_filter(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_analyses_variants():
                resp = await client.post("/api/analyses", json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": { "requestParameters": {        },
                    "filters": [
            {"id":"ENSGLOSSARY:0000150", "scope":"genomicVariation"}],
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
            loop.run_until_complete(test_check_analyses_variants())
            loop.run_until_complete(client.close())
    def test_runs_with_variant_filter(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_runs_variants():
                resp = await client.post("/api/runs", json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": { "requestParameters": {        },
                    "filters": [
            {"id":"ENSGLOSSARY:0000150", "scope":"genomicVariation"}],
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
            loop.run_until_complete(test_check_runs_variants())
            loop.run_until_complete(client.close())
    def test_variants_with_run_filter(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_runs_variants():
                resp = await client.post("/api/g_variants", json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": { "requestParameters": {        },
                    "filters": [
            {"id":"GENEPIO:0001966", "scope":"run"}],
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
            loop.run_until_complete(test_check_runs_variants())
            loop.run_until_complete(client.close())
    def test_individuals_with_run_filter(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_runs_variants():
                resp = await client.post("/api/individuals", json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query":{ "requestParameters": {
                
                    },
                    "filters": [
            {"id":"GENEPIO:0001966", "scope":"run"}],
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
            loop.run_until_complete(test_check_runs_variants())
            loop.run_until_complete(client.close())
    def test_analyses_with_run_filter(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_runs_variants():
                resp = await client.post("/api/analyses", json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query":{ "requestParameters": {
                
                    },
                    "filters": [
            {"id":"GENEPIO:0001966", "scope":"run"}],
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
            loop.run_until_complete(test_check_runs_variants())
            loop.run_until_complete(client.close())
    def test_biosamples_with_run_filter(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_runs_variants():
                resp = await client.post("/api/biosamples", json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query":{ "requestParameters": {
                
                    },
                    "filters": [
            {"id":"GENEPIO:0001966", "scope":"run"}],
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
            loop.run_until_complete(test_check_runs_variants())
            loop.run_until_complete(client.close())
    def test_variants_with_biosample_filter(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_runs_variants():
                resp = await client.post("/api/g_variants", json={
            "meta": {
                "apiVersion": "2.0"
            },
            "query":{ "requestParameters": {
            
                },
                "filters": [
        {"id":"EFO:0009655", "scope":"biosample"}],
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
            loop.run_until_complete(test_check_runs_variants())
            loop.run_until_complete(client.close())
    def test_individuals_with_biosample_filter(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_runs_variants():
                resp = await client.post("/api/individuals", json={
            "meta": {
                "apiVersion": "2.0"
            },
            "query":{ "requestParameters": {
            
                },
                "filters": [
        {"id":"EFO:0009655", "scope":"biosample"}],
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
            loop.run_until_complete(test_check_runs_variants())
            loop.run_until_complete(client.close())
    def test_analyses_with_biosample_filter(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_runs_variants():
                resp = await client.post("/api/analyses", json={
            "meta": {
                "apiVersion": "2.0"
            },
            "query":{ "requestParameters": {
            
                },
                "filters": [
        {"id":"EFO:0009655", "scope":"biosample"}],
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
            loop.run_until_complete(test_check_runs_variants())
            loop.run_until_complete(client.close())
    def test_runs_with_biosample_filter(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_runs_variants():
                resp = await client.post("/api/runs", json={
            "meta": {
                "apiVersion": "2.0"
            },
            "query":{ "requestParameters": {
            
                },
                "filters": [
        {"id":"EFO:0009655", "scope":"biosample"}],
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
            loop.run_until_complete(test_check_runs_variants())
            loop.run_until_complete(client.close())
    def test_individuals_with_request_parameters(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_runs_variants():
                resp = await client.post("/api/individuals", json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": {
                    "requestParameters": {
                    "alternateBases": "A" ,
                "referenceBases": "G" ,
            "start": [43045703],
                        "referenceName": "17",
            "assemblyId": "GRCh38"
            },        
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
            loop.run_until_complete(test_check_runs_variants())
            loop.run_until_complete(client.close())
    def test_biosamples_with_request_parameters(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_runs_variants():
                resp = await client.post("/api/biosamples", json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": {
                    "requestParameters": {
                    "alternateBases": "A" ,
                "referenceBases": "G" ,
            "start": [43045703],
                        "referenceName": "17",
            "assemblyId": "GRCh38"
            },        
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
            loop.run_until_complete(test_check_runs_variants())
            loop.run_until_complete(client.close())
    def test_analyses_with_request_parameters(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_runs_variants():
                resp = await client.post("/api/analyses", json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": {
                    "requestParameters": {
                    "alternateBases": "A" ,
                "referenceBases": "G" ,
            "start": [43045703],
                        "referenceName": "17",
            "assemblyId": "GRCh38"
            },        
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
            loop.run_until_complete(test_check_runs_variants())
            loop.run_until_complete(client.close())
    def test_variants_with_request_parameters_and_filters(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_runs_variants():
                resp = await client.post("/api/g_variants", json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": {
                    "requestParameters": {
                    "alternateBases": "A" ,
                "referenceBases": "G" ,
            "start": [43045703],
                        "referenceName": "17",
            "assemblyId": "GRCh38"
            },        
            "filters": [{"id":"ENSGLOSSARY:0000150", "scope":"genomicVariation"}],
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
            loop.run_until_complete(test_check_runs_variants())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_sequence_query_fails(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_endpoint_with_parameters_is_working():
                resp = await client.get("/api/g_variants?start=43045703&referenceName=17&referenceBases=G&alternateBases=A")
                assert resp.status == 400
            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())# pragma: no cover
    def test_main_check_g_variants_range_query_fails(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_endpoint_with_parameters_is_working():
                resp = await client.get("/api/g_variants?start=345675&referenceName=2&end=345681")
                assert resp.status == 400
            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())# pragma: no cover
    def test_main_check_g_variants_bracket_query_fails(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_endpoint_with_parameters_is_working():
                resp = await client.get("/api/g_variants?start=43045703,43045704&end=43045704,43045705&referenceName=17")
                assert resp.status == 400
            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())# pragma: no cover
    def test_main_check_test_mode_fails(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_endpoint_with_parameters_is_working():
                resp = await client.get("/api/g_variants?start=43045703,43045704&end=43045704,43045705&referenceName=17&assemblyId=GRCh38&testMode=3")
                assert resp.status == 400
            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())# pragma: no cover
    def test_descendant_terms(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_runs_variants():
                resp = await client.post("/api/individuals", json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query":{ "requestParameters": {
                
                    },
                    "filters": [
            {"id":"MONDO:0004975", "scope":"individual", "includeDescendantTerms": True}],
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
            loop.run_until_complete(test_check_runs_variants())
            loop.run_until_complete(client.close())# pragma: no cover
    def test_main_check_g_variants_range_query_chrX(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_endpoint_with_parameters_is_working():
                resp = await client.get("/api/g_variants?start=31121923&referenceName=X&assemblyId=GRCh38&end=31121924")
                assert resp.status == 200
            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())# pragma: no cover
    def test_main_check_g_variants_range_query_chrY(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_endpoint_with_parameters_is_working():
                resp = await client.get("/api/g_variants?start=31121923&referenceName=Y&assemblyId=GRCh38&end=31121924")
                assert resp.status == 200
            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())# pragma: no cover

if __name__ == '__main__':
    unittest.main()