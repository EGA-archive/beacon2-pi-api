from aiohttp.test_utils import TestClient, TestServer, loop_context
from aiohttp import web
from beacon.__main__ import Collection, Resultset, Info, ServiceInfo, Map, Configuration, FilteringTerms, EntryTypes, error_middleware
import json
import unittest
import beacon.conf.conf as conf
from beacon.logs.logs import LOG
from beacon.conf import analysis, biosample, cohort, dataset, genomicVariant, individual, run
from aiohttp_middlewares import cors_middleware
from beacon.validator.configuration import check_configuration



def create_app():
    app = web.Application()
    app = web.Application(
        middlewares=[
            cors_middleware(origins=conf.cors_urls), error_middleware
        ]
    )
    #app.on_startup.append(initialize)
    app.add_routes([web.post(conf.uri_subpath+'', Info)])
    app.add_routes([web.post(conf.uri_subpath+'/info', Info)])
    app.add_routes([web.post(conf.uri_subpath+'/entry_types', EntryTypes)])
    app.add_routes([web.post(conf.uri_subpath+'/service-info', ServiceInfo)])
    app.add_routes([web.post(conf.uri_subpath+'/configuration', Configuration)])
    app.add_routes([web.post(conf.uri_subpath+'/map', Map)])
    app.add_routes([web.post(conf.uri_subpath+'/filtering_terms', FilteringTerms)])
    app.add_routes([web.get(conf.uri_subpath+'', Info)])
    app.add_routes([web.get(conf.uri_subpath+'/info', Info)])
    app.add_routes([web.get(conf.uri_subpath+'/entry_types', EntryTypes)])
    app.add_routes([web.get(conf.uri_subpath+'/service-info', ServiceInfo)])
    app.add_routes([web.get(conf.uri_subpath+'/configuration', Configuration)])
    app.add_routes([web.get(conf.uri_subpath+'/map', Map)])
    app.add_routes([web.get(conf.uri_subpath+'/filtering_terms', FilteringTerms)])
    if dataset.endpoint_name != '':
        app.add_routes([web.post(conf.uri_subpath+'/'+dataset.endpoint_name, Collection)])
        app.add_routes([web.get(conf.uri_subpath+'/'+dataset.endpoint_name, Collection)])
        if dataset.singleEntryUrl == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+dataset.endpoint_name+'/{id}', Collection)])
            app.add_routes([web.get(conf.uri_subpath+'/'+dataset.endpoint_name+'/{id}', Collection)])
        if dataset.analysis_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+analysis.endpoint_name, Resultset)])
            app.add_routes([web.get(conf.uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+analysis.endpoint_name, Resultset)])
        if dataset.biosample_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+biosample.endpoint_name, Resultset)])
            app.add_routes([web.get(conf.uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+biosample.endpoint_name, Resultset)])
        if dataset.cohort_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+cohort.endpoint_name, Collection)])
            app.add_routes([web.get(conf.uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+cohort.endpoint_name, Collection)])
        if dataset.genomicVariant_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, Resultset)])
            app.add_routes([web.get(conf.uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, Resultset)])
        if dataset.individual_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+individual.endpoint_name, Resultset)])
            app.add_routes([web.get(conf.uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+individual.endpoint_name, Resultset)])
        if dataset.run_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+run.endpoint_name, Resultset)])
            app.add_routes([web.get(conf.uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+run.endpoint_name, Resultset)])
    if cohort.endpoint_name != '':
        app.add_routes([web.post(conf.uri_subpath+'/'+cohort.endpoint_name, Collection)])
        app.add_routes([web.get(conf.uri_subpath+'/'+cohort.endpoint_name, Collection)])
        if cohort.singleEntryUrl == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+cohort.endpoint_name+'/{id}', Collection)])
            app.add_routes([web.get(conf.uri_subpath+'/'+cohort.endpoint_name+'/{id}', Collection)])
        if cohort.analysis_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+analysis.endpoint_name, Resultset)])
            app.add_routes([web.get(conf.uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+analysis.endpoint_name, Resultset)])
        if cohort.biosample_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+biosample.endpoint_name, Resultset)])
            app.add_routes([web.get(conf.uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+biosample.endpoint_name, Resultset)])
        if cohort.dataset_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+dataset.endpoint_name, Collection)])
            app.add_routes([web.get(conf.uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+dataset.endpoint_name, Collection)])
        if cohort.genomicVariant_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, Resultset)])
            app.add_routes([web.get(conf.uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, Resultset)])
        if cohort.individual_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+individual.endpoint_name, Resultset)])
            app.add_routes([web.get(conf.uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+individual.endpoint_name, Resultset)])
        if cohort.run_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+run.endpoint_name, Resultset)])
            app.add_routes([web.get(conf.uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+run.endpoint_name, Resultset)])
    if analysis.endpoint_name != '':
        app.add_routes([web.post(conf.uri_subpath+'/'+analysis.endpoint_name, Resultset)])
        app.add_routes([web.get(conf.uri_subpath+'/'+analysis.endpoint_name, Resultset)])
        if analysis.singleEntryUrl == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+analysis.endpoint_name+'/{id}', Resultset)])
            app.add_routes([web.get(conf.uri_subpath+'/'+analysis.endpoint_name+'/{id}', Resultset)])
        if analysis.cohort_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+cohort.endpoint_name, Collection)])
            app.add_routes([web.get(conf.uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+cohort.endpoint_name, Collection)])
        if analysis.biosample_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+biosample.endpoint_name, Resultset)])
            app.add_routes([web.get(conf.uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+biosample.endpoint_name, Resultset)])
        if analysis.dataset_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+dataset.endpoint_name, Collection)])
            app.add_routes([web.get(conf.uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+dataset.endpoint_name, Collection)])
        if analysis.genomicVariant_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, Resultset)])
            app.add_routes([web.get(conf.uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, Resultset)])
        if analysis.individual_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+individual.endpoint_name, Resultset)])
            app.add_routes([web.get(conf.uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+individual.endpoint_name, Resultset)])
        if analysis.run_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+run.endpoint_name, Resultset)])
            app.add_routes([web.get(conf.uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+run.endpoint_name, Resultset)])
    if biosample.endpoint_name != '':
        app.add_routes([web.post(conf.uri_subpath+'/'+biosample.endpoint_name, Resultset)])
        app.add_routes([web.get(conf.uri_subpath+'/'+biosample.endpoint_name, Resultset)])
        if biosample.singleEntryUrl == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+biosample.endpoint_name+'/{id}', Resultset)])
            app.add_routes([web.get(conf.uri_subpath+'/'+biosample.endpoint_name+'/{id}', Resultset)])
        if biosample.cohort_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+cohort.endpoint_name, Collection)])
            app.add_routes([web.get(conf.uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+cohort.endpoint_name, Collection)])
        if biosample.analysis_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+analysis.endpoint_name, Resultset)])
            app.add_routes([web.get(conf.uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+analysis.endpoint_name, Resultset)])
        if biosample.dataset_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+dataset.endpoint_name, Collection)])
            app.add_routes([web.get(conf.uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+dataset.endpoint_name, Collection)])
        if biosample.genomicVariant_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, Resultset)])
            app.add_routes([web.get(conf.uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, Resultset)])
        if biosample.individual_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+individual.endpoint_name, Resultset)])
            app.add_routes([web.get(conf.uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+individual.endpoint_name, Resultset)])
        if biosample.run_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+run.endpoint_name, Resultset)])
            app.add_routes([web.get(conf.uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+run.endpoint_name, Resultset)])
    if genomicVariant.endpoint_name != '':
        app.add_routes([web.post(conf.uri_subpath+'/'+genomicVariant.endpoint_name, Resultset)])
        app.add_routes([web.get(conf.uri_subpath+'/'+genomicVariant.endpoint_name, Resultset)])
        if genomicVariant.singleEntryUrl == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}', Resultset)])
            app.add_routes([web.get(conf.uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}', Resultset)])
        if genomicVariant.cohort_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+cohort.endpoint_name, Collection)])
            app.add_routes([web.get(conf.uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+cohort.endpoint_name, Collection)])
        if genomicVariant.analysis_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+analysis.endpoint_name, Resultset)])
            app.add_routes([web.get(conf.uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+analysis.endpoint_name, Resultset)])
        if genomicVariant.dataset_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+dataset.endpoint_name, Collection)])
            app.add_routes([web.get(conf.uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+dataset.endpoint_name, Collection)])
        if genomicVariant.biosample_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+biosample.endpoint_name, Resultset)])
            app.add_routes([web.get(conf.uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+biosample.endpoint_name, Resultset)])
        if genomicVariant.individual_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+individual.endpoint_name, Resultset)])
            app.add_routes([web.get(conf.uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+individual.endpoint_name, Resultset)])
        if genomicVariant.run_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+run.endpoint_name, Resultset)])
            app.add_routes([web.get(conf.uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+run.endpoint_name, Resultset)])
    if individual.endpoint_name != '':
        app.add_routes([web.post(conf.uri_subpath+'/'+individual.endpoint_name, Resultset)])
        app.add_routes([web.get(conf.uri_subpath+'/'+individual.endpoint_name, Resultset)])
        if individual.singleEntryUrl == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+individual.endpoint_name+'/{id}', Resultset)])
            app.add_routes([web.get(conf.uri_subpath+'/'+individual.endpoint_name+'/{id}', Resultset)])
        if individual.cohort_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+individual.endpoint_name+'/{id}/'+cohort.endpoint_name, Collection)])
            app.add_routes([web.get(conf.uri_subpath+'/'+individual.endpoint_name+'/{id}/'+cohort.endpoint_name, Collection)])
        if individual.analysis_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+individual.endpoint_name+'/{id}/'+analysis.endpoint_name, Resultset)])
            app.add_routes([web.get(conf.uri_subpath+'/'+individual.endpoint_name+'/{id}/'+analysis.endpoint_name, Resultset)])
        if individual.dataset_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+individual.endpoint_name+'/{id}/'+dataset.endpoint_name, Collection)])
            app.add_routes([web.get(conf.uri_subpath+'/'+individual.endpoint_name+'/{id}/'+dataset.endpoint_name, Collection)])
        if individual.biosample_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+individual.endpoint_name+'/{id}/'+biosample.endpoint_name, Resultset)])
            app.add_routes([web.get(conf.uri_subpath+'/'+individual.endpoint_name+'/{id}/'+biosample.endpoint_name, Resultset)])
        if individual.genomicVariant_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+individual.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, Resultset)])
            app.add_routes([web.get(conf.uri_subpath+'/'+individual.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, Resultset)])
        if individual.run_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+individual.endpoint_name+'/{id}/'+run.endpoint_name, Resultset)])
            app.add_routes([web.get(conf.uri_subpath+'/'+individual.endpoint_name+'/{id}/'+run.endpoint_name, Resultset)])
    if run.endpoint_name != '':
        app.add_routes([web.post(conf.uri_subpath+'/'+run.endpoint_name, Resultset)])
        app.add_routes([web.get(conf.uri_subpath+'/'+run.endpoint_name, Resultset)])
        if run.singleEntryUrl == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+run.endpoint_name+'/{id}', Resultset)])
            app.add_routes([web.get(conf.uri_subpath+'/'+run.endpoint_name+'/{id}', Resultset)])
        if run.cohort_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+run.endpoint_name+'/{id}/'+cohort.endpoint_name, Collection)])
            app.add_routes([web.get(conf.uri_subpath+'/'+run.endpoint_name+'/{id}/'+cohort.endpoint_name, Collection)])
        if run.analysis_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+run.endpoint_name+'/{id}/'+analysis.endpoint_name, Resultset)])
            app.add_routes([web.get(conf.uri_subpath+'/'+run.endpoint_name+'/{id}/'+analysis.endpoint_name, Resultset)])
        if run.dataset_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+run.endpoint_name+'/{id}/'+dataset.endpoint_name, Collection)])
            app.add_routes([web.get(conf.uri_subpath+'/'+run.endpoint_name+'/{id}/'+dataset.endpoint_name, Collection)])
        if run.biosample_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+run.endpoint_name+'/{id}/'+biosample.endpoint_name, Resultset)])
            app.add_routes([web.get(conf.uri_subpath+'/'+run.endpoint_name+'/{id}/'+biosample.endpoint_name, Resultset)])
        if run.genomicVariant_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+run.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, Resultset)])
            app.add_routes([web.get(conf.uri_subpath+'/'+run.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, Resultset)])
        if run.individual_lookup == True:
            app.add_routes([web.post(conf.uri_subpath+'/'+run.endpoint_name+'/{id}/'+individual.endpoint_name, Resultset)])
            app.add_routes([web.get(conf.uri_subpath+'/'+run.endpoint_name+'/{id}/'+individual.endpoint_name, Resultset)])
    return app

