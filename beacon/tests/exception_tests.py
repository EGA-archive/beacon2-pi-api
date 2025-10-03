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
import logging
import yaml
from beacon.tests.__main__ import create_app


class TestConfigurationExceptions(unittest.TestCase):
    def test_main_check_configuration_wrong_security_levels(self):
        with loop_context() as loop:
            from beacon.conf import conf
            conf.security_levels="api"
            async def test_check_configuration_wrong_security_levels():
                try:
                    check_configuration()
                except Exception:
                    try:
                        conf.security_levels=["api"]
                        check_configuration()
                    except Exception:
                        pass
            loop.run_until_complete(test_check_configuration_wrong_security_levels())
            conf.security_levels=['PUBLIC', 'REGISTERED', 'CONTROLLED']
    def test_main_check_configuration_wrong_cors_urls(self):
        with loop_context() as loop:
            from beacon.conf import conf
            conf.cors_urls="api"
            async def test_check_configuration_wrong_cors_urls():
                try:
                    check_configuration()
                except Exception:
                    try:
                        conf.cors_urls=["api"]
                        check_configuration()
                    except Exception:
                        pass
            loop.run_until_complete(test_check_configuration_wrong_cors_urls())
            conf.cors_urls = ["http://localhost:3003", "http://localhost:3000"]
    def test_analyses_contains_special_chars(self):
        with loop_context() as loop:
            from beacon.conf import analysis
            analysis.endpoint_name="%aydga&-_al)"
            async def test_check_endpoint_contains_special_chars():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_endpoint_contains_special_chars())
            analysis.endpoint_name="analyses"
    def test_biosamples_contains_special_chars(self):
        with loop_context() as loop:
            from beacon.conf import biosample
            biosample.endpoint_name="%aydga&-_al)"
            async def test_check_endpoint_contains_special_chars():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_endpoint_contains_special_chars())
            biosample.endpoint_name="biosamples"
    def test_cohorts_contains_special_chars(self):
        with loop_context() as loop:
            from beacon.conf import cohort
            cohort.endpoint_name="%aydga&-_al)"
            async def test_check_endpoint_contains_special_chars():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_endpoint_contains_special_chars())
            cohort.endpoint_name="cohorts"
    def test_datasets_contains_special_chars(self):
        with loop_context() as loop:
            from beacon.conf import dataset
            dataset.endpoint_name="%aydga&-_al)"
            async def test_check_endpoint_contains_special_chars():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_endpoint_contains_special_chars())
            dataset.endpoint_name="datasets"
    def test_g_variants_contains_special_chars(self):
        with loop_context() as loop:
            from beacon.conf import genomicVariant
            genomicVariant.endpoint_name="%aydga&-_al)"
            async def test_check_endpoint_contains_special_chars():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_endpoint_contains_special_chars())
            genomicVariant.endpoint_name="g_variants"
    def test_runs_contains_special_chars(self):
        with loop_context() as loop:
            from beacon.conf import run
            run.endpoint_name="%aydga&-_al)"
            async def test_check_endpoint_contains_special_chars():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_endpoint_contains_special_chars())
            run.endpoint_name="runs"
    def test_individuals_contains_special_chars(self):
        with loop_context() as loop:
            from beacon.conf import individual
            individual.endpoint_name="%aydga&-_al)"
            async def test_check_endpoint_contains_special_chars():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_endpoint_contains_special_chars())
            individual.endpoint_name="individuals"
    def test_analyses_open_api_endpoints_definition(self):
        with loop_context() as loop:
            from beacon.conf import analysis
            analysis.open_api_endpoints_definition=3
            async def test_check_analyses_open_api_endpoints_definition():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_open_api_endpoints_definition())
            analysis.open_api_endpoints_definition="string"
    def test_analyses_id(self):
        with loop_context() as loop:
            from beacon.conf import analysis
            analysis.id="something"
            async def test_check_analyses_id():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_id())
            analysis.id="analysis"
    def test_analyses_name(self):
        with loop_context() as loop:
            from beacon.conf import analysis
            analysis.name=3
            async def test_check_analyses_name():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_name())
            analysis.name="string"
    def test_analyses_ontology_id(self):
        with loop_context() as loop:
            from beacon.conf import analysis
            analysis.ontology_id="NOT13132 CURIE_!"
            async def test_check_analyses_ontology_id():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_ontology_id())
            analysis.ontology_id="CURIE:12345"
    def test_analyses_ontology_name(self):
        with loop_context() as loop:
            from beacon.conf import analysis
            analysis.ontology_name=3
            async def test_check_analyses_ontology_name():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_ontology_name())
            analysis.ontology_name="string"
    def test_analyses_specification(self):
        with loop_context() as loop:
            from beacon.conf import analysis
            analysis.specification=3
            async def test_check_analyses_specification():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_specification())
            analysis.specification="string"
    def test_analyses_description(self):
        with loop_context() as loop:
            from beacon.conf import analysis
            analysis.description=3
            async def test_check_analyses_description():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_description())
            analysis.description="string"
    def test_analyses_default_schema_id(self):
        with loop_context() as loop:
            from beacon.conf import analysis
            analysis.defaultSchema_id=3
            async def test_check_analyses_default_schema_id():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_default_schema_id())
            analysis.defaultSchema_id="string"
    def test_analyses_default_schema_name(self):
        with loop_context() as loop:
            from beacon.conf import analysis
            analysis.defaultSchema_name=3
            async def test_check_analyses_default_schema_name():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_default_schema_name())
            analysis.defaultSchema_name="string"
    def test_analyses_reference_to_schema_definition(self):
        with loop_context() as loop:
            from beacon.conf import analysis
            analysis.defaultSchema_reference_to_schema_definition=3
            async def test_check_analyses_reference_to_schema_definition():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_reference_to_schema_definition())
            analysis.defaultSchema_reference_to_schema_definition="string"
    def test_analyses_default_schema_version(self):
        with loop_context() as loop:
            from beacon.conf import analysis
            analysis.defaultSchema_schema_version=3
            async def test_check_analyses_default_schema_version():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_default_schema_version())
            analysis.defaultSchema_schema_version="string"
    def test_analyses_additionally_supported_schemas(self):
        with loop_context() as loop:
            from beacon.conf import analysis
            analysis.aditionally_supported_schemas=3
            async def test_check_analyses_additionally_supported_schemas():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_additionally_supported_schemas())
            analysis.aditionally_supported_schemas=["string"]
    def test_analyses_allow_queries_without_filters(self):
        with loop_context() as loop:
            from beacon.conf import analysis
            analysis.allow_queries_without_filters=3
            async def test_check_analyses_allow_queries_without_filters():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_allow_queries_without_filters())
            analysis.allow_queries_without_filters=True
    def test_analyses_singleEntryUrl(self):
        with loop_context() as loop:
            from beacon.conf import analysis
            analysis.singleEntryUrl=3
            async def test_check_analyses_singleEntryUrl():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_singleEntryUrl())
            analysis.singleEntryUrl=True
    def test_analyses_biosample_lookup(self):
        with loop_context() as loop:
            from beacon.conf import analysis
            analysis.biosample_lookup=3
            async def test_check_analyses_biosample_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_biosample_lookup())
            analysis.biosample_lookup=True
    def test_analyses_cohort_lookup(self):
        with loop_context() as loop:
            from beacon.conf import analysis
            analysis.cohort_lookup=3
            async def test_check_analyses_cohort_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_cohort_lookup())
            analysis.cohort_lookup=True
    def test_analyses_dataset_lookup(self):
        with loop_context() as loop:
            from beacon.conf import analysis
            analysis.dataset_lookup=3
            async def test_check_analyses_dataset_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_dataset_lookup())
            analysis.dataset_lookup=True
    def test_analyses_genomicVariant_lookup(self):
        with loop_context() as loop:
            from beacon.conf import analysis
            analysis.genomicVariant_lookup=3
            async def test_check_analyses_genomicVariant_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_genomicVariant_lookup())
            analysis.genomicVariant_lookup=True
    def test_analyses_individual_lookup(self):
        with loop_context() as loop:
            from beacon.conf import analysis
            analysis.individual_lookup=3
            async def test_check_analyses_individual_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_individual_lookup())
            analysis.individual_lookup=True
    def test_analyses_run_lookup(self):
        with loop_context() as loop:
            from beacon.conf import analysis
            analysis.run_lookup=3
            async def test_check_analyses_run_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_analyses_run_lookup())
            analysis.run_lookup=True
    def test_biosamples_open_api_endpoints_definition(self):
        with loop_context() as loop:
            from beacon.conf import biosample
            biosample.open_api_endpoints_definition=3
            async def test_check_biosamples_open_api_endpoints_definition():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_open_api_endpoints_definition())
            biosample.open_api_endpoints_definition="string"
    def test_biosamples_id(self):
        with loop_context() as loop:
            from beacon.conf import biosample
            biosample.id="something"
            async def test_check_biosamples_id():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_id())
            biosample.id="biosample"
    def test_biosamples_name(self):
        with loop_context() as loop:
            from beacon.conf import biosample
            biosample.name=3
            async def test_check_biosamples_name():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_name())
            biosample.name="string"
    def test_biosamples_ontology_id(self):
        with loop_context() as loop:
            from beacon.conf import biosample
            biosample.ontology_id="NOT CURIE"
            async def test_check_biosamples_ontology_id():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_ontology_id())
            biosample.ontology_id="CURIE:12345"
    def test_biosamples_ontology_name(self):
        with loop_context() as loop:
            from beacon.conf import biosample
            biosample.ontology_name=3
            async def test_check_biosamples_ontology_name():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_ontology_name())
            biosample.ontology_name="string"
    def test_biosamples_specification(self):
        with loop_context() as loop:
            from beacon.conf import biosample
            biosample.specification=3
            async def test_check_biosamples_specification():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_specification())
            biosample.specification="string"
    def test_biosamples_description(self):
        with loop_context() as loop:
            from beacon.conf import biosample
            biosample.description=3
            async def test_check_biosamples_description():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_description())
            biosample.description="string"
    def test_biosamples_default_schema_id(self):
        with loop_context() as loop:
            from beacon.conf import biosample
            biosample.defaultSchema_id=3
            async def test_check_biosamples_default_schema_id():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_default_schema_id())
            biosample.defaultSchema_id="string"
    def test_biosamples_default_schema_name(self):
        with loop_context() as loop:
            from beacon.conf import biosample
            biosample.defaultSchema_name=3
            async def test_check_biosamples_default_schema_name():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_default_schema_name())
            biosample.defaultSchema_name="string"
    def test_biosamples_reference_to_schema_definition(self):
        with loop_context() as loop:
            from beacon.conf import biosample
            biosample.defaultSchema_reference_to_schema_definition=3
            async def test_check_biosamples_reference_to_schema_definition():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_reference_to_schema_definition())
            biosample.defaultSchema_reference_to_schema_definition="string"
    def test_biosamples_default_schema_version(self):
        with loop_context() as loop:
            from beacon.conf import biosample
            biosample.defaultSchema_schema_version=3
            async def test_check_biosamples_default_schema_version():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_default_schema_version())
            biosample.defaultSchema_schema_version="string"
    def test_biosamples_additionally_supported_schemas(self):
        with loop_context() as loop:
            from beacon.conf import biosample
            biosample.aditionally_supported_schemas=3
            async def test_check_biosamples_additionally_supported_schemas():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_additionally_supported_schemas())
            biosample.aditionally_supported_schemas=["string"]
    def test_biosamples_allow_queries_without_filters(self):
        with loop_context() as loop:
            from beacon.conf import biosample
            biosample.allow_queries_without_filters=3
            async def test_check_biosamples_allow_queries_without_filters():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_allow_queries_without_filters())
            biosample.allow_queries_without_filters=True
    def test_biosamples_singleEntryUrl(self):
        with loop_context() as loop:
            from beacon.conf import biosample
            biosample.singleEntryUrl=3
            async def test_check_biosamples_singleEntryUrl():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_singleEntryUrl())
            biosample.singleEntryUrl=True
    def test_biosamples_analysis_lookup(self):
        with loop_context() as loop:
            from beacon.conf import biosample
            biosample.analysis_lookup=3
            async def test_check_biosamples_analysis_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_analysis_lookup())
            biosample.analysis_lookup=True
    def test_biosamples_cohort_lookup(self):
        with loop_context() as loop:
            from beacon.conf import biosample
            biosample.cohort_lookup=3
            async def test_check_biosamples_cohort_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_cohort_lookup())
            biosample.cohort_lookup=True
    def test_biosamples_dataset_lookup(self):
        with loop_context() as loop:
            from beacon.conf import biosample
            biosample.dataset_lookup=3
            async def test_check_biosamples_dataset_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_dataset_lookup())
            biosample.dataset_lookup=True
    def test_biosamples_genomicVariant_lookup(self):
        with loop_context() as loop:
            from beacon.conf import biosample
            biosample.genomicVariant_lookup=3
            async def test_check_biosamples_genomicVariant_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_genomicVariant_lookup())
            biosample.genomicVariant_lookup=True
    def test_biosamples_individual_lookup(self):
        with loop_context() as loop:
            from beacon.conf import biosample
            biosample.individual_lookup=3
            async def test_check_biosamples_individual_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_individual_lookup())
            biosample.individual_lookup=True
    def test_biosamples_run_lookup(self):
        with loop_context() as loop:
            from beacon.conf import biosample
            biosample.run_lookup=3
            async def test_check_biosamples_run_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_biosamples_run_lookup())
            biosample.run_lookup=True
    def test_cohorts_open_api_endpoints_definition(self):
        with loop_context() as loop:
            from beacon.conf import cohort
            cohort.open_api_endpoints_definition=3
            async def test_check_cohorts_open_api_endpoints_definition():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_open_api_endpoints_definition())
            cohort.open_api_endpoints_definition="string"
    def test_cohorts_id(self):
        with loop_context() as loop:
            from beacon.conf import cohort
            cohort.id="something"
            async def test_check_cohorts_id():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_id())
            cohort.id="cohort"
    def test_cohorts_name(self):
        with loop_context() as loop:
            from beacon.conf import cohort
            cohort.name=3
            async def test_check_cohorts_name():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_name())
            cohort.name="string"
    def test_cohorts_ontology_id(self):
        with loop_context() as loop:
            from beacon.conf import cohort
            cohort.ontology_id="NOT CURIE"
            async def test_check_cohorts_ontology_id():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_ontology_id())
            cohort.ontology_id="CURIE:12345"
    def test_cohorts_ontology_name(self):
        with loop_context() as loop:
            from beacon.conf import cohort
            cohort.ontology_name=3
            async def test_check_cohorts_ontology_name():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_ontology_name())
            cohort.ontology_name="string"
    def test_cohorts_specification(self):
        with loop_context() as loop:
            from beacon.conf import cohort
            cohort.specification=3
            async def test_check_cohorts_specification():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_specification())
            cohort.specification="string"
    def test_cohorts_description(self):
        with loop_context() as loop:
            from beacon.conf import cohort
            cohort.description=3
            async def test_check_cohorts_description():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_description())
            cohort.description="string"
    def test_cohorts_default_schema_id(self):
        with loop_context() as loop:
            from beacon.conf import cohort
            cohort.defaultSchema_id=3
            async def test_check_cohorts_default_schema_id():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_default_schema_id())
            cohort.defaultSchema_id="string"
    def test_cohorts_default_schema_name(self):
        with loop_context() as loop:
            from beacon.conf import cohort
            cohort.defaultSchema_name=3
            async def test_check_cohorts_default_schema_name():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_default_schema_name())
            cohort.defaultSchema_name="string"
    def test_cohorts_reference_to_schema_definition(self):
        with loop_context() as loop:
            from beacon.conf import cohort
            cohort.defaultSchema_reference_to_schema_definition=3
            async def test_check_cohorts_reference_to_schema_definition():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_reference_to_schema_definition())
            cohort.defaultSchema_reference_to_schema_definition="string"
    def test_cohorts_default_schema_version(self):
        with loop_context() as loop:
            from beacon.conf import cohort
            cohort.defaultSchema_schema_version=3
            async def test_check_cohorts_default_schema_version():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_default_schema_version())
            cohort.defaultSchema_schema_version="string"
    def test_cohorts_additionally_supported_schemas(self):
        with loop_context() as loop:
            from beacon.conf import cohort
            cohort.aditionally_supported_schemas=3
            async def test_check_cohorts_additionally_supported_schemas():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_additionally_supported_schemas())
            cohort.aditionally_supported_schemas=["string"]
    def test_cohorts_allow_queries_without_filters(self):
        with loop_context() as loop:
            from beacon.conf import cohort
            cohort.allow_queries_without_filters=3
            async def test_check_cohorts_allow_queries_without_filters():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_allow_queries_without_filters())
            cohort.allow_queries_without_filters=True
    def test_cohorts_singleEntryUrl(self):
        with loop_context() as loop:
            from beacon.conf import cohort
            cohort.singleEntryUrl=3
            async def test_check_cohorts_singleEntryUrl():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_singleEntryUrl())
            cohort.singleEntryUrl=True
    def test_cohorts_analysis_lookup(self):
        with loop_context() as loop:
            from beacon.conf import cohort
            cohort.analysis_lookup=3
            async def test_check_cohorts_analysis_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_analysis_lookup())
            cohort.analysis_lookup=True
    def test_cohorts_biosample_lookup(self):
        with loop_context() as loop:
            from beacon.conf import cohort
            cohort.biosample_lookup=3
            async def test_check_cohorts_biosample_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_biosample_lookup())
            cohort.biosample_lookup=True
    def test_cohorts_dataset_lookup(self):
        with loop_context() as loop:
            from beacon.conf import cohort
            cohort.dataset_lookup=3
            async def test_check_cohorts_dataset_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_dataset_lookup())
            cohort.dataset_lookup=True
    def test_cohorts_genomicVariant_lookup(self):
        with loop_context() as loop:
            from beacon.conf import cohort
            cohort.genomicVariant_lookup=3
            async def test_check_cohorts_genomicVariant_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_genomicVariant_lookup())
            cohort.genomicVariant_lookup=True
    def test_cohorts_individual_lookup(self):
        with loop_context() as loop:
            from beacon.conf import cohort
            cohort.individual_lookup=3
            async def test_check_cohorts_individual_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_individual_lookup())
            cohort.individual_lookup=True
    def test_cohorts_run_lookup(self):
        with loop_context() as loop:
            from beacon.conf import cohort
            cohort.run_lookup=3
            async def test_check_cohorts_run_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_run_lookup())
            cohort.run_lookup=True
    def test_datasets_open_api_endpoints_definition(self):
        with loop_context() as loop:
            from beacon.conf import dataset
            dataset.open_api_endpoints_definition=3
            async def test_check_datasets_open_api_endpoints_definition():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_open_api_endpoints_definition())
            dataset.open_api_endpoints_definition="string"
    def test_datasets_id(self):
        with loop_context() as loop:
            from beacon.conf import dataset
            dataset.id="something"
            async def test_check_datasets_id():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_id())
            dataset.id="dataset"
    def test_datasets_name(self):
        with loop_context() as loop:
            from beacon.conf import dataset
            dataset.name=3
            async def test_check_datasets_name():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_name())
            dataset.name="string"
    def test_datasets_ontology_id(self):
        with loop_context() as loop:
            from beacon.conf import dataset
            dataset.ontology_id="NOT CURIE"
            async def test_check_datasets_ontology_id():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_ontology_id())
            dataset.ontology_id="CURIE:12345"
    def test_datasets_ontology_name(self):
        with loop_context() as loop:
            from beacon.conf import dataset
            dataset.ontology_name=3
            async def test_check_datasets_ontology_name():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_ontology_name())
            dataset.ontology_name="string"
    def test_datasets_specification(self):
        with loop_context() as loop:
            from beacon.conf import dataset
            dataset.specification=3
            async def test_check_datasets_specification():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_specification())
            dataset.specification="string"
    def test_datasets_description(self):
        with loop_context() as loop:
            from beacon.conf import dataset
            dataset.description=3
            async def test_check_datasets_description():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_description())
            dataset.description="string"
    def test_datasets_default_schema_id(self):
        with loop_context() as loop:
            from beacon.conf import dataset
            dataset.defaultSchema_id=3
            async def test_check_datasets_default_schema_id():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_default_schema_id())
            dataset.defaultSchema_id="string"
    def test_datasets_default_schema_name(self):
        with loop_context() as loop:
            from beacon.conf import dataset
            dataset.defaultSchema_name=3
            async def test_check_datasets_default_schema_name():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_default_schema_name())
            dataset.defaultSchema_name="string"
    def test_datasets_reference_to_schema_definition(self):
        with loop_context() as loop:
            from beacon.conf import dataset
            dataset.defaultSchema_reference_to_schema_definition=3
            async def test_check_datasets_reference_to_schema_definition():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_reference_to_schema_definition())
            dataset.defaultSchema_reference_to_schema_definition="string"
    def test_datasets_default_schema_version(self):
        with loop_context() as loop:
            from beacon.conf import dataset
            dataset.defaultSchema_schema_version=3
            async def test_check_datasets_default_schema_version():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_default_schema_version())
            dataset.defaultSchema_schema_version="string"
    def test_datasets_additionally_supported_schemas(self):
        with loop_context() as loop:
            from beacon.conf import dataset
            dataset.aditionally_supported_schemas=3
            async def test_check_datasets_additionally_supported_schemas():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_additionally_supported_schemas())
            dataset.aditionally_supported_schemas=["string"]
    def test_datasets_allow_queries_without_filters(self):
        with loop_context() as loop:
            from beacon.conf import dataset
            dataset.allow_queries_without_filters=3
            async def test_check_datasets_allow_queries_without_filters():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_allow_queries_without_filters())
            dataset.allow_queries_without_filters=True
    def test_datasets_singleEntryUrl(self):
        with loop_context() as loop:
            from beacon.conf import dataset
            dataset.singleEntryUrl=3
            async def test_check_datasets_singleEntryUrl():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_singleEntryUrl())
            dataset.singleEntryUrl=True
    def test_datasets_analysis_lookup(self):
        with loop_context() as loop:
            from beacon.conf import dataset
            dataset.analysis_lookup=3
            async def test_check_datasets_analysis_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_analysis_lookup())
            dataset.analysis_lookup=True
    def test_datasets_biosample_lookup(self):
        with loop_context() as loop:
            from beacon.conf import dataset
            dataset.biosample_lookup=3
            async def test_check_datasets_biosample_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_biosample_lookup())
            dataset.biosample_lookup=True
    def test_datasets_cohort_lookup(self):
        with loop_context() as loop:
            from beacon.conf import dataset
            dataset.cohort_lookup=3
            async def test_check_datasets_cohort_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_cohort_lookup())
            dataset.cohort_lookup=True
    def test_datasets_genomicVariant_lookup(self):
        with loop_context() as loop:
            from beacon.conf import dataset
            dataset.genomicVariant_lookup=3
            async def test_check_datasets_genomicVariant_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_genomicVariant_lookup())
            dataset.genomicVariant_lookup=True
    def test_datasets_individual_lookup(self):
        with loop_context() as loop:
            from beacon.conf import dataset
            dataset.individual_lookup=3
            async def test_check_datasets_individual_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_individual_lookup())
            dataset.individual_lookup=True
    def test_datasets_run_lookup(self):
        with loop_context() as loop:
            from beacon.conf import dataset
            dataset.run_lookup=3
            async def test_check_datasets_run_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_datasets_run_lookup())
            dataset.run_lookup=True
    def test_g_variants_open_api_endpoints_definition(self):
        with loop_context() as loop:
            from beacon.conf import genomicVariant
            genomicVariant.open_api_endpoints_definition=3
            async def test_check_g_variants_open_api_endpoints_definition():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_open_api_endpoints_definition())
            genomicVariant.open_api_endpoints_definition="string"
    def test_g_variants_id(self):
        with loop_context() as loop:
            from beacon.conf import genomicVariant
            genomicVariant.id="something"
            async def test_check_g_variants_id():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_id())
            genomicVariant.id="genomicVariant"
    def test_g_variants_name(self):
        with loop_context() as loop:
            from beacon.conf import genomicVariant
            genomicVariant.name=3
            async def test_check_g_variants_name():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_name())
            genomicVariant.name="string"
    def test_g_variants_ontology_id(self):
        with loop_context() as loop:
            from beacon.conf import genomicVariant
            genomicVariant.ontology_id="NOT CURIE"
            async def test_check_g_variants_ontology_id():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_ontology_id())
            genomicVariant.ontology_id="CURIE:12345"
    def test_g_variants_ontology_name(self):
        with loop_context() as loop:
            from beacon.conf import genomicVariant
            genomicVariant.ontology_name=3
            async def test_check_g_variants_ontology_name():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_ontology_name())
            genomicVariant.ontology_name="string"
    def test_g_variants_specification(self):
        with loop_context() as loop:
            from beacon.conf import genomicVariant
            genomicVariant.specification=3
            async def test_check_g_variants_specification():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_specification())
            genomicVariant.specification="string"
    def test_g_variants_description(self):
        with loop_context() as loop:
            from beacon.conf import genomicVariant
            genomicVariant.description=3
            async def test_check_g_variants_description():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_description())
            genomicVariant.description="string"
    def test_g_variants_default_schema_id(self):
        with loop_context() as loop:
            from beacon.conf import genomicVariant
            genomicVariant.defaultSchema_id=3
            async def test_check_g_variants_default_schema_id():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_default_schema_id())
            genomicVariant.defaultSchema_id="string"
    def test_g_variants_default_schema_name(self):
        with loop_context() as loop:
            from beacon.conf import genomicVariant
            genomicVariant.defaultSchema_name=3
            async def test_check_g_variants_default_schema_name():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_default_schema_name())
            genomicVariant.defaultSchema_name="string"
    def test_g_variants_reference_to_schema_definition(self):
        with loop_context() as loop:
            from beacon.conf import genomicVariant
            genomicVariant.defaultSchema_reference_to_schema_definition=3
            async def test_check_g_variants_reference_to_schema_definition():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_reference_to_schema_definition())
            genomicVariant.defaultSchema_reference_to_schema_definition="string"
    def test_g_variants_default_schema_version(self):
        with loop_context() as loop:
            from beacon.conf import genomicVariant
            genomicVariant.defaultSchema_schema_version=3
            async def test_check_g_variants_default_schema_version():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_default_schema_version())
            genomicVariant.defaultSchema_schema_version="string"
    def test_g_variants_additionally_supported_schemas(self):
        with loop_context() as loop:
            from beacon.conf import genomicVariant
            genomicVariant.aditionally_supported_schemas=3
            async def test_check_g_variants_additionally_supported_schemas():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_additionally_supported_schemas())
            genomicVariant.aditionally_supported_schemas=["string"]
    def test_g_variants_allow_queries_without_filters(self):
        with loop_context() as loop:
            from beacon.conf import genomicVariant
            genomicVariant.allow_queries_without_filters=3
            async def test_check_g_variants_allow_queries_without_filters():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_allow_queries_without_filters())
            genomicVariant.allow_queries_without_filters=True
    def test_g_variants_singleEntryUrl(self):
        with loop_context() as loop:
            from beacon.conf import genomicVariant
            genomicVariant.singleEntryUrl=3
            async def test_check_g_variants_singleEntryUrl():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_singleEntryUrl())
            genomicVariant.singleEntryUrl=True
    def test_g_variants_analysis_lookup(self):
        with loop_context() as loop:
            from beacon.conf import genomicVariant
            genomicVariant.analysis_lookup=3
            async def test_check_g_variants_analysis_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_analysis_lookup())
            genomicVariant.analysis_lookup=True
    def test_g_variants_biosample_lookup(self):
        with loop_context() as loop:
            from beacon.conf import genomicVariant
            genomicVariant.biosample_lookup=3
            async def test_check_g_variants_biosample_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_biosample_lookup())
            genomicVariant.biosample_lookup=True
    def test_g_variants_cohort_lookup(self):
        with loop_context() as loop:
            from beacon.conf import genomicVariant
            genomicVariant.cohort_lookup=3
            async def test_check_g_variants_cohort_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_cohort_lookup())
            genomicVariant.cohort_lookup=True
    def test_g_variants_dataset_lookup(self):
        with loop_context() as loop:
            from beacon.conf import genomicVariant
            genomicVariant.dataset_lookup=3
            async def test_check_g_variants_dataset_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_dataset_lookup())
            genomicVariant.dataset_lookup=True
    def test_g_variants_individual_lookup(self):
        with loop_context() as loop:
            from beacon.conf import genomicVariant
            genomicVariant.individual_lookup=3
            async def test_check_g_variants_individual_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_individual_lookup())
            genomicVariant.individual_lookup=True
    def test_g_variants_run_lookup(self):
        with loop_context() as loop:
            from beacon.conf import genomicVariant
            genomicVariant.run_lookup=3
            async def test_check_g_variants_run_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_g_variants_run_lookup())
            genomicVariant.run_lookup=True
    def test_individuals_open_api_endpoints_definition(self):
        with loop_context() as loop:
            from beacon.conf import individual
            individual.open_api_endpoints_definition=3
            async def test_check_individuals_open_api_endpoints_definition():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_individuals_open_api_endpoints_definition())
            individual.open_api_endpoints_definition="string"
    def test_individuals_id(self):
        with loop_context() as loop:
            from beacon.conf import individual
            individual.id="something"
            async def test_check_individuals_id():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_individuals_id())
            individual.id="individual"
    def test_individuals_name(self):
        with loop_context() as loop:
            from beacon.conf import individual
            individual.name=3
            async def test_check_individuals_name():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_individuals_name())
            individual.name="string"
    def test_individuals_ontology_id(self):
        with loop_context() as loop:
            from beacon.conf import individual
            individual.ontology_id="NOT CURIE"
            async def test_check_individuals_ontology_id():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_individuals_ontology_id())
            individual.ontology_id="CURIE:12345"
    def test_individuals_ontology_name(self):
        with loop_context() as loop:
            from beacon.conf import individual
            individual.ontology_name=3
            async def test_check_individuals_ontology_name():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_individuals_ontology_name())
            individual.ontology_name="string"
    def test_individuals_specification(self):
        with loop_context() as loop:
            from beacon.conf import individual
            individual.specification=3
            async def test_check_individuals_specification():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_individuals_specification())
            individual.specification="string"
    def test_individuals_description(self):
        with loop_context() as loop:
            from beacon.conf import individual
            individual.description=3
            async def test_check_individuals_description():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_individuals_description())
            individual.description="string"
    def test_individuals_default_schema_id(self):
        with loop_context() as loop:
            from beacon.conf import individual
            individual.defaultSchema_id=3
            async def test_check_individuals_default_schema_id():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_individuals_default_schema_id())
            individual.defaultSchema_id="string"
    def test_individuals_default_schema_name(self):
        with loop_context() as loop:
            from beacon.conf import individual
            individual.defaultSchema_name=3
            async def test_check_individuals_default_schema_name():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_individuals_default_schema_name())
            individual.defaultSchema_name="string"
    def test_individuals_reference_to_schema_definition(self):
        with loop_context() as loop:
            from beacon.conf import individual
            individual.defaultSchema_reference_to_schema_definition=3
            async def test_check_individuals_reference_to_schema_definition():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_individuals_reference_to_schema_definition())
            individual.defaultSchema_reference_to_schema_definition="string"
    def test_individuals_default_schema_version(self):
        with loop_context() as loop:
            from beacon.conf import individual
            individual.defaultSchema_schema_version=3
            async def test_check_individuals_default_schema_version():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_individuals_default_schema_version())
            individual.defaultSchema_schema_version="string"
    def test_individuals_additionally_supported_schemas(self):
        with loop_context() as loop:
            from beacon.conf import individual
            individual.aditionally_supported_schemas=3
            async def test_check_individuals_additionally_supported_schemas():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_individuals_additionally_supported_schemas())
            individual.aditionally_supported_schemas=["string"]
    def test_individuals_allow_queries_without_filters(self):
        with loop_context() as loop:
            from beacon.conf import individual
            individual.allow_queries_without_filters=3
            async def test_check_individuals_allow_queries_without_filters():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_individuals_allow_queries_without_filters())
            individual.allow_queries_without_filters=True
    def test_individuals_singleEntryUrl(self):
        with loop_context() as loop:
            from beacon.conf import individual
            individual.singleEntryUrl=3
            async def test_check_individuals_singleEntryUrl():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_individuals_singleEntryUrl())
            individual.singleEntryUrl=True
    def test_individuals_analysis_lookup(self):
        with loop_context() as loop:
            from beacon.conf import individual
            individual.analysis_lookup=3
            async def test_check_individuals_analysis_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_individuals_analysis_lookup())
            individual.analysis_lookup=True
    def test_individuals_biosample_lookup(self):
        with loop_context() as loop:
            from beacon.conf import individual
            individual.biosample_lookup=3
            async def test_check_individuals_biosample_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_individuals_biosample_lookup())
            individual.biosample_lookup=True
    def test_individuals_cohort_lookup(self):
        with loop_context() as loop:
            from beacon.conf import individual
            individual.cohort_lookup=3
            async def test_check_individuals_cohort_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_individuals_cohort_lookup())
            individual.cohort_lookup=True
    def test_individuals_dataset_lookup(self):
        with loop_context() as loop:
            from beacon.conf import individual
            individual.dataset_lookup=3
            async def test_check_individuals_dataset_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_individuals_dataset_lookup())
            individual.dataset_lookup=True
    def test_individuals_genomicVariant_lookup(self):
        with loop_context() as loop:
            from beacon.conf import individual
            individual.genomicVariant_lookup=3
            async def test_check_individuals_genomicVariant_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_individuals_genomicVariant_lookup())
            individual.genomicVariant_lookup=True
    def test_individuals_run_lookup(self):
        with loop_context() as loop:
            from beacon.conf import individual
            individual.run_lookup=3
            async def test_check_individuals_run_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_individuals_run_lookup())
            individual.run_lookup=True
    def test_runs_open_api_endpoints_definition(self):
        with loop_context() as loop:
            from beacon.conf import run
            run.open_api_endpoints_definition=3
            async def test_check_runs_open_api_endpoints_definition():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_open_api_endpoints_definition())
            run.open_api_endpoints_definition="string"
    def test_runs_id(self):
        with loop_context() as loop:
            from beacon.conf import run
            run.id="something"
            async def test_check_runs_id():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_id())
            run.id="run"
    def test_runs_name(self):
        with loop_context() as loop:
            from beacon.conf import run
            run.name=3
            async def test_check_runs_name():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_name())
            run.name="string"
    def test_runs_ontology_id(self):
        with loop_context() as loop:
            from beacon.conf import run
            run.ontology_id="NOT CURIE"
            async def test_check_runs_ontology_id():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_ontology_id())
            run.ontology_id="CURIE:12345"
    def test_runs_ontology_name(self):
        with loop_context() as loop:
            from beacon.conf import run
            run.ontology_name=3
            async def test_check_runs_ontology_name():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_ontology_name())
            run.ontology_name="string"
    def test_runs_specification(self):
        with loop_context() as loop:
            from beacon.conf import run
            run.specification=3
            async def test_check_runs_specification():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_specification())
            run.specification="string"
    def test_runs_description(self):
        with loop_context() as loop:
            from beacon.conf import run
            run.description=3
            async def test_check_runs_description():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_description())
            run.description="string"
    def test_runs_default_schema_id(self):
        with loop_context() as loop:
            from beacon.conf import run
            run.defaultSchema_id=3
            async def test_check_runs_default_schema_id():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_default_schema_id())
            run.defaultSchema_id="string"
    def test_runs_default_schema_name(self):
        with loop_context() as loop:
            from beacon.conf import run
            run.defaultSchema_name=3
            async def test_check_runs_default_schema_name():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_default_schema_name())
            run.defaultSchema_name="string"
    def test_runs_reference_to_schema_definition(self):
        with loop_context() as loop:
            from beacon.conf import run
            run.defaultSchema_reference_to_schema_definition=3
            async def test_check_runs_reference_to_schema_definition():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_reference_to_schema_definition())
            run.defaultSchema_reference_to_schema_definition="string"
    def test_runs_default_schema_version(self):
        with loop_context() as loop:
            from beacon.conf import run
            run.defaultSchema_schema_version=3
            async def test_check_runs_default_schema_version():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_default_schema_version())
            run.defaultSchema_schema_version="string"
    def test_runs_additionally_supported_schemas(self):
        with loop_context() as loop:
            from beacon.conf import run
            run.aditionally_supported_schemas=3
            async def test_check_runs_additionally_supported_schemas():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_additionally_supported_schemas())
            run.aditionally_supported_schemas=["string"]
    def test_runs_allow_queries_without_filters(self):
        with loop_context() as loop:
            from beacon.conf import run
            run.allow_queries_without_filters=3
            async def test_check_runs_allow_queries_without_filters():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_allow_queries_without_filters())
            run.allow_queries_without_filters=True
    def test_runs_singleEntryUrl(self):
        with loop_context() as loop:
            from beacon.conf import run
            run.singleEntryUrl=3
            async def test_check_runs_singleEntryUrl():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_singleEntryUrl())
            run.singleEntryUrl=True
    def test_runs_analysis_lookup(self):
        with loop_context() as loop:
            from beacon.conf import run
            run.analysis_lookup=3
            async def test_check_runs_analysis_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_analysis_lookup())
            run.analysis_lookup=True
    def test_runs_biosample_lookup(self):
        with loop_context() as loop:
            from beacon.conf import run
            run.biosample_lookup=3
            async def test_check_runs_biosample_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_biosample_lookup())
            run.biosample_lookup=True
    def test_runs_cohort_lookup(self):
        with loop_context() as loop:
            from beacon.conf import run
            run.cohort_lookup=3
            async def test_check_runs_cohort_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_cohort_lookup())
            run.cohort_lookup=True
    def test_runs_dataset_lookup(self):
        with loop_context() as loop:
            from beacon.conf import run
            run.dataset_lookup=3
            async def test_check_runs_dataset_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_dataset_lookup())
            run.dataset_lookup=True
    def test_runs_genomicVariant_lookup(self):
        with loop_context() as loop:
            from beacon.conf import run
            run.genomicVariant_lookup=3
            async def test_check_runs_genomicVariant_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_genomicVariant_lookup())
            run.genomicVariant_lookup=True
    def test_runs_individual_lookup(self):
        with loop_context() as loop:
            from beacon.conf import run
            run.individual_lookup=3
            async def test_check_runs_individual_lookup():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_check_runs_individual_lookup())
            run.individual_lookup=True
    def test_conf_level_wrong(self):
        with loop_context() as loop:
            from beacon.conf import conf
            conf.level='something'
            async def test_conf_level_wrong():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_conf_level_wrong())
            conf.level=logging.NOTSET
    def test_conf_log_file_wrong(self):
        with loop_context() as loop:
            from beacon.conf import conf
            conf.log_file=3
            async def test_conf_log_file_wrong():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_conf_log_file_wrong())
            conf.log_file=None
    def test_conf_wrong_beacon_id(self):
        with loop_context() as loop:
            from beacon.conf import conf
            conf.beacon_id=3
            async def test_conf_wrong_beacon_id():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_conf_wrong_beacon_id())
            conf.beacon_id="string"
    def test_conf_wrong_beacon_name(self):
        with loop_context() as loop:
            from beacon.conf import conf
            conf.beacon_name=3
            async def test_conf_wrong_beacon_name():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_conf_wrong_beacon_name())
            conf.beacon_name="string"
    def test_conf_wrong_api_version(self):
        with loop_context() as loop:
            from beacon.conf import conf
            conf.api_version=3
            async def test_conf_wrong_api_version():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_conf_wrong_api_version())
            conf.api_version="string"
    def test_conf_wrong_description(self):
        with loop_context() as loop:
            from beacon.conf import conf
            conf.description=3
            async def test_conf_wrong_description():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_conf_wrong_description())
            conf.description="string"
    def test_conf_wrong_welcome_url(self):
        with loop_context() as loop:
            from beacon.conf import conf
            conf.welcome_url=3
            async def test_conf_wrong_welcome_url():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_conf_wrong_welcome_url())
            conf.welcome_url="string"
    def test_conf_wrong_alternative_url(self):
        with loop_context() as loop:
            from beacon.conf import conf
            conf.alternative_url=3
            async def test_conf_wrong_alternative_url():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_conf_wrong_alternative_url())
            conf.alternative_url="string"
    def test_conf_wrong_create_datetime(self):
        with loop_context() as loop:
            from beacon.conf import conf
            conf.create_datetime=3
            async def test_conf_wrong_create_datetime():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_conf_wrong_create_datetime())
            conf.create_datetime="string"
    def test_conf_wrong_update_datetime(self):
        with loop_context() as loop:
            from beacon.conf import conf
            conf.update_datetime=3
            async def test_conf_wrong_update_datetime():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_conf_wrong_update_datetime())
            conf.update_datetime="string"
    def test_conf_wrong_documentation_url(self):
        with loop_context() as loop:
            from beacon.conf import conf
            conf.documentation_url=3
            async def test_conf_wrong_documentation_url():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_conf_wrong_documentation_url())
            conf.documentation_url="string"
    def test_conf_wrong_welcome_url_no_http(self):
        with loop_context() as loop:
            from beacon.conf import conf
            conf.welcome_url="something"
            async def test_conf_wrong_welcome_url():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_conf_wrong_welcome_url())
            conf.welcome_url="https://beacon.ega-archive.org/"
    def test_conf_wrong_alternative_url_no_http(self):
        with loop_context() as loop:
            from beacon.conf import conf
            conf.alternative_url="something"
            async def test_conf_wrong_alternative_url():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_conf_wrong_alternative_url())
            conf.alternative_url="https://beacon.ega-archive.org/api"
    def test_conf_wrong_documentation_url_no_http(self):
        with loop_context() as loop:
            from beacon.conf import conf
            conf.documentation_url="string"
            async def test_conf_wrong_documentation_url():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_conf_wrong_documentation_url())
            conf.documentation_url="https://b2ri-documentation-demo.ega-archive.org/"
    def test_wrong_datasets_permissions(self):
        with loop_context() as loop:
            data={
                "testing": {
                    "registere": "yes"
                }
            }
            with open('/beacon/permissions/datasets/datasets_permissions.yml', 'w') as outfile:
                yaml.dump(data, outfile, default_flow_style=False)
            async def test_conf_wrong_datasets_permissions():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_conf_wrong_datasets_permissions())
    def test_wrong_datasets_permissions_2(self):
        with loop_context() as loop:
            data={
                "testing": {
                    "registered": {"yes": "no"}
                }
            }
            with open('/beacon/permissions/datasets/datasets_permissions.yml', 'w') as outfile:
                yaml.dump(data, outfile, default_flow_style=False)
            async def test_conf_wrong_datasets_permissions_2():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_conf_wrong_datasets_permissions_2())
    def test_wrong_datasets_permissions_3(self):
        with loop_context() as loop:
            data={
                "testing": {
                    "controlled": {"user-list": [{"user": "unknown"}]}
                }
            }
            with open('/beacon/permissions/datasets/datasets_permissions.yml', 'w') as outfile:
                yaml.dump(data, outfile, default_flow_style=False)
            async def test_conf_wrong_datasets_permissions_3():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_conf_wrong_datasets_permissions_3())
    def test_wrong_datasets_conf(self):
        with loop_context() as loop:
            data={
                "testing": {
                    "registere": "yes"
                }
            }
            with open('/beacon/conf/datasets/datasets_conf.yml', 'w') as outfile:
                yaml.dump(data, outfile, default_flow_style=False)
            async def test_conf_wrong_datasets_conf():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_conf_wrong_datasets_conf())
    def test_wrong_datasets_conf_2(self):
        with loop_context() as loop:
            data={
                "testing": {
                    "isTest": "yes"
                }
            }
            with open('/beacon/conf/datasets/datasets_conf.yml', 'w') as outfile:
                yaml.dump(data, outfile, default_flow_style=False)
            async def test_conf_wrong_datasets_conf_2():
                try:
                    check_configuration()
                except Exception:
                    pass
            loop.run_until_complete(test_conf_wrong_datasets_conf_2())



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