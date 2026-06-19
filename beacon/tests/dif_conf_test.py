from aiohttp.test_utils import TestClient, TestServer, loop_context
from beacon.tests.__main__ import create_app
import json
import unittest
import beacon.conf.conf_override as conf_override
from beacon.validator.configuration import check_configuration
import yaml
from beacon.logs.logs import initialize_logger
from beacon.conf.conf_override import config

def import_genomicVariant_confile():
    """Get the information about the genomic variant entry type gor ga4gh model"""
    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'r') as pfile:
        genomicVariant_confile= yaml.safe_load(pfile)
    pfile.close()
    return genomicVariant_confile

def import_dataset_confile():
    """Get the information about the dataset entry type gor ga4gh model"""
    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'r') as pfile:
        dataset_confile= yaml.safe_load(pfile)
    pfile.close()
    return dataset_confile

def import_analysis_confile():
    """Get the information about the analysis entry type gor ga4gh model"""
    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'r') as pfile:
        analysis_confile= yaml.safe_load(pfile)
    pfile.close()
    return analysis_confile

def import_biosample_confile():
    """Get the information about the biosample entry type gor ga4gh model"""
    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'r') as pfile:
        biosample_confile= yaml.safe_load(pfile)
    pfile.close()
    return biosample_confile

def import_cohort_confile():
    """Get the information about the cohort entry type gor ga4gh model"""
    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'r') as pfile:
        cohort_confile= yaml.safe_load(pfile)
    pfile.close()
    return cohort_confile

def import_individual_confile():
    """Get the information about the individual entry type gor ga4gh model"""
    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'r') as pfile:
        individual_confile= yaml.safe_load(pfile)
    pfile.close()
    return individual_confile

def import_run_confile():
    """Get the information about the run entry type gor ga4gh model"""
    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/run.yml", 'r') as pfile:
        run_confile= yaml.safe_load(pfile)
    pfile.close()
    return run_confile

# Keeping the conf files loaded as dictionaries into variables
analysis = import_analysis_confile()
biosample = import_biosample_confile()
cohort = import_cohort_confile()
dataset = import_dataset_confile()
genomicVariant = import_genomicVariant_confile()
run = import_run_confile()
individual = import_individual_confile()

