from beacon.conf import conf_override
from beacon.logs.logs import log_with_args_check_configuration
import os
import re
import logging
import yaml
from beacon.utils.modules import get_modules_confiles
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
    LOG=None
):
    # Load conf file for connection to check which are enabled
    with open('/beacon/conf/connections/connections_conf.yml') as infile:
        connections_conf=yaml.safe_load(infile)
    # Get array of enabled connections
    connections_enabled=[]
    for k, v in connections_conf.items():
        if v['connection_enabled']==True:
            connections_enabled.append(k)
    all_conf_files=get_modules_confiles()
    # -------------------------------------------------------------------------
    # Entry type enablement validation
    # Ensure that the "entry_type_enabled" flag is explicitly configured as a
    # boolean value for every supported Beacon entity.
    # -------------------------------------------------------------------------
    for file in all_conf_files:
        for k, v in file.items():
            if isinstance(v["entry_type_enabled"], bool):
                pass
            else:
                raise Exception(
                    "{}.entry_type_enabled variable from {}.py must be boolean".format(
                        k, k
                    )
                )
    # -------------------------------------------------------------------------
    # Endpoint granularity validation
    # Validate that enabled endpoints only use Beacon-supported granularity
    # levels: boolean, count or record.
    # -------------------------------------------------------------------------
            if (
                v["endpoint_name"] != ''
                and v["max_granularity"]
                not in ['boolean', 'count', 'record']
            ):
                raise Exception(
                    "{}granularity must be one string between boolean, count or record".format(k)
                )

            if v["connection"]["name"] not in connections_enabled:
                raise Exception(
                    'The connection {} for {} records needs to be enabled in case you want to use it'.format(
                        v["connection"]["name"], k
                    )
                )

            # Validate the configured backend for run records.
            if v["connection"]["name"] not in [
                name
                for name in os.listdir("/beacon/connections")
                if os.path.isdir(os.path.join("/beacon/connections", name))
            ]:
                raise Exception(
                    'The database {} for {}records needs to match a directory name in the beacon/connections folder'.format(
                        v["connection"]["name"], k
                    )
                )
            
    # -------------------------------------------------------------------------
    # Endpoint name validation
    # Validate that all endpoint names are strings and only contain
    # supported characters. Endpoint names are used to generate routes,
    # therefore special characters are not allowed.
    # -------------------------------------------------------------------------

            if not isinstance(v["endpoint_name"], str):
                raise Exception('The endpoint_name variable for {} entry type must be of type string'.format(k))
            if contains_special_characters(v["endpoint_name"]):
                raise Exception('The endpoint_name variable for {} entry type can not have special characters'.format(k))

    # -------------------------------------------------------------------------
    # Analysis configuration validation
    # Verify that the analysis entry type contains all mandatory Beacon
    # metadata fields, schema definitions and query configuration flags.
    # -------------------------------------------------------------------------

            if not isinstance(v["open_api_definition"], str):
                raise Exception('The {} open_api_definition must be of type string.'.format(k))

            # Validate ontology metadata used to describe the entry type.
            if not isinstance(v["info"]["name"], str):
                raise Exception('The {} info name must be of type string.'.format(k))

            # Ontology identifiers must follow CURIE notation.
            if not isinstance(v["info"]["ontology_id"], str) or not re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v["info"]["ontology_id"]):
                raise Exception('The {} ["info"]["ontology_id"] must be of type string and CURIE.'.format(k))

            if not isinstance(v["info"]["ontology_name"], str):
                raise Exception('The {} ["info"]["ontology_name"] must be of type string.'.format(k))

            # Validate schema definition metadata.
            if not isinstance(v["schema"]["specification"], str):
                raise Exception('The {} schema ["schema"]["specification"] must be of type string.'.format(k))

            if not isinstance(v["info"]["description"], str):
                raise Exception('The {} description must be of type string.'.format(k))

            if not isinstance(v["schema"]["default_schema_id"], str):
                raise Exception('The {} default_schema_id must be of type string.'.format(k))

            if not isinstance(v["schema"]["default_schema_name"], str):
                raise Exception('The {} default_schema_name must be of type string.'.format(k))

            if not isinstance(v["schema"]["reference_to_default_schema_definition"], str):
                raise Exception('The {} reference_to_default_schema_definition must be of type string.'.format(k))

            if not isinstance(v["schema"]["default_schema_version"], str):
                raise Exception('The ["schema"]["default_schema_version"] for entry type {} must be of type string.'.format(k))

            # Multiple schemas can be supported by the same entry type.
            if not isinstance(v["schema"]["supported_schemas"], list):
                raise Exception('The {} supported_schemas must be of type list.'.format(k))

            # Validate query behaviour configuration.
            if not isinstance(v["allow_queries_without_filters"], bool):
                raise Exception('The {} allow_queries_without_filters must be of type bool.'.format(k))

            if not isinstance(v["allow_id_query"], bool):
                raise Exception('The {} allow id query must be of type bool.'.format(k))
    
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
            datasets_conf = yaml.safe_load(pfile)

        pfile.close()

        # Validate each dataset configuration block
        for dataset_name, configuration in datasets_conf.items():

            for property, value in configuration.items():

                # Only two dataset-level properties are supported
                if property not in ['isTest', 'isSynthetic', 'isDeprecated']:
                    raise Exception(
                        "keys for datasets properties in datasets_conf.yml "
                        "have to be isTest, isDeprecated or isSynthetic"
                    )

                # Dataset properties must be booleans
                if not isinstance(value, bool):
                    raise Exception(
                        "values for datasets properties in datasets_conf.yml "
                        "have to be boolean"
                    )

    except Exception:
        raise