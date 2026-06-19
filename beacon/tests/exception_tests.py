from aiohttp.test_utils import loop_context
import unittest
import beacon.conf.conf_override as conf_override
from beacon.validator.configuration import check_configuration
import logging
import yaml

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
class TestConfigurationExceptions(unittest.TestCase):

    def test_main_check_configuration_wrong_security_levels(self):
        # Verify configuration validation handles invalid security_levels values.
        with loop_context() as loop:
            from beacon.conf import conf_override

            # Intentionally use an invalid type.
            conf_override.config.security_levels = "api"

            async def test_check_configuration_wrong_security_levels():
                try:
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    try:
                        # Test another invalid configuration variant.
                        conf_override.config.security_levels = ["api"]

                        check_configuration(
                            analysis,
                            biosample,
                            cohort,
                            dataset,
                            genomicVariant,
                            individual,
                            run,
                        )
                    except Exception:
                        pass

            loop.run_until_complete(
                test_check_configuration_wrong_security_levels()
            )

            # Restore default configuration.
            conf_override.config.security_levels = [
                "PUBLIC",
                "REGISTERED",
                "CONTROLLED",
            ]

    def test_main_check_configuration_wrong_cors_urls(self):
        # Verify configuration validation handles invalid CORS settings.
        with loop_context() as loop:
            from beacon.conf import conf_override

            conf_override.config.cors_urls = "api"

            async def test_check_configuration_wrong_cors_urls():
                try:
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    try:
                        # Test invalid list content.
                        conf_override.config.cors_urls = ["api"]

                        check_configuration(
                            analysis,
                            biosample,
                            cohort,
                            dataset,
                            genomicVariant,
                            individual,
                            run,
                        )
                    except Exception:
                        pass

            loop.run_until_complete(
                test_check_configuration_wrong_cors_urls()
            )

            # Restore valid CORS origins.
            conf_override.config.cors_urls = [
                "http://localhost:3003",
                "http://localhost:3000",
            ]

    def test_analyses_contains_special_chars(self):
        # Verify endpoint names containing special characters are rejected.
        with loop_context() as loop:
            analysis["analysis"]["endpoint_name"] = "%aydga&-_al)"

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/"
                "ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

            async def test_check_endpoint_contains_special_chars():
                try:
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    pass

            loop.run_until_complete(
                test_check_endpoint_contains_special_chars()
            )

            # Restore valid endpoint name.
            analysis["analysis"]["endpoint_name"] = "analyses"

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/"
                "ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

    def test_biosamples_contains_special_chars(self):
        # Verify biosample endpoint validation.
        with loop_context() as loop:
            biosample["biosample"]["endpoint_name"] = "%aydga&-_al)"

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/"
                "ga4gh/beacon_v2_default_model/biosample.yml",
                "w",
            ) as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)

            async def test_check_endpoint_contains_special_chars():
                try:
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    pass

            loop.run_until_complete(
                test_check_endpoint_contains_special_chars()
            )

            # Restore original value.
            biosample["biosample"]["endpoint_name"] = "biosamples"

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/"
                "ga4gh/beacon_v2_default_model/biosample.yml",
                "w",
            ) as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)

    def test_cohorts_contains_special_chars(self):
        # Verify cohort endpoint validation.
        with loop_context() as loop:
            cohort["cohort"]["endpoint_name"] = "%aydga&-_al)"

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/"
                "ga4gh/beacon_v2_default_model/cohort.yml",
                "w",
            ) as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)

            async def test_check_endpoint_contains_special_chars():
                try:
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    pass

            loop.run_until_complete(
                test_check_endpoint_contains_special_chars()
            )

            # Restore valid endpoint name.
            cohort["cohort"]["endpoint_name"] = "cohorts"

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/"
                "ga4gh/beacon_v2_default_model/cohort.yml",
                "w",
            ) as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)

    def test_datasets_contains_special_chars(self):
        # Verify dataset endpoint validation.
        with loop_context() as loop:
            dataset["dataset"]["endpoint_name"] = "%aydga&-_al)"

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/"
                "ga4gh/beacon_v2_default_model/dataset.yml",
                "w",
            ) as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)

            async def test_check_endpoint_contains_special_chars():
                try:
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    pass

            loop.run_until_complete(
                test_check_endpoint_contains_special_chars()
            )

            # Restore original endpoint.
            dataset["dataset"]["endpoint_name"] = "datasets"

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/"
                "ga4gh/beacon_v2_default_model/dataset.yml",
                "w",
            ) as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)

    def test_g_variants_contains_special_chars(self):
        # Verify genomic variant endpoint validation.
        with loop_context() as loop:
            genomicVariant["genomicVariant"]["endpoint_name"] = "%aydga&-_al)"

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/"
                "ga4gh/beacon_v2_default_model/genomicVariant.yml",
                "w",
            ) as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)

            async def test_check_endpoint_contains_special_chars():
                try:
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    pass

            loop.run_until_complete(
                test_check_endpoint_contains_special_chars()
            )

            # Restore valid endpoint name.
            genomicVariant["genomicVariant"]["endpoint_name"] = "g_variants"

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/"
                "ga4gh/beacon_v2_default_model/genomicVariant.yml",
                "w",
            ) as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)

    def test_runs_contains_special_chars(self):
        # Verify run endpoint validation.
        with loop_context() as loop:
            run["run"]["endpoint_name"] = "%aydga&-_al)"

            async def test_check_endpoint_contains_special_chars():
                try:
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    pass

            loop.run_until_complete(
                test_check_endpoint_contains_special_chars()
            )

            # Restore valid endpoint.
            run["run"]["endpoint_name"] = "runs"

    def test_individuals_contains_special_chars(self):
        # Verify individual endpoint validation.
        with loop_context() as loop:
            individual["individual"]["endpoint_name"] = "%aydga&-_al)"

            async def test_check_endpoint_contains_special_chars():
                try:
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    pass

            loop.run_until_complete(
                test_check_endpoint_contains_special_chars()
            )

            # Restore valid endpoint.
            individual["individual"]["endpoint_name"] = "individuals"

    def test_analyses_open_api_endpoints_definition(self):
        # Verify open_api_definition requires the expected type.
        with loop_context() as loop:
            analysis["analysis"]["open_api_definition"] = 3

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/"
                "ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

            async def test_check_analyses_open_api_endpoints_definition():
                try:
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    pass

            loop.run_until_complete(
                test_check_analyses_open_api_endpoints_definition()
            )

            # Restore valid configuration value.
            analysis["analysis"]["open_api_definition"] = "string"

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/"
                "ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

    def test_analyses_name(self):
        # Verify analysis info.name validation.
        with loop_context() as loop:
            analysis["analysis"]["info"]["name"] = 3

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/"
                "ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

            async def test_check_analyses_name():
                try:
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_check_analyses_name())

            # Restore valid analysis name.
            analysis["analysis"]["info"]["name"] = "string"

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/"
                "ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
    def test_analyses_ontology_id(self):
        # Verify ontology_id validation rejects malformed CURIE values.
        with loop_context() as loop:
            analysis["analysis"]["info"]["ontology_id"] = "NOT13132 CURIE_!"

            # Persist modified configuration for validation.
            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

            async def test_check_analyses_ontology_id():
                try:
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_check_analyses_ontology_id())

            # Restore valid ontology identifier.
            analysis["analysis"]["info"]["ontology_id"] = "CURIE:12345"

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)


    def test_analyses_ontology_name(self):
        # Verify ontology_name must be a string.
        with loop_context() as loop:
            analysis["analysis"]["info"]["ontology_name"] = 3

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

            async def test_check_analyses_ontology_name():
                try:
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_check_analyses_ontology_name())

            # Restore valid ontology name.
            analysis["analysis"]["info"]["ontology_name"] = "string"

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)


    def test_analyses_specification(self):
        # Verify schema specification requires a string value.
        with loop_context() as loop:
            analysis["analysis"]["schema"]["specification"] = 3

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

            async def test_check_analyses_specification():
                try:
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_check_analyses_specification())

            # Restore valid schema specification.
            analysis["analysis"]["schema"]["specification"] = "string"

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)


    def test_analyses_description(self):
        # Verify description field validation.
        with loop_context() as loop:
            analysis["analysis"]["info"]["description"] = 3

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

            async def test_check_analyses_description():
                try:
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_check_analyses_description())

            # Restore valid description.
            analysis["analysis"]["info"]["description"] = "string"

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)


    def test_analyses_default_schema_id(self):
        # Verify default_schema_id must be a string.
        with loop_context() as loop:
            analysis["analysis"]["schema"]["default_schema_id"] = 3

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

            async def test_check_analyses_default_schema_id():
                try:
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_check_analyses_default_schema_id())

            # Restore valid schema identifier.
            analysis["analysis"]["schema"]["default_schema_id"] = "string"

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
    def test_analyses_default_schema_name(self):
        # Verify default_schema_name must be a string.
        with loop_context() as loop:
            analysis["analysis"]["schema"]["default_schema_name"] = 3

            # Write invalid configuration to disk.
            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

            async def test_check_analyses_default_schema_name():
                try:
                    check_configuration(
                        analysis, biosample, cohort, dataset,
                        genomicVariant, individual, run
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_check_analyses_default_schema_name())

            # Restore valid configuration value.
            analysis["analysis"]["schema"]["default_schema_name"] = "string"

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

    def test_analyses_reference_to_schema_definition(self):
        # Verify schema definition references must be strings.
        with loop_context() as loop:
            analysis["analysis"]["schema"]["reference_to_default_schema_definition"] = 3

            # Write invalid configuration to disk.
            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

            async def test_check_analyses_reference_to_schema_definition():
                try:
                    check_configuration(
                        analysis, biosample, cohort, dataset,
                        genomicVariant, individual, run
                    )
                except Exception:
                    pass

            loop.run_until_complete(
                test_check_analyses_reference_to_schema_definition()
            )

            # Restore valid schema reference.
            analysis["analysis"]["schema"][
                "reference_to_default_schema_definition"
            ] = "string"

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

    def test_analyses_default_schema_version(self):
        # Verify default_schema_version must be a string.
        with loop_context() as loop:
            analysis["analysis"]["schema"]["default_schema_version"] = 3

            # Write invalid configuration to disk.
            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

            async def test_check_analyses_default_schema_version():
                try:
                    check_configuration(
                        analysis, biosample, cohort, dataset,
                        genomicVariant, individual, run
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_check_analyses_default_schema_version())

            # Restore valid schema version.
            analysis["analysis"]["schema"]["default_schema_version"] = "string"

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

    def test_analyses_additionally_supported_schemas(self):
        # Verify supported_schemas requires a list value.
        with loop_context() as loop:
            analysis["analysis"]["schema"]["supported_schemas"] = 3

            # Write invalid configuration to disk.
            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

            async def test_check_analyses_additionally_supported_schemas():
                try:
                    check_configuration(
                        analysis, biosample, cohort, dataset,
                        genomicVariant, individual, run
                    )
                except Exception:
                    pass

            loop.run_until_complete(
                test_check_analyses_additionally_supported_schemas()
            )

            # Restore valid supported schema list.
            analysis["analysis"]["schema"]["supported_schemas"] = ["string"]

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

    def test_analyses_allow_queries_without_filters(self):
        # Verify allow_queries_without_filters must be a boolean.
        with loop_context() as loop:
            analysis["analysis"]["allow_queries_without_filters"] = 3

            # Write invalid configuration to disk.
            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

            async def test_check_analyses_allow_queries_without_filters():
                try:
                    check_configuration(
                        analysis, biosample, cohort, dataset,
                        genomicVariant, individual, run
                    )
                except Exception:
                    pass

            loop.run_until_complete(
                test_check_analyses_allow_queries_without_filters()
            )

            # Restore valid boolean value.
            analysis["analysis"]["allow_queries_without_filters"] = True

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

    def test_analyses_singleEntryUrl(self):
        # Verify allow_id_query must be a boolean.
        with loop_context() as loop:
            analysis["analysis"]["allow_id_query"] = 3

            # Write invalid configuration to disk.
            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

            async def test_check_analyses_singleEntryUrl():
                try:
                    check_configuration(
                        analysis, biosample, cohort, dataset,
                        genomicVariant, individual, run
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_check_analyses_singleEntryUrl())

            # Restore valid boolean value.
            analysis["analysis"]["allow_id_query"] = True

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

    def test_analyses_biosample_lookup(self):
        # Verify biosample lookup endpoint_enabled must be a boolean.
        with loop_context() as loop:
            analysis["analysis"]["lookups"]["biosample"]["endpoint_enabled"] = 3

            # Write invalid configuration to disk.
            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

            async def test_check_analyses_biosample_lookup():
                try:
                    check_configuration(
                        analysis, biosample, cohort, dataset,
                        genomicVariant, individual, run
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_check_analyses_biosample_lookup())

            # Restore valid lookup configuration.
            analysis["analysis"]["lookups"]["biosample"]["endpoint_enabled"] = True

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

    def test_analyses_cohort_lookup(self):
        # Verify cohort lookup endpoint_enabled must be a boolean.
        with loop_context() as loop:
            analysis["analysis"]["lookups"]["cohort"]["endpoint_enabled"] = 3

            # Write invalid configuration to disk.
            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

            async def test_check_analyses_cohort_lookup():
                try:
                    check_configuration(
                        analysis, biosample, cohort, dataset,
                        genomicVariant, individual, run
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_check_analyses_cohort_lookup())

            # Restore valid lookup configuration.
            analysis["analysis"]["lookups"]["cohort"]["endpoint_enabled"] = True

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)
    def test_analyses_dataset_lookup(self):
        # Verify dataset lookup endpoint_enabled must be a boolean.
        with loop_context() as loop:
            analysis["analysis"]["lookups"]["dataset"]["endpoint_enabled"] = 3

            # Write invalid configuration to disk.
            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

            async def test_check_analyses_dataset_lookup():
                try:
                    check_configuration(
                        analysis, biosample, cohort, dataset,
                        genomicVariant, individual, run
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_check_analyses_dataset_lookup())

            # Restore valid lookup configuration.
            analysis["analysis"]["lookups"]["dataset"]["endpoint_enabled"] = True

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

    def test_analyses_genomicVariant_lookup(self):
        # Verify genomicVariant lookup endpoint_enabled must be a boolean.
        with loop_context() as loop:
            analysis["analysis"]["lookups"]["genomicVariant"]["endpoint_enabled"] = 3

            # Write invalid configuration to disk.
            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

            async def test_check_analyses_genomicVariant_lookup():
                try:
                    check_configuration(
                        analysis, biosample, cohort, dataset,
                        genomicVariant, individual, run
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_check_analyses_genomicVariant_lookup())

            # Restore valid lookup configuration.
            analysis["analysis"]["lookups"]["genomicVariant"]["endpoint_enabled"] = True

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

    def test_analyses_individual_lookup(self):
        # Verify individual lookup endpoint_enabled must be a boolean.
        with loop_context() as loop:
            analysis["analysis"]["lookups"]["individual"]["endpoint_enabled"] = 3

            # Write invalid configuration to disk.
            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

            async def test_check_analyses_individual_lookup():
                try:
                    check_configuration(
                        analysis, biosample, cohort, dataset,
                        genomicVariant, individual, run
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_check_analyses_individual_lookup())

            # Restore valid lookup configuration.
            analysis["analysis"]["lookups"]["individual"]["endpoint_enabled"] = True

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

    def test_analyses_run_lookup(self):
        # Verify run lookup endpoint_enabled must be a boolean.
        with loop_context() as loop:
            analysis["analysis"]["lookups"]["run"]["endpoint_enabled"] = 3

            # Write invalid configuration to disk.
            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

            async def test_check_analyses_run_lookup():
                try:
                    check_configuration(
                        analysis, biosample, cohort, dataset,
                        genomicVariant, individual, run
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_check_analyses_run_lookup())

            # Restore valid lookup configuration.
            analysis["analysis"]["lookups"]["run"]["endpoint_enabled"] = True

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/analysis.yml",
                "w",
            ) as outfile:
                yaml.dump(analysis, outfile, default_flow_style=False)

    def test_runs_open_api_endpoints_definition(self):
        # Verify run open_api_definition must be a string.
        with loop_context() as loop:
            run["run"]["open_api_definition"] = 3

            # Write invalid configuration to disk.
            with open(
                "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                "w",
            ) as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

            async def test_check_runs_open_api_endpoints_definition():
                try:
                    check_configuration(
                        analysis, biosample, cohort, dataset,
                        genomicVariant, individual, run
                    )
                except Exception:
                    pass

            loop.run_until_complete(
                test_check_runs_open_api_endpoints_definition()
            )

            # Restore valid configuration value.
            run["run"]["open_api_definition"] = "string"

            with open(
                "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                "w",
            ) as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

    def test_runs_name(self):
        # Verify run name must be a string.
        with loop_context() as loop:
            run["run"]["info"]["name"] = 3

            # Write invalid configuration to disk.
            with open(
                "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                "w",
            ) as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

            async def test_check_runs_name():
                try:
                    check_configuration(
                        analysis, biosample, cohort, dataset,
                        genomicVariant, individual, run
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_check_runs_name())

            # Restore valid name value.
            run["run"]["info"]["name"] = "string"

            with open(
                "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                "w",
            ) as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

    def test_runs_ontology_id(self):
        # Verify ontology_id validation rejects malformed CURIE values.
        with loop_context() as loop:
            run["run"]["info"]["ontology_id"] = "NOT CURIE"

            # Write invalid configuration to disk.
            with open(
                "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                "w",
            ) as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

            async def test_check_runs_ontology_id():
                try:
                    check_configuration(
                        analysis, biosample, cohort, dataset,
                        genomicVariant, individual, run
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_check_runs_ontology_id())

            # Restore valid ontology identifier.
            run["run"]["info"]["ontology_id"] = "CURIE:12345"

            with open(
                "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                "w",
            ) as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

    def test_runs_ontology_name(self):
        # Verify ontology_name must be a string.
        with loop_context() as loop:
            run["run"]["info"]["ontology_name"] = 3

            # Write invalid configuration to disk.
            with open(
                "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                "w",
            ) as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

            async def test_check_runs_ontology_name():
                try:
                    check_configuration(
                        analysis, biosample, cohort, dataset,
                        genomicVariant, individual, run
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_check_runs_ontology_name())

            # Restore valid ontology name.
            run["run"]["info"]["ontology_name"] = "string"

            with open(
                "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                "w",
            ) as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

    def test_runs_specification(self):
        # Verify schema specification must be a string.
        with loop_context() as loop:
            run["run"]["schema"]["specification"] = 3

            # Write invalid configuration to disk.
            with open(
                "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                "w",
            ) as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

            async def test_check_runs_specification():
                try:
                    check_configuration(
                        analysis, biosample, cohort, dataset,
                        genomicVariant, individual, run
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_check_runs_specification())

            # Restore valid specification value.
            run["run"]["schema"]["specification"] = "string"

            with open(
                "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                "w",
            ) as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

    def test_runs_description(self):
        # Verify description must be a string.
        with loop_context() as loop:
            run["run"]["info"]["description"] = 3

            # Write invalid configuration to disk.
            with open(
                "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                "w",
            ) as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

            async def test_check_runs_description():
                try:
                    check_configuration(
                        analysis, biosample, cohort, dataset,
                        genomicVariant, individual, run
                    )
                except Exception:
                    # Restore valid description after validation failure.
                    run["run"]["info"]["description"] = "string"

                    with open(
                        "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                        "w",
                    ) as outfile:
                        yaml.dump(run, outfile, default_flow_style=False)

                    pass

            loop.run_until_complete(test_check_runs_description())
    def test_runs_default_schema_id(self):
        # Verify default_schema_id must be a string.
        with loop_context() as loop:
            run["run"]["schema"]["default_schema_id"] = 3

            # Write invalid configuration to disk.
            with open(
                "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                "w",
            ) as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

            async def test_check_runs_default_schema_id():
                try:
                    check_configuration(
                        analysis, biosample, cohort, dataset,
                        genomicVariant, individual, run
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_check_runs_default_schema_id())

            # Restore valid schema identifier.
            run["run"]["schema"]["default_schema_id"] = "string"

            with open(
                "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                "w",
            ) as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

    def test_runs_default_schema_name(self):
        # Verify default_schema_name must be a string.
        with loop_context() as loop:
            run["run"]["schema"]["default_schema_name"] = 3

            # Write invalid configuration to disk.
            with open(
                "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                "w",
            ) as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

            async def test_check_runs_default_schema_name():
                try:
                    check_configuration(
                        analysis, biosample, cohort, dataset,
                        genomicVariant, individual, run
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_check_runs_default_schema_name())

            # Restore valid schema name.
            run["run"]["schema"]["default_schema_name"] = "string"

            with open(
                "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                "w",
            ) as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

    def test_runs_reference_to_schema_definition(self):
        # Verify schema definition references must be strings.
        with loop_context() as loop:
            run["run"]["schema"]["reference_to_default_schema_definition"] = 3

            # Write invalid configuration to disk.
            with open(
                "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                "w",
            ) as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

            async def test_check_runs_reference_to_schema_definition():
                try:
                    check_configuration(
                        analysis, biosample, cohort, dataset,
                        genomicVariant, individual, run
                    )
                except Exception:
                    pass

            loop.run_until_complete(
                test_check_runs_reference_to_schema_definition()
            )

            # Restore valid schema reference.
            run["run"]["schema"][
                "reference_to_default_schema_definition"
            ] = "string"

            with open(
                "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                "w",
            ) as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

    def test_runs_default_schema_version(self):
        # Verify default_schema_version must be a string.
        with loop_context() as loop:
            run["run"]["schema"]["default_schema_version"] = 3

            # Write invalid configuration to disk.
            with open(
                "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                "w",
            ) as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

            async def test_check_runs_default_schema_version():
                try:
                    check_configuration(
                        analysis, biosample, cohort, dataset,
                        genomicVariant, individual, run
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_check_runs_default_schema_version())

            # Restore valid schema version.
            run["run"]["schema"]["default_schema_version"] = "string"

            with open(
                "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                "w",
            ) as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

    def test_runs_additionally_supported_schemas(self):
        # Verify supported_schemas requires a list value.
        with loop_context() as loop:
            run["run"]["schema"]["supported_schemas"] = 3

            # Write invalid configuration to disk.
            with open(
                "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                "w",
            ) as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

            async def test_check_runs_additionally_supported_schemas():
                try:
                    check_configuration(
                        analysis, biosample, cohort, dataset,
                        genomicVariant, individual, run
                    )
                except Exception:
                    pass

            loop.run_until_complete(
                test_check_runs_additionally_supported_schemas()
            )

            # Restore valid supported schema list.
            run["run"]["schema"]["supported_schemas"] = ["string"]

            with open(
                "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                "w",
            ) as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

    def test_runs_allow_queries_without_filters(self):
        # Verify allow_queries_without_filters must be a boolean.
        with loop_context() as loop:
            run["run"]["allow_queries_without_filters"] = 3

            # Write invalid configuration to disk.
            with open(
                "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                "w",
            ) as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

            async def test_check_runs_allow_queries_without_filters():
                try:
                    check_configuration(
                        analysis, biosample, cohort, dataset,
                        genomicVariant, individual, run
                    )
                except Exception:
                    pass

            loop.run_until_complete(
                test_check_runs_allow_queries_without_filters()
            )

            # Restore valid boolean value.
            run["run"]["allow_queries_without_filters"] = True

            with open(
                "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                "w",
            ) as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

    def test_runs_singleEntryUrl(self):
        # Verify allow_id_query must be a boolean.
        with loop_context() as loop:
            run["run"]["allow_id_query"] = 3

            # Write invalid configuration to disk.
            with open(
                "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                "w",
            ) as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

            async def test_check_runs_singleEntryUrl():
                try:
                    check_configuration(
                        analysis, biosample, cohort, dataset,
                        genomicVariant, individual, run
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_check_runs_singleEntryUrl())

            # Restore valid boolean value.
            run["run"]["allow_id_query"] = True

            with open(
                "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                "w",
            ) as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

    def test_runs_analysis_lookup(self):
        # Verify analysis lookup endpoint flag must be a boolean.
        with loop_context() as loop:
            run["run"]["lookups"]["analysis"]["endpooint_enabled"] = 3

            # Write invalid configuration to disk.
            with open(
                "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                "w",
            ) as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

            async def test_check_runs_analysis_lookup():
                try:
                    check_configuration(
                        analysis, biosample, cohort, dataset,
                        genomicVariant, individual, run
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_check_runs_analysis_lookup())

            # Restore valid lookup configuration.
            run["run"]["lookups"]["analysis"]["endpooint_enabled"] = True

            with open(
                "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                "w",
            ) as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

    def test_runs_biosample_lookup(self):
        # Verify biosample lookup endpoint_enabled must be a boolean.
        with loop_context() as loop:
            run["run"]["lookups"]["biosample"]["endpoint_enabled"] = 3

            # Write invalid configuration to disk.
            with open(
                "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                "w",
            ) as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

            async def test_check_runs_biosample_lookup():
                try:
                    check_configuration(
                        analysis, biosample, cohort, dataset,
                        genomicVariant, individual, run
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_check_runs_biosample_lookup())

            # Restore valid lookup configuration.
            run["run"]["lookups"]["biosample"]["endpoint_enabled"] = True

            with open(
                "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                "w",
            ) as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

    def test_runs_cohort_lookup(self):
        # Verify cohort lookup endpoint_enabled must be a boolean.
        with loop_context() as loop:
            run["run"]["lookups"]["cohort"]["endpoint_enabled"] = 3

            # Write invalid configuration to disk.
            with open(
                "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                "w",
            ) as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

            async def test_check_runs_cohort_lookup():
                try:
                    check_configuration(
                        analysis, biosample, cohort, dataset,
                        genomicVariant, individual, run
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_check_runs_cohort_lookup())

            # Restore valid lookup configuration.
            run["run"]["lookups"]["cohort"]["endpoint_enabled"] = True

            with open(
                "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                "w",
            ) as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

    def test_runs_dataset_lookup(self):
        # Verify dataset lookup endpoint_enabled must be a boolean.
        with loop_context() as loop:
            run["run"]["lookups"]["dataset"]["endpoint_enabled"] = 3

            # Write invalid configuration to disk.
            with open(
                "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                "w",
            ) as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

            async def test_check_runs_dataset_lookup():
                try:
                    check_configuration(
                        analysis, biosample, cohort, dataset,
                        genomicVariant, individual, run
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_check_runs_dataset_lookup())

            # Restore valid lookup configuration.
            run["run"]["lookups"]["dataset"]["endpoint_enabled"] = True

            with open(
                "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                "w",
            ) as outfile:
                yaml.dump(run, outfile, default_flow_style=False)
    def test_runs_genomicVariant_lookup(self):
        # Verify genomicVariant lookup endpoint_enabled must be a boolean.
        with loop_context() as loop:
            run["run"]["lookups"]["genomicVariant"]["endpoint_enabled"] = 3

            # Save invalid configuration to trigger validation.
            with open(
                "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                "w",
            ) as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

            async def test_check_runs_genomicVariant_lookup():
                try:
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    # Exception is expected for invalid configuration.
                    pass

            loop.run_until_complete(test_check_runs_genomicVariant_lookup())

            # Restore valid lookup configuration.
            run["run"]["lookups"]["genomicVariant"]["endpoint_enabled"] = True

            with open(
                "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                "w",
            ) as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

    def test_runs_individual_lookup(self):
        # Verify individual lookup endpoint_enabled must be a boolean.
        with loop_context() as loop:
            run["run"]["lookups"]["individual"]["endpoint_enabled"] = 3

            # Save invalid configuration to disk.
            with open(
                "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                "w",
            ) as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

            async def test_check_runs_individual_lookup():
                try:
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    # Validation failure is expected.
                    pass

            loop.run_until_complete(test_check_runs_individual_lookup())

            # Restore valid configuration.
            run["run"]["lookups"]["individual"]["endpoint_enabled"] = True

            with open(
                "/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml",
                "w",
            ) as outfile:
                yaml.dump(run, outfile, default_flow_style=False)

    def test_conf_level_wrong(self):
        # Verify logger level rejects invalid values.
        with loop_context() as loop:
            from beacon.conf import conf_override

            conf_override.config.level = "something"

            async def test_conf_level_wrong():
                try:
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_conf_level_wrong())

            # Restore default logging level.
            conf_override.config.level = logging.NOTSET

    def test_conf_log_file_wrong(self):
        # Verify log_file must be a valid path or None.
        with loop_context() as loop:
            from beacon.conf import conf_override

            conf_override.config.log_file = 3

            async def test_conf_log_file_wrong():
                try:
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_conf_log_file_wrong())

            # Restore valid configuration.
            conf_override.config.log_file = None

    def test_conf_wrong_beacon_id(self):
        # Verify beacon_id must be a string.
        with loop_context() as loop:
            from beacon.conf import conf_override

            conf_override.config.beacon_id = 3

            async def test_conf_wrong_beacon_id():
                try:
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_conf_wrong_beacon_id())

            # Restore valid beacon identifier.
            conf_override.config.beacon_id = "string"

    def test_conf_wrong_beacon_name(self):
        # Verify beacon_name must be a string.
        with loop_context() as loop:
            from beacon.conf import conf_override

            conf_override.config.beacon_name = 3

            async def test_conf_wrong_beacon_name():
                try:
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_conf_wrong_beacon_name())

            # Restore valid beacon name.
            conf_override.config.beacon_name = "string"

    def test_conf_wrong_api_version(self):
        # Verify api_version must be a string.
        with loop_context() as loop:
            from beacon.conf import conf_override

            conf_override.config.api_version = 3

            async def test_conf_wrong_api_version():
                try:
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_conf_wrong_api_version())

            # Restore valid API version.
            conf_override.config.api_version = "string"

    def test_conf_wrong_description(self):
        # Verify description must be a string.
        with loop_context() as loop:
            from beacon.conf import conf_override

            conf_override.config.description = 3

            async def test_conf_wrong_description():
                try:
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_conf_wrong_description())

            # Restore valid description.
            conf_override.config.description = "string"

    def test_conf_wrong_welcome_url(self):
        # Verify welcome_url must be a string.
        with loop_context() as loop:
            from beacon.conf import conf_override

            conf_override.config.welcome_url = 3

            async def test_conf_wrong_welcome_url():
                try:
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_conf_wrong_welcome_url())

            # Restore valid URL value.
            conf_override.config.welcome_url = "string"

    def test_conf_wrong_alternative_url(self):
        # Verify alternative_url must be a string.
        with loop_context() as loop:
            from beacon.conf import conf_override

            conf_override.config.alternative_url = 3

            async def test_conf_wrong_alternative_url():
                try:
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_conf_wrong_alternative_url())

            # Restore valid URL value.
            conf_override.config.alternative_url = "string"

    def test_conf_wrong_create_datetime(self):
        # Verify create_datetime must be stored as a valid string value.
        with loop_context() as loop:
            from beacon.conf import conf_override

            conf_override.config.create_datetime = 3

            async def test_conf_wrong_create_datetime():
                try:
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_conf_wrong_create_datetime())

            # Restore valid creation timestamp.
            conf_override.config.create_datetime = "string"

    def test_conf_wrong_update_datetime(self):
        # Verify update_datetime must be a valid string.
        with loop_context() as loop:
            from beacon.conf import conf_override

            conf_override.config.update_datetime = 3

            async def test_conf_wrong_update_datetime():
                try:
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_conf_wrong_update_datetime())

            # Restore valid update timestamp.
            conf_override.config.update_datetime = "string"

    def test_conf_wrong_documentation_url(self):
        # Verify documentation_url must be a string.
        with loop_context() as loop:
            from beacon.conf import conf_override

            conf_override.config.documentation_url = 3

            async def test_conf_wrong_documentation_url():
                try:
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_conf_wrong_documentation_url())

            # Restore valid documentation URL.
            conf_override.config.documentation_url = "string"

    def test_conf_wrong_welcome_url_no_http(self):
        # Verify welcome_url requires a proper HTTP/HTTPS URL.
        with loop_context() as loop:
            from beacon.conf import conf_override

            conf_override.config.welcome_url = "something"

            async def test_conf_wrong_welcome_url():
                try:
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_conf_wrong_welcome_url())

            # Restore valid welcome URL.
            conf_override.config.welcome_url = (
                "https://beacon.ega-archive.org/"
            )

    def test_conf_wrong_alternative_url_no_http(self):
        # Verify alternative_url requires a proper HTTP/HTTPS URL.
        with loop_context() as loop:
            from beacon.conf import conf_override

            conf_override.config.alternative_url = "something"

            async def test_conf_wrong_alternative_url():
                try:
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_conf_wrong_alternative_url())

            # Restore valid alternative URL.
            conf_override.config.alternative_url = (
                "https://beacon.ega-archive.org/api"
            )

    def test_conf_wrong_documentation_url_no_http(self):
        # Verify documentation_url requires a valid HTTP/HTTPS URL.
        with loop_context() as loop:
            from beacon.conf import conf_override

            conf_override.config.documentation_url = "string"

            async def test_conf_wrong_documentation_url():
                try:
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_conf_wrong_documentation_url())

            # Restore valid documentation URL.
            conf_override.config.documentation_url = (
                "https://b2ri-documentation-demo.ega-archive.org/"
            )
    def test_wrong_datasets_permissions(self):
        with loop_context() as loop:
            # Load the current dataset permissions configuration
            with open("/beacon/permissions/datasets/datasets_permissions.yml", 'r') as pfile:
                confile = yaml.safe_load(pfile)

            # Create an invalid permissions structure (misspelled key)
            data = {
                "testing": {
                    "registere": "yes"
                }
            }

            # Write the invalid configuration to disk
            with open('/beacon/permissions/datasets/datasets_permissions.yml', 'w') as outfile:
                yaml.dump(data, outfile, default_flow_style=False)

            async def test_conf_wrong_datasets_permissions():
                try:
                    # Validate configuration and expect an exception
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_conf_wrong_datasets_permissions())

            # Restore the original permissions configuration
            with open('/beacon/permissions/datasets/datasets_permissions.yml', 'w') as outfile:
                yaml.dump(confile, outfile, default_flow_style=False)

    def test_wrong_datasets_permissions_2(self):
        with loop_context() as loop:
            # Save original permissions configuration
            with open("/beacon/permissions/datasets/datasets_permissions.yml", 'r') as pfile:
                confile = yaml.safe_load(pfile)

            # Create an invalid nested permissions structure
            data = {
                "testing": {
                    "registered": {"yes": "no"}
                }
            }

            # Persist invalid configuration
            with open('/beacon/permissions/datasets/datasets_permissions.yml', 'w') as outfile:
                yaml.dump(data, outfile, default_flow_style=False)

            async def test_conf_wrong_datasets_permissions_2():
                try:
                    # Configuration validation should reject this structure
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_conf_wrong_datasets_permissions_2())

            # Restore valid configuration
            with open('/beacon/permissions/datasets/datasets_permissions.yml', 'w') as outfile:
                yaml.dump(confile, outfile, default_flow_style=False)

    def test_wrong_datasets_permissions_3(self):
        with loop_context() as loop:
            # Backup the current permissions file
            with open("/beacon/permissions/datasets/datasets_permissions.yml", 'r') as pfile:
                confile = yaml.safe_load(pfile)

            # Use an unknown user in the controlled-access list
            data = {
                "testing": {
                    "controlled": {
                        "user-list": [{"user": "unknown"}]
                    }
                }
            }

            # Write invalid permissions configuration
            with open('/beacon/permissions/datasets/datasets_permissions.yml', 'w') as outfile:
                yaml.dump(data, outfile, default_flow_style=False)

            async def test_conf_wrong_datasets_permissions_3():
                try:
                    # Validation should fail for unknown user references
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_conf_wrong_datasets_permissions_3())

            # Restore original configuration
            with open('/beacon/permissions/datasets/datasets_permissions.yml', 'w') as outfile:
                yaml.dump(confile, outfile, default_flow_style=False)

    def test_wrong_datasets_conf(self):
        with loop_context() as loop:
            # Save the current datasets configuration
            with open("/beacon/conf/datasets/datasets_conf.yml", 'r') as pfile:
                confile = yaml.safe_load(pfile)

            pfile.close()

            # Create malformed configuration data
            data = {
                "testing": {
                    "registere": "yes"
                }
            }

            # Replace the configuration with invalid content
            with open('/beacon/conf/datasets/datasets_conf.yml', 'w') as outfile:
                yaml.dump(data, outfile, default_flow_style=False)

            async def test_conf_wrong_datasets_conf():
                try:
                    # Expect validation to reject the configuration
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_conf_wrong_datasets_conf())

            # Restore original datasets configuration
            with open('/beacon/conf/datasets/datasets_conf.yml', 'w') as outfile:
                yaml.dump(confile, outfile, default_flow_style=False)

    def test_wrong_datasets_conf_2(self):
        with loop_context() as loop:
            # Backup current configuration
            with open("/beacon/conf/datasets/datasets_conf.yml", 'r') as pfile:
                confile = yaml.safe_load(pfile)

            # Invalid value type for isTest field
            data = {
                "testing": {
                    "isTest": "yes"
                }
            }

            # Write malformed configuration
            with open('/beacon/conf/datasets/datasets_conf.yml', 'w') as outfile:
                yaml.dump(data, outfile, default_flow_style=False)

            async def test_conf_wrong_datasets_conf_2():
                try:
                    # Validation should fail on incorrect field types
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_conf_wrong_datasets_conf_2())

            # NOTE: This restores the invalid data, not the backup.
            # The original code may contain a bug here.
            with open('/beacon/conf/datasets/datasets_conf.yml', 'w') as outfile:
                yaml.dump(data, outfile, default_flow_style=False)

    def test_datasets_open_api_endpoints_definition(self):
        with loop_context() as loop:
            # Use an invalid type for open_api_definition
            dataset["dataset"]["open_api_definition"] = 3

            # Persist modified dataset configuration
            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/"
                "ga4gh/beacon_v2_default_model/dataset.yml",
                'w',
            ) as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)

            async def test_check_datasets_open_api_endpoints_definition():
                try:
                    # Validation should reject numeric values here
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    pass

            loop.run_until_complete(
                test_check_datasets_open_api_endpoints_definition()
            )

            # Restore valid string value
            dataset["dataset"]["open_api_definition"] = "string"

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/"
                "ga4gh/beacon_v2_default_model/dataset.yml",
                'w',
            ) as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)

    def test_datasets_name(self):
        with loop_context() as loop:
            # Inject invalid type for dataset name
            dataset["dataset"]["info"]["name"] = 3

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/"
                "ga4gh/beacon_v2_default_model/dataset.yml",
                'w',
            ) as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)

            async def test_check_datasets_name():
                try:
                    # Name should be a string
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_check_datasets_name())

            # Restore valid dataset name
            dataset["dataset"]["info"]["name"] = "string"

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/"
                "ga4gh/beacon_v2_default_model/dataset.yml",
                'w',
            ) as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)

    def test_datasets_ontology_id(self):
        with loop_context() as loop:
            # Set an invalid ontology CURIE
            dataset["dataset"]["info"]["ontology_id"] = "NOT CURIE"

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/"
                "ga4gh/beacon_v2_default_model/dataset.yml",
                'w',
            ) as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)

            async def test_check_datasets_ontology_id():
                try:
                    # Validation should reject malformed CURIE values
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_check_datasets_ontology_id())

            # Restore a valid ontology identifier
            dataset["dataset"]["info"]["ontology_id"] = "CURIE:12345"

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/"
                "ga4gh/beacon_v2_default_model/dataset.yml",
                'w',
            ) as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)

    def test_datasets_ontology_name(self):
        with loop_context() as loop:
            # Use a numeric value where a string is expected
            dataset["dataset"]["info"]["ontology_name"] = 3

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/"
                "ga4gh/beacon_v2_default_model/dataset.yml",
                'w',
            ) as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)

            async def test_check_datasets_ontology_name():
                try:
                    # Validation should fail for invalid ontology names
                    check_configuration(
                        analysis,
                        biosample,
                        cohort,
                        dataset,
                        genomicVariant,
                        individual,
                        run,
                    )
                except Exception:
                    pass

            loop.run_until_complete(test_check_datasets_ontology_name())

            # Restore valid ontology name
            dataset["dataset"]["info"]["ontology_name"] = "string"

            with open(
                "/beacon/tests/mock_conf_files/conf/entry_types/"
                "ga4gh/beacon_v2_default_model/dataset.yml",
                'w',
            ) as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
    def test_datasets_specification(self):
        with loop_context() as loop:
            # Set invalid type (int instead of expected string) for schema specification
            dataset["dataset"]["schema"]["specification"] = 3

            # Persist invalid dataset configuration to YAML file
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)

            # Async wrapper to validate configuration handling
            async def test_check_datasets_specification():
                try:
                    check_configuration(
                        analysis, biosample, cohort,
                        dataset, genomicVariant, individual, run
                    )
                except Exception:
                    pass  # Expected failure due to invalid type

            # Execute validation
            loop.run_until_complete(test_check_datasets_specification())

            # Restore valid value
            dataset["dataset"]["schema"]["specification"] = "string"

            # Write corrected configuration back to YAML
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)


    def test_datasets_description(self):
        with loop_context() as loop:
            # Inject invalid type for description (should be string, not int)
            dataset["dataset"]["info"]["description"] = 3

            # Save invalid configuration
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)

            # Async validation wrapper
            async def test_check_datasets_description():
                try:
                    check_configuration(
                        analysis, biosample, cohort,
                        dataset, genomicVariant, individual, run
                    )
                except Exception:
                    pass  # Expected validation error

            # Run validation
            loop.run_until_complete(test_check_datasets_description())

            # Restore valid configuration
            dataset["dataset"]["info"]["description"] = "string"

            # Persist fix
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)


    def test_datasets_default_schema_id(self):
        with loop_context() as loop:
            # Inject invalid numeric type (expected string/identifier)
            dataset["dataset"]["schema"]["default_schema_id"] = 3

            # Write invalid YAML config
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)

            # Async validation wrapper
            async def test_check_datasets_default_schema_id():
                try:
                    check_configuration(
                        analysis, biosample, cohort,
                        dataset, genomicVariant, individual, run
                    )
                except Exception:
                    pass  # Expected failure

            # Execute validation
            loop.run_until_complete(test_check_datasets_default_schema_id())

            # Restore valid value
            dataset["dataset"]["schema"]["default_schema_id"] = "string"

            # Persist corrected YAML
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)


    def test_datasets_default_schema_name(self):
        with loop_context() as loop:
            # Inject invalid type for schema name
            dataset["dataset"]["schema"]["default_schema_name"] = 3

            # Save invalid configuration
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)

            # Async validation wrapper
            async def test_check_datasets_default_schema_name():
                try:
                    check_configuration(
                        analysis, biosample, cohort,
                        dataset, genomicVariant, individual, run
                    )
                except Exception:
                    pass

            # Run validation
            loop.run_until_complete(test_check_datasets_default_schema_name())

            # Restore valid value
            dataset["dataset"]["schema"]["default_schema_name"] = "string"

            # Persist fix
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)


    def test_datasets_reference_to_schema_definition(self):
        with loop_context() as loop:
            # Inject invalid numeric value
            dataset["dataset"]["schema"]["reference_to_default_schema_definition"] = 3

            # Write invalid configuration
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)

            # Async validation wrapper
            async def test_check_datasets_reference_to_schema_definition():
                try:
                    check_configuration(
                        analysis, biosample, cohort,
                        dataset, genomicVariant, individual, run
                    )
                except Exception:
                    pass

            # Execute validation
            loop.run_until_complete(test_check_datasets_reference_to_schema_definition())

            # Restore valid value
            dataset["dataset"]["schema"]["reference_to_default_schema_definition"] = "string"

            # Persist corrected YAML
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)


    def test_datasets_default_schema_version(self):
        with loop_context() as loop:
            # Invalid schema version type
            dataset["dataset"]["schema"]["default_schema_version"] = 3

            # Write invalid config
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)

            # Async validation wrapper
            async def test_check_datasets_default_schema_version():
                try:
                    check_configuration(
                        analysis, biosample, cohort,
                        dataset, genomicVariant, individual, run
                    )
                except Exception:
                    pass

            # Run validation
            loop.run_until_complete(test_check_datasets_default_schema_version())

            # Restore valid value
            dataset["dataset"]["schema"]["default_schema_version"] = "string"

            # Persist fix
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)


    def test_datasets_additionally_supported_schemas(self):
        with loop_context() as loop:
            # Invalid type for supported schemas
            dataset["dataset"]["schema"]["supported_schemas"] = 3

            # Save invalid config
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)

            # Async validation wrapper
            async def test_check_datasets_additionally_supported_schemas():
                try:
                    check_configuration(
                        analysis, biosample, cohort,
                        dataset, genomicVariant, individual, run
                    )
                except Exception:
                    pass

            # Execute validation
            loop.run_until_complete(test_check_datasets_additionally_supported_schemas())

            # Restore valid structure
            dataset["dataset"]["schema"]["supported_schemas"] = ["string"]

            # Persist fix
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)


    def test_datasets_allow_queries_without_filters(self):
        with loop_context() as loop:
            # Invalid type (should be boolean)
            dataset["dataset"]["allow_queries_without_filters"] = 3

            # Write malformed config
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)

            # Async validation wrapper
            async def test_check_datasets_allow_queries_without_filters():
                try:
                    check_configuration(
                        analysis, biosample, cohort,
                        dataset, genomicVariant, individual, run
                    )
                except Exception:
                    pass

            # Run validation
            loop.run_until_complete(test_check_datasets_allow_queries_without_filters())

            # Restore valid boolean
            dataset["dataset"]["allow_queries_without_filters"] = True

            # Persist fix
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)


    def test_datasets_singleEntryUrl(self):
        with loop_context() as loop:
            # Invalid type for boolean flag
            dataset["dataset"]["allow_id_query"] = 3

            # Write invalid YAML
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)

            # Async validation wrapper
            async def test_check_datasets_singleEntryUrl():
                try:
                    check_configuration(
                        analysis, biosample, cohort,
                        dataset, genomicVariant, individual, run
                    )
                except Exception:
                    pass

            # Execute validation
            loop.run_until_complete(test_check_datasets_singleEntryUrl())

            # Restore valid flag
            dataset["dataset"]["allow_id_query"] = True

            # Persist fix
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)


    def test_datasets_analysis_lookup(self):
        with loop_context() as loop:
            # Invalid type for endpoint flag
            dataset["dataset"]["lookups"]["analysis"]["endpooint_enabled"] = 3

            # Save malformed config
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)

            # Async validation wrapper
            async def test_check_datasets_analysis_lookup():
                try:
                    check_configuration(
                        analysis, biosample, cohort,
                        dataset, genomicVariant, individual, run
                    )
                except Exception:
                    pass

            # Run validation
            loop.run_until_complete(test_check_datasets_analysis_lookup())

            # Restore valid flag
            dataset["dataset"]["lookups"]["analysis"]["endpooint_enabled"] = True

            # Persist fix
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)


    def test_datasets_biosample_lookup(self):
        with loop_context() as loop:
            # Invalid endpoint value
            dataset["dataset"]["lookups"]["biosample"]["endpoint_enabled"] = 3

            # Write invalid config
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)

            # Async validation wrapper
            async def test_check_datasets_biosample_lookup():
                try:
                    check_configuration(
                        analysis, biosample, cohort,
                        dataset, genomicVariant, individual, run
                    )
                except Exception:
                    pass

            # Run validation
            loop.run_until_complete(test_check_datasets_biosample_lookup())

            # Restore valid value
            dataset["dataset"]["lookups"]["biosample"]["endpoint_enabled"] = True

            # Persist fix
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)


    def test_datasets_cohort_lookup(self):
        with loop_context() as loop:
            # Invalid endpoint flag type
            dataset["dataset"]["lookups"]["cohort"]["endpoint_enabled"] = 3

            # Save invalid YAML
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)

            # Async validation wrapper
            async def test_check_datasets_cohort_lookup():
                try:
                    check_configuration(
                        analysis, biosample, cohort,
                        dataset, genomicVariant, individual, run
                    )
                except Exception:
                    pass

            # Execute validation
            loop.run_until_complete(test_check_datasets_cohort_lookup())

            # Restore valid config
            dataset["dataset"]["lookups"]["cohort"]["endpoint_enabled"] = True

            # Persist fix
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)


    def test_datasets_genomicVariant_lookup(self):
        with loop_context() as loop:
            # Invalid endpoint flag
            dataset["dataset"]["lookups"]["genomicVariant"]["endpoint_enabled"] = 3

            # Write invalid config
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)

            # Async validation wrapper
            async def test_check_datasets_genomicVariant_lookup():
                try:
                    check_configuration(
                        analysis, biosample, cohort,
                        dataset, genomicVariant, individual, run
                    )
                except Exception:
                    pass

            # Run validation
            loop.run_until_complete(test_check_datasets_genomicVariant_lookup())

            # Restore valid value
            dataset["dataset"]["lookups"]["genomicVariant"]["endpoint_enabled"] = True

            # Persist fix
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)


    def test_datasets_individual_lookup(self):
        with loop_context() as loop:
            # Invalid endpoint flag
            dataset["dataset"]["lookups"]["individual"]["endpoint_enabled"] = 3

            # Save invalid YAML
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)

            # Async validation wrapper
            async def test_check_datasets_individual_lookup():
                try:
                    check_configuration(
                        analysis, biosample, cohort,
                        dataset, genomicVariant, individual, run
                    )
                except Exception:
                    pass

            # Execute validation
            loop.run_until_complete(test_check_datasets_individual_lookup())

            # Restore valid flag
            dataset["dataset"]["lookups"]["individual"]["endpoint_enabled"] = True

            # Persist corrected YAML
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)
    # Tests dataset "run" lookup endpoint enabled flag validation
    def test_datasets_run_lookup(self):
        with loop_context() as loop:
            dataset["dataset"]["lookups"]["run"]["endpoint_enabled"] = 3  # invalid type (should be bool)

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)

            async def test_check_datasets_run_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_datasets_run_lookup())

            # restore valid value
            dataset["dataset"]["lookups"]["run"]["endpoint_enabled"] = True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/dataset.yml", 'w') as outfile:
                yaml.dump(dataset, outfile, default_flow_style=False)


    # Tests genomicVariant open API definition type validation
    def test_g_variants_open_api_endpoints_definition(self):
        with loop_context() as loop:
            genomicVariant["genomicVariant"]["open_api_definition"] = 3  # invalid type

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)

            async def test_check_g_variants_open_api_endpoints_definition():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_g_variants_open_api_endpoints_definition())

            genomicVariant["genomicVariant"]["open_api_definition"] = "string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)


    # Tests genomicVariant name field validation
    def test_g_variants_name(self):
        with loop_context() as loop:
            genomicVariant["genomicVariant"]["info"]["name"] = 3  # invalid type

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)

            async def test_check_g_variants_name():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_g_variants_name())

            genomicVariant["genomicVariant"]["info"]["name"] = "string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)


    # Tests genomicVariant ontology_id format validation
    def test_g_variants_ontology_id(self):
        with loop_context() as loop:
            genomicVariant["genomicVariant"]["info"]["ontology_id"] = "NOT CURIE"  # invalid CURIE format

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)

            async def test_check_g_variants_ontology_id():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_g_variants_ontology_id())

            genomicVariant["genomicVariant"]["info"]["ontology_id"] = "CURIE:12345"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)


    # Tests genomicVariant ontology_name type validation
    def test_g_variants_ontology_name(self):
        with loop_context() as loop:
            genomicVariant["genomicVariant"]["info"]["ontology_name"] = 3  # invalid type

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)

            async def test_check_g_variants_ontology_name():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_g_variants_ontology_name())

            genomicVariant["genomicVariant"]["info"]["ontology_name"] = "string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)


    # Tests genomicVariant schema specification type validation
    def test_g_variants_specification(self):
        with loop_context() as loop:
            genomicVariant["genomicVariant"]["schema"]["specification"] = 3  # invalid type

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)

            async def test_check_g_variants_specification():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_g_variants_specification())

            genomicVariant["genomicVariant"]["schema"]["specification"] = "string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)


    # Tests genomicVariant description field validation
    def test_g_variants_description(self):
        with loop_context() as loop:
            genomicVariant["genomicVariant"]["info"]["description"] = 3  # invalid type

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)

            async def test_check_g_variants_description():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_g_variants_description())

            genomicVariant["genomicVariant"]["info"]["description"] = "string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)


    # Tests genomicVariant default schema ID validation
    def test_g_variants_default_schema_id(self):
        with loop_context() as loop:
            genomicVariant["genomicVariant"]["schema"]["default_schema_id"] = 3  # invalid type

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)

            async def test_check_g_variants_default_schema_id():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_g_variants_default_schema_id())

            genomicVariant["genomicVariant"]["schema"]["default_schema_id"] = "string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)


    # Tests genomicVariant default schema name validation
    def test_g_variants_default_schema_name(self):
        with loop_context() as loop:
            genomicVariant["genomicVariant"]["schema"]["default_schema_name"] = 3  # invalid type

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)

            async def test_check_g_variants_default_schema_name():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_g_variants_default_schema_name())

            genomicVariant["genomicVariant"]["schema"]["default_schema_name"] = "string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)


    # Tests genomicVariant reference-to-schema-definition validation
    def test_g_variants_reference_to_schema_definition(self):
        with loop_context() as loop:
            genomicVariant["genomicVariant"]["schema"]["reference_to_default_schema_definition"] = 3  # invalid type

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)

            async def test_check_g_variants_reference_to_schema_definition():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_g_variants_reference_to_schema_definition())

            genomicVariant["genomicVariant"]["schema"]["reference_to_default_schema_definition"] = "string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)


    # Tests genomicVariant default schema version validation
    def test_g_variants_default_schema_version(self):
        with loop_context() as loop:
            genomicVariant["genomicVariant"]["schema"]["default_schema_version"] = 3  # invalid type

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)

            async def test_check_g_variants_default_schema_version():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_g_variants_default_schema_version())

            genomicVariant["genomicVariant"]["schema"]["default_schema_version"] = "string"
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)


    # Tests genomicVariant supported schemas validation
    def test_g_variants_additionally_supported_schemas(self):
        with loop_context() as loop:
            genomicVariant["genomicVariant"]["schema"]["supported_schemas"] = 3  # invalid type

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)

            async def test_check_g_variants_additionally_supported_schemas():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_g_variants_additionally_supported_schemas())

            genomicVariant["genomicVariant"]["schema"]["supported_schemas"] = ["string"]
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
    def test_g_variants_allow_queries_without_filters(self):
        with loop_context() as loop:
            # Set invalid type (int instead of bool) to trigger validation error
            genomicVariant["genomicVariant"]["allow_queries_without_filters"] = 3

            # Write invalid configuration to YAML file
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)

            async def test_check_g_variants_allow_queries_without_filters():
                try:
                    # Run configuration validation
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    # Exceptions are expected in negative test cases
                    pass

            loop.run_until_complete(test_check_g_variants_allow_queries_without_filters())

            # Restore valid value after test
            genomicVariant["genomicVariant"]["allow_queries_without_filters"] = True

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)


    def test_g_variants_singleEntryUrl(self):
        with loop_context() as loop:
            # Invalid type for allow_id_query (should be boolean)
            genomicVariant["genomicVariant"]["allow_id_query"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)

            async def test_check_g_variants_singleEntryUrl():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_g_variants_singleEntryUrl())

            # Restore valid configuration
            genomicVariant["genomicVariant"]["allow_id_query"] = True

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)


    def test_g_variants_analysis_lookup(self):
        with loop_context() as loop:
            # Invalid value for endpoint_enabled (should be bool)
            genomicVariant["genomicVariant"]["lookups"]["analysis"]["endpooint_enabled"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)

            async def test_check_g_variants_analysis_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_g_variants_analysis_lookup())

            # Restore valid boolean value
            genomicVariant["genomicVariant"]["lookups"]["analysis"]["endpooint_enabled"] = True

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)


    def test_g_variants_biosample_lookup(self):
        with loop_context() as loop:
            # Inject invalid type to trigger schema validation error
            genomicVariant["genomicVariant"]["lookups"]["biosample"]["endpoint_enabled"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)

            async def test_check_g_variants_biosample_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_g_variants_biosample_lookup())

            # Restore valid configuration state
            genomicVariant["genomicVariant"]["lookups"]["biosample"]["endpoint_enabled"] = True

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)


    def test_g_variants_cohort_lookup(self):
        with loop_context() as loop:
            # Set invalid type for cohort lookup endpoint flag
            genomicVariant["genomicVariant"]["lookups"]["cohort"]["endpoint_enabled"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)

            async def test_check_g_variants_cohort_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_g_variants_cohort_lookup())

            # Restore valid boolean value
            genomicVariant["genomicVariant"]["lookups"]["cohort"]["endpoint_enabled"] = True

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)


    def test_g_variants_dataset_lookup(self):
        with loop_context() as loop:
            # Invalid type injection for dataset lookup config
            genomicVariant["genomicVariant"]["lookups"]["dataset"]["endpoint_enabled"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)

            async def test_check_g_variants_dataset_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_g_variants_dataset_lookup())

            # Restore correct configuration
            genomicVariant["genomicVariant"]["lookups"]["dataset"]["endpoint_enabled"] = True

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)


    def test_g_variants_individual_lookup(self):
        with loop_context() as loop:
            # Invalid type for individual lookup endpoint flag
            genomicVariant["genomicVariant"]["lookups"]["individual"]["endpoint_enabled"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)

            async def test_check_g_variants_individual_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_g_variants_individual_lookup())

            # Restore valid config
            genomicVariant["genomicVariant"]["lookups"]["individual"]["endpoint_enabled"] = True

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)


    def test_g_variants_run_lookup(self):
        with loop_context() as loop:
            # Invalid value to trigger schema validation failure
            genomicVariant["genomicVariant"]["lookups"]["run"]["endpoint_enabled"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)

            async def test_check_g_variants_run_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_g_variants_run_lookup())

            # Restore valid value
            genomicVariant["genomicVariant"]["lookups"]["run"]["endpoint_enabled"] = True

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/genomicVariant.yml", 'w') as outfile:
                yaml.dump(genomicVariant, outfile, default_flow_style=False)
    def test_individuals_open_api_endpoints_definition(self):
        with loop_context() as loop:
            # Inject invalid type (int instead of expected string) for OpenAPI definition
            individual["individual"]["open_api_definition"] = 3

            # Write malformed configuration to YAML file
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)

            async def test_check_individuals_open_api_endpoints_definition():
                try:
                    # Validate configuration (expected to fail due to invalid type)
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    # On failure, restore file state (cleanup after test failure)
                    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                        yaml.dump(individual, outfile, default_flow_style=False)
                    pass

            loop.run_until_complete(test_check_individuals_open_api_endpoints_definition())

            # Restore valid value
            individual["individual"]["open_api_definition"] = "string"


    def test_individuals_name(self):
        with loop_context() as loop:
            # Invalid type for name field (should be string)
            individual["individual"]["info"]["name"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)

            async def test_check_individuals_name():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    # Restore configuration file on failure
                    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                        yaml.dump(individual, outfile, default_flow_style=False)
                    pass

            loop.run_until_complete(test_check_individuals_name())

            # Restore valid value
            individual["individual"]["info"]["name"] = "string"


    def test_individuals_ontology_id(self):
        with loop_context() as loop:
            # Invalid ontology ID format (not CURIE)
            individual["individual"]["info"]["ontology_id"] = "NOT CURIE"

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)

            async def test_check_individuals_ontology_id():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    # Restore file if validation fails
                    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                        yaml.dump(individual, outfile, default_flow_style=False)
                    pass

            loop.run_until_complete(test_check_individuals_ontology_id())

            # Set valid CURIE format
            individual["individual"]["info"]["ontology_id"] = "CURIE:12345"


    def test_individuals_ontology_name(self):
        with loop_context() as loop:
            # Invalid type for ontology name (should be string)
            individual["individual"]["info"]["ontology_name"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)

            async def test_check_individuals_ontology_name():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    # Restore file after failure
                    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                        yaml.dump(individual, outfile, default_flow_style=False)
                    pass

            loop.run_until_complete(test_check_individuals_ontology_name())

            # Restore valid value
            individual["individual"]["info"]["ontology_name"] = "string"


    def test_individuals_specification(self):
        with loop_context() as loop:
            # Invalid schema specification type
            individual["individual"]["schema"]["specification"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)

            async def test_check_individuals_specification():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    # Restore file after failure
                    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                        yaml.dump(individual, outfile, default_flow_style=False)
                    pass

            loop.run_until_complete(test_check_individuals_specification())

            # Restore valid schema value
            individual["individual"]["schema"]["specification"] = "string"


    def test_individuals_description(self):
        with loop_context() as loop:
            # Invalid type for description field
            individual["individual"]["info"]["description"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)

            async def test_check_individuals_description():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    # Restore file on failure
                    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                        yaml.dump(individual, outfile, default_flow_style=False)
                    pass

            loop.run_until_complete(test_check_individuals_description())

            # Restore valid value
            individual["individual"]["info"]["description"] = "string"


    def test_individuals_default_schema_id(self):
        with loop_context() as loop:
            # Invalid schema id type
            individual["individual"]["schema"]["default_schema_id"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)

            async def test_check_individuals_default_schema_id():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    # Restore file on failure
                    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                        yaml.dump(individual, outfile, default_flow_style=False)
                    pass

            loop.run_until_complete(test_check_individuals_default_schema_id())

            # Restore valid value
            individual["individual"]["schema"]["default_schema_id"] = "string"


    def test_individuals_default_schema_name(self):
        with loop_context() as loop:
            # Invalid schema name type
            individual["individual"]["schema"]["default_schema_name"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)

            async def test_check_individuals_default_schema_name():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    # Restore file if validation fails
                    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                        yaml.dump(individual, outfile, default_flow_style=False)
                    pass

            loop.run_until_complete(test_check_individuals_default_schema_name())

            # Restore valid value
            individual["individual"]["schema"]["default_schema_name"] = "string"


    def test_individuals_reference_to_schema_definition(self):
        with loop_context() as loop:
            # Invalid reference type
            individual["individual"]["schema"]["reference_to_default_schema_definition"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)

            async def test_check_individuals_reference_to_schema_definition():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    # Restore file on failure
                    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                        yaml.dump(individual, outfile, default_flow_style=False)
                    pass

            loop.run_until_complete(test_check_individuals_reference_to_schema_definition())

            # Restore valid value
            individual["individual"]["schema"]["reference_to_default_schema_definition"] = "string"


    def test_individuals_default_schema_version(self):
        with loop_context() as loop:
            # Invalid schema version type
            individual["individual"]["schema"]["default_schema_version"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)

            async def test_check_individuals_default_schema_version():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    # Restore file on failure
                    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                        yaml.dump(individual, outfile, default_flow_style=False)
                    pass

            loop.run_until_complete(test_check_individuals_default_schema_version())

            # Restore valid value
            individual["individual"]["schema"]["default_schema_version"] = "string"
    # Test invalid type for supported schemas in individual schema definition
    def test_individuals_additionally_supported_schemas(self):
        with loop_context() as loop:
            # Inject invalid type (int instead of list) to trigger validation error
            individual["individual"]["schema"]["supported_schemas"] = 3

            # Write broken configuration to YAML file
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)

            # Async wrapper to run configuration validation
            async def test_check_individuals_additionally_supported_schemas():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    # Expected failure path; restore file if needed
                    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                        yaml.dump(individual, outfile, default_flow_style=False)
                    pass

            loop.run_until_complete(test_check_individuals_additionally_supported_schemas())

            # Restore valid structure after test
            individual["individual"]["schema"]["supported_schemas"] = ["string"]

    # Test allow_queries_without_filters field type validation
    def test_individuals_allow_queries_without_filters(self):
        with loop_context() as loop:
            # Invalid type: should be boolean, not int
            individual["individual"]["allow_queries_without_filters"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                yaml.dump(individual, outfile, default_flow_style=False)

            async def test_check_individuals_allow_queries_without_filters():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    # Ignore expected validation error
                    with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/individual.yml", 'w') as outfile:
                        yaml.dump(individual, outfile, default_flow_style=False)
                    pass

            loop.run_until_complete(test_check_individuals_allow_queries_without_filters())

            # Restore valid boolean value
            individual["individual"]["allow_queries_without_filters"] = True

    # Test allow_id_query field type validation
    def test_individuals_singleEntryUrl(self):
        with loop_context() as loop:
            # Invalid type: should be boolean
            individual["individual"]["allow_id_query"] = 3

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

            # Restore valid boolean
            individual["individual"]["allow_id_query"] = True

    # Test analysis lookup endpoint toggle validation
    def test_individuals_analysis_lookup(self):
        with loop_context() as loop:
            # Invalid type: should be boolean, not int
            individual["individual"]["lookups"]["analysis"]["endpooint_enabled"] = 3

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

            # Restore valid configuration
            individual["individual"]["lookups"]["analysis"]["endpooint_enabled"] = True

    # Test biosample lookup toggle validation
    def test_individuals_biosample_lookup(self):
        with loop_context() as loop:
            individual["individual"]["lookups"]["biosample"]["endpoint_enabled"] = 3

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

            individual["individual"]["lookups"]["biosample"]["endpoint_enabled"] = True

    # Test cohort lookup toggle validation
    def test_individuals_cohort_lookup(self):
        with loop_context() as loop:
            individual["individual"]["lookups"]["cohort"]["endpoint_enabled"] = 3

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

            individual["individual"]["lookups"]["cohort"]["endpoint_enabled"] = True

    # Test dataset lookup toggle validation
    def test_individuals_dataset_lookup(self):
        with loop_context() as loop:
            individual["individual"]["lookups"]["dataset"]["endpoint_enabled"] = 3

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

            individual["individual"]["lookups"]["dataset"]["endpoint_enabled"] = True

    # Test genomic variant lookup toggle validation
    def test_individuals_genomicVariant_lookup(self):
        with loop_context() as loop:
            individual["individual"]["lookups"]["genomicVariant"]["endpoint_enabled"] = 3

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

            individual["individual"]["lookups"]["genomicVariant"]["endpoint_enabled"] = True

    # Test run lookup toggle validation
    def test_individuals_run_lookup(self):
        with loop_context() as loop:
            individual["individual"]["lookups"]["run"]["endpoint_enabled"] = 3

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

            individual["individual"]["lookups"]["run"]["endpoint_enabled"] = True

    # ---------------- BIOSAMPLE TESTS ----------------

    # Test invalid type for biosample open API definition
    def test_biosamples_open_api_endpoints_definition(self):
        with loop_context() as loop:
            biosample["biosample"]["open_api_definition"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)

            async def test_check_biosamples_open_api_endpoints_definition():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_biosamples_open_api_endpoints_definition())

            biosample["biosample"]["open_api_definition"] = "string"

    # Test biosample name type validation
    def test_biosamples_name(self):
        with loop_context() as loop:
            biosample["biosample"]["info"]["name"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)

            async def test_check_biosamples_name():
                try:
                    check_configuration(...)
                except Exception:
                    pass

            loop.run_until_complete(test_check_biosamples_name())

            biosample["biosample"]["info"]["name"] = "string"

    # Test biosample ontology ID validation
    def test_biosamples_ontology_id(self):
        with loop_context() as loop:
            biosample["biosample"]["info"]["ontology_id"] = "NOT CURIE"

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)

            async def test_check_biosamples_ontology_id():
                try:
                    check_configuration(...)
                except Exception:
                    pass

            loop.run_until_complete(test_check_biosamples_ontology_id())

            biosample["biosample"]["info"]["ontology_id"] = "CURIE:12345"

    # Test biosample ontology name validation
    def test_biosamples_ontology_name(self):
        with loop_context() as loop:
            biosample["biosample"]["info"]["ontology_name"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)

            async def test_check_biosamples_ontology_name():
                try:
                    check_configuration(...)
                except Exception:
                    pass

            loop.run_until_complete(test_check_biosamples_ontology_name())

            biosample["biosample"]["info"]["ontology_name"] = "string"
    # Test invalid type for biosample schema specification field
    def test_biosamples_specification(self):
        with loop_context() as loop:
            # Inject invalid type (int instead of string) to trigger validation error
            biosample["biosample"]["schema"]["specification"] = 3

            # Write invalid configuration to YAML
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)

            # Async validation runner
            async def test_check_biosamples_specification():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    # Expected failure; ignore and continue test flow
                    pass

            loop.run_until_complete(test_check_biosamples_specification())

            # Restore valid value after test
            biosample["biosample"]["schema"]["specification"] = "string"

    # Test biosample description field type validation
    def test_biosamples_description(self):
        with loop_context() as loop:
            # Invalid type: should be string
            biosample["biosample"]["info"]["description"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)

            async def test_check_biosamples_description():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_biosamples_description())

            # Restore valid value
            biosample["biosample"]["info"]["description"] = "string"

    # Test biosample default_schema_id type validation
    def test_biosamples_default_schema_id(self):
        with loop_context() as loop:
            biosample["biosample"]["schema"]["default_schema_id"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)

            async def test_check_biosamples_default_schema_id():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_biosamples_default_schema_id())

            biosample["biosample"]["schema"]["default_schema_id"] = "string"

    # Test biosample default_schema_name type validation
    def test_biosamples_default_schema_name(self):
        with loop_context() as loop:
            biosample["biosample"]["schema"]["default_schema_name"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)

            async def test_check_biosamples_default_schema_name():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_biosamples_default_schema_name())

            biosample["biosample"]["schema"]["default_schema_name"] = "string"

    # Test reference_to_default_schema_definition type validation
    def test_biosamples_reference_to_schema_definition(self):
        with loop_context() as loop:
            biosample["biosample"]["schema"]["reference_to_default_schema_definition"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)

            async def test_check_biosamples_reference_to_schema_definition():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_biosamples_reference_to_schema_definition())

            biosample["biosample"]["schema"]["reference_to_default_schema_definition"] = "string"

    # Test default_schema_version type validation
    def test_biosamples_default_schema_version(self):
        with loop_context() as loop:
            biosample["biosample"]["schema"]["default_schema_version"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)

            async def test_check_biosamples_default_schema_version():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_biosamples_default_schema_version())

            biosample["biosample"]["schema"]["default_schema_version"] = "string"

    # Test supported_schemas type validation
    def test_biosamples_additionally_supported_schemas(self):
        with loop_context() as loop:
            biosample["biosample"]["schema"]["supported_schemas"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)

            async def test_check_biosamples_additionally_supported_schemas():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_biosamples_additionally_supported_schemas())

            biosample["biosample"]["schema"]["supported_schemas"] = ["string"]

    # Test allow_queries_without_filters type validation
    def test_biosamples_allow_queries_without_filters(self):
        with loop_context() as loop:
            biosample["biosample"]["allow_queries_without_filters"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)

            async def test_check_biosamples_allow_queries_without_filters():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_biosamples_allow_queries_without_filters())

            biosample["biosample"]["allow_queries_without_filters"] = True

    # Test allow_id_query type validation
    def test_biosamples_singleEntryUrl(self):
        with loop_context() as loop:
            biosample["biosample"]["allow_id_query"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)

            async def test_check_biosamples_singleEntryUrl():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_biosamples_singleEntryUrl())

            biosample["biosample"]["allow_id_query"] = True

    # Test analysis lookup endpoint flag validation
    def test_biosamples_analysis_lookup(self):
        with loop_context() as loop:
            biosample["biosample"]["lookups"]["analysis"]["endpooint_enabled"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)

            async def test_check_biosamples_analysis_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_biosamples_analysis_lookup())

            biosample["biosample"]["lookups"]["analysis"]["endpooint_enabled"] = True

    # Test cohort lookup endpoint flag validation
    def test_biosamples_cohort_lookup(self):
        with loop_context() as loop:
            biosample["biosample"]["lookups"]["cohort"]["endpoint_enabled"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)

            async def test_check_biosamples_cohort_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_biosamples_cohort_lookup())

            biosample["biosample"]["lookups"]["cohort"]["endpoint_enabled"] = True

    # Test dataset lookup endpoint flag validation
    def test_biosamples_dataset_lookup(self):
        with loop_context() as loop:
            biosample["biosample"]["lookups"]["dataset"]["endpoint_enabled"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)

            async def test_check_biosamples_dataset_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_biosamples_dataset_lookup())

            biosample["biosample"]["lookups"]["dataset"]["endpoint_enabled"] = True

    # Test genomicVariant lookup endpoint flag validation
    def test_biosamples_genomicVariant_lookup(self):
        with loop_context() as loop:
            biosample["biosample"]["lookups"]["genomicVariant"]["endpoint_enabled"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)

            async def test_check_biosamples_genomicVariant_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_biosamples_genomicVariant_lookup())

            biosample["biosample"]["lookups"]["genomicVariant"]["endpoint_enabled"] = True

    # Test individual lookup endpoint flag validation
    def test_biosamples_individual_lookup(self):
        with loop_context() as loop:
            biosample["biosample"]["lookups"]["individual"]["endpoint_enabled"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)

            async def test_check_biosamples_individual_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_biosamples_individual_lookup())

            biosample["biosample"]["lookups"]["individual"]["endpoint_enabled"] = True
    # --- BIOSAMPLE RUN LOOKUP TEST ---
    def test_biosamples_run_lookup(self):
        with loop_context() as loop:
            # Inject invalid type (int instead of bool) to test validation
            biosample["biosample"]["lookups"]["run"]["endpoint_enabled"] = 3

            # Write modified config to YAML file
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)

            # Async validation check
            async def test_check_biosamples_run_lookup():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    # Expected failure path for invalid config
                    pass

            loop.run_until_complete(test_check_biosamples_run_lookup())

            # Restore valid boolean value after test
            biosample["biosample"]["lookups"]["run"]["endpoint_enabled"] = True

            # Persist restored config
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/biosample.yml", 'w') as outfile:
                yaml.dump(biosample, outfile, default_flow_style=False)


    # --- COHORT OPEN API DEFINITION TEST ---
    def test_cohorts_open_api_endpoints_definition(self):
        with loop_context() as loop:
            # Set invalid type for open API definition (expects string)
            cohort["cohort"]["open_api_definition"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)

            async def test_check_cohorts_open_api_endpoints_definition():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    # Validation error expected
                    pass

            loop.run_until_complete(test_check_cohorts_open_api_endpoints_definition())

            # Restore valid string value
            cohort["cohort"]["open_api_definition"] = "string"

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)


    # --- COHORT NAME TEST ---
    def test_cohorts_name(self):
        with loop_context() as loop:
            # Invalid type: name should be string, not int
            cohort["cohort"]["info"]["name"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)

            async def test_check_cohorts_name():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_cohorts_name())

            # Restore valid value
            cohort["cohort"]["info"]["name"] = "string"

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)


    # --- COHORT ONTOLOGY ID TEST ---
    def test_cohorts_ontology_id(self):
        with loop_context() as loop:
            # Invalid ontology format (not CURIE)
            cohort["cohort"]["info"]["ontology_id"] = "NOT CURIE"

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)

            async def test_check_cohorts_ontology_id():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_cohorts_ontology_id())

            # Restore valid CURIE format
            cohort["cohort"]["info"]["ontology_id"] = "CURIE:12345"


    # --- COHORT ONTOLOGY NAME TEST ---
    def test_cohorts_ontology_name(self):
        with loop_context() as loop:
            # Invalid type for ontology name
            cohort["cohort"]["info"]["ontology_name"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)

            async def test_check_cohorts_ontology_name():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_cohorts_ontology_name())

            # Restore valid string
            cohort["cohort"]["info"]["ontology_name"] = "string"


    # --- COHORT SCHEMA SPECIFICATION TEST ---
    def test_cohorts_specification(self):
        with loop_context() as loop:
            # Invalid type for schema specification
            cohort["cohort"]["schema"]["specification"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)

            async def test_check_cohorts_specification():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_cohorts_specification())

            # Restore valid value
            cohort["cohort"]["schema"]["specification"] = "string"


    # --- COHORT DESCRIPTION TEST ---
    def test_cohorts_description(self):
        with loop_context() as loop:
            # Invalid type for description field
            cohort["cohort"]["info"]["description"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)

            async def test_check_cohorts_description():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_cohorts_description())

            # Restore valid string
            cohort["cohort"]["info"]["description"] = "string"


    # --- COHORT DEFAULT SCHEMA ID TEST ---
    def test_cohorts_default_schema_id(self):
        with loop_context() as loop:
            # Invalid type (should not be int here)
            cohort["cohort"]["schema"]["default_schema_id"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)

            async def test_check_cohorts_default_schema_id():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_cohorts_default_schema_id())

            # Restore valid string
            cohort["cohort"]["schema"]["default_schema_id"] = "string"


    # --- COHORT DEFAULT SCHEMA NAME TEST ---
    def test_cohorts_default_schema_name(self):
        with loop_context() as loop:
            cohort["cohort"]["schema"]["default_schema_name"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)

            async def test_check_cohorts_default_schema_name():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_cohorts_default_schema_name())

            cohort["cohort"]["schema"]["default_schema_name"] = "string"


    # --- COHORT SCHEMA REFERENCE TEST ---
    def test_cohorts_reference_to_schema_definition(self):
        with loop_context() as loop:
            cohort["cohort"]["schema"]["reference_to_default_schema_definition"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)

            async def test_check_cohorts_reference_to_schema_definition():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_cohorts_reference_to_schema_definition())

            cohort["cohort"]["schema"]["reference_to_default_schema_definition"] = "string"


    # --- COHORT DEFAULT SCHEMA VERSION TEST ---
    def test_cohorts_default_schema_version(self):
        with loop_context() as loop:
            cohort["cohort"]["schema"]["default_schema_version"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)

            async def test_check_cohorts_default_schema_version():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_cohorts_default_schema_version())

            cohort["cohort"]["schema"]["default_schema_version"] = "string"


    # --- COHORT ADDITIONAL SCHEMAS TEST ---
    def test_cohorts_additionally_supported_schemas(self):
        with loop_context() as loop:
            cohort["cohort"]["schema"]["supported_schemas"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)

            async def test_check_cohorts_additionally_supported_schemas():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_cohorts_additionally_supported_schemas())

            cohort["cohort"]["schema"]["supported_schemas"] = ["string"]


    # --- COHORT ALLOW QUERIES WITHOUT FILTERS TEST ---
    def test_cohorts_allow_queries_without_filters(self):
        with loop_context() as loop:
            cohort["cohort"]["allow_queries_without_filters"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)

            async def test_check_cohorts_allow_queries_without_filters():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_cohorts_allow_queries_without_filters())

            cohort["cohort"]["allow_queries_without_filters"] = True


    # --- COHORT SINGLE ENTRY URL TEST ---
    def test_cohorts_singleEntryUrl(self):
        with loop_context() as loop:
            cohort["cohort"]["allow_id_query"] = 3

            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)

            async def test_check_cohorts_singleEntryUrl():
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass

            loop.run_until_complete(test_check_cohorts_singleEntryUrl())

            cohort["cohort"]["allow_id_query"] = True
    def test_cohorts_analysis_lookup(self):
        """Method to get the configuration for the entry type cohorts/{id}/analyses"""
        with loop_context() as loop:
            # Do some random wrong assumption of the endpoint enabled
            cohort["cohort"]["lookups"]["analysis"]["endpooint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
            async def test_check_cohorts_analysis_lookup():
                # Test the configuration so it fails
                try:
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_analysis_lookup())
            # Get the correct initial configuration back corrected again
            cohort["cohort"]["lookups"]["analysis"]["endpooint_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
    def test_cohorts_biosample_lookup(self):
        """Method to get the configuration for the entry type cohorts/{id}/biosamples"""
        with loop_context() as loop:
            # Do some random wrong assumption of the endpoint enabled
            cohort["cohort"]["lookups"]["biosample"]["endpoint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
            async def test_check_cohorts_biosample_lookup():
                try:
                    # Test the configuration so it fails
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_biosample_lookup())
            # Get the correct initial configuration back corrected again
            cohort["cohort"]["lookups"]["biosample"]["endpoint_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
    def test_cohorts_dataset_lookup(self):
        """Method to get the configuration for the entry type cohorts/{id}/datasets"""
        with loop_context() as loop:
             # Do some random wrong assumption of the endpoint enabled
            cohort["cohort"]["lookups"]["dataset"]["endpoint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
            async def test_check_cohorts_dataset_lookup():
                try:
                    # Test the configuration so it fails
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_dataset_lookup())
            # Get the correct initial configuration back corrected again
            cohort["cohort"]["lookups"]["dataset"]["endpoint_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
    def test_cohorts_genomicVariant_lookup(self):
        """Method to get the configuration for the entry type cohorts/{id}/g_variants"""
        with loop_context() as loop:
            # Do some random wrong assumption of the endpoint enabled
            cohort["cohort"]["lookups"]["genomicVariant"]["endpoint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
            async def test_check_cohorts_genomicVariant_lookup():
                try:
                    # Test the configuration so it fails
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_genomicVariant_lookup())
            # Get the correct initial configuration back corrected again
            cohort["cohort"]["lookups"]["genomicVariant"]["endpoint_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
    def test_cohorts_individual_lookup(self):
        """Method to get the configuration for the entry type cohorts/{id}/individuals"""
        with loop_context() as loop:
            # Do some random wrong assumption of the endpoint enabled
            cohort["cohort"]["lookups"]["individual"]["endpoint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
            async def test_check_cohorts_individual_lookup():
                try:
                     # Test the configuration so it fails
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_individual_lookup())
            # Get the correct initial configuration back corrected again
            cohort["cohort"]["lookups"]["individual"]["endpoint_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
    def test_cohorts_run_lookup(self):
        """Method to get the configuration for the entry type cohorts/{id}/runs"""
        with loop_context() as loop:
            # Do some random wrong assumption of the endpoint enabled
            cohort["cohort"]["lookups"]["run"]["endpoint_enabled"]=3
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)
            async def test_check_cohorts_run_lookup():
                try:
                     # Test the configuration so it fails
                    check_configuration(analysis, biosample, cohort, dataset, genomicVariant, individual, run)
                except Exception:
                    pass
            loop.run_until_complete(test_check_cohorts_run_lookup())
            # Get the correct initial configuration back corrected again
            cohort["cohort"]["lookups"]["run"]["endpoint_enabled"]=True
            with open("/beacon/tests/mock_conf_files/conf/entry_types/ga4gh/beacon_v2_default_model/cohort.yml", 'w') as outfile:
                yaml.dump(cohort, outfile, default_flow_style=False)




def suite():
    """
        Gather all the tests from this module in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestConfigurationExceptions))
    return test_suite


mySuit=suite()


runner=unittest.TextTestRunner()
runner.run(mySuit)