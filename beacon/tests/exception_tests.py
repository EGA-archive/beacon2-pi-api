from aiohttp.test_utils import TestClient, TestServer, loop_context
from aiohttp import web
from beacon.tests.__main__ import create_app
import unittest
import beacon.conf.conf_override as conf_override
from beacon.logs.logs import LOG
from aiohttp_middlewares import cors_middleware
from beacon.validator.configuration import contains_special_characters, check_configuration
import logging
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


class TestConfigurationExceptions(unittest.TestCase):
    def test_main_check_configuration_wrong_security_levels(self):
        with loop_context() as loop:
            from beacon.conf import conf_override
            conf_override.config.security_levels="api"
            async def test_check_configuration_wrong_security_levels():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    try:
                        conf_override.config.security_levels=["api"]
                        check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                    except Exception:
                        pass
            loop.run_until_complete(test_check_configuration_wrong_security_levels())
            conf_override.config.security_levels=['PUBLIC', 'REGISTERED', 'CONTROLLED']
    def test_main_check_configuration_wrong_cors_urls(self):
        with loop_context() as loop:
            from beacon.conf import conf_override
            conf_override.config.cors_urls="api"
            async def test_check_configuration_wrong_cors_urls():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    try:
                        conf_override.config.cors_urls=["api"]
                        check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                    except Exception:
                        pass
            loop.run_until_complete(test_check_configuration_wrong_cors_urls())
            conf_override.config.cors_urls = ["http://localhost:3003", "http://localhost:3000"]
    def test_analyses_contains_special_chars(self):
        with loop_context() as loop:
            analysis["analysis"]["endpoint_name"]="%aydga&-_al)"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
            async def test_check_endpoint_contains_special_chars():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_endpoint_contains_special_chars())
            analysis["analysis"]["endpoint_name"]="analyses"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
    def test_biosamples_contains_special_chars(self):
        with loop_context() as loop:
            biosample["biosample"]["endpoint_name"]="%aydga&-_al)"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
            async def test_check_endpoint_contains_special_chars():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_endpoint_contains_special_chars())
            biosample["biosample"]["endpoint_name"]="biosamples"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
    def test_cohorts_contains_special_chars(self):
        with loop_context() as loop:
            cohort["cohort"]["endpoint_name"]="%aydga&-_al)"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
            async def test_check_endpoint_contains_special_chars():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_endpoint_contains_special_chars())
            cohort["cohort"]["endpoint_name"]="cohorts"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
    def test_datasets_contains_special_chars(self):
        with loop_context() as loop:
            dataset["dataset"]["endpoint_name"]="%aydga&-_al)"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
            async def test_check_endpoint_contains_special_chars():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_endpoint_contains_special_chars())
            dataset["dataset"]["endpoint_name"]="datasets"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
    def test_g_variants_contains_special_chars(self):
        with loop_context() as loop:
            genomicVariant["genomicVariant"]["endpoint_name"]="%aydga&-_al)"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
            async def test_check_endpoint_contains_special_chars():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_endpoint_contains_special_chars())
            genomicVariant["genomicVariant"]["endpoint_name"]="g_variants"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
    def test_runs_contains_special_chars(self):
        with loop_context() as loop:
            run["run"]["endpoint_name"]="%aydga&-_al)"
            async def test_check_endpoint_contains_special_chars():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_endpoint_contains_special_chars())
            run["run"]["endpoint_name"]="runs"
    def test_individuals_contains_special_chars(self):
        with loop_context() as loop:
            individual["individual"]["endpoint_name"]="%aydga&-_al)"
            async def test_check_endpoint_contains_special_chars():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_endpoint_contains_special_chars())
            individual["individual"]["endpoint_name"]="individuals"
    def test_analyses_open_api_endpoints_definition(self):
        with loop_context() as loop:
            analysis["analysis"]["open_api_definition"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
            async def test_check_analyses_open_api_endpoints_definition():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_open_api_endpoints_definition())
            analysis["analysis"]["open_api_definition"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
    def test_analyses_name(self):
        with loop_context() as loop:
            analysis["analysis"]["info"]["name"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
            async def test_check_analyses_name():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_name())
            analysis["analysis"]["info"]["name"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
    def test_analyses_ontology_id(self):
        with loop_context() as loop:
            analysis["analysis"]["info"]["ontology_id"]="NOT13132 CURIE_!"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
            async def test_check_analyses_ontology_id():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_ontology_id())
            analysis["analysis"]["info"]["ontology_id"]="CURIE:12345"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
    def test_analyses_ontology_name(self):
        with loop_context() as loop:
            analysis["analysis"]["info"]["ontology_name"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
            async def test_check_analyses_ontology_name():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_ontology_name())
            analysis["analysis"]["info"]["ontology_name"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
    def test_analyses_specification(self):
        with loop_context() as loop:
            analysis["analysis"]["schema"]["specification"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
            async def test_check_analyses_specification():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_specification())
            analysis["analysis"]["schema"]["specification"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
    def test_analyses_description(self):
        with loop_context() as loop:
            analysis["analysis"]["info"]["description"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
            async def test_check_analyses_description():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_description())
            analysis["analysis"]["info"]["description"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
    def test_analyses_default_schema_id(self):
        with loop_context() as loop:
            analysis["analysis"]["schema"]["default_schema_id"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
            async def test_check_analyses_default_schema_id():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_default_schema_id())
            analysis["analysis"]["schema"]["default_schema_id"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
    def test_analyses_default_schema_name(self):
        with loop_context() as loop:
            analysis["analysis"]["schema"]["default_schema_name"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
            async def test_check_analyses_default_schema_name():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_default_schema_name())
            analysis["analysis"]["schema"]["default_schema_name"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
    def test_analyses_reference_to_schema_definition(self):
        with loop_context() as loop:
            analysis["analysis"]["schema"]["reference_to_default_schema_definition"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
            async def test_check_analyses_reference_to_schema_definition():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_reference_to_schema_definition())
            analysis["analysis"]["schema"]["reference_to_default_schema_definition"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
    def test_analyses_default_schema_version(self):
        with loop_context() as loop:
            analysis["analysis"]["schema"]["default_schema_version"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
            async def test_check_analyses_default_schema_version():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_default_schema_version())
            analysis["analysis"]["schema"]["default_schema_version"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
    def test_analyses_additionally_supported_schemas(self):
        with loop_context() as loop:
            analysis["analysis"]["schema"]["supported_schemas"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
            async def test_check_analyses_additionally_supported_schemas():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_additionally_supported_schemas())
            analysis["analysis"]["schema"]["supported_schemas"]=["string"]
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
    def test_analyses_allow_queries_without_filters(self):
        with loop_context() as loop:
            analysis["analysis"]["allow_queries_without_filters"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
            async def test_check_analyses_allow_queries_without_filters():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_allow_queries_without_filters())
            analysis["analysis"]["allow_queries_without_filters"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
    def test_analyses_singleEntryUrl(self):
        with loop_context() as loop:
            analysis["analysis"]["allow_id_query"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
            async def test_check_analyses_singleEntryUrl():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_singleEntryUrl())
            analysis["analysis"]["allow_id_query"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
    def test_analyses_biosample_lookup(self):
        with loop_context() as loop:
            analysis["analysis"]["lookups"]["biosample"]["endpoint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
            async def test_check_analyses_biosample_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_biosample_lookup())
            analysis["analysis"]["lookups"]["biosample"]["endpoint_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
    def test_analyses_cohort_lookup(self):
        with loop_context() as loop:
            analysis["analysis"]["lookups"]["cohort"]["endpoint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
            async def test_check_analyses_cohort_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_cohort_lookup())
            analysis["analysis"]["lookups"]["cohort"]["endpoint_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
    def test_analyses_dataset_lookup(self):
        with loop_context() as loop:
            analysis["analysis"]["lookups"]["dataset"]["endpoint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
            async def test_check_analyses_dataset_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_dataset_lookup())
            analysis["analysis"]["lookups"]["dataset"]["endpoint_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
    def test_analyses_genomicVariant_lookup(self):
        with loop_context() as loop:
            analysis["analysis"]["lookups"]["genomicVariant"]["endpoint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
            async def test_check_analyses_genomicVariant_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_genomicVariant_lookup())
            analysis["analysis"]["lookups"]["genomicVariant"]["endpoint_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
    def test_analyses_individual_lookup(self):
        with loop_context() as loop:
            analysis["analysis"]["lookups"]["individual"]["endpoint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
            async def test_check_analyses_individual_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_individual_lookup())
            analysis["analysis"]["lookups"]["individual"]["endpoint_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
    def test_analyses_run_lookup(self):
        with loop_context() as loop:
            analysis["analysis"]["lookups"]["run"]["endpoint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
            async def test_check_analyses_run_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_run_lookup())
            analysis["analysis"]["lookups"]["run"]["endpoint_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
    def test_runs_open_api_endpoints_definition(self):
        with loop_context() as loop:
            run["run"]["open_api_definition"]=3
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
            async def test_check_runs_open_api_endpoints_definition():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_open_api_endpoints_definition())
            run["run"]["open_api_definition"]="string"
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
    def test_runs_name(self):
        with loop_context() as loop:
            run["run"]["info"]["name"]=3
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
            async def test_check_runs_name():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_name())
            run["run"]["info"]["name"]="string"
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
    def test_runs_ontology_id(self):
        with loop_context() as loop:
            run["run"]["info"]["ontology_id"]="NOT CURIE"
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
            async def test_check_runs_ontology_id():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_ontology_id())
            run["run"]["info"]["ontology_id"]="CURIE:12345"
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
    def test_runs_ontology_name(self):
        with loop_context() as loop:
            run["run"]["info"]["ontology_name"]=3
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
            async def test_check_runs_ontology_name():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_ontology_name())
            run["run"]["info"]["ontology_name"]="string"
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
    def test_runs_specification(self):
        with loop_context() as loop:
            run["run"]["schema"]["specification"]=3
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
            async def test_check_runs_specification():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_specification())
            run["run"]["schema"]["specification"]="string"
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
    def test_runs_description(self):
        with loop_context() as loop:
            run["run"]["info"]["description"]=3
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
            async def test_check_runs_description():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    run["run"]["info"]["description"]="string"
                    with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                        yaml.dump(run, outfile, default_flow_style=False)
                    pass
            loop.run_until_complete(test_check_runs_description())
    def test_runs_default_schema_id(self):
        with loop_context() as loop:
            run["run"]["schema"]["default_schema_id"]=3
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
            async def test_check_runs_default_schema_id():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_default_schema_id())
            run["run"]["schema"]["default_schema_id"]="string"
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

    def test_runs_default_schema_name(self):
        with loop_context() as loop:
            run["run"]["schema"]["default_schema_name"]=3
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
            async def test_check_runs_default_schema_name():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_default_schema_name())
            run["run"]["schema"]["default_schema_name"]="string"
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
    def test_runs_reference_to_schema_definition(self):
        with loop_context() as loop:
            run["run"]["schema"]["reference_to_default_schema_definition"]=3
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
            async def test_check_runs_reference_to_schema_definition():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_reference_to_schema_definition())
            run["run"]["schema"]["reference_to_default_schema_definition"]="string"
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
    def test_runs_default_schema_version(self):
        with loop_context() as loop:
            run["run"]["schema"]["default_schema_version"]=3
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
            async def test_check_runs_default_schema_version():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_default_schema_version())
            run["run"]["schema"]["default_schema_version"]="string"
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
    def test_runs_additionally_supported_schemas(self):
        with loop_context() as loop:
            run["run"]["schema"]["supported_schemas"]=3
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
            async def test_check_runs_additionally_supported_schemas():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_additionally_supported_schemas())
            run["run"]["schema"]["supported_schemas"]=["string"]
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
    def test_runs_allow_queries_without_filters(self):
        with loop_context() as loop:
            run["run"]["allow_queries_without_filters"]=3
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
            async def test_check_runs_allow_queries_without_filters():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_allow_queries_without_filters())
            run["run"]["allow_queries_without_filters"]=True
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
    def test_runs_singleEntryUrl(self):
        with loop_context() as loop:
            run["run"]["allow_id_query"]=3
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
            async def test_check_runs_singleEntryUrl():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_singleEntryUrl())
            run["run"]["allow_id_query"]=True
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
    def test_runs_analysis_lookup(self):
        with loop_context() as loop:
            run["run"]["lookups"]["analysis"]["endpooint_enabled"]=3
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
            async def test_check_runs_analysis_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_analysis_lookup())
            run["run"]["lookups"]["analysis"]["endpooint_enabled"]=True
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
    def test_runs_biosample_lookup(self):
        with loop_context() as loop:
            run["run"]["lookups"]["biosample"]["endpoint_enabled"]=3
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
            async def test_check_runs_biosample_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_biosample_lookup())
            run["run"]["lookups"]["biosample"]["endpoint_enabled"]=True
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
    def test_runs_cohort_lookup(self):
        with loop_context() as loop:
            run["run"]["lookups"]["cohort"]["endpoint_enabled"]=3
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
            async def test_check_runs_cohort_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_cohort_lookup())
            run["run"]["lookups"]["cohort"]["endpoint_enabled"]=True
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
    def test_runs_dataset_lookup(self):
        with loop_context() as loop:
            run["run"]["lookups"]["dataset"]["endpoint_enabled"]=3
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
            async def test_check_runs_dataset_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_dataset_lookup())
            run["run"]["lookups"]["dataset"]["endpoint_enabled"]=True
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
    def test_runs_genomicVariant_lookup(self):
        with loop_context() as loop:
            run["run"]["lookups"]["genomicVariant"]["endpoint_enabled"]=3
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
            async def test_check_runs_genomicVariant_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_genomicVariant_lookup())
            run["run"]["lookups"]["genomicVariant"]["endpoint_enabled"]=True
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
    def test_runs_individual_lookup(self):
        with loop_context() as loop:
            run["run"]["lookups"]["individual"]["endpoint_enabled"]=3
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
            async def test_check_runs_individual_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_individual_lookup())
            run["run"]["lookups"]["individual"]["endpoint_enabled"]=True
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
    def test_conf_level_wrong(self):
        with loop_context() as loop:
            from beacon.conf import conf_override
            conf_override.config.level='something'
            async def test_conf_level_wrong():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_conf_level_wrong())
            conf_override.config.level=logging.NOTSET
    def test_conf_log_file_wrong(self):
        with loop_context() as loop:
            from beacon.conf import conf_override
            conf_override.config.log_file=3
            async def test_conf_log_file_wrong():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_conf_log_file_wrong())
            conf_override.config.log_file=None
    def test_conf_wrong_beacon_id(self):
        with loop_context() as loop:
            from beacon.conf import conf_override
            conf_override.config.beacon_id=3
            async def test_conf_wrong_beacon_id():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_conf_wrong_beacon_id())
            conf_override.config.beacon_id="string"
    def test_conf_wrong_beacon_name(self):
        with loop_context() as loop:
            from beacon.conf import conf_override
            conf_override.config.beacon_name=3
            async def test_conf_wrong_beacon_name():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_conf_wrong_beacon_name())
            conf_override.config.beacon_name="string"
    def test_conf_wrong_api_version(self):
        with loop_context() as loop:
            from beacon.conf import conf_override
            conf_override.config.api_version=3
            async def test_conf_wrong_api_version():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_conf_wrong_api_version())
            conf_override.config.api_version="string"
    def test_conf_wrong_description(self):
        with loop_context() as loop:
            from beacon.conf import conf_override
            conf_override.config.description=3
            async def test_conf_wrong_description():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_conf_wrong_description())
            conf_override.config.description="string"
    def test_conf_wrong_welcome_url(self):
        with loop_context() as loop:
            from beacon.conf import conf_override
            conf_override.config.welcome_url=3
            async def test_conf_wrong_welcome_url():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_conf_wrong_welcome_url())
            conf_override.config.welcome_url="string"
    def test_conf_wrong_alternative_url(self):
        with loop_context() as loop:
            from beacon.conf import conf_override
            conf_override.config.alternative_url=3
            async def test_conf_wrong_alternative_url():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_conf_wrong_alternative_url())
            conf_override.config.alternative_url="string"
    def test_conf_wrong_create_datetime(self):
        with loop_context() as loop:
            from beacon.conf import conf_override
            conf_override.config.create_datetime=3
            async def test_conf_wrong_create_datetime():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_conf_wrong_create_datetime())
            conf_override.config.create_datetime="string"
    def test_conf_wrong_update_datetime(self):
        with loop_context() as loop:
            from beacon.conf import conf_override
            conf_override.config.update_datetime=3
            async def test_conf_wrong_update_datetime():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_conf_wrong_update_datetime())
            conf_override.config.update_datetime="string"
    def test_conf_wrong_documentation_url(self):
        with loop_context() as loop:
            from beacon.conf import conf_override
            conf_override.config.documentation_url=3
            async def test_conf_wrong_documentation_url():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_conf_wrong_documentation_url())
            conf_override.config.documentation_url="string"
    def test_conf_wrong_welcome_url_no_http(self):
        with loop_context() as loop:
            from beacon.conf import conf_override
            conf_override.config.welcome_url="something"
            async def test_conf_wrong_welcome_url():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_conf_wrong_welcome_url())
            conf_override.config.welcome_url="https://beacon.ega-archive.org/"
    def test_conf_wrong_alternative_url_no_http(self):
        with loop_context() as loop:
            from beacon.conf import conf_override
            conf_override.config.alternative_url="something"
            async def test_conf_wrong_alternative_url():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_conf_wrong_alternative_url())
            conf_override.config.alternative_url="https://beacon.ega-archive.org/api"
    def test_conf_wrong_documentation_url_no_http(self):
        with loop_context() as loop:
            from beacon.conf import conf_override
            conf_override.config.documentation_url="string"
            async def test_conf_wrong_documentation_url():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_conf_wrong_documentation_url())
            conf_override.config.documentation_url="https://b2ri-documentation-demo.ega-archive.org/"
    def test_wrong_datasets_permissions(self):
        with loop_context() as loop:
            with open("/beacon/permissions/datasets/datasets_permissions.yml", 'r') as pfile:
                confile= yaml.safe_load(pfile)
            data={
                "testing": {
                    "registere": "yes"
                }
            }
            with open('/beacon/permissions/datasets/datasets_permissions.yml', 'w') as outfile:
                yaml.dump(data, outfile, default_flow_style=False)
            async def test_conf_wrong_datasets_permissions():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_conf_wrong_datasets_permissions())
            with open('/beacon/permissions/datasets/datasets_permissions.yml', 'w') as outfile:
                yaml.dump(confile, outfile, default_flow_style=False)
    def test_wrong_datasets_permissions_2(self):
        with loop_context() as loop:
            with open("/beacon/permissions/datasets/datasets_permissions.yml", 'r') as pfile:
                confile= yaml.safe_load(pfile)
            data={
                "testing": {
                    "registered": {"yes": "no"}
                }
            }
            with open('/beacon/permissions/datasets/datasets_permissions.yml', 'w') as outfile:
                yaml.dump(data, outfile, default_flow_style=False)
            async def test_conf_wrong_datasets_permissions_2():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_conf_wrong_datasets_permissions_2())
            with open('/beacon/permissions/datasets/datasets_permissions.yml', 'w') as outfile:
                yaml.dump(confile, outfile, default_flow_style=False)
    def test_wrong_datasets_permissions_3(self):
        with loop_context() as loop:
            with open("/beacon/permissions/datasets/datasets_permissions.yml", 'r') as pfile:
                confile= yaml.safe_load(pfile)
            data={
                "testing": {
                    "controlled": {"user-list": [{"user": "unknown"}]}
                }
            }
            with open('/beacon/permissions/datasets/datasets_permissions.yml', 'w') as outfile:
                yaml.dump(data, outfile, default_flow_style=False)
            async def test_conf_wrong_datasets_permissions_3():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_conf_wrong_datasets_permissions_3())
            with open('/beacon/permissions/datasets/datasets_permissions.yml', 'w') as outfile:
                yaml.dump(confile, outfile, default_flow_style=False)
    def test_wrong_datasets_conf(self):
        with loop_context() as loop:
            with open("/beacon/conf/datasets/datasets_conf.yml", 'r') as pfile:
                confile= yaml.safe_load(pfile)
            pfile.close()
            data={
                "testing": {
                    "registere": "yes"
                }
            }
            with open('/beacon/conf/datasets/datasets_conf.yml', 'w') as outfile:
                yaml.dump(data, outfile, default_flow_style=False)
            async def test_conf_wrong_datasets_conf():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_conf_wrong_datasets_conf())
            with open('/beacon/conf/datasets/datasets_conf.yml', 'w') as outfile:
                yaml.dump(confile, outfile, default_flow_style=False)
    def test_wrong_datasets_conf_2(self):
        with loop_context() as loop:
            with open("/beacon/conf/datasets/datasets_conf.yml", 'r') as pfile:
                confile= yaml.safe_load(pfile)
            data={
                "testing": {
                    "isTest": "yes"
                }
            }
            with open('/beacon/conf/datasets/datasets_conf.yml', 'w') as outfile:
                yaml.dump(data, outfile, default_flow_style=False)
            async def test_conf_wrong_datasets_conf_2():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_conf_wrong_datasets_conf_2())
            with open('/beacon/conf/datasets/datasets_conf.yml', 'w') as outfile:
                yaml.dump(data, outfile, default_flow_style=False)
    def test_datasets_open_api_endpoints_definition(self):
        with loop_context() as loop:
            dataset["dataset"]["open_api_definition"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
            async def test_check_datasets_open_api_endpoints_definition():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_open_api_endpoints_definition())
            dataset["dataset"]["open_api_definition"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
    def test_datasets_name(self):
        with loop_context() as loop:
            dataset["dataset"]["info"]["name"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
            async def test_check_datasets_name():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_name())
            dataset["dataset"]["info"]["name"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
    def test_datasets_ontology_id(self):
        with loop_context() as loop:
            dataset["dataset"]["info"]["ontology_id"]="NOT CURIE"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
            async def test_check_datasets_ontology_id():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_ontology_id())
            dataset["dataset"]["info"]["ontology_id"]="CURIE:12345"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
    def test_datasets_ontology_name(self):
        with loop_context() as loop:
            dataset["dataset"]["info"]["ontology_name"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
            async def test_check_datasets_ontology_name():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_ontology_name())
            dataset["dataset"]["info"]["ontology_name"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
    def test_datasets_specification(self):
        with loop_context() as loop:
            dataset["dataset"]["schema"]["specification"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
            async def test_check_datasets_specification():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_specification())
            dataset["dataset"]["schema"]["specification"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
    def test_datasets_description(self):
        with loop_context() as loop:
            dataset["dataset"]["info"]["description"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
            async def test_check_datasets_description():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_description())
            dataset["dataset"]["info"]["description"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
    def test_datasets_default_schema_id(self):
        with loop_context() as loop:
            dataset["dataset"]["schema"]["default_schema_id"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
            async def test_check_datasets_default_schema_id():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_default_schema_id())
            dataset["dataset"]["schema"]["default_schema_id"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
    def test_datasets_default_schema_name(self):
        with loop_context() as loop:
            dataset["dataset"]["schema"]["default_schema_name"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
            async def test_check_datasets_default_schema_name():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_default_schema_name())
            dataset["dataset"]["schema"]["default_schema_name"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
    def test_datasets_reference_to_schema_definition(self):
        with loop_context() as loop:
            dataset["dataset"]["schema"]["reference_to_default_schema_definition"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
            async def test_check_datasets_reference_to_schema_definition():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_reference_to_schema_definition())
            dataset["dataset"]["schema"]["reference_to_default_schema_definition"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
    def test_datasets_default_schema_version(self):
        with loop_context() as loop:
            dataset["dataset"]["schema"]["default_schema_version"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
            async def test_check_datasets_default_schema_version():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_default_schema_version())
            dataset["dataset"]["schema"]["default_schema_version"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
    def test_datasets_additionally_supported_schemas(self):
        with loop_context() as loop:
            dataset["dataset"]["schema"]["supported_schemas"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
            async def test_check_datasets_additionally_supported_schemas():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_additionally_supported_schemas())
            dataset["dataset"]["schema"]["supported_schemas"]=["string"]
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
    def test_datasets_allow_queries_without_filters(self):
        with loop_context() as loop:
            dataset["dataset"]["allow_queries_without_filters"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
            async def test_check_datasets_allow_queries_without_filters():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_allow_queries_without_filters())
            dataset["dataset"]["allow_queries_without_filters"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
    def test_datasets_singleEntryUrl(self):
        with loop_context() as loop:
            dataset["dataset"]["allow_id_query"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
            async def test_check_datasets_singleEntryUrl():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_singleEntryUrl())
            dataset["dataset"]["allow_id_query"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
    def test_datasets_analysis_lookup(self):
        with loop_context() as loop:
            dataset["dataset"]["lookups"]["analysis"]["endpooint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
            async def test_check_datasets_analysis_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_analysis_lookup())
            dataset["dataset"]["lookups"]["analysis"]["endpooint_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
    def test_datasets_biosample_lookup(self):
        with loop_context() as loop:
            dataset["dataset"]["lookups"]["biosample"]["endpoint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
            async def test_check_datasets_biosample_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_biosample_lookup())
            dataset["dataset"]["lookups"]["biosample"]["endpoint_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
    def test_datasets_cohort_lookup(self):
        with loop_context() as loop:
            dataset["dataset"]["lookups"]["cohort"]["endpoint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
            async def test_check_datasets_cohort_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_cohort_lookup())
            dataset["dataset"]["lookups"]["cohort"]["endpoint_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
    def test_datasets_genomicVariant_lookup(self):
        with loop_context() as loop:
            dataset["dataset"]["lookups"]["genomicVariant"]["endpoint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
            async def test_check_datasets_genomicVariant_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_genomicVariant_lookup())
            dataset["dataset"]["lookups"]["genomicVariant"]["endpoint_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
    def test_datasets_individual_lookup(self):
        with loop_context() as loop:
            dataset["dataset"]["lookups"]["individual"]["endpoint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
            async def test_check_datasets_individual_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_individual_lookup())
            dataset["dataset"]["lookups"]["individual"]["endpoint_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
    def test_datasets_run_lookup(self):
        with loop_context() as loop:
            dataset["dataset"]["lookups"]["run"]["endpoint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
            async def test_check_datasets_run_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_run_lookup())
            dataset["dataset"]["lookups"]["run"]["endpoint_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
    def test_g_variants_open_api_endpoints_definition(self):
        with loop_context() as loop:
            genomicVariant["genomicVariant"]["open_api_definition"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
            async def test_check_g_variants_open_api_endpoints_definition():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_open_api_endpoints_definition())
            genomicVariant["genomicVariant"]["open_api_definition"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
    def test_g_variants_name(self):
        with loop_context() as loop:
            genomicVariant["genomicVariant"]["info"]["name"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
            async def test_check_g_variants_name():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_name())
            genomicVariant["genomicVariant"]["info"]["name"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
    def test_g_variants_ontology_id(self):
        with loop_context() as loop:
            genomicVariant["genomicVariant"]["info"]["ontology_id"]="NOT CURIE"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
            async def test_check_g_variants_ontology_id():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_ontology_id())
            genomicVariant["genomicVariant"]["info"]["ontology_id"]="CURIE:12345"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
    def test_g_variants_ontology_name(self):
        with loop_context() as loop:
            genomicVariant["genomicVariant"]["info"]["ontology_name"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
            async def test_check_g_variants_ontology_name():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_ontology_name())
            genomicVariant["genomicVariant"]["info"]["ontology_name"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
    def test_g_variants_specification(self):
        with loop_context() as loop:
            genomicVariant["genomicVariant"]["schema"]["specification"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
            async def test_check_g_variants_specification():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_specification())
            genomicVariant["genomicVariant"]["schema"]["specification"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
    def test_g_variants_description(self):
        with loop_context() as loop:
            genomicVariant["genomicVariant"]["info"]["description"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
            async def test_check_g_variants_description():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_description())
            genomicVariant["genomicVariant"]["info"]["description"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
    def test_g_variants_default_schema_id(self):
        with loop_context() as loop:
            genomicVariant["genomicVariant"]["schema"]["default_schema_id"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
            async def test_check_g_variants_default_schema_id():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_default_schema_id())
            genomicVariant["genomicVariant"]["schema"]["default_schema_id"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
    def test_g_variants_default_schema_name(self):
        with loop_context() as loop:
            genomicVariant["genomicVariant"]["schema"]["default_schema_name"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
            async def test_check_g_variants_default_schema_name():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_default_schema_name())
            genomicVariant["genomicVariant"]["schema"]["default_schema_name"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
    def test_g_variants_reference_to_schema_definition(self):
        with loop_context() as loop:
            genomicVariant["genomicVariant"]["schema"]["reference_to_default_schema_definition"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
            async def test_check_g_variants_reference_to_schema_definition():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_reference_to_schema_definition())
            genomicVariant["genomicVariant"]["schema"]["reference_to_default_schema_definition"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
    def test_g_variants_default_schema_version(self):
        with loop_context() as loop:
            genomicVariant["genomicVariant"]["schema"]["default_schema_version"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
            async def test_check_g_variants_default_schema_version():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_default_schema_version())
            genomicVariant["genomicVariant"]["schema"]["default_schema_version"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
    def test_g_variants_additionally_supported_schemas(self):
        with loop_context() as loop:
            genomicVariant["genomicVariant"]["schema"]["supported_schemas"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
            async def test_check_g_variants_additionally_supported_schemas():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_additionally_supported_schemas())
            genomicVariant["genomicVariant"]["schema"]["supported_schemas"]=["string"]
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
    def test_g_variants_allow_queries_without_filters(self):
        with loop_context() as loop:
            genomicVariant["genomicVariant"]["allow_queries_without_filters"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
            async def test_check_g_variants_allow_queries_without_filters():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_allow_queries_without_filters())
            genomicVariant["genomicVariant"]["allow_queries_without_filters"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
    def test_g_variants_singleEntryUrl(self):
        with loop_context() as loop:
            genomicVariant["genomicVariant"]["allow_id_query"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
            async def test_check_g_variants_singleEntryUrl():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_singleEntryUrl())
            genomicVariant["genomicVariant"]["allow_id_query"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
    def test_g_variants_analysis_lookup(self):
        with loop_context() as loop:
            genomicVariant["genomicVariant"]["lookups"]["analysis"]["endpooint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
            async def test_check_g_variants_analysis_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_analysis_lookup())
            genomicVariant["genomicVariant"]["lookups"]["analysis"]["endpooint_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
    def test_g_variants_biosample_lookup(self):
        with loop_context() as loop:
            genomicVariant["genomicVariant"]["lookups"]["biosample"]["endpoint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
            async def test_check_g_variants_biosample_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_biosample_lookup())
            genomicVariant["genomicVariant"]["lookups"]["biosample"]["endpoint_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
    def test_g_variants_cohort_lookup(self):
        with loop_context() as loop:
            genomicVariant["genomicVariant"]["lookups"]["cohort"]["endpoint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
            async def test_check_g_variants_cohort_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_cohort_lookup())
            genomicVariant["genomicVariant"]["lookups"]["cohort"]["endpoint_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
    def test_g_variants_dataset_lookup(self):
        with loop_context() as loop:
            genomicVariant["genomicVariant"]["lookups"]["dataset"]["endpoint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
            async def test_check_g_variants_dataset_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_dataset_lookup())
            genomicVariant["genomicVariant"]["lookups"]["dataset"]["endpoint_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
    def test_g_variants_individual_lookup(self):
        with loop_context() as loop:
            genomicVariant["genomicVariant"]["lookups"]["individual"]["endpoint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
            async def test_check_g_variants_individual_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_individual_lookup())
            genomicVariant["genomicVariant"]["lookups"]["individual"]["endpoint_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
    def test_g_variants_run_lookup(self):
        with loop_context() as loop:
            genomicVariant["genomicVariant"]["lookups"]["run"]["endpoint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
            async def test_check_g_variants_run_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_run_lookup())
            genomicVariant["genomicVariant"]["lookups"]["run"]["endpoint_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
    def test_individuals_open_api_endpoints_definition(self):
        with loop_context() as loop:
            individual["individual"]["open_api_definition"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)
            async def test_check_individuals_open_api_endpoints_definition():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                        yaml.dump(individual, outfile, default_flow_style=False)
                    pass
            loop.run_until_complete(test_check_individuals_open_api_endpoints_definition())
            individual["individual"]["open_api_definition"]="string"
    def test_individuals_name(self):
        with loop_context() as loop:
            individual["individual"]["info"]["name"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)
            async def test_check_individuals_name():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                        yaml.dump(individual, outfile, default_flow_style=False)
                    pass
            loop.run_until_complete(test_check_individuals_name())
            individual["individual"]["info"]["name"]="string"
    def test_individuals_ontology_id(self):
        with loop_context() as loop:
            individual["individual"]["info"]["ontology_id"]="NOT CURIE"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)
            async def test_check_individuals_ontology_id():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                        yaml.dump(individual, outfile, default_flow_style=False)
                    pass
            loop.run_until_complete(test_check_individuals_ontology_id())
            individual["individual"]["info"]["ontology_id"]="CURIE:12345"
    def test_individuals_ontology_name(self):
        with loop_context() as loop:
            individual["individual"]["info"]["ontology_name"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)
            async def test_check_individuals_ontology_name():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                        yaml.dump(individual, outfile, default_flow_style=False)
                    pass
            loop.run_until_complete(test_check_individuals_ontology_name())
            individual["individual"]["info"]["ontology_name"]="string"
    def test_individuals_specification(self):
        with loop_context() as loop:
            individual["individual"]["schema"]["specification"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)
            async def test_check_individuals_specification():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                        yaml.dump(individual, outfile, default_flow_style=False)
                    pass
            loop.run_until_complete(test_check_individuals_specification())
            individual["individual"]["schema"]["specification"]="string"
    def test_individuals_description(self):
        with loop_context() as loop:
            individual["individual"]["info"]["description"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)
            async def test_check_individuals_description():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                        yaml.dump(individual, outfile, default_flow_style=False)
                    pass
            loop.run_until_complete(test_check_individuals_description())
            individual["individual"]["info"]["description"]="string"
    def test_individuals_default_schema_id(self):
        with loop_context() as loop:
            individual["individual"]["schema"]["default_schema_id"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)
            async def test_check_individuals_default_schema_id():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                        yaml.dump(individual, outfile, default_flow_style=False)
                    pass
            loop.run_until_complete(test_check_individuals_default_schema_id())
            individual["individual"]["schema"]["default_schema_id"]="string"
    def test_individuals_default_schema_name(self):
        with loop_context() as loop:
            individual["individual"]["schema"]["default_schema_name"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)
            async def test_check_individuals_default_schema_name():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                        yaml.dump(individual, outfile, default_flow_style=False)
                    pass
            loop.run_until_complete(test_check_individuals_default_schema_name())
            individual["individual"]["schema"]["default_schema_name"]="string"
    def test_individuals_reference_to_schema_definition(self):
        with loop_context() as loop:
            individual["individual"]["schema"]["reference_to_default_schema_definition"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)
            async def test_check_individuals_reference_to_schema_definition():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                        yaml.dump(individual, outfile, default_flow_style=False)
                    pass
            loop.run_until_complete(test_check_individuals_reference_to_schema_definition())
            individual["individual"]["schema"]["reference_to_default_schema_definition"]="string"
    def test_individuals_default_schema_version(self):
        with loop_context() as loop:
            individual["individual"]["schema"]["default_schema_version"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)
            async def test_check_individuals_default_schema_version():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                        yaml.dump(individual, outfile, default_flow_style=False)
                    pass
            loop.run_until_complete(test_check_individuals_default_schema_version())
            individual["individual"]["schema"]["default_schema_version"]="string"
    def test_individuals_additionally_supported_schemas(self):
        with loop_context() as loop:
            individual["individual"]["schema"]["supported_schemas"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)
            async def test_check_individuals_additionally_supported_schemas():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                        yaml.dump(individual, outfile, default_flow_style=False)
                    pass
            loop.run_until_complete(test_check_individuals_additionally_supported_schemas())
            individual["individual"]["schema"]["supported_schemas"]=["string"]
    def test_individuals_allow_queries_without_filters(self):
        with loop_context() as loop:
            individual["individual"]["allow_queries_without_filters"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)
            async def test_check_individuals_allow_queries_without_filters():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                        yaml.dump(individual, outfile, default_flow_style=False)
                    pass
            loop.run_until_complete(test_check_individuals_allow_queries_without_filters())
            individual["individual"]["allow_queries_without_filters"]=True
    def test_individuals_singleEntryUrl(self):
        with loop_context() as loop:
            individual["individual"]["allow_id_query"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)
            async def test_check_individuals_singleEntryUrl():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                        yaml.dump(individual, outfile, default_flow_style=False)
                    pass
            loop.run_until_complete(test_check_individuals_singleEntryUrl())
            individual["individual"]["allow_id_query"]=True
    def test_individuals_analysis_lookup(self):
        with loop_context() as loop:
            individual["individual"]["lookups"]["analysis"]["endpooint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)
            async def test_check_individuals_analysis_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                        yaml.dump(individual, outfile, default_flow_style=False)
                    pass
            loop.run_until_complete(test_check_individuals_analysis_lookup())
            individual["individual"]["lookups"]["analysis"]["endpooint_enabled"]=True
    def test_individuals_biosample_lookup(self):
        with loop_context() as loop:
            individual["individual"]["lookups"]["biosample"]["endpoint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)
            async def test_check_individuals_biosample_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                        yaml.dump(individual, outfile, default_flow_style=False)
                    pass
            loop.run_until_complete(test_check_individuals_biosample_lookup())
            individual["individual"]["lookups"]["biosample"]["endpoint_enabled"]=True
    def test_individuals_cohort_lookup(self):
        with loop_context() as loop:
            individual["individual"]["lookups"]["cohort"]["endpoint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)
            async def test_check_individuals_cohort_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                        yaml.dump(individual, outfile, default_flow_style=False)
                    pass
            loop.run_until_complete(test_check_individuals_cohort_lookup())
            individual["individual"]["lookups"]["cohort"]["endpoint_enabled"]=True
    def test_individuals_dataset_lookup(self):
        with loop_context() as loop:
            individual["individual"]["lookups"]["dataset"]["endpoint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)
            async def test_check_individuals_dataset_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                        yaml.dump(individual, outfile, default_flow_style=False)
                    pass
            loop.run_until_complete(test_check_individuals_dataset_lookup())
            individual["individual"]["lookups"]["dataset"]["endpoint_enabled"]=True
    def test_individuals_genomicVariant_lookup(self):
        with loop_context() as loop:
            individual["individual"]["lookups"]["genomicVariant"]["endpoint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)
            async def test_check_individuals_genomicVariant_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                        yaml.dump(individual, outfile, default_flow_style=False)
                    pass
            loop.run_until_complete(test_check_individuals_genomicVariant_lookup())
            individual["individual"]["lookups"]["genomicVariant"]["endpoint_enabled"]=True
    def test_individuals_run_lookup(self):
        with loop_context() as loop:
            individual["individual"]["lookups"]["run"]["endpoint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)
            async def test_check_individuals_run_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                        yaml.dump(individual, outfile, default_flow_style=False)
                    pass
            loop.run_until_complete(test_check_individuals_run_lookup())
            individual["individual"]["lookups"]["run"]["endpoint_enabled"]=True
    def test_biosamples_open_api_endpoints_definition(self):
        with loop_context() as loop:
            biosample["biosample"]["open_api_definition"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
            async def test_check_biosamples_open_api_endpoints_definition():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_open_api_endpoints_definition())
            biosample["biosample"]["open_api_definition"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
    def test_biosamples_name(self):
        with loop_context() as loop:
            biosample["biosample"]["info"]["name"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
            async def test_check_biosamples_name():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_name())
            biosample["biosample"]["info"]["name"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
    def test_biosamples_ontology_id(self):
        with loop_context() as loop:
            biosample["biosample"]["info"]["ontology_id"]="NOT CURIE"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
            async def test_check_biosamples_ontology_id():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_ontology_id())
            biosample["biosample"]["info"]["ontology_id"]="CURIE:12345"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
    def test_biosamples_ontology_name(self):
        with loop_context() as loop:
            biosample["biosample"]["info"]["ontology_name"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
            async def test_check_biosamples_ontology_name():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_ontology_name())
            biosample["biosample"]["info"]["ontology_name"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
    def test_biosamples_specification(self):
        with loop_context() as loop:
            biosample["biosample"]["schema"]["specification"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
            async def test_check_biosamples_specification():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_specification())
            biosample["biosample"]["schema"]["specification"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
    def test_biosamples_description(self):
        with loop_context() as loop:
            biosample["biosample"]["info"]["description"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
            async def test_check_biosamples_description():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_description())
            biosample["biosample"]["info"]["description"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
    def test_biosamples_default_schema_id(self):
        with loop_context() as loop:
            biosample["biosample"]["schema"]["default_schema_id"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
            async def test_check_biosamples_default_schema_id():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_default_schema_id())
            biosample["biosample"]["schema"]["default_schema_id"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
    def test_biosamples_default_schema_name(self):
        with loop_context() as loop:
            biosample["biosample"]["schema"]["default_schema_name"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
            async def test_check_biosamples_default_schema_name():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_default_schema_name())
            biosample["biosample"]["schema"]["default_schema_name"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
    def test_biosamples_reference_to_schema_definition(self):
        with loop_context() as loop:
            biosample["biosample"]["schema"]["reference_to_default_schema_definition"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
            async def test_check_biosamples_reference_to_schema_definition():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_reference_to_schema_definition())
            biosample["biosample"]["schema"]["reference_to_default_schema_definition"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
    def test_biosamples_default_schema_version(self):
        with loop_context() as loop:
            biosample["biosample"]["schema"]["default_schema_version"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
            async def test_check_biosamples_default_schema_version():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_default_schema_version())
            biosample["biosample"]["schema"]["default_schema_version"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
    def test_biosamples_additionally_supported_schemas(self):
        with loop_context() as loop:
            biosample["biosample"]["schema"]["supported_schemas"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
            async def test_check_biosamples_additionally_supported_schemas():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_additionally_supported_schemas())
            biosample["biosample"]["schema"]["supported_schemas"]=["string"]
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
    def test_biosamples_allow_queries_without_filters(self):
        with loop_context() as loop:
            biosample["biosample"]["allow_queries_without_filters"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
            async def test_check_biosamples_allow_queries_without_filters():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_allow_queries_without_filters())
            biosample["biosample"]["allow_queries_without_filters"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
    def test_biosamples_singleEntryUrl(self):
        with loop_context() as loop:
            biosample["biosample"]["allow_id_query"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
            async def test_check_biosamples_singleEntryUrl():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_singleEntryUrl())
            biosample["biosample"]["allow_id_query"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
    def test_biosamples_analysis_lookup(self):
        with loop_context() as loop:
            biosample["biosample"]["lookups"]["analysis"]["endpooint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
            async def test_check_biosamples_analysis_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_analysis_lookup())
            biosample["biosample"]["lookups"]["analysis"]["endpooint_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
    def test_biosamples_cohort_lookup(self):
        with loop_context() as loop:
            biosample["biosample"]["lookups"]["cohort"]["endpoint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
            async def test_check_biosamples_cohort_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_cohort_lookup())
            biosample["biosample"]["lookups"]["cohort"]["endpoint_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
    def test_biosamples_dataset_lookup(self):
        with loop_context() as loop:
            biosample["biosample"]["lookups"]["dataset"]["endpoint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
            async def test_check_biosamples_dataset_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_dataset_lookup())
            biosample["biosample"]["lookups"]["dataset"]["endpoint_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
    def test_biosamples_genomicVariant_lookup(self):
        with loop_context() as loop:
            biosample["biosample"]["lookups"]["genomicVariant"]["endpoint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
            async def test_check_biosamples_genomicVariant_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_genomicVariant_lookup())
            biosample["biosample"]["lookups"]["genomicVariant"]["endpoint_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
    def test_biosamples_individual_lookup(self):
        with loop_context() as loop:
            biosample["biosample"]["lookups"]["individual"]["endpoint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
            async def test_check_biosamples_individual_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_individual_lookup())
            biosample["biosample"]["lookups"]["individual"]["endpoint_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
    def test_biosamples_run_lookup(self):
        with loop_context() as loop:
            biosample["biosample"]["lookups"]["run"]["endpoint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
            async def test_check_biosamples_run_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_run_lookup())
            biosample["biosample"]["lookups"]["run"]["endpoint_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
    def test_cohorts_open_api_endpoints_definition(self):
        with loop_context() as loop:
            cohort["cohort"]["open_api_definition"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
            async def test_check_cohorts_open_api_endpoints_definition():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_open_api_endpoints_definition())
            cohort["cohort"]["open_api_definition"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
    def test_cohorts_name(self):
        with loop_context() as loop:
            cohort["cohort"]["info"]["name"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
            async def test_check_cohorts_name():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_name())
            cohort["cohort"]["info"]["name"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
    def test_cohorts_ontology_id(self):
        with loop_context() as loop:
            cohort["cohort"]["info"]["ontology_id"]="NOT CURIE"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
            async def test_check_cohorts_ontology_id():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_ontology_id())
            cohort["cohort"]["info"]["ontology_id"]="CURIE:12345"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
    def test_cohorts_ontology_name(self):
        with loop_context() as loop:
            cohort["cohort"]["info"]["ontology_name"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
            async def test_check_cohorts_ontology_name():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_ontology_name())
            cohort["cohort"]["info"]["ontology_name"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
    def test_cohorts_specification(self):
        with loop_context() as loop:
            cohort["cohort"]["schema"]["specification"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
            async def test_check_cohorts_specification():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_specification())
            cohort["cohort"]["schema"]["specification"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
    def test_cohorts_description(self):
        with loop_context() as loop:
            cohort["cohort"]["info"]["description"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
            async def test_check_cohorts_description():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_description())
            cohort["cohort"]["info"]["description"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
    def test_cohorts_default_schema_id(self):
        with loop_context() as loop:
            cohort["cohort"]["schema"]["default_schema_id"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
            async def test_check_cohorts_default_schema_id():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_default_schema_id())
            cohort["cohort"]["schema"]["default_schema_id"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
    def test_cohorts_default_schema_name(self):
        with loop_context() as loop:
            cohort["cohort"]["schema"]["default_schema_name"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
            async def test_check_cohorts_default_schema_name():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_default_schema_name())
            cohort["cohort"]["schema"]["default_schema_name"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
    def test_cohorts_reference_to_schema_definition(self):
        with loop_context() as loop:
            cohort["cohort"]["schema"]["reference_to_default_schema_definition"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
            async def test_check_cohorts_reference_to_schema_definition():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_reference_to_schema_definition())
            cohort["cohort"]["schema"]["reference_to_default_schema_definition"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
    def test_cohorts_default_schema_version(self):
        with loop_context() as loop:
            cohort["cohort"]["schema"]["default_schema_version"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
            async def test_check_cohorts_default_schema_version():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_default_schema_version())
            cohort["cohort"]["schema"]["default_schema_version"]="string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
    def test_cohorts_additionally_supported_schemas(self):
        with loop_context() as loop:
            cohort["cohort"]["schema"]["supported_schemas"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
            async def test_check_cohorts_additionally_supported_schemas():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_additionally_supported_schemas())
            cohort["cohort"]["schema"]["supported_schemas"]=["string"]
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
    def test_cohorts_allow_queries_without_filters(self):
        with loop_context() as loop:
            cohort["cohort"]["allow_queries_without_filters"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
            async def test_check_cohorts_allow_queries_without_filters():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_allow_queries_without_filters())
            cohort["cohort"]["allow_queries_without_filters"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
    def test_cohorts_singleEntryUrl(self):
        with loop_context() as loop:
            cohort["cohort"]["allow_id_query"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
            async def test_check_cohorts_singleEntryUrl():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_singleEntryUrl())
            cohort["cohort"]["allow_id_query"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
    def test_cohorts_analysis_lookup(self):
        with loop_context() as loop:
            cohort["cohort"]["lookups"]["analysis"]["endpooint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
            async def test_check_cohorts_analysis_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_analysis_lookup())
            cohort["cohort"]["lookups"]["analysis"]["endpooint_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
    def test_cohorts_biosample_lookup(self):
        with loop_context() as loop:
            cohort["cohort"]["lookups"]["biosample"]["endpoint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
            async def test_check_cohorts_biosample_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_biosample_lookup())
            cohort["cohort"]["lookups"]["biosample"]["endpoint_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
    def test_cohorts_dataset_lookup(self):
        with loop_context() as loop:
            cohort["cohort"]["lookups"]["dataset"]["endpoint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
            async def test_check_cohorts_dataset_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_dataset_lookup())
            cohort["cohort"]["lookups"]["dataset"]["endpoint_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
    def test_cohorts_genomicVariant_lookup(self):
        with loop_context() as loop:
            cohort["cohort"]["lookups"]["genomicVariant"]["endpoint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
            async def test_check_cohorts_genomicVariant_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_genomicVariant_lookup())
            cohort["cohort"]["lookups"]["genomicVariant"]["endpoint_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
    def test_cohorts_individual_lookup(self):
        with loop_context() as loop:
            cohort["cohort"]["lookups"]["individual"]["endpoint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
            async def test_check_cohorts_individual_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_individual_lookup())
            cohort["cohort"]["lookups"]["individual"]["endpoint_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
    def test_cohorts_run_lookup(self):
        with loop_context() as loop:
            cohort["cohort"]["lookups"]["run"]["endpoint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
            async def test_check_cohorts_run_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_run_lookup())
            cohort["cohort"]["lookups"]["run"]["endpoint_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)




def suite():
    """
        Gather all the tests from this module in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestConfigurationExceptions))
    #test_suite.addTest(unittest.makeSuite(TestBudget2))
    return test_suite


mySuit=suite()


runner=unittest.TextTestRunner()
runner.run(mySuit)