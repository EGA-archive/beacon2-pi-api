from beacon.conf import conf_override
from beacon.logs.logs import log_with_args_check_configuration
import os
import re
import logging
import yaml
from beacon.models.ga4gh.beacon_v2_default_model.connections.mongo.utils import import_dataset_confile, import_analysis_confile, import_biosample_confile, import_cohort_confile, import_individual_confile, import_genomicVariant_confile, import_run_confile
import datetime
import time

# Create the regex pattern to validate the timestamps received
timestamp_regex = re.compile(r"^.+(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})")

def contains_special_characters(string):
    """Check if a string contains special characters (chars that are not digit, alphanumeric values or spaces)"""
    for char in string:
        if char == '_':
            pass
        elif not (char.isdigit() or char.isalpha() or char == ' '):
            return True
    return False

# 
def check_logs_configuration():
    """Check that the configuration of the logs is correct and doesn't contain meaningless values"""
    # Stdout the name of the function that is being initialized and the datetime because this is run before the logger initializes
    print('DEBUG - {}Z - {} - initial call'.format(datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3], check_logs_configuration.__name__), flush=True)
    # Get the time in counter format so we can now when we started the operation
    start = time.perf_counter()
    # Go over the level variable in configuration to see if the values are correct
    if conf_override.config.level not in [logging.NOTSET, logging.INFO, logging.DEBUG, logging.WARNING, logging.ERROR, logging.FATAL, logging.CRITICAL]:
        raise Exception('The config parameter level must be one possible logging library level (NOTSET, DEBUG, INFO, etc...')
    # Check that the log_file variable is a stringl, otherwise raise an exception
    if not isinstance(conf_override.config.log_file, str):
        if conf_override.config.log_file != None:
            raise Exception('The config parameter log_file must be a string with the path to the dir where to store the logs or a variable None for not storing any log')
    # Get the time in counter format so we can now when we finished the operation
    finish = time.perf_counter()
    # Stdout the name of the function that just finished and the datetime because this is run before the logger initializes
    print('DEBUG - {}Z - {} - {}s - returned OK'.format(datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3], check_logs_configuration.__name__, round(finish-start,3)), flush=True)

