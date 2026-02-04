from aiohttp.test_utils import TestClient, TestServer, loop_context
from beacon.tests.__main__ import create_app
import json
import unittest
import beacon.conf.conf_override as conf_override
from beacon.logs.logs import LOG
from beacon.validator.configuration import check_configuration
import yaml

def import_genomicVariant_confile():
    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'r') as pfile:
        genomicVariant_confile= yaml.safe_load(pfile)
    pfile.close()
    return genomicVariant_confile

def import_dataset_confile():
    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'r') as pfile:
        dataset_confile= yaml.safe_load(pfile)
    pfile.close()
    return dataset_confile

def import_analysis_confile():
    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'r') as pfile:
        analysis_confile= yaml.safe_load(pfile)
    pfile.close()
    return analysis_confile

def import_biosample_confile():
    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'r') as pfile:
        biosample_confile= yaml.safe_load(pfile)
    pfile.close()
    return biosample_confile

def import_cohort_confile():
    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'r') as pfile:
        cohort_confile= yaml.safe_load(pfile)
    pfile.close()
    return cohort_confile

def import_individual_confile():
    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'r') as pfile:
        individual_confile= yaml.safe_load(pfile)
    pfile.close()
    return individual_confile

def import_run_confile():
    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/run.yml", 'r') as pfile:
        run_confile= yaml.safe_load(pfile)
    pfile.close()
    return run_confile

analysis = import_analysis_confile()
biosample = import_biosample_confile()
cohort = import_cohort_confile()
dataset = import_dataset_confile()
genomicVariant = import_genomicVariant_confile()
run = import_run_confile()
individual = import_individual_confile()

