from aiohttp.test_utils import TestClient, TestServer, loop_context
from beacon.tests.__main__ import create_app
import json
import unittest
import beacon.conf.conf_override as conf_override
from beacon.logs.logs import LOG
from beacon.validator.configuration import check_configuration

class TestNoFilters(unittest.TestCase):
    def test_no_filters_analysis_query_without_filters_allowed(self):
        with loop_context() as loop:
            from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import analysis
            analysis.allow_queries_without_filters=False
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_analysis_query_without_filters_allowed():
                resp = await client.get(conf_override.config.uri_subpath+"/"+analysis.endpoint_name)
                assert resp.status == 400
            loop.run_until_complete(test_analysis_query_without_filters_allowed())
            loop.run_until_complete(client.close())
            analysis.allow_queries_without_filters=True
    def test_no_filters_biosample_query_without_filters_allowed(self):
        with loop_context() as loop:
            from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import biosample
            biosample.allow_queries_without_filters=False
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_biosample_query_without_filters_allowed():
                resp = await client.get(conf_override.config.uri_subpath+"/"+biosample.endpoint_name)
                assert resp.status == 400
            loop.run_until_complete(test_biosample_query_without_filters_allowed())
            loop.run_until_complete(client.close())
            biosample.allow_queries_without_filters=True
    def test_no_filters_cohort_query_without_filters_allowed(self):
        with loop_context() as loop:
            from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import cohort
            cohort.allow_queries_without_filters=False
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_cohort_query_without_filters_allowed():
                resp = await client.get(conf_override.config.uri_subpath+"/"+cohort.endpoint_name)
                assert resp.status == 400
            loop.run_until_complete(test_cohort_query_without_filters_allowed())
            loop.run_until_complete(client.close())
            cohort.allow_queries_without_filters=True
    def test_no_filters_dataset_query_without_filters_allowed(self):
        with loop_context() as loop:
            from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import dataset
            dataset.allow_queries_without_filters=False
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_dataset_query_without_filters_allowed():
                resp = await client.get(conf_override.config.uri_subpath+"/"+dataset.endpoint_name)
                assert resp.status == 400
            loop.run_until_complete(test_dataset_query_without_filters_allowed())
            loop.run_until_complete(client.close())
            dataset.allow_queries_without_filters=True
    def test_no_filters_genomicVariation_query_without_filters_allowed(self):
        with loop_context() as loop:
            from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import genomicVariant
            genomicVariant.allow_queries_without_filters=False
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_genomicVariant_query_without_filters_allowed():
                resp = await client.get(conf_override.config.uri_subpath+"/"+genomicVariant.endpoint_name)
                assert resp.status == 400
            loop.run_until_complete(test_genomicVariant_query_without_filters_allowed())
            loop.run_until_complete(client.close())
            genomicVariant.allow_queries_without_filters=True
    def test_no_filters_individual_query_without_filters_allowed(self):
        with loop_context() as loop:
            from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import individual
            individual.allow_queries_without_filters=False
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_individual_query_without_filters_allowed():
                resp = await client.get(conf_override.config.uri_subpath+"/"+individual.endpoint_name)
                assert resp.status == 400
            loop.run_until_complete(test_individual_query_without_filters_allowed())
            loop.run_until_complete(client.close())
            individual.allow_queries_without_filters=True
    def test_no_filters_run_query_without_filters_allowed(self):
        with loop_context() as loop:
            from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import run
            run.allow_queries_without_filters=False
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_run_query_without_filters_allowed():
                resp = await client.get(conf_override.config.uri_subpath+"/"+run.endpoint_name)
                assert resp.status == 400
            loop.run_until_complete(test_run_query_without_filters_allowed())
            loop.run_until_complete(client.close())
            run.allow_queries_without_filters=True
    def test_map_endpoint_response_with_disabled_endpoint(self):
        with loop_context() as loop:
            from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import analysis
            analysis.enable_endpoint=False
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_map_endpoint_response_with_disabled_endpoint():
                resp = await client.get(conf_override.config.uri_subpath+"/map")
                assert resp.status == 200
                responsetext=await resp.text()
                responsedict=json.loads(responsetext)
                self.assertNotIn("analysis",responsedict["response"]["endpointSets"])
            loop.run_until_complete(test_check_map_endpoint_response_with_disabled_endpoint())
            loop.run_until_complete(client.close())
            analysis.enable_endpoint=True
    def test_configuration_endpoint_response_with_disabled_endpoint(self):
        with loop_context() as loop:
            from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import analysis
            analysis.enable_endpoint=False
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_endpoint_response_with_disabled_endpoint():
                resp = await client.get(conf_override.config.uri_subpath+"/configuration")
                assert resp.status == 200
                responsetext=await resp.text()
                responsedict=json.loads(responsetext)
                self.assertNotIn("analysis",responsedict["response"]["entryTypes"])
            loop.run_until_complete(test_check_configuration_endpoint_response_with_disabled_endpoint())
            loop.run_until_complete(client.close())
            analysis.enable_endpoint=True
    def test_main_check_configuration_with_wrong_analysis_enable_endpoint(self):
        with loop_context() as loop:
            from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import analysis
            analysis.enable_endpoint="no Boolean"
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_analysis():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_analysis())
            loop.run_until_complete(client.close())
            analysis.enable_endpoint=True
    def test_main_check_configuration_with_wrong_biosample_enable_endpoint(self):
        with loop_context() as loop:
            from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import biosample
            biosample.enable_endpoint="no Boolean"
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_biosample():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_biosample())
            loop.run_until_complete(client.close())
            biosample.enable_endpoint=True
    def test_main_check_configuration_with_wrong_cohort_enable_endpoint(self):
        with loop_context() as loop:
            from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import cohort
            cohort.enable_endpoint="no Boolean"
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_cohort():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_cohort())
            loop.run_until_complete(client.close())
            cohort.enable_endpoint=True
    def test_main_check_configuration_with_wrong_dataset_enable_endpoint(self):
        with loop_context() as loop:
            from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import dataset
            dataset.enable_endpoint="no Boolean"
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_dataset():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_dataset())
            loop.run_until_complete(client.close())
            dataset.enable_endpoint=True
    def test_main_check_configuration_with_wrong_individual_enable_endpoint(self):
        with loop_context() as loop:
            from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import individual
            individual.enable_endpoint="no Boolean"
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_individual():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_individual())
            loop.run_until_complete(client.close())
            individual.enable_endpoint=True
    def test_main_check_configuration_with_wrong_genomicVariant_enable_endpoint(self):
        with loop_context() as loop:
            from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import genomicVariant
            genomicVariant.enable_endpoint="no Boolean"
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_genomicVariant():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_genomicVariant())
            loop.run_until_complete(client.close())
            genomicVariant.enable_endpoint=True
    def test_main_check_configuration_with_wrong_run_enable_endpoint(self):
        with loop_context() as loop:
            from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import run
            run.enable_endpoint="no Boolean"
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_run():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_run())
            loop.run_until_complete(client.close())
            run.enable_endpoint=True
    def test_main_check_configuration_with_wrong_analysis_granularity(self):
        with loop_context() as loop:
            from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import analysis
            analysis.granularity="no Boolean"
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_analysis():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_analysis())
            loop.run_until_complete(client.close())
            analysis.granularity="record"
    def test_main_check_configuration_with_wrong_biosample_granularity(self):
        with loop_context() as loop:
            from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import biosample
            biosample.granularity="no Boolean"
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_biosample():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_biosample())
            loop.run_until_complete(client.close())
            biosample.granularity="record"
    def test_main_check_configuration_with_wrong_cohort_granularity(self):
        with loop_context() as loop:
            from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import cohort
            cohort.granularity="no Boolean"
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_cohort():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_cohort())
            loop.run_until_complete(client.close())
            cohort.granularity="record"
    def test_main_check_configuration_with_wrong_dataset_granularity(self):
        with loop_context() as loop:
            from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import dataset
            dataset.granularity="no Boolean"
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_dataset():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_dataset())
            loop.run_until_complete(client.close())
            dataset.granularity="record"
    def test_main_check_configuration_with_wrong_individual_granularity(self):
        with loop_context() as loop:
            from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import individual
            individual.granularity="no Boolean"
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_individual():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_individual())
            loop.run_until_complete(client.close())
            individual.granularity="record"
    def test_main_check_configuration_with_wrong_genomicVariant_granularity(self):
        with loop_context() as loop:
            from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import genomicVariant
            genomicVariant.granularity="no Boolean"
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_genomicVariant():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_genomicVariant())
            loop.run_until_complete(client.close())
            genomicVariant.granularity="record"
    def test_main_check_configuration_with_wrong_run_granularity(self):
        with loop_context() as loop:
            from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import run
            run.granularity="no Boolean"
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_granularity_run():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_granularity_run())
            loop.run_until_complete(client.close())
            run.granularity="record"
    def test_main_check_configuration_http(self):
        with loop_context() as loop:
            from beacon.conf import conf_override
            conf_override.config.uri="https://localhost:5010"
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_http():
                check_configuration()
            loop.run_until_complete(test_check_configuration_http())
            loop.run_until_complete(client.close())
            conf_override.config.uri="http://localhost:50101"
    def test_main_check_configuration_wrong_uri(self):
        with loop_context() as loop:
            from beacon.conf import conf_override
            conf_override.config.uri="afafsafas"
            async def test_check_configuration_wrong_uri():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_wrong_uri())
            conf_override.config.uri="http://localhost:50101"
    def test_main_check_configuration_wrong_uri_trailing_slash(self):
        with loop_context() as loop:
            from beacon.conf import conf_override
            conf_override.config.uri="http://localhost:50101/"

            async def test_check_configuration_wrong_uri_trailing_slash():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_wrong_uri_trailing_slash())
            conf_override.config.uri="http://localhost:50101"
    def test_main_check_configuration_wrong_uri_subpath_trailing_slash(self):
        with loop_context() as loop:
            from beacon.conf import conf_override
            conf_override.config.uri_subpath="/api/"
            async def test_check_configuration_wrong_uri_subpath_trailing_slash():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_wrong_uri_subpath_trailing_slash())
            conf_override.config.uri_subpath="/api"
    def test_main_check_configuration_wrong_uri_subpath_starting_slash_missing(self):
        with loop_context() as loop:
            from beacon.conf import conf_override
            conf_override.config.uri_subpath="api"
            async def test_check_configuration_wrong_uri_subpath_starting_slash():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_wrong_uri_subpath_starting_slash())
            conf_override.config.uri_subpath="/api"
    def test_main_check_configuration_wrong_query_budget_amount(self):
        with loop_context() as loop:
            from beacon.conf import conf_override
            conf_override.config.query_budget_amount="api"
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_wrong_query_budget_amount():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_wrong_query_budget_amount())
            loop.run_until_complete(client.close())
            conf_override.config.query_budget_amount=3
    def test_main_check_configuration_wrong_query_budget_time(self):
        with loop_context() as loop:
            from beacon.conf import conf_override
            conf_override.config.query_budget_time_in_seconds="api"
            async def test_check_configuration_wrong_query_budget_time():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_wrong_query_budget_time())
            conf_override.config.query_budget_time_in_seconds=3
    def test_main_check_configuration_wrong_query_budget_user(self):
        with loop_context() as loop:
            from beacon.conf import conf_override
            conf_override.config.query_budget_per_user="api"
            async def test_check_configuration_wrong_query_budget_user():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_wrong_query_budget_user())
            conf_override.config.query_budget_per_user=False
    def test_main_check_configuration_wrong_query_budget_ip(self):
        with loop_context() as loop:
            from beacon.conf import conf_override
            conf_override.config.query_budget_per_ip="api"
            async def test_check_configuration_wrong_query_budget_ip():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_wrong_query_budget_ip())
            conf_override.config.query_budget_per_ip=False
    def test_main_check_configuration_wrong_query_budget_database(self):
        with loop_context() as loop:
            from beacon.conf import conf_override
            conf_override.config.query_budget_database="api"
            async def test_check_configuration_wrong_query_budget_database():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_wrong_query_budget_database())
            conf_override.config.query_budget_database="mongo"
    def test_main_check_configuration_with_wrong_analysis_database(self):
        with loop_context() as loop:
            from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import analysis
            analysis.database="no Boolean"
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_analysis():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_analysis())
            loop.run_until_complete(client.close())
            analysis.database="mongo"
    def test_main_check_configuration_with_wrong_biosample_database(self):
        with loop_context() as loop:
            from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import biosample
            biosample.database="no Boolean"
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_biosample():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_biosample())
            loop.run_until_complete(client.close())
            biosample.database="mongo"
    def test_main_check_configuration_with_wrong_cohort_database(self):
        with loop_context() as loop:
            from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import cohort
            cohort.database="no Boolean"
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_cohort():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_cohort())
            loop.run_until_complete(client.close())
            cohort.database="mongo"
    def test_main_check_configuration_with_wrong_dataset_database(self):
        with loop_context() as loop:
            from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import dataset
            dataset.database="no Boolean"
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_dataset():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_dataset())
            loop.run_until_complete(client.close())
            dataset.database="mongo"
    def test_main_check_configuration_with_wrong_individual_database(self):
        with loop_context() as loop:
            from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import individual
            individual.database="no Boolean"
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_individual():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_individual())
            loop.run_until_complete(client.close())
            individual.database="mongo"
    def test_main_check_configuration_with_wrong_genomicVariant_database(self):
        with loop_context() as loop:
            from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import genomicVariant
            genomicVariant.database="no Boolean"
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_genomicVariant():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_genomicVariant())
            loop.run_until_complete(client.close())
            genomicVariant.database="mongo"
    def test_main_check_configuration_with_wrong_run_database(self):
        with loop_context() as loop:
            from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import run
            run.database="no Boolean"
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_database_run():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_database_run())
            loop.run_until_complete(client.close())
            run.database="mongo"
    def test_main_check_configuration_wrong_environment(self):
        with loop_context() as loop:
            from beacon.conf import conf_override
            conf_override.config.environment="api"
            async def test_check_configuration_wrong_environment():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_wrong_environment())
            conf_override.config.environment="dev"
    def test_main_check_configuration_wrong_default_granularity(self):
        with loop_context() as loop:
            from beacon.conf import conf_override
            conf_override.config.default_beacon_granularity="api"
            async def test_check_configuration_wrong_granularity():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_wrong_granularity())
            conf_override.config.default_beacon_granularity="record"
    def test_analyses_endpoint_name_is_string(self):
        with loop_context() as loop:
            from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import analysis
            analysis.endpoint_name=3
            async def test_check_endpoint_endpoint_name_is_string():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_endpoint_endpoint_name_is_string())
            analysis.endpoint_name="analyses"
    def test_biosamples_endpoint_name_is_string(self):
        with loop_context() as loop:
            from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import biosample
            biosample.endpoint_name=3
            async def test_check_endpoint_endpoint_name_is_string():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_endpoint_endpoint_name_is_string())
            biosample.endpoint_name="biosamples"
    def test_cohorts_endpoint_name_is_string(self):
        with loop_context() as loop:
            from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import cohort
            cohort.endpoint_name=3
            async def test_check_endpoint_endpoint_name_is_string():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_endpoint_endpoint_name_is_string())
            cohort.endpoint_name="cohorts"
    def test_datasets_endpoint_name_is_string(self):
        with loop_context() as loop:
            from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import dataset
            dataset.endpoint_name=3
            async def test_check_endpoint_endpoint_name_is_string():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_endpoint_endpoint_name_is_string())
            dataset.endpoint_name="datasets"
    def test_g_variants_endpoint_name_is_string(self):
        with loop_context() as loop:
            from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import genomicVariant
            genomicVariant.endpoint_name=3
            async def test_check_endpoint_endpoint_name_is_string():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_endpoint_endpoint_name_is_string())
            genomicVariant.endpoint_name="g_variants"
    def test_runs_endpoint_name_is_string(self):
        with loop_context() as loop:
            from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import run
            run.endpoint_name=3
            async def test_check_endpoint_endpoint_name_is_string():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_endpoint_endpoint_name_is_string())
            run.endpoint_name="runs"
    def test_individuals_endpoint_name_is_string(self):
        with loop_context() as loop:
            from beacon.models.ga4gh.beacon_v2_default_model.conf.entry_types import individual
            individual.endpoint_name=3
            async def test_check_endpoint_endpoint_name_is_string():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_endpoint_endpoint_name_is_string())
            individual.endpoint_name="individuals"

    

def suite():
    """
        Gather all the tests from this module in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestNoFilters))
    #test_suite.addTest(unittest.makeSuite(TestBudget2))
    return test_suite


mySuit=suite()


runner=unittest.TextTestRunner()
runner.run(mySuit)