class TestNoFilters(unittest.TestCase):
    def test_no_filters_analysis_query_without_filters_allowed(self):
        with loop_context() as loop:
            from beacon.conf import analysis
            analysis.allow_queries_without_filters=False
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_analysis_query_without_filters_allowed():
                resp = await client.get(conf.uri_subpath+"/"+analysis.endpoint_name)
                assert resp.status == 400
            loop.run_until_complete(test_analysis_query_without_filters_allowed())
            loop.run_until_complete(client.close())
            analysis.allow_queries_without_filters=True
    def test_no_filters_biosample_query_without_filters_allowed(self):
        with loop_context() as loop:
            from beacon.conf import biosample
            biosample.allow_queries_without_filters=False
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_biosample_query_without_filters_allowed():
                resp = await client.get(conf.uri_subpath+"/"+biosample.endpoint_name)
                assert resp.status == 400
            loop.run_until_complete(test_biosample_query_without_filters_allowed())
            loop.run_until_complete(client.close())
            biosample.allow_queries_without_filters=True
    def test_no_filters_cohort_query_without_filters_allowed(self):
        with loop_context() as loop:
            from beacon.conf import cohort
            cohort.allow_queries_without_filters=False
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_cohort_query_without_filters_allowed():
                resp = await client.get(conf.uri_subpath+"/"+cohort.endpoint_name)
                assert resp.status == 400
            loop.run_until_complete(test_cohort_query_without_filters_allowed())
            loop.run_until_complete(client.close())
            cohort.allow_queries_without_filters=True
    def test_no_filters_dataset_query_without_filters_allowed(self):
        with loop_context() as loop:
            from beacon.conf import dataset
            dataset.allow_queries_without_filters=False
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_dataset_query_without_filters_allowed():
                resp = await client.get(conf.uri_subpath+"/"+dataset.endpoint_name)
                assert resp.status == 400
            loop.run_until_complete(test_dataset_query_without_filters_allowed())
            loop.run_until_complete(client.close())
            dataset.allow_queries_without_filters=True
    def test_no_filters_genomicVariation_query_without_filters_allowed(self):
        with loop_context() as loop:
            from beacon.conf import genomicVariant
            genomicVariant.allow_queries_without_filters=False
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_genomicVariant_query_without_filters_allowed():
                resp = await client.get(conf.uri_subpath+"/"+genomicVariant.endpoint_name)
                assert resp.status == 400
            loop.run_until_complete(test_genomicVariant_query_without_filters_allowed())
            loop.run_until_complete(client.close())
            genomicVariant.allow_queries_without_filters=True
    def test_no_filters_individual_query_without_filters_allowed(self):
        with loop_context() as loop:
            from beacon.conf import individual
            individual.allow_queries_without_filters=False
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_individual_query_without_filters_allowed():
                resp = await client.get(conf.uri_subpath+"/"+individual.endpoint_name)
                assert resp.status == 400
            loop.run_until_complete(test_individual_query_without_filters_allowed())
            loop.run_until_complete(client.close())
            individual.allow_queries_without_filters=True
    def test_no_filters_run_query_without_filters_allowed(self):
        with loop_context() as loop:
            from beacon.conf import run
            run.allow_queries_without_filters=False
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_run_query_without_filters_allowed():
                resp = await client.get(conf.uri_subpath+"/"+run.endpoint_name)
                LOG.warning(resp.status)
                assert resp.status == 400
            loop.run_until_complete(test_run_query_without_filters_allowed())
            loop.run_until_complete(client.close())
            run.allow_queries_without_filters=True
    def test_map_endpoint_response_with_disabled_endpoint(self):
        with loop_context() as loop:
            from beacon.conf import analysis
            analysis.enable_endpoint=False
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_map_endpoint_response_with_disabled_endpoint():
                resp = await client.get(conf.uri_subpath+"/map")
                assert resp.status == 200
                responsetext=await resp.text()
                responsedict=json.loads(responsetext)
                self.assertNotIn("analysis",responsedict["response"]["endpointSets"])
            loop.run_until_complete(test_check_map_endpoint_response_with_disabled_endpoint())
            loop.run_until_complete(client.close())
            analysis.enable_endpoint=True
    def test_configuration_endpoint_response_with_disabled_endpoint(self):
        with loop_context() as loop:
            from beacon.conf import analysis
            analysis.enable_endpoint=False
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_endpoint_response_with_disabled_endpoint():
                resp = await client.get(conf.uri_subpath+"/configuration")
                assert resp.status == 200
                responsetext=await resp.text()
                responsedict=json.loads(responsetext)
                self.assertNotIn("analysis",responsedict["response"]["entryTypes"])
            loop.run_until_complete(test_check_configuration_endpoint_response_with_disabled_endpoint())
            loop.run_until_complete(client.close())
            analysis.enable_endpoint=True
    def test_main_check_configuration_with_wrong_analysis_enable_endpoint(self):
        with loop_context() as loop:
            from beacon.conf import analysis
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
            from beacon.conf import biosample
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
            from beacon.conf import cohort
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
            from beacon.conf import dataset
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
            from beacon.conf import individual
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
            from beacon.conf import genomicVariant
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
            from beacon.conf import run
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
            from beacon.conf import analysis
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
            from beacon.conf import biosample
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
            from beacon.conf import cohort
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
            from beacon.conf import dataset
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
            from beacon.conf import individual
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
            from beacon.conf import genomicVariant
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
            from beacon.conf import run
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
            from beacon.conf import conf
            conf.uri="https://localhost:5010"
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_http():
                check_configuration()
            loop.run_until_complete(test_check_configuration_http())
            loop.run_until_complete(client.close())
            conf.uri="http://localhost:50101"
    def test_main_check_configuration_wrong_uri(self):
        with loop_context() as loop:
            from beacon.conf import conf
            conf.uri="afafsafas"
            async def test_check_configuration_wrong_uri():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_wrong_uri())
            conf.uri="http://localhost:50101"
    def test_main_check_configuration_wrong_uri_trailing_slash(self):
        with loop_context() as loop:
            from beacon.conf import conf
            conf.uri="http://localhost:50101/"

            async def test_check_configuration_wrong_uri_trailing_slash():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_wrong_uri_trailing_slash())
            conf.uri="http://localhost:50101"
    def test_main_check_configuration_wrong_uri_subpath_trailing_slash(self):
        with loop_context() as loop:
            from beacon.conf import conf
            conf.uri_subpath="/api/"
            async def test_check_configuration_wrong_uri_subpath_trailing_slash():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_wrong_uri_subpath_trailing_slash())
            conf.uri_subpath="/api"
    def test_main_check_configuration_wrong_uri_subpath_starting_slash_missing(self):
        with loop_context() as loop:
            from beacon.conf import conf
            conf.uri_subpath="api"
            async def test_check_configuration_wrong_uri_subpath_starting_slash():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_wrong_uri_subpath_starting_slash())
            conf.uri_subpath="/api"
    def test_main_check_configuration_wrong_query_budget_amount(self):
        with loop_context() as loop:
            from beacon.conf import conf
            conf.query_budget_amount="api"
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
            conf.query_budget_amount=3
    def test_main_check_configuration_wrong_query_budget_time(self):
        with loop_context() as loop:
            from beacon.conf import conf
            conf.query_budget_time_in_seconds="api"
            async def test_check_configuration_wrong_query_budget_time():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_wrong_query_budget_time())
            conf.query_budget_time_in_seconds=3
    def test_main_check_configuration_wrong_query_budget_user(self):
        with loop_context() as loop:
            from beacon.conf import conf
            conf.query_budget_per_user="api"
            async def test_check_configuration_wrong_query_budget_user():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_wrong_query_budget_user())
            conf.query_budget_per_user=False
    def test_main_check_configuration_wrong_query_budget_ip(self):
        with loop_context() as loop:
            from beacon.conf import conf
            conf.query_budget_per_ip="api"
            async def test_check_configuration_wrong_query_budget_ip():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_wrong_query_budget_ip())
            conf.query_budget_per_ip=False
    def test_main_check_configuration_wrong_query_budget_database(self):
        with loop_context() as loop:
            from beacon.conf import conf
            conf.query_budget_database="api"
            async def test_check_configuration_wrong_query_budget_database():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_wrong_query_budget_database())
            conf.query_budget_database="mongo"
    def test_main_check_configuration_with_wrong_analysis_database(self):
        with loop_context() as loop:
            from beacon.conf import analysis
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
            from beacon.conf import biosample
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
            from beacon.conf import cohort
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
            from beacon.conf import dataset
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
            from beacon.conf import individual
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
            from beacon.conf import genomicVariant
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
            from beacon.conf import run
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
            from beacon.conf import conf
            conf.environment="api"
            async def test_check_configuration_wrong_environment():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_wrong_environment())
            conf.environment="dev"
    def test_main_check_configuration_wrong_default_granularity(self):
        with loop_context() as loop:
            from beacon.conf import conf
            conf.default_beacon_granularity="api"
            async def test_check_configuration_wrong_granularity():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_wrong_granularity())
            conf.default_beacon_granularity="record"
    def test_analyses_endpoint_name_is_string(self):
        with loop_context() as loop:
            from beacon.conf import analysis
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
            from beacon.conf import biosample
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
            from beacon.conf import cohort
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
            from beacon.conf import dataset
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
            from beacon.conf import genomicVariant
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
            from beacon.conf import run
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
            from beacon.conf import individual
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