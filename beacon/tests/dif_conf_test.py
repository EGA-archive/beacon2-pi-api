from aiohttp.test_utils import TestClient, TestServer, loop_context
from aiohttp import web
from beacon.__main__ import Collection, Resultset, Info, ServiceInfo, Map, Configuration, FilteringTerms, EntryTypes, error_middleware
import json
import unittest
import beacon.conf.conf as conf
from beacon.logs.logs import LOG
from beacon.conf import analysis, biosample, cohort, dataset, genomicVariant, individual, run
from aiohttp_middlewares import cors_middleware
from beacon.validator.configuration import contains_special_characters, check_configuration



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
    def test_endpoint_contains_special_chars(self):
        with loop_context() as loop:
            from beacon.conf import analysis
            analysis.endpoint_name="%aydga&-_al)"
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_endpoint_contains_special_chars():
                contains_special_characters(analysis.endpoint_name)
            loop.run_until_complete(test_check_endpoint_contains_special_chars())
            loop.run_until_complete(client.close())
            analysis.endpoint_name="analyses"
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