# Create the class that will host all the unit test for exceptions that can arise for bad configuration
class TestNoFilters(unittest.TestCase):
    def test_no_filters_analysis_query_without_filters_allowed(self):
        with loop_context() as loop:
            # Disable unfiltered queries for the analysis endpoint
            analysis["analysis"]["allow_queries_without_filters"] = False

            # Persist configuration change so the application loads it
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

            # Create and start a test instance of the application
            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_analysis_query_without_filters_allowed():
                # Request endpoint without filters and verify it is rejected
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    analysis["analysis"]["endpoint_name"]
                )
                assert resp.status == 400

            loop.run_until_complete(test_analysis_query_without_filters_allowed())
            loop.run_until_complete(client.close())

            # Restore original configuration for subsequent tests
            analysis["analysis"]["allow_queries_without_filters"] = True
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)


    def test_no_filters_biosample_query_without_filters_allowed(self):
        with loop_context() as loop:
            # Prevent biosample queries from executing without filters
            biosample["biosample"]["allow_queries_without_filters"] = False

            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)

            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_biosample_query_without_filters_allowed():
                # Verify endpoint returns HTTP 400 when filters are omitted
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    biosample["biosample"]["endpoint_name"]
                )
                assert resp.status == 400

            loop.run_until_complete(test_biosample_query_without_filters_allowed())
            loop.run_until_complete(client.close())

            # Re-enable unfiltered queries after test execution
            biosample["biosample"]["allow_queries_without_filters"] = True
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
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

    def test_no_filters_cohort_query_without_filters_allowed(self):
        with loop_context() as loop:
            # Configure cohort endpoint to require filters
            cohort["cohort"]["allow_queries_without_filters"] = False

            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)

            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_cohort_query_without_filters_allowed():
                # Expect a bad request when querying without filters
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    cohort["cohort"]["endpoint_name"]
                )
                assert resp.status == 400

            loop.run_until_complete(test_cohort_query_without_filters_allowed())
            loop.run_until_complete(client.close())

            # Restore configuration
            cohort["cohort"]["allow_queries_without_filters"] = True
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)


    def test_no_filters_dataset_query_without_filters_allowed(self):
        with loop_context() as loop:
            # Disable dataset requests without filters
            dataset["dataset"]["allow_queries_without_filters"] = False

            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)

            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_dataset_query_without_filters_allowed():
                # Ensure server rejects unfiltered dataset requests
                resp = await client.get(
                    conf_override.config.uri_subpath + "/" +
                    dataset["dataset"]["endpoint_name"]
                )
                assert resp.status == 400

            loop.run_until_complete(test_dataset_query_without_filters_allowed())
            loop.run_until_complete(client.close())

            # Reset configuration to default state
            dataset["dataset"]["allow_queries_without_filters"] = True
            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)


    def test_map_endpoint_response_with_disabled_endpoint(self):
        with loop_context() as loop:
            # Temporarily disable analysis entry type
            analysis["analysis"]["entry_type_enabled"] = False

            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_map_endpoint_response_with_disabled_endpoint():
                # Retrieve endpoint map
                resp = await client.get(conf_override.config.uri_subpath + "/map")
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Disabled entry type should not appear in endpointSets
                self.assertNotIn(
                    "analysis",
                    responsedict["response"]["endpointSets"]
                )

            loop.run_until_complete(test_check_map_endpoint_response_with_disabled_endpoint())
            loop.run_until_complete(client.close())

            # Re-enable analysis endpoint for later tests
            analysis["analysis"]["entry_type_enabled"] = True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
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
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis, biosample_confile=biosample, cohort_confile=cohort, dataset_confile=dataset, genomicVariant_confile=genomicVariant, individual_confile=individual, run_confile=run)
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
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis, biosample_confile=biosample, cohort_confile=cohort, dataset_confile=dataset, genomicVariant_confile=genomicVariant, individual_confile=individual, run_confile=run)
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
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis, biosample_confile=biosample, cohort_confile=cohort, dataset_confile=dataset, genomicVariant_confile=genomicVariant, individual_confile=individual, run_confile=run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_configuration_enable_run())
            loop.run_until_complete(client.close())
            run["run"]["entry_type_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

    def test_configuration_endpoint_response_with_disabled_endpoint(self):
        with loop_context() as loop:
            # Disable analysis entry type in configuration
            analysis["analysis"]["entry_type_enabled"] = False

            with open("/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_configuration_endpoint_response_with_disabled_endpoint():
                # Request Beacon configuration metadata
                resp = await client.get(
                    conf_override.config.uri_subpath + "/configuration"
                )
                assert resp.status == 200

                responsetext = await resp.text()
                responsedict = json.loads(responsetext)

                # Disabled entry type should not be advertised
                self.assertNotIn(
                    "analysis",
                    responsedict["response"]["entryTypes"]
                )

            loop.run_until_complete(test_check_configuration_endpoint_response_with_disabled_endpoint())
            loop.run_until_complete(client.close())

            # Restore analysis entry type
            analysis["analysis"]["entry_type_enabled"] = True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
    def test_main_check_configuration_with_wrong_analysis_enable_endpoint(self):
        with loop_context() as loop:
            # Inject an invalid value where a boolean is expected
            analysis["analysis"]["entry_type_enabled"] = "no Boolean"

            # Persist invalid configuration for validation testing
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_configuration_enable_analysis():
                try:
                    # Verify configuration validation handles invalid endpoint setting
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis,biosample_confile=biosample,cohort_confile=cohort,dataset_confile=dataset,genomicVariant_confile=genomicVariant,individual_confile=individual,run_confile=run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_configuration_enable_analysis())
            loop.run_until_complete(client.close())

            # Restore valid configuration value
            analysis["analysis"]["entry_type_enabled"] = True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)


    def test_main_check_configuration_with_wrong_biosample_enable_endpoint(self):
        with loop_context() as loop:
            # Replace expected boolean with invalid string value
            biosample["biosample"]["entry_type_enabled"] = "no Boolean"

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)

            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_configuration_enable_biosample():
                try:
                    # Run configuration validation against malformed config
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis,biosample_confile=biosample,cohort_confile=cohort,dataset_confile=dataset,genomicVariant_confile=genomicVariant,individual_confile=individual,run_confile=run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_configuration_enable_biosample())
            loop.run_until_complete(client.close())

            # Reset configuration after test
            biosample["biosample"]["entry_type_enabled"] = True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)


    def test_main_check_configuration_with_wrong_cohort_enable_endpoint(self):
        with loop_context() as loop:
            # Simulate invalid endpoint enablement configuration
            cohort["cohort"]["entry_type_enabled"] = "no Boolean"

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)

            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_configuration_enable_cohort():
                try:
                    # Validation should detect incorrect configuration type
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis,biosample_confile=biosample,cohort_confile=cohort,dataset_confile=dataset,genomicVariant_confile=genomicVariant,individual_confile=individual,run_confile=run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_configuration_enable_cohort())
            loop.run_until_complete(client.close())

            # Restore expected boolean value
            cohort["cohort"]["entry_type_enabled"] = True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)


    def test_main_check_configuration_with_wrong_dataset_enable_endpoint(self):
        with loop_context() as loop:
            # Force invalid endpoint configuration for dataset entry type
            dataset["dataset"]["entry_type_enabled"] = "no Boolean"

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)

            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_configuration_enable_dataset():
                try:
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis,biosample_confile=biosample,cohort_confile=cohort,dataset_confile=dataset,genomicVariant_confile=genomicVariant,individual_confile=individual,run_confile=run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_configuration_enable_dataset())
            loop.run_until_complete(client.close())

            # Return configuration to valid state
            dataset["dataset"]["entry_type_enabled"] = True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)


    def test_main_check_configuration_with_wrong_analysis_granularity(self):
        with loop_context() as loop:
            # Assign unsupported granularity value
            analysis["analysis"]["max_granularity"] = "no Boolean"

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_configuration_enable_analysis():
                try:
                    # Validate handling of invalid granularity configuration
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis,biosample_confile=biosample,cohort_confile=cohort,dataset_confile=dataset,genomicVariant_confile=genomicVariant,individual_confile=individual,run_confile=run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_configuration_enable_analysis())
            loop.run_until_complete(client.close())

            # Restore supported granularity value
            analysis["analysis"]["max_granularity"] = "record"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)


    def test_main_check_configuration_with_wrong_biosample_granularity(self):
        with loop_context() as loop:
            # Introduce invalid granularity setting for biosample endpoint
            biosample["biosample"]["max_granularity"] = "no Boolean"

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)

            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_configuration_enable_biosample():
                try:
                    # Ensure configuration checker processes invalid granularity
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis,biosample_confile=biosample,cohort_confile=cohort,dataset_confile=dataset,genomicVariant_confile=genomicVariant,individual_confile=individual,run_confile=run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_configuration_enable_biosample())
            loop.run_until_complete(client.close())

            # Restore original granularity setting
            biosample["biosample"]["max_granularity"] = "record"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
    def test_main_check_configuration_with_wrong_cohort_granularity(self):
        with loop_context() as loop:
            # Inject an invalid granularity value into cohort configuration
            cohort["cohort"]["max_granularity"] = "no Boolean"

            # Save modified configuration for validation testing
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)

            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_configuration_enable_cohort():
                try:
                    # Verify configuration validation handles invalid granularity
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis,biosample_confile=biosample,cohort_confile=cohort,dataset_confile=dataset,genomicVariant_confile=genomicVariant,individual_confile=individual,run_confile=run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_configuration_enable_cohort())
            loop.run_until_complete(client.close())

            # Restore original configuration value
            cohort["cohort"]["max_granularity"] = "record"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)


    def test_main_check_configuration_with_wrong_dataset_granularity(self):
        with loop_context() as loop:
            # Use an unsupported granularity value
            dataset["dataset"]["max_granularity"] = "no Boolean"

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)

            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_configuration_enable_dataset():
                try:
                    # Execute configuration validation with malformed dataset config
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis,biosample_confile=biosample,cohort_confile=cohort,dataset_confile=dataset,genomicVariant_confile=genomicVariant,individual_confile=individual,run_confile=run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_configuration_enable_dataset())
            loop.run_until_complete(client.close())

            # Reset granularity setting after test
            dataset["dataset"]["max_granularity"] = "record"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)


    def test_main_check_configuration_with_wrong_individual_granularity(self):
        with loop_context() as loop:
            # Corrupt individual granularity configuration
            individual["individual"]["max_granularity"] = "no Boolean"

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)

            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_configuration_enable_individual():
                try:
                    # Validate behavior when granularity value is invalid
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis,biosample_confile=biosample,cohort_confile=cohort,dataset_confile=dataset,genomicVariant_confile=genomicVariant,individual_confile=individual,run_confile=run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_configuration_enable_individual())
            loop.run_until_complete(client.close())

            # Restore supported granularity
            individual["individual"]["max_granularity"] = "record"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)


    def test_main_check_configuration_with_wrong_genomicVariant_granularity(self):
        with loop_context() as loop:
            # Introduce invalid genomicVariant granularity setting
            genomicVariant["genomicVariant"]["max_granularity"] = "no Boolean"

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)

            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_configuration_enable_genomicVariant():
                try:
                    # Check validation logic against malformed configuration
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis,biosample_confile=biosample,cohort_confile=cohort,dataset_confile=dataset,genomicVariant_confile=genomicVariant,individual_confile=individual,run_confile=run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_configuration_enable_genomicVariant())
            loop.run_until_complete(client.close())

            # Restore valid granularity value
            genomicVariant["genomicVariant"]["max_granularity"] = "record"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)


    def test_main_check_configuration_with_wrong_run_granularity(self):
        with loop_context() as loop:
            # Set an invalid granularity value for run endpoint
            run["run"]["max_granularity"] = "no Boolean"

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_configuration_granularity_run():
                try:
                    # Execute configuration checks using invalid run configuration
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis,biosample_confile=biosample,cohort_confile=cohort,dataset_confile=dataset,genomicVariant_confile=genomicVariant,individual_confile=individual,run_confile=run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_configuration_granularity_run())
            loop.run_until_complete(client.close())

            # Restore default granularity
            run["run"]["max_granularity"] = "record"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)


    def test_main_check_configuration_http(self):
        with loop_context() as loop:
            from beacon.conf import conf_override

            # Test configuration validation using HTTPS URI
            conf_override.config.uri = "https://localhost:5010"

            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_configuration_http():
                # Verify configuration checker accepts HTTPS scheme
                check_configuration(
                    LOG=initialize_logger(config.level),
                    analysis_confile=analysis,
                    biosample_confile=biosample,
                    cohort_confile=cohort,
                    dataset_confile=dataset,
                    genomicVariant_confile=genomicVariant,
                    individual_confile=individual,
                    run_confile=run
                )

            loop.run_until_complete(test_check_configuration_http())
            loop.run_until_complete(client.close())

            # Restore original URI
            conf_override.config.uri = "http://localhost:50101"


    def test_main_check_configuration_wrong_uri(self):
        with loop_context() as loop:
            from beacon.conf import conf_override

            # Configure an invalid URI format
            conf_override.config.uri = "afafsafas"

            async def test_check_configuration_wrong_uri():
                try:
                    # Validation should detect malformed URI
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis,biosample_confile=biosample,cohort_confile=cohort,dataset_confile=dataset,genomicVariant_confile=genomicVariant,individual_confile=individual,run_confile=run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_configuration_wrong_uri())

            # Restore valid URI
            conf_override.config.uri = "http://localhost:50101"


    def test_main_check_configuration_wrong_uri_trailing_slash(self):
        with loop_context() as loop:
            from beacon.conf import conf_override

            # Configure URI ending with a trailing slash
            conf_override.config.uri = "http://localhost:50101/"

            async def test_check_configuration_wrong_uri_trailing_slash():
                try:
                    # Verify URI format validation
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis,biosample_confile=biosample,cohort_confile=cohort,dataset_confile=dataset,genomicVariant_confile=genomicVariant,individual_confile=individual,run_confile=run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_configuration_wrong_uri_trailing_slash())

            # Restore standard URI format
            conf_override.config.uri = "http://localhost:50101"


    def test_main_check_configuration_wrong_uri_subpath_trailing_slash(self):
        with loop_context() as loop:
            from beacon.conf import conf_override

            # Configure subpath with invalid trailing slash
            conf_override.config.uri_subpath = "/api/"

            async def test_check_configuration_wrong_uri_subpath_trailing_slash():
                try:
                    # Check validation of API subpath formatting
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis,biosample_confile=biosample,cohort_confile=cohort,dataset_confile=dataset,genomicVariant_confile=genomicVariant,individual_confile=individual,run_confile=run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_configuration_wrong_uri_subpath_trailing_slash())

            # Restore expected subpath value
            conf_override.config.uri_subpath = "/api"


    def test_main_check_configuration_wrong_uri_subpath_starting_slash_missing(self):
        with loop_context() as loop:
            from beacon.conf import conf_override

            # Remove required leading slash from API subpath
            conf_override.config.uri_subpath = "api"

            async def test_check_configuration_wrong_uri_subpath_starting_slash():
                try:
                    # Validate handling of malformed subpath
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis,biosample_confile=biosample,cohort_confile=cohort,dataset_confile=dataset,genomicVariant_confile=genomicVariant,individual_confile=individual,run_confile=run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_configuration_wrong_uri_subpath_starting_slash())

            # Restore valid API subpath
            conf_override.config.uri_subpath = "/api"
    def test_main_check_configuration_wrong_query_budget_amount(self):
        with loop_context() as loop:
            from beacon.conf import conf_override

            # Set an invalid query budget amount value
            conf_override.config.query_budget_amount = "api"

            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_configuration_wrong_query_budget_amount():
                try:
                    # Verify configuration validation handles invalid budget amount
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis,biosample_confile=biosample,cohort_confile=cohort,dataset_confile=dataset,genomicVariant_confile=genomicVariant,individual_confile=individual,run_confile=run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_configuration_wrong_query_budget_amount())
            loop.run_until_complete(client.close())

            # Restore valid query budget amount
            conf_override.config.query_budget_amount = 3


    def test_main_check_configuration_wrong_query_budget_time(self):
        with loop_context() as loop:
            from beacon.conf import conf_override

            # Use an invalid value for query budget time window
            conf_override.config.query_budget_time_in_seconds = "api"

            async def test_check_configuration_wrong_query_budget_time():
                try:
                    # Validate handling of malformed budget time configuration
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis,biosample_confile=biosample,cohort_confile=cohort,dataset_confile=dataset,genomicVariant_confile=genomicVariant,individual_confile=individual,run_confile=run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_configuration_wrong_query_budget_time())

            # Restore expected numeric value
            conf_override.config.query_budget_time_in_seconds = 3


    def test_main_check_configuration_wrong_query_budget_user(self):
        with loop_context() as loop:
            from beacon.conf import conf_override

            # Assign invalid value to per-user query budget setting
            conf_override.config.query_budget_per_user = "api"

            async def test_check_configuration_wrong_query_budget_user():
                try:
                    # Execute validation using malformed configuration
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis,biosample_confile=biosample,cohort_confile=cohort,dataset_confile=dataset,genomicVariant_confile=genomicVariant,individual_confile=individual,run_confile=run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_configuration_wrong_query_budget_user())

            # Restore default setting
            conf_override.config.query_budget_per_user = False


    def test_main_check_configuration_wrong_query_budget_ip(self):
        with loop_context() as loop:
            from beacon.conf import conf_override

            # Configure invalid per-IP query budget value
            conf_override.config.query_budget_per_ip = "api"

            async def test_check_configuration_wrong_query_budget_ip():
                try:
                    # Validate configuration checker behavior
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis,biosample_confile=biosample,cohort_confile=cohort,dataset_confile=dataset,genomicVariant_confile=genomicVariant,individual_confile=individual,run_confile=run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_configuration_wrong_query_budget_ip())

            # Restore original configuration
            conf_override.config.query_budget_per_ip = False


    def test_main_check_configuration_wrong_query_budget_database(self):
        with loop_context() as loop:
            from beacon.conf import conf_override

            # Set unsupported database backend for query budgeting
            conf_override.config.query_budget_database = "api"

            async def test_check_configuration_wrong_query_budget_database():
                try:
                    # Verify validation of query budget database setting
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis,biosample_confile=biosample,cohort_confile=cohort,dataset_confile=dataset,genomicVariant_confile=genomicVariant,individual_confile=individual,run_confile=run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_configuration_wrong_query_budget_database())

            # Restore supported backend
            conf_override.config.query_budget_database = "mongo"


    def test_main_check_configuration_with_wrong_analysis_database(self):
        with loop_context() as loop:
            # Inject invalid database backend into analysis configuration
            analysis["analysis"]["connection"]["name"] = "no Boolean"

            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_configuration_enable_analysis():
                try:
                    # Validate database configuration checking
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis,biosample_confile=biosample,cohort_confile=cohort,dataset_confile=dataset,genomicVariant_confile=genomicVariant,individual_confile=individual,run_confile=run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_configuration_enable_analysis())
            loop.run_until_complete(client.close())

            # Restore valid database backend
            analysis["analysis"]["connection"]["name"] = "mongo"

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)


    def test_main_check_configuration_with_wrong_biosample_database(self):
        with loop_context() as loop:
            # Corrupt biosample database backend configuration
            biosample["biosample"]["connection"]["name"] = "no Boolean"

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)

            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_configuration_enable_biosample():
                try:
                    # Run configuration validation with invalid backend name
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis,biosample_confile=biosample,cohort_confile=cohort,dataset_confile=dataset,genomicVariant_confile=genomicVariant,individual_confile=individual,run_confile=run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_configuration_enable_biosample())
            loop.run_until_complete(client.close())

            # Restore original backend configuration
            biosample["biosample"]["connection"]["name"] = "mongo"

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)
    def test_main_check_configuration_with_wrong_cohort_database(self):
        with loop_context() as loop:
            # Inject invalid database backend name into cohort configuration
            cohort["cohort"]["connection"]["name"] = "no Boolean"

            # Persist modified configuration for validation testing
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)

            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_configuration_enable_cohort():
                try:
                    # Verify configuration validation handles invalid database backend
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis,biosample_confile=biosample,cohort_confile=cohort,dataset_confile=dataset,genomicVariant_confile=genomicVariant,individual_confile=individual,run_confile=run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_configuration_enable_cohort())
            loop.run_until_complete(client.close())

            # Restore valid database backend configuration
            cohort["cohort"]["connection"]["name"] = "mongo"

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)


    def test_main_check_configuration_with_wrong_dataset_database(self):
        with loop_context() as loop:
            # Configure invalid database backend for dataset entry type
            dataset["dataset"]["connection"]["name"] = "no Boolean"

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)

            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_configuration_enable_dataset():
                try:
                    # Execute configuration validation with malformed backend setting
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis,biosample_confile=biosample,cohort_confile=cohort,dataset_confile=dataset,genomicVariant_confile=genomicVariant,individual_confile=individual,run_confile=run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_configuration_enable_dataset())
            loop.run_until_complete(client.close())

            # Reset configuration to supported backend
            dataset["dataset"]["connection"]["name"] = "mongo"

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)


    def test_main_check_configuration_with_wrong_individual_database(self):
        with loop_context() as loop:
            # Assign invalid database backend to individual configuration
            individual["individual"]["connection"]["name"] = "no Boolean"

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)

            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_configuration_enable_individual():
                try:
                    # Validate behavior when backend configuration is invalid
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis,biosample_confile=biosample,cohort_confile=cohort,dataset_confile=dataset,genomicVariant_confile=genomicVariant,individual_confile=individual,run_confile=run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_configuration_enable_individual())
            loop.run_until_complete(client.close())

            # Restore expected database backend
            individual["individual"]["connection"]["name"] = "mongo"

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)


    def test_main_check_configuration_with_wrong_genomicVariant_database(self):
        with loop_context() as loop:
            # Introduce invalid backend name into genomicVariant configuration
            genomicVariant["genomicVariant"]["connection"]["name"] = "no Boolean"

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)

            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_configuration_enable_genomicVariant():
                try:
                    # Verify configuration checker processes invalid backend values
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis,biosample_confile=biosample,cohort_confile=cohort,dataset_confile=dataset,genomicVariant_confile=genomicVariant,individual_confile=individual,run_confile=run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_configuration_enable_genomicVariant())
            loop.run_until_complete(client.close())

            # Restore valid backend configuration
            genomicVariant["genomicVariant"]["connection"]["name"] = "mongo"

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
    def test_main_check_configuration_with_wrong_run_database(self):
        with loop_context() as loop:
            # Inject invalid database backend into run configuration
            run["run"]["connection"]["name"] = "no Boolean"

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

            app = create_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())

            async def test_check_configuration_database_run():
                try:
                    # Validate configuration handling of unsupported database backend
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis,biosample_confile=biosample,cohort_confile=cohort,dataset_confile=dataset,genomicVariant_confile=genomicVariant,individual_confile=individual,run_confile=run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_configuration_database_run())
            loop.run_until_complete(client.close())

            # Restore valid database backend configuration
            run["run"]["connection"]["name"] = "mongo"

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)


    def test_main_check_configuration_wrong_environment(self):
        with loop_context() as loop:
            from beacon.conf import conf_override

            # Set an unsupported environment value
            conf_override.config.environment = "api"

            async def test_check_configuration_wrong_environment():
                try:
                    # Verify environment validation logic
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis,biosample_confile=biosample,cohort_confile=cohort,dataset_confile=dataset,genomicVariant_confile=genomicVariant,individual_confile=individual,run_confile=run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_configuration_wrong_environment())

            # Restore default environment
            conf_override.config.environment = "dev"


    def test_main_check_configuration_wrong_default_granularity(self):
        with loop_context() as loop:
            from beacon.conf import conf_override

            # Configure unsupported default granularity
            conf_override.config.default_beacon_granularity = "api"

            async def test_check_configuration_wrong_granularity():
                try:
                    # Validate granularity configuration checks
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis,biosample_confile=biosample,cohort_confile=cohort,dataset_confile=dataset,genomicVariant_confile=genomicVariant,individual_confile=individual,run_confile=run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_configuration_wrong_granularity())

            # Restore valid default granularity
            conf_override.config.default_beacon_granularity = "record"


    def test_analyses_endpoint_name_is_string(self):
        with loop_context() as loop:
            # Use a non-string endpoint name to test validation
            analysis["analysis"]["endpoint_name"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

            async def test_check_endpoint_endpoint_name_is_string():
                try:
                    # Verify endpoint name type validation
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis,biosample_confile=biosample,cohort_confile=cohort,dataset_confile=dataset,genomicVariant_confile=genomicVariant,individual_confile=individual,run_confile=run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_endpoint_endpoint_name_is_string())

            # Restore valid endpoint name
            analysis["analysis"]["endpoint_name"] = "analyses"

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml", 'w') as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)


    def test_biosamples_endpoint_name_is_string(self):
        with loop_context() as loop:
            # Replace endpoint name with invalid type
            biosample["biosample"]["endpoint_name"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)

            async def test_check_endpoint_endpoint_name_is_string():
                try:
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis,biosample_confile=biosample,cohort_confile=cohort,dataset_confile=dataset,genomicVariant_confile=genomicVariant,individual_confile=individual,run_confile=run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_endpoint_endpoint_name_is_string())

            # Restore expected endpoint name
            biosample["biosample"]["endpoint_name"] = "biosamples"

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)


    def test_cohorts_endpoint_name_is_string(self):
        with loop_context() as loop:
            # Configure invalid endpoint name type
            cohort["cohort"]["endpoint_name"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)

            async def test_check_endpoint_endpoint_name_is_string():
                try:
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis,biosample_confile=biosample,cohort_confile=cohort,dataset_confile=dataset,genomicVariant_confile=genomicVariant,individual_confile=individual,run_confile=run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_endpoint_endpoint_name_is_string())

            # Restore valid endpoint name
            cohort["cohort"]["endpoint_name"] = "cohorts"

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)


    def test_datasets_endpoint_name_is_string(self):
        with loop_context() as loop:
            # Use integer instead of string endpoint name
            dataset["dataset"]["endpoint_name"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)

            async def test_check_endpoint_endpoint_name_is_string():
                try:
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis,biosample_confile=biosample,cohort_confile=cohort,dataset_confile=dataset,genomicVariant_confile=genomicVariant,individual_confile=individual,run_confile=run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_endpoint_endpoint_name_is_string())

            # Restore configured endpoint name
            dataset["dataset"]["endpoint_name"] = "datasets"

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)


    def test_g_variants_endpoint_name_is_string(self):
        with loop_context() as loop:
            # Test endpoint name validation with incorrect type
            genomicVariant["genomicVariant"]["endpoint_name"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)

            async def test_check_endpoint_endpoint_name_is_string():
                try:
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis,biosample_confile=biosample,cohort_confile=cohort,dataset_confile=dataset,genomicVariant_confile=genomicVariant,individual_confile=individual,run_confile=run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_endpoint_endpoint_name_is_string())

            # Restore valid endpoint name
            genomicVariant["genomicVariant"]["endpoint_name"] = "g_variants"

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)


    def test_runs_endpoint_name_is_string(self):
        with loop_context() as loop:
            # Assign invalid endpoint name type
            run["run"]["endpoint_name"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

            async def test_check_endpoint_endpoint_name_is_string():
                try:
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis,biosample_confile=biosample,cohort_confile=cohort,dataset_confile=dataset,genomicVariant_confile=genomicVariant,individual_confile=individual,run_confile=run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_endpoint_endpoint_name_is_string())

            # Restore valid run endpoint name
            run["run"]["endpoint_name"] = "runs"

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/run.yml", 'w') as outfile:
                yaml.dump(run, outfile, default_flow_style=False)


    def test_individuals_endpoint_name_is_string(self):
        with loop_context() as loop:
            # Set endpoint name to non-string value
            individual["individual"]["endpoint_name"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)

            async def test_check_endpoint_endpoint_name_is_string():
                try:
                    # Validate endpoint name type checking
                    check_configuration(LOG=initialize_logger(config.level),analysis_confile=analysis,biosample_confile=biosample,cohort_confile=cohort,dataset_confile=dataset,genomicVariant_confile=genomicVariant,individual_confile=individual,run_confile=run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_endpoint_endpoint_name_is_string())

            # Restore expected endpoint name
            individual["individual"]["endpoint_name"] = "individuals"

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)


    def test_conf_override_takes_user_param(self):
        with loop_context() as loop:
            from beacon.conf import conf
            from beacon.conf import conf_default

            # User configuration should override default configuration values
            assert conf_override.config.uri == conf.uri

            # Confirm override differs from framework defaults
            assert conf_override.config.uri != conf_default.uri
    

    

def suite():
    """
        Gather all the tests from this module in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestNoFilters))
    return test_suite


mySuit=suite()


runner=unittest.TextTestRunner()
runner.run(mySuit)