class TestNoFilters(unittest.TestCase):
    def test_no_filters_analysis_query_without_filters_allowed(self):
        with loop_context() as loop:
            analysis["analysis"]["allow_queries_without_filters"]=False
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_analysis_query_without_filters_allowed():
                resp = await client.get(conf_override.config.uri_subpath+"/"+analysis["analysis"]["endpoint_name"])
                assert resp.status == 400
            loop.run_until_complete(test_analysis_query_without_filters_allowed())
            loop.run_until_complete(client.close())
            analysis["analysis"]["allow_queries_without_filters"]=True
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
    def test_no_filters_biosample_query_without_filters_allowed(self):
        with loop_context() as loop:
            biosample["biosample"]["allow_queries_without_filters"]=False
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_biosample_query_without_filters_allowed():
                resp = await client.get(conf_override.config.uri_subpath+"/"+biosample["biosample"]["endpoint_name"])
                assert resp.status == 400
            loop.run_until_complete(test_biosample_query_without_filters_allowed())
            loop.run_until_complete(client.close())
            biosample["biosample"]["allow_queries_without_filters"]=True
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
    def test_no_filters_cohort_query_without_filters_allowed(self):
        with loop_context() as loop:
            cohort["cohort"]["allow_queries_without_filters"]=False
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_cohort_query_without_filters_allowed():
                resp = await client.get(conf_override.config.uri_subpath+"/"+cohort["cohort"]["endpoint_name"])
                assert resp.status == 400
            loop.run_until_complete(test_cohort_query_without_filters_allowed())
            loop.run_until_complete(client.close())
            cohort["cohort"]["allow_queries_without_filters"]=True
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
    def test_no_filters_dataset_query_without_filters_allowed(self):
        with loop_context() as loop:
            dataset["dataset"]["allow_queries_without_filters"]=False
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_dataset_query_without_filters_allowed():
                resp = await client.get(conf_override.config.uri_subpath+"/"+dataset["dataset"]["endpoint_name"])
                assert resp.status == 400
            loop.run_until_complete(test_dataset_query_without_filters_allowed())
            loop.run_until_complete(client.close())
            dataset["dataset"]["allow_queries_without_filters"]=True
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
    def test_no_filters_genomicVariation_query_without_filters_allowed(self):
        with loop_context() as loop:
            genomicVariant["genomicVariant"]["allow_queries_without_filters"]=False
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_genomicVariant_query_without_filters_allowed():
                resp = await client.get(conf_override.config.uri_subpath+"/"+genomicVariant["genomicVariant"]["endpoint_name"])
                assert resp.status == 400
            loop.run_until_complete(test_genomicVariant_query_without_filters_allowed())
            loop.run_until_complete(client.close())
            genomicVariant["genomicVariant"]["allow_queries_without_filters"]=True
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
    def test_no_filters_individual_query_without_filters_allowed(self):
        with loop_context() as loop:
            individual["individual"]["allow_queries_without_filters"]=False
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_individual_query_without_filters_allowed():
                resp = await client.get(conf_override.config.uri_subpath+"/"+individual["individual"]["endpoint_name"])
                assert resp.status == 400
            loop.run_until_complete(test_individual_query_without_filters_allowed())
            loop.run_until_complete(client.close())
            individual["individual"]["allow_queries_without_filters"]=True
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)
    
    def test_no_filters_run_query_without_filters_allowed(self):
        with loop_context() as loop:
            run["run"]["allow_queries_without_filters"]=False
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_run_query_without_filters_allowed():
                resp = await client.get(conf_override.config.uri_subpath+"/"+run["run"]["endpoint_name"])
                assert resp.status == 400
            loop.run_until_complete(test_run_query_without_filters_allowed())
            loop.run_until_complete(client.close())
            run["run"]["allow_queries_without_filters"]=True
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
    def test_map_endpoint_response_with_disabled_endpoint(self):
        with loop_context() as loop:
            analysis["analysis"]["entry_type_enabled"]=False
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
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
            analysis["analysis"]["entry_type_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
    def test_configuration_endpoint_response_with_disabled_endpoint(self):
        with loop_context() as loop:
            analysis["analysis"]["entry_type_enabled"]=False
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
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
            analysis["analysis"]["entry_type_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
    def test_main_check_configuration_with_wrong_analysis_enable_endpoint(self):
        with loop_context() as loop:
            analysis["analysis"]["entry_type_enabled"]="no Boolean"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_analysis():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_analysis())
            loop.run_until_complete(client.close())
            analysis["analysis"]["entry_type_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
    def test_main_check_configuration_with_wrong_biosample_enable_endpoint(self):
        with loop_context() as loop:
            biosample["biosample"]["entry_type_enabled"]="no Boolean"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_biosample():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_biosample())
            loop.run_until_complete(client.close())
            biosample["biosample"]["entry_type_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
    def test_main_check_configuration_with_wrong_cohort_enable_endpoint(self):
        with loop_context() as loop:
            cohort["cohort"]["entry_type_enabled"]="no Boolean"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_cohort():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_cohort())
            loop.run_until_complete(client.close())
            cohort["cohort"]["entry_type_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
    def test_main_check_configuration_with_wrong_dataset_enable_endpoint(self):
        with loop_context() as loop:
            dataset["dataset"]["entry_type_enabled"]="no Boolean"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_dataset():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_dataset())
            loop.run_until_complete(client.close())
            dataset["dataset"]["entry_type_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
    def test_main_check_configuration_with_wrong_individual_enable_endpoint(self):
        with loop_context() as loop:
            individual["individual"]["entry_type_enabled"]="no Boolean"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_individual():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_individual())
            loop.run_until_complete(client.close())
            individual["individual"]["entry_type_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)
    def test_main_check_configuration_with_wrong_genomicVariant_enable_endpoint(self):
        with loop_context() as loop:
            genomicVariant["genomicVariant"]["entry_type_enabled"]="no Boolean"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_genomicVariant():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_genomicVariant())
            loop.run_until_complete(client.close())
            genomicVariant["genomicVariant"]["entry_type_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
    def test_main_check_configuration_with_wrong_run_enable_endpoint(self):
        with loop_context() as loop:
            run["run"]["entry_type_enabled"]="no Boolean"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_run():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_run())
            loop.run_until_complete(client.close())
            run["run"]["entry_type_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
    def test_main_check_configuration_with_wrong_analysis_granularity(self):
        with loop_context() as loop:
            analysis["analysis"]["max_granularity"]="no Boolean"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_analysis():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_analysis())
            loop.run_until_complete(client.close())
            analysis["analysis"]["max_granularity"]="record"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
    def test_main_check_configuration_with_wrong_biosample_granularity(self):
        with loop_context() as loop:
            biosample["biosample"]["max_granularity"]="no Boolean"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_biosample():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_biosample())
            loop.run_until_complete(client.close())
            biosample["biosample"]["max_granularity"]="record"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
    def test_main_check_configuration_with_wrong_cohort_granularity(self):
        with loop_context() as loop:
            cohort["cohort"]["max_granularity"]="no Boolean"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_cohort():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_cohort())
            loop.run_until_complete(client.close())
            cohort["cohort"]["max_granularity"]="record"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
    def test_main_check_configuration_with_wrong_dataset_granularity(self):
        with loop_context() as loop:
            dataset["dataset"]["max_granularity"]="no Boolean"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_dataset():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_dataset())
            loop.run_until_complete(client.close())
            dataset["dataset"]["max_granularity"]="record"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
    def test_main_check_configuration_with_wrong_individual_granularity(self):
        with loop_context() as loop:
            individual["individual"]["max_granularity"]="no Boolean"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_individual():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_individual())
            loop.run_until_complete(client.close())
            individual["individual"]["max_granularity"]="record"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)
    def test_main_check_configuration_with_wrong_genomicVariant_granularity(self):
        with loop_context() as loop:
            genomicVariant["genomicVariant"]["max_granularity"]="no Boolean"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_genomicVariant():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_genomicVariant())
            loop.run_until_complete(client.close())
            genomicVariant["genomicVariant"]["max_granularity"]="record"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
    def test_main_check_configuration_with_wrong_run_granularity(self):
        with loop_context() as loop:
            run["run"]["max_granularity"]="no Boolean"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_granularity_run():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_granularity_run())
            loop.run_until_complete(client.close())
            run["run"]["max_granularity"]="record"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
    def test_main_check_configuration_http(self):
        with loop_context() as loop:
            from beacon.conf import conf_override
            conf_override.config.uri="https://localhost:5010"
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_http():
                check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
            loop.run_until_complete(test_check_configuration_http())
            loop.run_until_complete(client.close())
            conf_override.config.uri="http://localhost:50101"
    def test_main_check_configuration_wrong_uri(self):
        with loop_context() as loop:
            from beacon.conf import conf_override
            conf_override.config.uri="afafsafas"
            async def test_check_configuration_wrong_uri():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
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
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
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
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
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
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
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
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
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
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
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
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
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
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
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
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_wrong_query_budget_database())
            conf_override.config.query_budget_database="mongo"
    def test_main_check_configuration_with_wrong_analysis_database(self):
        with loop_context() as loop:
            analysis["analysis"]["connection"]["name"]="no Boolean"
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_analysis():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_analysis())
            loop.run_until_complete(client.close())
            analysis["analysis"]["connection"]["name"]="mongo"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
    def test_main_check_configuration_with_wrong_biosample_database(self):
        with loop_context() as loop:
            biosample["biosample"]["connection"]["name"]="no Boolean"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_biosample():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_biosample())
            loop.run_until_complete(client.close())
            biosample["biosample"]["connection"]["name"]="mongo"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
    def test_main_check_configuration_with_wrong_cohort_database(self):
        with loop_context() as loop:
            cohort["cohort"]["connection"]["name"]="no Boolean"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_cohort():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_cohort())
            loop.run_until_complete(client.close())
            cohort["cohort"]["connection"]["name"]="mongo"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
    def test_main_check_configuration_with_wrong_dataset_database(self):
        with loop_context() as loop:
            dataset["dataset"]["connection"]["name"]="no Boolean"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_dataset():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_dataset())
            loop.run_until_complete(client.close())
            dataset["dataset"]["connection"]["name"]="mongo"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
    def test_main_check_configuration_with_wrong_individual_database(self):
        with loop_context() as loop:
            individual["individual"]["connection"]["name"]="no Boolean"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_individual():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_individual())
            loop.run_until_complete(client.close())
            individual["individual"]["connection"]["name"]="mongo"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)
    def test_main_check_configuration_with_wrong_genomicVariant_database(self):
        with loop_context() as loop:
            genomicVariant["genomicVariant"]["connection"]["name"]="no Boolean"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_enable_genomicVariant():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_genomicVariant())
            loop.run_until_complete(client.close())
            genomicVariant["genomicVariant"]["connection"]["name"]="mongo"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
    def test_main_check_configuration_with_wrong_run_database(self):
        with loop_context() as loop:
            run["run"]["connection"]["name"]="no Boolean"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_configuration_database_run():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_database_run())
            loop.run_until_complete(client.close())
            run["run"]["connection"]["name"]="mongo"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
    def test_main_check_configuration_wrong_environment(self):
        with loop_context() as loop:
            from beacon.conf import conf_override
            conf_override.config.environment="api"
            async def test_check_configuration_wrong_environment():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
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
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_wrong_granularity())
            conf_override.config.default_beacon_granularity="record"
    def test_analyses_endpoint_name_is_string(self):
        with loop_context() as loop:
            analysis["analysis"]["endpoint_name"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
            async def test_check_endpoint_endpoint_name_is_string():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_endpoint_endpoint_name_is_string())
            analysis["analysis"]["endpoint_name"]="analyses"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
    def test_biosamples_endpoint_name_is_string(self):
        with loop_context() as loop:
            biosample["biosample"]["endpoint_name"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
            async def test_check_endpoint_endpoint_name_is_string():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_endpoint_endpoint_name_is_string())
            biosample["biosample"]["endpoint_name"]="biosamples"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
    def test_cohorts_endpoint_name_is_string(self):
        with loop_context() as loop:
            cohort["cohort"]["endpoint_name"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
            async def test_check_endpoint_endpoint_name_is_string():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_endpoint_endpoint_name_is_string())
            cohort["cohort"]["endpoint_name"]="cohorts"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
    def test_datasets_endpoint_name_is_string(self):
        with loop_context() as loop:
            dataset["dataset"]["endpoint_name"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
            async def test_check_endpoint_endpoint_name_is_string():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_endpoint_endpoint_name_is_string())
            dataset["dataset"]["endpoint_name"]="datasets"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
    def test_g_variants_endpoint_name_is_string(self):
        with loop_context() as loop:
            genomicVariant["genomicVariant"]["endpoint_name"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
            async def test_check_endpoint_endpoint_name_is_string():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_endpoint_endpoint_name_is_string())
            genomicVariant["genomicVariant"]["endpoint_name"]="g_variants"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
    def test_runs_endpoint_name_is_string(self):
        with loop_context() as loop:
            run["run"]["endpoint_name"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
            async def test_check_endpoint_endpoint_name_is_string():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_endpoint_endpoint_name_is_string())
            run["run"]["endpoint_name"]="runs"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
    def test_individuals_endpoint_name_is_string(self):
        with loop_context() as loop:
            individual["individual"]["endpoint_name"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)
            async def test_check_endpoint_endpoint_name_is_string():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_endpoint_endpoint_name_is_string())
            individual["individual"]["endpoint_name"]="individuals"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)
    

    

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