@log_with_args_check_configuration(conf_override.config.level)
def check_configuration(
    LOG=None,
    analysis_confile=import_analysis_confile(),
    biosample_confile=import_biosample_confile(),
    cohort_confile=import_cohort_confile(),
    dataset_confile=import_dataset_confile(),
    genomicVariant_confile=import_genomicVariant_confile(),
    individual_confile=import_individual_confile(),
    run_confile=import_run_confile()
):

    # -------------------------------------------------------------------------
    # Entry type enablement validation
    # Ensure that the "entry_type_enabled" flag is explicitly configured as a
    # boolean value for every supported Beacon entity.
    # -------------------------------------------------------------------------

    if isinstance(analysis_confile["analysis"]["entry_type_enabled"], bool):
        pass
    else:
        raise Exception(
            "{}.enable_endpoint variable from {}.py must be boolean".format(
                'analysis', 'analysis'
            )
        )

    if isinstance(biosample_confile["biosample"]["entry_type_enabled"], bool):
        pass
    else:
        raise Exception(
            "{}.enable_endpoint variable from {}.py must be boolean".format(
                'biosample', 'biosample'
            )
        )

    if isinstance(cohort_confile["cohort"]["entry_type_enabled"], bool):
        pass
    else:
        raise Exception(
            "{}.enable_endpoint variable from {}.py must be boolean".format(
                'cohort', 'cohort'
            )
        )

    if isinstance(dataset_confile["dataset"]["entry_type_enabled"], bool):
        pass
    else:
        raise Exception(
            "{}.enable_endpoint variable from {}.py must be boolean".format(
                'dataset', 'dataset'
            )
        )

    if isinstance(genomicVariant_confile["genomicVariant"]["entry_type_enabled"], bool):
        pass
    else:
        raise Exception(
            "{}.enable_endpoint variable from {}.py must be boolean".format(
                'genomicVariant', 'genomicVariant'
            )
        )

    if isinstance(individual_confile["individual"]["entry_type_enabled"], bool):
        pass
    else:
        raise Exception(
            "{}.enable_endpoint variable from {}.py must be boolean".format(
                'individual', 'individual'
            )
        )

    if isinstance(run_confile["run"]["entry_type_enabled"], bool):
        pass
    else:
        raise Exception(
            "{}.enable_endpoint variable from {}.py must be boolean".format(
                'run', 'run'
            )
        )

    # -------------------------------------------------------------------------
    # Endpoint granularity validation
    # Validate that enabled endpoints only use Beacon-supported granularity
    # levels: boolean, count or record.
    # -------------------------------------------------------------------------

    if (
        analysis_confile["analysis"]["endpoint_name"] != ''
        and analysis_confile["analysis"]["max_granularity"]
        not in ['boolean', 'count', 'record']
    ):
        raise Exception(
            "analysis granularity must be one string between boolean, count or record"
        )

    if (
        biosample_confile["biosample"]["endpoint_name"] != ''
        and biosample_confile["biosample"]["max_granularity"]
        not in ['boolean', 'count', 'record']
    ):
        raise Exception(
            "biosample granularity must be one string between boolean, count or record"
        )

    if (
        cohort_confile["cohort"]["endpoint_name"] != ''
        and cohort_confile["cohort"]["max_granularity"]
        not in ['boolean', 'count', 'record']
    ):
        raise Exception(
            "cohort granularity must be one string between boolean, count or record"
        )

    if (
        dataset_confile["dataset"]["endpoint_name"] != ''
        and dataset_confile["dataset"]["max_granularity"]
        not in ['boolean', 'count', 'record']
    ):
        raise Exception(
            "dataset granularity must be one string between boolean, count or record"
        )

    if (
        genomicVariant_confile["genomicVariant"]["endpoint_name"] != ''
        and genomicVariant_confile["genomicVariant"]["max_granularity"]
        not in ['boolean', 'count', 'record']
    ):
        raise Exception(
            "genomicVariant granularity must be one string between boolean, count or record"
        )

    if (
        individual_confile["individual"]["endpoint_name"] != ''
        and individual_confile["individual"]["max_granularity"]
        not in ['boolean', 'count', 'record']
    ):
        raise Exception(
            "individual granularity must be one string between boolean, count or record"
        )

    if (
        run_confile["run"]["endpoint_name"] != ''
        and run_confile["run"]["max_granularity"]
        not in ['boolean', 'count', 'record']
    ):
        raise Exception(
            "run granularity must be one string between boolean, count or record"
        )

    # -------------------------------------------------------------------------
    # Beacon URI validation
    # Verify that the public Beacon URL follows the expected format and
    # encourage HTTPS usage whenever possible.
    # -------------------------------------------------------------------------

    if conf_override.config.uri.startswith('http://'):
        LOG.warning(
            'The uri of your beacon is not https. Please change to https as soon as you can.'
        )
    elif conf_override.config.uri.startswith('https://'):
        pass
    else:
        raise Exception(
            "The uri of your beacon must start with https protocol."
        )

    # Trailing slashes are forbidden to avoid URL composition issues.
    if conf_override.config.uri.endswith('/'):
        raise Exception("The uri can't end with trailing slash /")

    # Validate optional URI subpath configuration.
    if conf_override.config.uri_subpath.endswith('/'):
        raise Exception(
            "The uri_subpath can't end with trailing slash /, leave it empty if you don't want to add any subpath."
        )

    # URI subpaths must always begin with a slash.
    if conf_override.config.uri_subpath.startswith('/'):
        pass
    else:
        raise Exception(
            "The uri_subpath has to start with slash /."
        )

    # -------------------------------------------------------------------------
    # Query budget and rate-limiting validation
    # Ensure that throttling parameters are correctly defined before startup.
    # -------------------------------------------------------------------------

    if (
        not isinstance(conf_override.config.query_budget_amount, int)
        or conf_override.config.query_budget_amount < 0
    ):
        raise Exception(
            "The amount of query budget attempts allowed must be a natural number."
        )

    if (
        not isinstance(conf_override.config.query_budget_time_in_seconds, int)
        or conf_override.config.query_budget_time_in_seconds < 0
    ):
        raise Exception(
            "The rate of query time in seconds for the budget must be a natural number."
        )

    # Validate user-based rate limiting configuration.
    if not isinstance(conf_override.config.query_budget_per_user, bool):
        raise Exception(
            "The query budget per user parameter must be boolean."
        )

    # Validate IP-based rate limiting configuration.
    if not isinstance(conf_override.config.query_budget_per_ip, bool):
        raise Exception(
            "The query budget per ip parameter must be boolean."
        )

    # -------------------------------------------------------------------------
    # Database backend validation
    # Verify that every configured backend corresponds to an existing
    # connection implementation under /beacon/connections.
    # -------------------------------------------------------------------------

    if conf_override.config.query_budget_database not in [
        name
        for name in os.listdir("/beacon/connections")
        if os.path.isdir(os.path.join("/beacon/connections", name))
    ]:
        raise Exception(
            'The database {} for budget needs to match a directory name in the beacon/connections folder'.format(
                conf_override.config.query_budget_database
            )
        )

    # Validate the configured backend for run records.
    if run_confile["run"]["connection"]["name"] not in [
        name
        for name in os.listdir("/beacon/connections")
        if os.path.isdir(os.path.join("/beacon/connections", name))
    ]:
        raise Exception(
            'The database {} for run records needs to match a directory name in the beacon/connections folder'.format(
                run_confile["run"]["connection"]["name"]
            )
        )

    # Validate the configured backend for individual records.
    if individual_confile["individual"]["connection"]["name"] not in [
        name
        for name in os.listdir("/beacon/connections")
        if os.path.isdir(os.path.join("/beacon/connections", name))
    ]:
        raise Exception(
            'The database {} for individual records needs to match a directory name in the beacon/connections folder'.format(
                individual_confile["individual"]["connection"]["name"]
            )
        )

    # Additional backend validations follow the same pattern for
    # genomicVariant, dataset, cohort, biosample and analysis entities.

    # -------------------------------------------------------------------------
    # Environment and security configuration validation
    # Ensure deployment mode and security settings are supported.
    # -------------------------------------------------------------------------

    if conf_override.config.environment not in [
        'dev', 'test', 'prod',
        'DEV', 'TEST', 'PROD'
    ]:
        raise Exception(
            'The environment variable in conf must be one between test, dev, prod'
        )

    if conf_override.config.default_beacon_granularity not in [
        'boolean',
        'count',
        'record'
    ]:
        raise Exception(
            "Configuration parameter default_beacon_granularity must be one string between boolean, count or record"
        )

    # Security levels must be defined as a list.
    if not isinstance(conf_override.config.security_levels, list):
        raise Exception(
            "Configuration parameter security_levels must be of type array"
        )

    # Validate each declared security level.
    for security_level in conf_override.config.security_levels:
        if security_level not in ['PUBLIC', 'REGISTERED', 'CONTROLLED']:
            raise Exception(
                "Security levels can only have PUBLIC, REGISTERED or CONTROLLED level."
            )

    # -------------------------------------------------------------------------
    # CORS configuration validation
    # Verify that all allowed origins are provided as valid HTTP/HTTPS URLs.
    # -------------------------------------------------------------------------

    if not isinstance(conf_override.config.cors_urls, list):
        raise Exception(
            "Configuration parameter cors_urls must be of type array"
        )

    for cors_url in conf_override.config.cors_urls:
        if not cors_url.startswith('http://'):
            if not cors_url.startswith('https://'):
                raise Exception(
                    'The url {} in cors_urls variable must start with http protocol'.format(
                        cors_url
                    )
                )
    # -------------------------------------------------------------------------
    # Endpoint name validation
    # Validate that all endpoint names are strings and only contain
    # supported characters. Endpoint names are used to generate routes,
    # therefore special characters are not allowed.
    # -------------------------------------------------------------------------

    if not isinstance(run_confile["run"]["endpoint_name"], str):
        raise Exception('The run_confile["run"]["endpoint_name"] variable must be of type string')
    if contains_special_characters(run_confile["run"]["endpoint_name"]):
        raise Exception('The run_confile["run"]["endpoint_name"] variable can not have special characters')

    if not isinstance(individual_confile["individual"]["endpoint_name"], str):
        raise Exception('The individual_confile["individual"]["endpoint_name"] variable must be of type string')
    if contains_special_characters(individual_confile["individual"]["endpoint_name"]):
        raise Exception('The individual_confile["individual"]["endpoint_name"] variable can not have special characters')

    if not isinstance(genomicVariant_confile["genomicVariant"]["endpoint_name"], str):
        raise Exception('The genomicVariant_confile["genomicVariant"]["endpoint_name"] variable must be of type string')
    if contains_special_characters(genomicVariant_confile["genomicVariant"]["endpoint_name"]):
        raise Exception('The genomicVariant_confile["genomicVariant"]["endpoint_name"] variable can not have special characters')

    if not isinstance(dataset_confile["dataset"]["endpoint_name"], str):
        raise Exception('The dataset_confile["dataset"]["endpoint_name"] variable must be of type string')
    if contains_special_characters(dataset_confile["dataset"]["endpoint_name"]):
        raise Exception('The dataset_confile["dataset"]["endpoint_name"] variable can not have special characters')

    if not isinstance(cohort_confile["cohort"]["endpoint_name"], str):
        raise Exception('The cohort_confile["cohort"]["endpoint_name"] variable must be of type string')
    if contains_special_characters(cohort_confile["cohort"]["endpoint_name"]):
        raise Exception('The cohort_confile["cohort"]["endpoint_name"] variable can not have special characters')

    if not isinstance(biosample_confile["biosample"]["endpoint_name"], str):
        raise Exception('The biosample_confile["biosample"]["endpoint_name"] variable must be of type string')
    if contains_special_characters(biosample_confile["biosample"]["endpoint_name"]):
        raise Exception('The biosample_confile["biosample"]["endpoint_name"] variable can not have special characters')

    if not isinstance(analysis_confile["analysis"]["endpoint_name"], str):
        raise Exception('The analysis_confile["analysis"]["endpoint_name"] variable must be of type string')
    if contains_special_characters(analysis_confile["analysis"]["endpoint_name"]):
        raise Exception('The analysis_confile["analysis"]["endpoint_name"] variable can not have special characters')

    # -------------------------------------------------------------------------
    # Analysis configuration validation
    # Verify that the analysis entry type contains all mandatory Beacon
    # metadata fields, schema definitions and query configuration flags.
    # -------------------------------------------------------------------------

    if not isinstance(analysis_confile["analysis"]["open_api_definition"], str):
        raise Exception('The analysis open_api_definition must be of type string.')

    # Ensure the configuration root key matches the expected entry type.
    if 'analysis' not in analysis_confile:
        raise Exception('The analysis id variable must be analysis_confile')

    # Validate ontology metadata used to describe the entry type.
    if not isinstance(analysis_confile["analysis"]["info"]["name"], str):
        raise Exception('The analysis info name must be of type string.')

    # Ontology identifiers must follow CURIE notation.
    if not isinstance(analysis_confile["analysis"]["info"]["ontology_id"], str) or not re.match("[A-Za-z0-9]+:[A-Za-z0-9]", analysis_confile["analysis"]["info"]["ontology_id"]):
        raise Exception('The analysis ["info"]["ontology_id"] must be of type string and CURIE.')

    if not isinstance(analysis_confile["analysis"]["info"]["ontology_name"], str):
        raise Exception('The analysis ["info"]["ontology_name"] must be of type string.')

    # Validate schema definition metadata.
    if not isinstance(analysis_confile["analysis"]["schema"]["specification"], str):
        raise Exception('The analysis schema ["schema"]["specification"] must be of type string.')

    if not isinstance(analysis_confile["analysis"]["info"]["description"], str):
        raise Exception('The analysis description must be of type string.')

    if not isinstance(analysis_confile["analysis"]["schema"]["default_schema_id"], str):
        raise Exception('The analysis default_schema_id must be of type string.')

    if not isinstance(analysis_confile["analysis"]["schema"]["default_schema_name"], str):
        raise Exception('The analysis default_schema_name must be of type string.')

    if not isinstance(analysis_confile["analysis"]["schema"]["reference_to_default_schema_definition"], str):
        raise Exception('The analysis reference_to_default_schema_definition must be of type string.')

    if not isinstance(analysis_confile["analysis"]["schema"]["default_schema_version"], str):
        raise Exception('The analysis_confile["analysis"]["schema"]["default_schema_version"] must be of type string.')

    # Multiple schemas can be supported by the same entry type.
    if not isinstance(analysis_confile["analysis"]["schema"]["supported_schemas"], list):
        raise Exception('The analysis supported_schemas must be of type list.')

    # Validate query behaviour configuration.
    if not isinstance(analysis_confile["analysis"]["allow_queries_without_filters"], bool):
        raise Exception('The analysis allow_queries_without_filters must be of type bool.')

    if not isinstance(analysis_confile["analysis"]["allow_id_query"], bool):
        raise Exception('The analysis allow id query must be of type bool.')

    # -------------------------------------------------------------------------
    # Biosample configuration validation
    # Apply the same metadata, ontology and schema checks to the
    # biosample entry type configuration.
    # -------------------------------------------------------------------------

    if not isinstance(biosample_confile["biosample"]["open_api_definition"], str):
        raise Exception('The biosample_confile["cohort"]["open_api_definition"] must be of type string.')

    if 'biosample' not in biosample_confile:
        raise Exception('The biosample_confileid variable must be biosample_confile')

    if not isinstance(biosample_confile["biosample"]["info"]["name"], str):
        raise Exception('The biosample_confile["biosample"]["info"]["name"] must be of type string.')

    # Validate CURIE-compliant ontology identifier.
    if not isinstance(biosample_confile["biosample"]["info"]["ontology_id"], str) or not re.match("[A-Za-z0-9]+:[A-Za-z0-9]", biosample_confile["biosample"]["info"]["ontology_id"]):
        raise Exception('The biosample_confile["biosample"]["info"]["ontology_id"] must be of type string and CURIE.')

    if not isinstance(biosample_confile["biosample"]["info"]["ontology_name"], str):
        raise Exception('The biosample_confile["biosample"]["info"]["ontology_name"] must be of type string.')

    if not isinstance(biosample_confile["biosample"]["schema"]["specification"], str):
        raise Exception('The biosample_confile["biosample"]["schema"]["specification"] must be of type string.')

    if not isinstance(biosample_confile["biosample"]["info"]["description"], str):
        raise Exception('The biosample_confile["biosample"]["info"]["description"] must be of type string.')

    # Validate default schema metadata.
    if not isinstance(biosample_confile["biosample"]["schema"]["default_schema_id"], str):
        raise Exception('The biosample_confile["biosample"]["schema"]["default_schema_id"] must be of type string.')

    if not isinstance(biosample_confile["biosample"]["schema"]["default_schema_name"], str):
        raise Exception('The biosample_confile["biosample"]["schema"]["default_schema_name"] must be of type string.')

    if not isinstance(biosample_confile["biosample"]["schema"]["reference_to_default_schema_definition"], str):
        raise Exception('The biosample_confile["biosample"]["schema"]["reference_to_default_schema_definition"] must be of type string.')

    if not isinstance(biosample_confile["biosample"]["schema"]["default_schema_version"], str):
        raise Exception('The biosample_confile["biosample"]["schema"]["default_schema_version"] must be of type string.')

    if not isinstance(biosample_confile["biosample"]["schema"]["supported_schemas"], list):
        raise Exception('The biosample_confile["biosample"]["schema"]["supported_schemas"] must be of type list.')

    # Validate query permissions for this entry type.
    if not isinstance(biosample_confile["biosample"]["allow_queries_without_filters"], bool):
        raise Exception('The biosample_confile["analysis"]["allow_queries_without_filters"] must be of type bool.')

    if not isinstance(biosample_confile["biosample"]["allow_id_query"], bool):
        raise Exception('The biosample_confile["analysis"]["allow_id_query"] must be of type bool.')

    # -------------------------------------------------------------------------
    # Cohort configuration validation
    # Repeat the same consistency checks for cohort metadata,
    # schema definitions and query options.
    # -------------------------------------------------------------------------

    if not isinstance(cohort_confile["cohort"]["open_api_definition"], str):
        raise Exception('The cohort_confile["cohort"]["open_api_definition"] must be of type string.')

    if 'cohort' not in cohort_confile:
        raise Exception('The cohort_confileid variable must be cohort_confile')

    if not isinstance(cohort_confile["cohort"]["info"]["name"], str):
        raise Exception('The cohort_confile["cohort"]["info"]["name"] must be of type string.')

    # Cohort ontology identifiers must use CURIE format.
    if not isinstance(cohort_confile["cohort"]["info"]["ontology_id"], str) or not re.match("[A-Za-z0-9]+:[A-Za-z0-9]", cohort_confile["cohort"]["info"]["ontology_id"]):
        raise Exception('The cohort_confile["cohort"]["info"]["ontology_id"] must be of type string and CURIE.')

    # Validate cohort ontology name
    if not isinstance(cohort_confile["cohort"]["info"]["ontology_name"], str):
        raise Exception('The cohort_confile["cohort"]["info"]["ontology_name"] must be of type string.')

    # Validate cohort schema specification URL/reference
    if not isinstance(cohort_confile["cohort"]["schema"]["specification"], str):
        raise Exception('The cohort_confile["cohort"]["schema"]["specification"] must be of type string.')

    # Validate cohort description
    if not isinstance(cohort_confile["cohort"]["info"]["description"], str):
        raise Exception('The cohort_confile["cohort"]["info"]["description"] must be of type string.')

    # Validate cohort default schema ID
    if not isinstance(cohort_confile["cohort"]["schema"]["default_schema_id"], str):
        raise Exception('The cohort_confile["cohort"]["schema"]["default_schema_id"] must be of type string.')

    # Validate cohort default schema name
    if not isinstance(cohort_confile["cohort"]["schema"]["default_schema_name"], str):
        raise Exception('The cohort_confile["cohort"]["schema"]["default_schema_name"] must be of type string.')

    # Validate cohort schema definition reference
    if not isinstance(cohort_confile["cohort"]["schema"]["reference_to_default_schema_definition"], str):
        raise Exception('The cohort_confile["cohort"]["schema"]["reference_to_default_schema_definition"] must be of type string.')

    # Validate cohort schema version
    if not isinstance(cohort_confile["cohort"]["schema"]["default_schema_version"], str):
        raise Exception('The cohort_confile["cohort"]["schema"]["default_schema_version"] must be of type string.')

    # Supported schemas must be provided as a list
    if not isinstance(cohort_confile["cohort"]["schema"]["supported_schemas"], list):
        raise Exception('The cohort_confile["cohort"]["schema"]["supported_schemas"] must be of type list.')

    # Check cohort query configuration flags
    if not isinstance(cohort_confile["cohort"]["allow_queries_without_filters"], bool):
        raise Exception('The cohort_confile["analysis"]["allow_queries_without_filters"] must be of type bool.')

    if not isinstance(cohort_confile["cohort"]["allow_id_query"], bool):
        raise Exception('The cohort_confile["analysis"]["allow_id_query"] must be of type bool.')

    # Validate dataset OpenAPI definition path/reference
    if not isinstance(dataset_confile["dataset"]["open_api_definition"], str):
        raise Exception('The dataset_confile["cohort"]["open_api_definition"] must be of type string.')

    # Dataset root key must exist
    if 'dataset' not in dataset_confile:
        raise Exception('The dataset_confileid variable must be dataset_confile')

    # Dataset display name validation
    if not isinstance(dataset_confile["dataset"]["info"]["name"], str):
        raise Exception('The dataset_confilename must be of type string.')

    # Dataset ontology identifier must be CURIE compliant
    if not isinstance(dataset_confile["dataset"]["info"]["ontology_id"], str) or not re.match(
            "[A-Za-z0-9]+:[A-Za-z0-9]",
            dataset_confile["dataset"]["info"]["ontology_id"]):
        raise Exception('The dataset_confile["dataset"]["info"]["ontology_id"] must be of type string and CURIE.')

    # Dataset ontology name validation
    if not isinstance(dataset_confile["dataset"]["info"]["ontology_name"], str):
        raise Exception('The dataset_confile["dataset"]["info"]["ontology_name"] must be of type string.')

    # Dataset schema specification validation
    if not isinstance(dataset_confile["dataset"]["schema"]["specification"], str):
        raise Exception('The dataset_confile["dataset"]["schema"]["specification"] must be of type string.')

    # Dataset description validation
    if not isinstance(dataset_confile["dataset"]["info"]["description"], str):
        raise Exception('The dataset_confiledescription must be of type string.')

    # Dataset schema identifiers
    if not isinstance(dataset_confile["dataset"]["schema"]["default_schema_id"], str):
        raise Exception('The dataset_confile["dataset"]["schema"]["default_schema_id"] must be of type string.')

    if not isinstance(dataset_confile["dataset"]["schema"]["default_schema_name"], str):
        raise Exception('The dataset_confile["dataset"]["schema"]["default_schema_name"] must be of type string.')

    if not isinstance(dataset_confile["dataset"]["schema"]["reference_to_default_schema_definition"], str):
        raise Exception('The dataset_confile["dataset"]["schema"]["reference_to_default_schema_definition"] must be of type string.')

    if not isinstance(dataset_confile["dataset"]["schema"]["default_schema_version"], str):
        raise Exception('The dataset_confile["dataset"]["schema"]["default_schema_version"] must be of type string.')

    # Dataset supported schemas collection
    if not isinstance(dataset_confile["dataset"]["schema"]["supported_schemas"], list):
        raise Exception('The dataset_confile["dataset"]["schema"]["supported_schemas"] must be of type list.')

    # Dataset query behaviour flags
    if not isinstance(dataset_confile["dataset"]["allow_queries_without_filters"], bool):
        raise Exception('The dataset_confile["analysis"]["allow_queries_without_filters"] must be of type bool.')

    if not isinstance(dataset_confile["dataset"]["allow_id_query"], bool):
        raise Exception('The dataset_confile["analysis"]["allow_id_query"] must be of type bool.')

    # Validate genomicVariant OpenAPI definition
    if not isinstance(genomicVariant_confile["genomicVariant"]["open_api_definition"], str):
        raise Exception('The genomicVariant_confile["cohort"]["open_api_definition"] must be of type string.')

    # genomicVariant root section must exist
    if 'genomicVariant' not in genomicVariant_confile:
        raise Exception('The genomicVariant_confileid variable must be genomicVariant_confile')

    # Validate genomicVariant metadata fields
    if not isinstance(genomicVariant_confile["genomicVariant"]["info"]["name"], str):
        raise Exception('The genomicVariant_confilename must be of type string.')

    if not isinstance(genomicVariant_confile["genomicVariant"]["info"]["ontology_id"], str) or not re.match(
            "[A-Za-z0-9]+:[A-Za-z0-9]",
            genomicVariant_confile["genomicVariant"]["info"]["ontology_id"]):
        raise Exception('The genomicVariant_confile["dataset"]["info"]["ontology_id"] must be of type string and CURIE.')

    if not isinstance(genomicVariant_confile["genomicVariant"]["info"]["ontology_name"], str):
        raise Exception('The genomicVariant_confile["dataset"]["info"]["ontology_name"] must be of type string.')

    # Validate genomicVariant schema configuration
    if not isinstance(genomicVariant_confile["genomicVariant"]["schema"]["specification"], str):
        raise Exception('The genomicVariant_confile["genomicVariant"]["schema"]["specification"] must be of type string.')

    if not isinstance(genomicVariant_confile["genomicVariant"]["info"]["description"], str):
        raise Exception('The genomicVariant_confiledescription must be of type string.')

    if not isinstance(genomicVariant_confile["genomicVariant"]["schema"]["default_schema_id"], str):
        raise Exception('The genomicVariant_confile["genomicVariant"]["schema"]["default_schema_id"] must be of type string.')

    if not isinstance(genomicVariant_confile["genomicVariant"]["schema"]["default_schema_name"], str):
        raise Exception('The genomicVariant_confile["genomicVariant"]["schema"]["default_schema_name"] must be of type string.')

    if not isinstance(genomicVariant_confile["genomicVariant"]["schema"]["reference_to_default_schema_definition"], str):
        raise Exception('The genomicVariant_confile["genomicVariant"]["schema"]["reference_to_default_schema_definition"] must be of type string.')

    if not isinstance(genomicVariant_confile["genomicVariant"]["schema"]["default_schema_version"], str):
        raise Exception('The genomicVariant_confile["genomicVariant"]["schema"]["default_schema_version"] must be of type string.')

    if not isinstance(genomicVariant_confile["genomicVariant"]["schema"]["supported_schemas"], list):
        raise Exception('The genomicVariant_confile["genomicVariant"]["schema"]["supported_schemas"] must be of type list.')

    # Validate genomicVariant query permissions
    if not isinstance(genomicVariant_confile["genomicVariant"]["allow_queries_without_filters"], bool):
        raise Exception('The genomicVariant_confile["analysis"]["allow_queries_without_filters"] must be of type bool.')

    if not isinstance(genomicVariant_confile["genomicVariant"]["allow_id_query"], bool):
        raise Exception('The genomicVariant_confile["analysis"]["allow_id_query"] must be of type bool.')

    # Validate individual OpenAPI definition
    if not isinstance(individual_confile["individual"]["open_api_definition"], str):
        raise Exception('The individual_confile["cohort"]["open_api_definition"] must be of type string.')

    # Individual root section must exist
    if 'individual' not in individual_confile:
        raise Exception('The individual_confileid variable must be individual_confile')

    # Individual metadata validation
    if not isinstance(individual_confile["individual"]["info"]["name"], str):
        raise Exception('The individual_confilename must be of type string.')

    if not isinstance(individual_confile["individual"]["info"]["ontology_id"], str) or not re.match(
            "[A-Za-z0-9]+:[A-Za-z0-9]",
            individual_confile["individual"]["info"]["ontology_id"]):
        raise Exception('The individual_confile["dataset"]["info"]["ontology_id"] must be of type string and CURIE.')

    if not isinstance(individual_confile["individual"]["info"]["ontology_name"], str):
        raise Exception('The individual_confile["dataset"]["info"]["ontology_name"] must be of type string.')

    # Validate individual schema information
    if not isinstance(individual_confile["individual"]["schema"]["specification"], str):
        raise Exception('The individual_confile["genomicVariant"]["schema"]["specification"] must be of type string.')

    if not isinstance(individual_confile["individual"]["info"]["description"], str):
        raise Exception('The individual_confiledescription must be of type string.')

    if not isinstance(individual_confile["individual"]["schema"]["default_schema_id"], str):
        raise Exception('The individual_confile["genomicVariant"]["schema"]["default_schema_id"] must be of type string.')

    if not isinstance(individual_confile["individual"]["schema"]["default_schema_name"], str):
        raise Exception('The individual_confile["genomicVariant"]["schema"]["default_schema_name"] must be of type string.')

    if not isinstance(individual_confile["individual"]["schema"]["reference_to_default_schema_definition"], str):
        raise Exception('The individual_confile["genomicVariant"]["schema"]["reference_to_default_schema_definition"] must be of type string.')

    if not isinstance(individual_confile["individual"]["schema"]["default_schema_version"], str):
        raise Exception('The individual_confile["genomicVariant"]["schema"]["default_schema_version"] must be of type string.')

    if not isinstance(individual_confile["individual"]["schema"]["supported_schemas"], list):
        raise Exception('The individual_confile["genomicVariant"]["schema"]["supported_schemas"] must be of type list.')

    # Individual query settings
    if not isinstance(individual_confile["individual"]["allow_queries_without_filters"], bool):
        raise Exception('The individual_confile["analysis"]["allow_queries_without_filters"] must be of type bool.')

    if not isinstance(individual_confile["individual"]["allow_id_query"], bool):
        raise Exception('The individual_confile["analysis"]["allow_id_query"] must be of type bool.')

    # Validate run OpenAPI definition
    if not isinstance(run_confile["run"]["open_api_definition"], str):
        raise Exception('The run_confile["cohort"]["open_api_definition"] must be of type string.')

    # Run root section must exist
    if 'run' not in run_confile:
        raise Exception('The run_confileid variable must be run_confile')

    # Run metadata validation
    if not isinstance(run_confile["run"]["info"]["name"], str):
        raise Exception('The run_confilename must be of type string.')

    if not isinstance(run_confile["run"]["info"]["ontology_id"], str) or not re.match(
            "[A-Za-z0-9]+:[A-Za-z0-9]",
            run_confile["run"]["info"]["ontology_id"]):
        raise Exception('The run_confile["dataset"]["info"]["ontology_id"] must be of type string and CURIE.')

    if not isinstance(run_confile["run"]["info"]["ontology_name"], str):
        raise Exception('The run_confile["dataset"]["info"]["ontology_name"] must be of type string.')

    # Run schema validation
    if not isinstance(run_confile["run"]["schema"]["specification"], str):
        raise Exception('The run_confile["genomicVariant"]["schema"]["specification"] must be of type string.')

    if not isinstance(run_confile["run"]["info"]["description"], str):
        raise Exception('The run_confiledescription must be of type string.')

    if not isinstance(run_confile["run"]["schema"]["default_schema_id"], str):
        raise Exception('The run_confile["genomicVariant"]["schema"]["default_schema_id"] must be of type string.')

    if not isinstance(run_confile["run"]["schema"]["default_schema_name"], str):
        raise Exception('The run_confile["genomicVariant"]["schema"]["default_schema_name"] must be of type string.')

    if not isinstance(run_confile["run"]["schema"]["reference_to_default_schema_definition"], str):
        raise Exception('The run_confile["genomicVariant"]["schema"]["reference_to_default_schema_definition"] must be of type string.')

    if not isinstance(run_confile["run"]["schema"]["default_schema_version"], str):
        raise Exception('The run_confile["genomicVariant"]["schema"]["default_schema_version"] must be of type string.')

    if not isinstance(run_confile["run"]["schema"]["supported_schemas"], list):
        raise Exception('The run_confile["genomicVariant"]["schema"]["supported_schemas"] must be of type list.')

    # Validate run query permissions
    if not isinstance(run_confile["run"]["allow_queries_without_filters"], bool):
        raise Exception('The run_confile["analysis"]["allow_queries_without_filters"] must be of type bool.')

    if not isinstance(run_confile["run"]["allow_id_query"], bool):
        raise Exception('The run_confile["analysis"]["allow_id_query"] must be of type bool.')
    # Validate beacon metadata fields
    if not isinstance(conf_override.config.beacon_name, str):
        raise Exception('The beacon_name config parameter must be a string')

    if not isinstance(conf_override.config.beacon_id, str):
        raise Exception('The beacon_id config parameter must be a string')

    if not isinstance(conf_override.config.api_version, str):
        raise Exception('The api_version config parameter must be a string')

    if not isinstance(conf_override.config.description, str):
        raise Exception('The description config parameter must be a string')

    # Validate public-facing URLs
    if not isinstance(conf_override.config.welcome_url, str):
        raise Exception('The welcome_url config parameter must be a string')

    if not isinstance(conf_override.config.alternative_url, str):
        raise Exception('The alternative_url config parameter must be a string')

    # Validate creation timestamp format
    if not isinstance(conf_override.config.create_datetime, str):
        raise Exception('The create_datetime config parameter must be a string')

    try:
        timestamp_regex.match(conf_override.config.create_datetime)
    except Exception:
        raise Exception('The create_datetime_datetime config parameter must be timestamp')

    # Validate update timestamp format
    if not isinstance(conf_override.config.update_datetime, str):
        raise Exception('The update_datetime config parameter must be a string')

    try:
        timestamp_regex.match(conf_override.config.update_datetime)
    except Exception:
        raise Exception('The update_datetime config parameter must be timestamp')

    # Documentation URL must be a string
    if not isinstance(conf_override.config.documentation_url, str):
        raise Exception('The documentation_url config parameter must be a string')

    # Ensure welcome URL starts with a valid HTTP protocol
    if not conf_override.config.welcome_url.startswith('http://'):
        if not conf_override.config.welcome_url.startswith('https://'):
            raise Exception(
                'The url {} in welcome_url variable must start with http protocol'.format(
                    conf_override.config.welcome_url
                )
            )

    # Ensure alternative URL starts with a valid HTTP protocol
    if not conf_override.config.alternative_url.startswith('http://'):
        if not conf_override.config.alternative_url.startswith('https://'):
            raise Exception(
                'The url {} in alternative_url variable must start with http protocol'.format(
                    conf_override.config.alternative_url
                )
            )

    # Ensure documentation URL starts with a valid HTTP protocol
    if not conf_override.config.documentation_url.startswith('http://'):
        if not conf_override.config.documentation_url.startswith('https://'):
            raise Exception(
                'The url {} in documentation_url variable must start with http protocol'.format(
                    conf_override.config.documentation_url
                )
            )

    # Validate dataset permissions configuration file
    try:
        with open("/beacon/permissions/datasets/datasets_permissions.yml", 'r') as pfile:
            datasets = yaml.safe_load(pfile)

        pfile.close()

        # Iterate through dataset permission definitions
        for dataset_name, configuration in datasets.items():

            # Configuration can be a simple boolean or a permission object
            if not isinstance(configuration, bool):

                for security_level, securityconf in configuration.items():

                    # Only supported security levels are allowed
                    if security_level not in ['public', 'registered', 'controlled']:
                        raise Exception(
                            "keys for datasets have to be public, registered, controlled for security level"
                        )

                    # Security configuration can be boolean or detailed object
                    if not isinstance(securityconf, bool):

                        for parameters, paramsvalues in securityconf.items():

                            # Allowed permission configuration keys
                            if parameters not in [
                                'default_entry_types_granularity',
                                'entry_types_exceptions',
                                'user-list'
                            ]:
                                raise Exception(
                                    "entries for dataset settings have to be "
                                    "default_entry_types_granularity, "
                                    "entry_types_exceptions or user-list"
                                )

                            # Additional validation for controlled access users
                            if security_level == 'controlled':

                                if parameters == 'user-list':

                                    for user in paramsvalues:

                                        for confuser, valueuser in user.items():

                                            # Validate user-specific configuration keys
                                            if confuser not in [
                                                'user_e-mail',
                                                'default_entry_types_granularity',
                                                'entry_types_exceptions'
                                            ]:
                                                raise Exception(
                                                    "entries for user settings in user-list "
                                                    "must be be default_entry_types_granularity, "
                                                    "entry_types_exceptions or user_e-mail"
                                                )

    except Exception:
        raise

    # Validate datasets configuration file
    try:
        with open("/beacon/conf/datasets/datasets_conf.yml", 'r') as pfile:
            datasets = yaml.safe_load(pfile)

        pfile.close()

        # Validate each dataset configuration block
        for dataset_name, configuration in datasets.items():

            for property, value in configuration.items():

                # Only two dataset-level properties are supported
                if property not in ['isTest', 'isSynthetic']:
                    raise Exception(
                        "keys for datasets properties in datasets_conf.yml "
                        "have to be isTest or isSynthetic"
                    )

                # Dataset properties must be booleans
                if not isinstance(value, bool):
                    raise Exception(
                        "values for datasets properties in datasets_conf.yml "
                        "have to be boolean"
                    )

    except Exception:
        raise