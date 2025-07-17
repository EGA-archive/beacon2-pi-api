from aiohttp.test_utils import TestClient, TestServer, loop_context
from aiohttp import web
from beacon.__main__ import Collection, Resultset, Info, ServiceInfo, Map, Configuration, FilteringTerms, EntryTypes
import json
import unittest
import beacon.conf.conf as conf
from beacon.request.classes import ErrorClass
#from beacon.permissions.tests import TestAuthZ
#from beacon.auth.tests import TestAuthN
#from beacon.request.tests import TestRequest
from beacon.logs.logs import LOG
from beacon.connections.mongo.filters import cross_query
from unittest.mock import MagicMock
from beacon.conf import analysis, biosample, cohort, dataset, genomicVariant, individual, run



def create_app():
    app = web.Application()
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

class TestMain(unittest.TestCase):
    def test_main_check_slash_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_slash_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"")
                assert resp.status == 200
            loop.run_until_complete(test_check_slash_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_post_slash_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_post_slash_endpoint_is_working():
                resp = await client.post(conf.uri_subpath+"")
                assert resp.status == 200
            loop.run_until_complete(test_check_post_slash_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_info_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_info_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/info")
                assert resp.status == 200
            loop.run_until_complete(test_check_info_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_post_info_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_post_info_endpoint_is_working():
                resp = await client.post(conf.uri_subpath+"/info")
                assert resp.status == 200
            loop.run_until_complete(test_check_post_info_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_service_info_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_service_info_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/service-info")
                assert resp.status == 200
            loop.run_until_complete(test_check_service_info_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_post_service_info_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_post_service_info_endpoint_is_working():
                resp = await client.post(conf.uri_subpath+"/service-info")
                assert resp.status == 200
            loop.run_until_complete(test_check_post_service_info_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_entry_types_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_entry_types_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/entry_types")
                assert resp.status == 200
            loop.run_until_complete(test_check_entry_types_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_post_entry_types_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_post_entry_types_endpoint_is_working():
                resp = await client.post(conf.uri_subpath+"/entry_types")
                assert resp.status == 200
            loop.run_until_complete(test_check_post_entry_types_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_configuration_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/configuration")
                assert resp.status == 200
            loop.run_until_complete(test_check_configuration_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_post_configuration_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_post_configuration_endpoint_is_working():
                resp = await client.post(conf.uri_subpath+"/configuration")
                assert resp.status == 200
            loop.run_until_complete(test_check_post_configuration_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_map_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_map_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/map")
                assert resp.status == 200
            loop.run_until_complete(test_check_map_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_post_map_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_post_map_endpoint_is_working():
                resp = await client.post(conf.uri_subpath+"/map")
                assert resp.status == 200
            loop.run_until_complete(test_check_post_map_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_filtering_terms_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_filtering_terms_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/filtering_terms")
                assert resp.status == 200
            loop.run_until_complete(test_check_filtering_terms_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_post_filtering_terms_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_post_filtering_terms_endpoint_is_working():
                resp = await client.post(conf.uri_subpath+"/filtering_terms")
                assert resp.status == 200
            loop.run_until_complete(test_check_post_filtering_terms_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_datasets_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_datasets_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+dataset.endpoint_name)
                assert resp.status == 200
            loop.run_until_complete(test_check_datasets_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_post_datasets_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_post_datasets_endpoint_is_working():
                resp = await client.post(conf.uri_subpath+"/"+dataset.endpoint_name)
                assert resp.status == 200
            loop.run_until_complete(test_check_post_datasets_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+genomicVariant.endpoint_name)
                assert resp.status == 200
            loop.run_until_complete(test_check_g_variants_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_analyses_with_limit_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_analyses_with_limit_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+analysis.endpoint_name+"?limit=200")
                assert resp.status == 200
            loop.run_until_complete(test_check_analyses_with_limit_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_analyses_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_analyses_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+analysis.endpoint_name)
                assert resp.status == 200
            loop.run_until_complete(test_check_analyses_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_analyses_with_id_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_analyses_with_id_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+analysis.endpoint_name+"/EGA-testing")
                assert resp.status == 200
            loop.run_until_complete(test_check_analyses_with_id_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_analyses_g_variants_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_analyses_g_variants_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+analysis.endpoint_name+"/EGA-testing/"+genomicVariant.endpoint_name)
                assert resp.status == 200
            loop.run_until_complete(test_check_analyses_g_variants_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_analyses_runs_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_analyses_runs_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+analysis.endpoint_name+"/EGA-testing/"+run.endpoint_name)
                assert resp.status == 200
            loop.run_until_complete(test_check_analyses_runs_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_analyses_individuals_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_analyses_individuals_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+analysis.endpoint_name+"/EGA-testing/"+individual.endpoint_name)
                assert resp.status == 200
            loop.run_until_complete(test_check_analyses_individuals_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_analyses_biosamples_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_analyses_biosmples_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+analysis.endpoint_name+"/EGA-testing/"+biosample.endpoint_name)
                assert resp.status == 200
            loop.run_until_complete(test_check_analyses_biosmples_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_biosamples_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_biosamples_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+biosample.endpoint_name)
                assert resp.status == 200
            loop.run_until_complete(test_check_biosamples_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_biosamples_with_limit_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_biosamples_with_limit_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+biosample.endpoint_name+"?limit=200")
                assert resp.status == 200
            loop.run_until_complete(test_check_biosamples_with_limit_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_biosamples_with_id_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_biosamples_with_id_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+biosample.endpoint_name+"/SAMPLE3")
                assert resp.status == 200
            loop.run_until_complete(test_check_biosamples_with_id_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_biosamples_g_variants_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_biosamples_g_variants_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+biosample.endpoint_name+"/SAMPLE3/"+genomicVariant.endpoint_name)
                assert resp.status == 200
            loop.run_until_complete(test_check_biosamples_g_variants_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_biosamples_runs_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_biosamples_runs_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+biosample.endpoint_name+"/SAMPLE1/"+run.endpoint_name)
                assert resp.status == 200
            loop.run_until_complete(test_check_biosamples_runs_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_biosamples_analyses_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_biosamples_analyses_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+biosample.endpoint_name+"/SAMPLE1/"+analysis.endpoint_name)
                assert resp.status == 200
            loop.run_until_complete(test_check_biosamples_analyses_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_individuals_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_individuals_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+individual.endpoint_name)
                assert resp.status == 200
                responsetext=await resp.text()
                responsedict=json.loads(responsetext)
                from beacon.utils.handovers import handover_1
                assert responsedict["response"]["resultSets"][0]["resultsHandover"] == handover_1
            loop.run_until_complete(test_check_individuals_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_individuals_with_limit_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_individuals_with_limit_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+individual.endpoint_name+"?limit=200")
                assert resp.status == 200
            loop.run_until_complete(test_check_individuals_with_limit_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_individuals_with_id_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_individuals_with_id_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+individual.endpoint_name+"/SAMPLE2")
                assert resp.status == 200
            loop.run_until_complete(test_check_individuals_with_id_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_individuals_g_variants_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_individuals_g_variants_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+individual.endpoint_name+"/SAMPLE2/"+genomicVariant.endpoint_name)
                assert resp.status == 200
            loop.run_until_complete(test_check_individuals_g_variants_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_individuals_biosamples_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_individuals_biosamples_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+individual.endpoint_name+"/SAMPLE2/"+biosample.endpoint_name)
                assert resp.status == 200
            loop.run_until_complete(test_check_individuals_biosamples_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_runs_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_runs_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+run.endpoint_name)
                assert resp.status == 200
            loop.run_until_complete(test_check_runs_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_runs_with_limit_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_runs_with_limit_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+run.endpoint_name+"?limit=200")
                assert resp.status == 200
            loop.run_until_complete(test_check_runs_with_limit_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_runs_with_id_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_runs_with_id_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+run.endpoint_name+"/EGA-testing")
                assert resp.status == 200
            loop.run_until_complete(test_check_runs_with_id_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_runs_g_variants_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_runs_g_variants_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+run.endpoint_name+"/EGA-testing/"+genomicVariant.endpoint_name)
                assert resp.status == 200
            loop.run_until_complete(test_check_runs_g_variants_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_runs_analyses_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_runs_analyses_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+run.endpoint_name+"/EGA-testing/"+analysis.endpoint_name)
                assert resp.status == 200
            loop.run_until_complete(test_check_runs_analyses_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_runs_biosamples_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_runs_biosamples_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+run.endpoint_name+"/EGA-testing/"+biosample.endpoint_name)
                assert resp.status == 200
            loop.run_until_complete(test_check_runs_biosamples_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_runs_individuals_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_runs_individuals_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+run.endpoint_name+"/EGA-testing/"+individual.endpoint_name)
                assert resp.status == 200
            loop.run_until_complete(test_check_runs_individuals_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_cohorts_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_cohorts_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+cohort.endpoint_name)
                assert resp.status == 200
            loop.run_until_complete(test_check_cohorts_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_cohorts_with_limit_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_cohorts_with_limit_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+cohort.endpoint_name+"?limit=200")
                assert resp.status == 200
            loop.run_until_complete(test_check_cohorts_with_limit_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_cohorts_with_id_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_cohorts_with_id_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+cohort.endpoint_name+"/EGA-testing")
                assert resp.status == 200
            loop.run_until_complete(test_check_cohorts_with_id_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_cohorts_runs_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_cohorts_runs_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+cohort.endpoint_name+"/EGA-testing/"+run.endpoint_name)
                assert resp.status == 200
            loop.run_until_complete(test_check_cohorts_runs_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_cohorts_biosamples_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_cohorts_biosamples_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+cohort.endpoint_name+"/EGA-testing/"+biosample.endpoint_name)
                assert resp.status == 200
            loop.run_until_complete(test_check_cohorts_biosamples_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_cohorts_analyses_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_cohorts_analyses_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+cohort.endpoint_name+"/EGA-testing/"+analysis.endpoint_name)
                assert resp.status == 200
            loop.run_until_complete(test_check_cohorts_analyses_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_cohorts_individuals_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_cohorts_inividuals_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+cohort.endpoint_name+"/EGA-testing/"+individual.endpoint_name)
                assert resp.status == 200
            loop.run_until_complete(test_check_cohorts_inividuals_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_cohorts_g_variants_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_cohorts_g_variants_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+cohort.endpoint_name+"/EGA-testing/"+genomicVariant.endpoint_name)
                assert resp.status == 200
            loop.run_until_complete(test_check_cohorts_g_variants_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_datasets_with_limit_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_datasets_with_limit_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+dataset.endpoint_name+"?limit=200")
                assert resp.status == 200
            loop.run_until_complete(test_check_datasets_with_limit_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_datasets_with_id_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_datasets_with_id_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+dataset.endpoint_name+"/test")
                assert resp.status == 200
            loop.run_until_complete(test_check_datasets_with_id_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_datasets_runs_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_datasets_runs_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+dataset.endpoint_name+"/test/"+run.endpoint_name)
                assert resp.status == 200
            loop.run_until_complete(test_check_datasets_runs_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_datasets_g_variants_2_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_datasets_g_variants_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+dataset.endpoint_name+"/test/"+genomicVariant.endpoint_name)
                assert resp.status == 200
            loop.run_until_complete(test_check_datasets_g_variants_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_datasets_biosamples_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_datasets_biosamples_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+dataset.endpoint_name+"/test/"+biosample.endpoint_name)
                assert resp.status == 200
            loop.run_until_complete(test_check_datasets_biosamples_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_datasets_analyses_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_datasets_analyses_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+dataset.endpoint_name+"/test/"+analysis.endpoint_name)
                assert resp.status == 200
            loop.run_until_complete(test_check_datasets_analyses_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_datasets_individuals_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_datasets_inividuals_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+dataset.endpoint_name+"/test/"+individual.endpoint_name)
                assert resp.status == 200
            loop.run_until_complete(test_check_datasets_inividuals_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_with_limit_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_with_limit_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"?limit=200")
                assert resp.status == 200
            loop.run_until_complete(test_check_g_variants_with_limit_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_with_id_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_with_id_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"/96c010bc-1449-11f0-83f8-0242ac120003:G:A")
                responsetext=await resp.text()
                responsedict=json.loads(responsetext)
                assert responsedict["responseSummary"]["numTotalResults"] == 1
                assert resp.status == 200
            loop.run_until_complete(test_check_g_variants_with_id_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_runs_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_runs_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"/96c010bc-1449-11f0-83f8-0242ac120003:G:A/"+run.endpoint_name)
                responsetext=await resp.text()
                responsedict=json.loads(responsetext)
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
                resp = await client.get(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"/96c010bc-1449-11f0-83f8-0242ac120003:G:A/"+biosample.endpoint_name)
                responsetext=await resp.text()
                responsedict=json.loads(responsetext)
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
                resp = await client.get(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"/96c010bc-1449-11f0-83f8-0242ac120003:G:A/"+analysis.endpoint_name)
                responsetext=await resp.text()
                responsedict=json.loads(responsetext)
                assert responsedict["responseSummary"]["numTotalResults"] == 1
                assert resp.status == 200
            loop.run_until_complete(test_check_g_variants_analyses_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_individuals_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_inividuals_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"/96c010bc-1449-11f0-83f8-0242ac120003:G:A/"+individual.endpoint_name)
                responsetext=await resp.text()
                responsedict=json.loads(responsetext)
                assert responsedict["responseSummary"]["numTotalResults"] == 15
                assert resp.status == 200
            loop.run_until_complete(test_check_g_variants_inividuals_endpoint_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_endpoint_NONE_resultSetResponse_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_endpoint_NONE_resultSetResponse_is_working():
                resp = await client.get(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"?includeResultsetResponses=NONE")
                assert resp.status == 200
            loop.run_until_complete(test_check_g_variants_endpoint_NONE_resultSetResponse_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_endpoint_MISS_resultSetResponse_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_endpoint_MISS_resultSetResponse_is_working():
                resp = await client.get(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"?includeResultsetResponses=MISS")
                assert resp.status == 200
            loop.run_until_complete(test_check_g_variants_endpoint_MISS_resultSetResponse_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_endpoint_ALL_resultSetResponse_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_endpoint_ALL_resultSetResponse_is_working():
                resp = await client.get(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"?includeResultsetResponses=ALL")
                assert resp.status == 200
            loop.run_until_complete(test_check_g_variants_endpoint_ALL_resultSetResponse_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_sequence_query(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_endpoint_with_parameters_is_working():
                resp = await client.get(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"?start=43045703&referenceName=17&assemblyId=GRCh38&referenceBases=G&alternateBases=A")
                assert resp.status == 200
            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_range_query(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_endpoint_with_parameters_is_working():
                resp = await client.get(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"?start=345675&referenceName=2&assemblyId=GRCh37&end=345681")
                responsetext=await resp.text()
                responsedict=json.loads(responsetext)
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
                resp = await client.get(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"?geneId=BRCA1")
                assert resp.status == 200
            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_bracket_query(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_endpoint_with_parameters_is_working():
                resp = await client.get(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"?start=43045703,43045704&end=43045704,43045705&referenceName=17&assemblyId=GRCh38")
                assert resp.status == 200
            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_genomic_allele_query(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_endpoint_with_parameters_is_working():
                resp = await client.get(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"?genomicAlleleShortForm=NC_000008.10:g.467881AGCAG>A")
                responsetext=await resp.text()
                responsedict=json.loads(responsetext)
                assert responsedict["responseSummary"]["numTotalResults"] == 1
                assert resp.status == 200
            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_g_variants_aminoacidChange_query(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_endpoint_with_parameters_is_working():
                resp = await client.get(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"?aminoacidChange=Pro1856Ser&geneId=BRCA1")
                responsetext=await resp.text()
                responsedict=json.loads(responsetext)
                assert responsedict["responseSummary"]["numTotalResults"] == 1
                assert resp.status == 200
            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_post_cross_query_individuals_g_variants_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_post_cross_query_g_variants_individuals_is_working():
                resp = await client.post(conf.uri_subpath+"/"+genomicVariant.endpoint_name, json={"meta": {
                    "apiVersion": "2.0"
                },
                "query": {
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
                resp = await client.post(conf.uri_subpath+"/"+biosample.endpoint_name, json={"meta": {
                    "apiVersion": "2.0"
                },
                "query": {
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
                resp = await client.get(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"?star=12448")
                assert resp.status == 400
            loop.run_until_complete(test_check_request_parameters_fail())
            loop.run_until_complete(client.close())# pragma: no cover
    def test_main_check_wrong_combination_request_parameters(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_wrong_combination_request_parameters():
                resp = await client.get(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"?start=12448")
                assert resp.status == 400
            loop.run_until_complete(test_wrong_combination_request_parameters())
            loop.run_until_complete(client.close())# pragma: no cover
    def test_main_check_datasets_g_variants_endpoint_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_datasets_g_variants_endpoint_is_working():
                resp = await client.get(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"?datasets=test")
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
                resp = cross_query(MagicClass, {'$or': [{'ethnicity.id': 'NCIT:C43851'}]}, 'individual', 'biosamples', {}, 'test')
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
                resp = cross_query(MagicClass, {'$or': [{'ethnicity.id': 'NCIT:C43851'}]}, 'individual', 'g_variants', {}, 'test')
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
                resp = cross_query(MagicClass, {'$or': [{'platformModel.id': 'OBI:0002048'}]}, 'run', 'individuals', {}, 'test')
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
                resp = cross_query(MagicClass, {'$or': [{'platformModel.id': 'OBI:0002048'}]}, 'run', 'biosamples', {}, 'test')
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
                resp = cross_query(MagicClass, {'$or': [{'platformModel.id': 'OBI:0002048'}]}, 'run', 'g_variants', {}, 'test')
                assert resp != {}
            loop.run_until_complete(test_check_cross_query_9_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_alphanumeric_equal_query_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_alphanumeric_equal_query_is_working():
                resp = await client.post(conf.uri_subpath+"/"+individual.endpoint_name, json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": {
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
                resp = await client.post(conf.uri_subpath+"/"+individual.endpoint_name, json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": {
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
                resp = await client.post(conf.uri_subpath+"/"+individual.endpoint_name, json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": {
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
                resp = await client.post(conf.uri_subpath+"/"+individual.endpoint_name, json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": {
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
                resp = await client.post(conf.uri_subpath+"/"+individual.endpoint_name, json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": {
                    "filters": [
            {"id": "exposures.ageAtExposure.iso8601duration",
                    "operator": ">",
                    "value": "31"}],
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
                resp = await client.post(conf.uri_subpath+"/"+individual.endpoint_name, json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": {
                    "filters": [
            {"id": "exposures.ageAtExposure.iso8601duration",
                    "operator": "<",
                    "value": "33"}],
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
                resp = await client.post(conf.uri_subpath+"/"+individual.endpoint_name, json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": {
                    "filters": [
            {"id": "exposures.ageAtExposure.iso8601duration",
                    "operator": "=",
                    "value": "34"}],
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
                resp = await client.post(conf.uri_subpath+"/"+individual.endpoint_name, json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": {
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
                resp = await client.post(conf.uri_subpath+"/"+biosample.endpoint_name, json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": {
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
                resp = await client.get(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"?start=345675&referenceName=2&assemblyId=GRCh38&end=345681&variantMinLength=0&variantMaxLength=10&testMode=true")
                assert resp.status == 200
            loop.run_until_complete(test_check_range_query_with_variant_min_and_max_lengths_working())
            loop.run_until_complete(client.close())
    def test_main_check_filters_as_request_parameter_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_filters_as_request_parameter_working():
                resp = await client.get(conf.uri_subpath+"/"+individual.endpoint_name+"?filters=NCIT:C16576&testMode=true")
                assert resp.status == 200
            loop.run_until_complete(test_check_filters_as_request_parameter_working())
            loop.run_until_complete(client.close())
    def test_main_check_datasets_list_query_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_datasets_list_query_is_working():
                resp = await client.post(conf.uri_subpath+"/"+individual.endpoint_name, json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": { "requestParameters": {
                "datasets": ["test"]
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
                resp = await client.get(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"?start=16050074&end=16050075&assemblyId=GRCh38&referenceName=22")
                assert resp.status == 200
            loop.run_until_complete(test_check_range_query_with_variant_assemblyId_GRCh38_working())
            loop.run_until_complete(client.close())
    def test_main_check_range_query_with_variant_assemblyId_GRCh37_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_range_query_with_variant_assemblyId_GRCh37_working():
                resp = await client.get(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"?start=16050074&end=16050075&assemblyId=GRCh37&referenceName=22")
                assert resp.status == 200
            loop.run_until_complete(test_check_range_query_with_variant_assemblyId_GRCh37_working())
            loop.run_until_complete(client.close())
    def test_main_check_range_query_with_variant_assemblyId_NCBI36_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_range_query_with_variant_assemblyId_NCBI36_working():
                resp = await client.get(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"?start=16050074&end=16050075&assemblyId=NCBI36&referenceName=22")
                assert resp.status == 200
            loop.run_until_complete(test_check_range_query_with_variant_assemblyId_NCBI36_working())
            loop.run_until_complete(client.close())
    def test_main_check_NONE_count_query_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_NONE_count_query_is_working():
                resp = await client.post(conf.uri_subpath+"/"+individual.endpoint_name, json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": {
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
                resp = await client.post(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"/96c1004e-1449-11f0-83f8-0242ac120003:G:ATG/"+individual.endpoint_name, json={
                    "meta": {
                        "apiVersion": "2.0"
                    },
                    "query":{
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
                responsetext=await resp.text()
                responsedict=json.loads(responsetext)
                assert responsedict["responseSummary"]["numTotalResults"] == 7
                assert resp.status == 200
            loop.run_until_complete(test_check_heterozygosity())
            loop.run_until_complete(client.close())
    def test_individuals_variants_with_homozygosity(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_homozygosity():
                resp = await client.post(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"/96c0d754-1449-11f0-83f8-0242ac120003:T:TGCAAATGCAAATGCAAATGCAAA/"+individual.endpoint_name, json={
                    "meta": {
                        "apiVersion": "2.0"
                    },
                    "query":{
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
                resp = await client.post(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"/96c1004e-1449-11f0-83f8-0242ac120003:G:ATG/"+individual.endpoint_name, json={
                    "meta": {
                        "apiVersion": "2.0"
                    },
                    "query":{
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
                resp = await client.post(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"/96c1004e-1449-11f0-83f8-0242ac120003:G:ATG/"+analysis.endpoint_name+"", json={
                    "meta": {
                        "apiVersion": "2.0"
                    },
                    "query":{
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
                resp = await client.post(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"/96c0d754-1449-11f0-83f8-0242ac120003:T:TGCAAATGCAAATGCAAATGCAAA/"+analysis.endpoint_name+"", json={
                    "meta": {
                        "apiVersion": "2.0"
                    },
                    "query":{
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
                resp = await client.post(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"/96c1004e-1449-11f0-83f8-0242ac120003:G:ATG/"+analysis.endpoint_name+"", json={
                    "meta": {
                        "apiVersion": "2.0"
                    },
                    "query":{
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
                resp = await client.post(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"/96c1004e-1449-11f0-83f8-0242ac120003:G:ATG/"+biosample.endpoint_name, json={
                    "meta": {
                        "apiVersion": "2.0"
                    },
                    "query":{
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
                resp = await client.post(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"/96c0d754-1449-11f0-83f8-0242ac120003:T:TGCAAATGCAAATGCAAATGCAAA/"+biosample.endpoint_name, json={
                    "meta": {
                        "apiVersion": "2.0"
                    },
                    "query":{
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
                resp = await client.post(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"/96c37518-1449-11f0-83f8-0242ac120003:AGCAG:A/"+biosample.endpoint_name, json={
                    "meta": {
                        "apiVersion": "2.0"
                    },
                    "query":{
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
                resp = await client.post(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"/96c1004e-1449-11f0-83f8-0242ac120003:G:ATG/"+run.endpoint_name, json={
                    "meta": {
                        "apiVersion": "2.0"
                    },
                    "query":{
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
                resp = await client.post(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"/96c0d754-1449-11f0-83f8-0242ac120003:T:TGCAAATGCAAATGCAAATGCAAA/"+run.endpoint_name, json={
                    "meta": {
                        "apiVersion": "2.0"
                    },
                    "query":{
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
                resp = await client.post(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"/96c1004e-1449-11f0-83f8-0242ac120003:G:ATG/"+run.endpoint_name, json={
                    "meta": {
                        "apiVersion": "2.0"
                    },
                    "query":{
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
    '''
    def test_individuals_with_variant_filter(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_individuals_variants():
                resp = await client.post(conf.uri_subpath+"/"+individual.endpoint_name, json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": {
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
                resp = await client.post(conf.uri_subpath+"/"+biosample.endpoint_name, json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": {
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
                resp = await client.post(conf.uri_subpath+"/"+analysis.endpoint_name+"", json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": {
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
                resp = await client.post(conf.uri_subpath+"/"+run.endpoint_name, json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": {
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
    '''
    def test_variants_with_run_filter(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_runs_variants():
                resp = await client.post(conf.uri_subpath+"/"+genomicVariant.endpoint_name, json={
                    "meta": {
                        "apiVersion": "2.0"
                    },
                    "query": {
                "filters": [{"id": "GENEPIO:0001966", "scope": "run"}],
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
                resp = await client.post(conf.uri_subpath+"/"+individual.endpoint_name, json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query":{
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
                resp = await client.post(conf.uri_subpath+"/"+analysis.endpoint_name+"", json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query":{
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
                resp = await client.post(conf.uri_subpath+"/"+biosample.endpoint_name, json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query":{
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
                resp = await client.post(conf.uri_subpath+"/"+genomicVariant.endpoint_name, json={
            "meta": {
                "apiVersion": "2.0"
            },
            "query":{
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
                resp = await client.post(conf.uri_subpath+"/"+individual.endpoint_name, json={
            "meta": {
                "apiVersion": "2.0"
            },
            "query":{
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
                resp = await client.post(conf.uri_subpath+"/"+analysis.endpoint_name+"", json={
            "meta": {
                "apiVersion": "2.0"
            },
            "query":{
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
                resp = await client.post(conf.uri_subpath+"/"+run.endpoint_name, json={
            "meta": {
                "apiVersion": "2.0"
            },
            "query":{
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
                resp = await client.post(conf.uri_subpath+"/"+individual.endpoint_name, json={
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
                resp = await client.post(conf.uri_subpath+"/"+biosample.endpoint_name, json={
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
                resp = await client.post(conf.uri_subpath+"/"+analysis.endpoint_name+"", json={
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
    '''
    def test_variants_with_request_parameters_and_filters(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_runs_variants():
                resp = await client.post(conf.uri_subpath+"/"+genomicVariant.endpoint_name, json={
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
    '''
    def test_main_check_g_variants_sequence_query_fails(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_endpoint_with_parameters_is_working():
                resp = await client.get(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"?start=43045703&referenceName=17&referenceBases=G&alternateBases=A")
                assert resp.status == 400
            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())# pragma: no cover
    def test_main_check_g_variants_range_query_fails(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_endpoint_with_parameters_is_working():
                resp = await client.get(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"?start=345675&referenceName=2&end=345681")
                assert resp.status == 400
            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())# pragma: no cover
    def test_main_check_g_variants_bracket_query_fails(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_endpoint_with_parameters_is_working():
                resp = await client.get(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"?start=43045703,43045704&end=43045704,43045705&referenceName=17")
                assert resp.status == 400
            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())# pragma: no cover
    def test_main_check_test_mode_fails(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_endpoint_with_parameters_is_working():
                resp = await client.get(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"?start=43045703,43045704&end=43045704,43045705&referenceName=17&assemblyId=GRCh38&testMode=3")
                assert resp.status == 400
            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())# pragma: no cover
    def test_descendant_terms(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_runs_variants():
                resp = await client.post(conf.uri_subpath+"/"+individual.endpoint_name, json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query":{
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
                resp = await client.get(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"?start=31121923&referenceName=X&assemblyId=GRCh38&end=31121924")
                assert resp.status == 200
            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())# pragma: no cover
    def test_main_check_g_variants_range_query_chrY(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_g_variants_endpoint_with_parameters_is_working():
                resp = await client.get(conf.uri_subpath+"/"+genomicVariant.endpoint_name+"?start=31121923&referenceName=Y&assemblyId=GRCh38&end=31121924")
                assert resp.status == 200
            loop.run_until_complete(test_check_g_variants_endpoint_with_parameters_is_working())
            loop.run_until_complete(client.close())# pragma: no cover
    def test_main_check_limit_query_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_limit_query_is_working():
                resp = await client.post(conf.uri_subpath+"/"+individual.endpoint_name, json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": { "requestParameters": {
                "datasets": ["test"]
                },
                    "filters": [                ],
                    "includeResultsetResponses": "HIT",
                    "pagination": {
                        "skip": 0,
                        "limit": 15
                    },
                    "testMode": True,
                    "requestedGranularity": "record"
                }
            }
            )
                responsetext=await resp.text()
                responsedict=json.loads(responsetext)
                assert len(responsedict["response"]["resultSets"][0]["results"]) == 15
                assert resp.status == 200
            loop.run_until_complete(test_check_limit_query_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_record_resultSet_query_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_record_resultSet_query_is_working():
                resp = await client.post(conf.uri_subpath+"/"+individual.endpoint_name, json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": { "requestParameters": {
                "datasets": ["test"]
                },
                    "filters": [                ],
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
                responsetext=await resp.text()
                responsedict=json.loads(responsetext)
                assert len(responsedict["response"]["resultSets"][0]["results"]) == 10
                assert resp.status == 200
            loop.run_until_complete(test_check_record_resultSet_query_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_count_resultSet_query_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_count_resultSet_query_is_working():
                resp = await client.post(conf.uri_subpath+"/"+individual.endpoint_name, json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": { "requestParameters": {
                "datasets": ["test"]
                },
                    "filters": [                ],
                    "includeResultsetResponses": "HIT",
                    "pagination": {
                        "skip": 0,
                        "limit": 10
                    },
                    "testMode": True,
                    "requestedGranularity": "count"
                }
            }
            )
                responsetext=await resp.text()
                responsedict=json.loads(responsetext)
                assert responsedict["response"]["resultSets"][0].get("results") == None
                assert responsedict["responseSummary"]["numTotalResults"] == 20
                assert responsedict["response"]["resultSets"][0]["resultsCount"] == 20
                assert resp.status == 200
            loop.run_until_complete(test_check_count_resultSet_query_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_boolean_resultSet_query_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_boolean_resultSet_query_is_working():
                resp = await client.post(conf.uri_subpath+"/"+individual.endpoint_name, json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": { "requestParameters": {
                "datasets": ["test"]
                },
                    "filters": [                ],
                    "includeResultsetResponses": "HIT",
                    "pagination": {
                        "skip": 0,
                        "limit": 10
                    },
                    "testMode": True,
                    "requestedGranularity": "boolean"
                }
            }
            )
                responsetext=await resp.text()
                responsedict=json.loads(responsetext)
                assert responsedict["response"]["resultSets"][0].get("results") == None
                assert responsedict["response"]["resultSets"][0].get("resultsCount") == None
                assert responsedict["response"]["resultSets"][0]["exists"] == True
                assert resp.status == 200
            loop.run_until_complete(test_check_boolean_resultSet_query_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_boolean_query_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_boolean_query_is_working():
                resp = await client.post(conf.uri_subpath+"/"+individual.endpoint_name, json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": { "requestParameters": {
                "datasets": ["test"]
                },
                    "filters": [                ],
                    "includeResultsetResponses": "NONE",
                    "pagination": {
                        "skip": 0,
                        "limit": 10
                    },
                    "testMode": True,
                    "requestedGranularity": "boolean"
                }
            }
            )
                responsetext=await resp.text()
                responsedict=json.loads(responsetext)
                assert responsedict.get("response") == None
                assert responsedict["responseSummary"]["exists"] == True
                assert responsedict["responseSummary"].get("numTotalResults") == None
                assert resp.status == 200
            loop.run_until_complete(test_check_boolean_query_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_counts_query_is_working(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_counts_query_is_working():
                resp = await client.post(conf.uri_subpath+"/"+individual.endpoint_name, json={
                "meta": {
                    "apiVersion": "2.0"
                },
                "query": { "requestParameters": {
                "datasets": ["test"]
                },
                    "filters": [                ],
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
                responsetext=await resp.text()
                responsedict=json.loads(responsetext)
                assert responsedict.get("response") == None
                assert responsedict["responseSummary"]["exists"] == True
                assert responsedict["responseSummary"]["numTotalResults"] == 20
                assert resp.status == 200
            loop.run_until_complete(test_check_counts_query_is_working())
            loop.run_until_complete(client.close())
    def test_main_check_requestedSchemas(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_requestedSchemas():
                resp = await client.post(conf.uri_subpath+"/"+individual.endpoint_name, json={
                "meta": {
                    "apiVersion": "2.0",
                    "requestedSchemas": [{"schema": "beacon-individual-v2.0.0"}]
                },
                "query": { "requestParameters": {
                "datasets": ["test"]
                },
                    "filters": [                ],
                    "includeResultsetResponses": "HIT",
                    "pagination": {
                        "skip": 0,
                        "limit": 10
                    },
                    "testMode": True,
                    "requestedGranularity": "boolean"
                }
            }
            )
                assert resp.status == 200
            loop.run_until_complete(test_check_requestedSchemas())
            loop.run_until_complete(client.close())
    def test_main_check_requestedSchemas_fails(self):
        with loop_context() as loop:
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_requestedSchemas_fails():
                resp = await client.post(conf.uri_subpath+"/"+individual.endpoint_name, json={
                "meta": {
                    "apiVersion": "2.0",
                    "requestedSchemas": [{"schema": "beacon-individua-v2.0.0"}]
                },
                "query": { "requestParameters": {
                "datasets": ["test"]
                },
                    "filters": [                ],
                    "includeResultsetResponses": "HIT",
                    "pagination": {
                        "skip": 0,
                        "limit": 10
                    },
                    "testMode": True,
                    "requestedGranularity": "boolean"
                }
            }
            )
                assert resp.status == 400
            loop.run_until_complete(test_check_requestedSchemas_fails())
            loop.run_until_complete(client.close())

if __name__ == '__main__':
    unittest.main()