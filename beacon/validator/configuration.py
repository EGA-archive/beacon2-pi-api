from beacon.conf import analysis, biosample, cohort, dataset, genomicVariant, individual, run
from beacon.conf import conf
from beacon.logs.logs import LOG
import os
import re
import logging
import yaml

def contains_special_characters(string):
    for char in string:
        if char == '_':
            pass
        elif not (char.isdigit() or char.isalpha() or char == ' '):
            return True
    return False

def check_configuration():
    if analysis.endpoint_name != '' and analysis.granularity not in ['boolean', 'count', 'record']:
        raise Exception("analysis granularity must be one string between boolean, count or record")
    if biosample.endpoint_name != '' and biosample.granularity not in ['boolean', 'count', 'record']:
        raise Exception("biosample granularity must be one string between boolean, count or record")
    if cohort.endpoint_name != '' and cohort.granularity not in ['boolean', 'count', 'record']:
        raise Exception("cohort granularity must be one string between boolean, count or record")
    if dataset.endpoint_name != '' and dataset.granularity not in ['boolean', 'count', 'record']:
        raise Exception("dataset granularity must be one string between boolean, count or record")
    if genomicVariant.endpoint_name != '' and genomicVariant.granularity not in ['boolean', 'count', 'record']:
        raise Exception("genomicVariant granularity must be one string between boolean, count or record")
    if individual.endpoint_name != '' and individual.granularity not in ['boolean', 'count', 'record']:
        raise Exception("individual granularity must be one string between boolean, count or record")
    if run.endpoint_name != '' and run.granularity not in ['boolean', 'count', 'record']:
        raise Exception("run granularity must be one string between boolean, count or record")
    if conf.uri.startswith('http://'):
        LOG.warning('The uri of your beacon is not https. Please change to https as soon as you can.')
    elif conf.uri.startswith('https://'):
        pass
    else:
        raise Exception("The uri of your beacon must start with https protocol.")
    if conf.uri_subpath.startswith('/') and conf.uri.endswith('/'):
        raise Exception("The uri_subpath can not start with slash / if the conf.uri ends with slash /")
    if conf.uri.endswith('/'):
        raise Exception("The uri can't end with trailing slash /")
    if conf.uri_subpath.endswith('/'):
        raise Exception("The uri_subpath can't end with trailing slash /, leave it empty if you don't want to add any subpath.")
    if conf.uri_subpath.startswith('/'):
        pass
    else:
        raise Exception("The uri_subpath has to start with slash /.")
    if not isinstance(conf.query_budget_amount, int) or conf.query_budget_amount<0:
        raise Exception("The amount of query budget attempts allowed must be a natural number.")
    if not isinstance(conf.query_budget_time_in_seconds, int) or conf.query_budget_time_in_seconds<0:
        raise Exception("The rate of query time in seconds for the budget must be a natural number.")
    if not isinstance(conf.query_budget_per_user, bool):
        raise Exception("The query budget per user parameter must be boolean.")
    if not isinstance(conf.query_budget_per_ip, bool):
        raise Exception("The query budget per ip parameter must be boolean.")
    if conf.query_budget_database not in [name for name in os.listdir("/beacon/connections") if os.path.isdir(os.path.join("/beacon/connections", name))]:
        raise Exception('The database {} for budget needs to match a directory name in the beacon/connections folder'.format(conf.query_budget_database))
    if run.database not in [name for name in os.listdir("/beacon/connections") if os.path.isdir(os.path.join("/beacon/connections", name))]:
        raise Exception('The database {} for run records needs to match a directory name in the beacon/connections folder'.format(run.database))
    if individual.database not in [name for name in os.listdir("/beacon/connections") if os.path.isdir(os.path.join("/beacon/connections", name))]:
        raise Exception('The database {} for individual records needs to match a directory name in the beacon/connections folder'.format(individual.database))
    if genomicVariant.database not in [name for name in os.listdir("/beacon/connections") if os.path.isdir(os.path.join("/beacon/connections", name))]:
        raise Exception('The database {} for genomicVariant records needs to match a directory name in the beacon/connections folder'.format(genomicVariant.database))
    if dataset.database not in [name for name in os.listdir("/beacon/connections") if os.path.isdir(os.path.join("/beacon/connections", name))]:
        raise Exception('The database {} for dataset records needs to match a directory name in the beacon/connections folder'.format(dataset.database))
    if cohort.database not in [name for name in os.listdir("/beacon/connections") if os.path.isdir(os.path.join("/beacon/connections", name))]:
        raise Exception('The database {} for cohort records needs to match a directory name in the beacon/connections folder'.format(cohort.database))
    if biosample.database not in [name for name in os.listdir("/beacon/connections") if os.path.isdir(os.path.join("/beacon/connections", name))]:
        raise Exception('The database {} for biosample records needs to match a directory name in the beacon/connections folder'.format(biosample.database))
    if analysis.database not in [name for name in os.listdir("/beacon/connections") if os.path.isdir(os.path.join("/beacon/connections", name))]:
        raise Exception('The database {} for analysis records needs to match a directory name in the beacon/connections folder'.format(analysis.database))
    if conf.environment not in ['dev', 'test', 'prod', 'DEV', 'TEST', 'PROD']:
        raise Exception('The environment variable in conf must be one between test, dev, prod')
    if conf.default_beacon_granularity not in ['boolean', 'count', 'record']:
        raise Exception("Configuration parameter default_beacon_granularity must be one string between boolean, count or record")
    if not isinstance(conf.security_levels, list):
        raise Exception("Configuration parameter security_levels must be of type array")
    for security_level in conf.security_levels:
        if security_level not in ['PUBLIC', 'REGISTERED', 'CONTROLLED']:
            raise Exception("Security levels can only have PUBLIC, REGISTERED or CONTROLLED level.")
    if not isinstance(conf.cors_urls, list):
        raise Exception("Configuration parameter cors_urls must be of type array")
    for cors_url in conf.cors_urls:
        if not cors_url.startswith('http://'):
            if not cors_url.startswith('https://'):
                raise Exception('The url {} in cors_urls variable must start with http protocol'.format(cors_url))
    if not isinstance(run.endpoint_name, str):
        raise Exception('The run.endpoint_name variable must be of type string')
    if contains_special_characters(run.endpoint_name):
        raise Exception('The run.endpoint_name variable can not have special characters')
    if not isinstance(individual.endpoint_name, str):
        raise Exception('The individual.endpoint_name variable must be of type string')
    if contains_special_characters(individual.endpoint_name):
        raise Exception('The individual.endpoint_name variable can not have special characters')
    if not isinstance(genomicVariant.endpoint_name, str):
        raise Exception('The genomicVariant.endpoint_name variable must be of type string')
    if contains_special_characters(genomicVariant.endpoint_name):
        raise Exception('The genomicVariant.endpoint_name variable can not have special characters')
    if not isinstance(dataset.endpoint_name, str):
        raise Exception('The dataset.endpoint_name variable must be of type string')
    if contains_special_characters(dataset.endpoint_name):
        raise Exception('The dataset.endpoint_name variable can not have special characters')
    if not isinstance(cohort.endpoint_name, str):
        raise Exception('The cohort.endpoint_name variable must be of type string')
    if contains_special_characters(cohort.endpoint_name):
        raise Exception('The cohort.endpoint_name variable can not have special characters')
    if not isinstance(biosample.endpoint_name, str):
        raise Exception('The biosample.endpoint_name variable must be of type string')
    if contains_special_characters(biosample.endpoint_name):
        raise Exception('The biosample.endpoint_name variable can not have special characters')
    if not isinstance(analysis.endpoint_name, str):
        raise Exception('The analysis.endpoint_name variable must be of type string')
    if contains_special_characters(analysis.endpoint_name):
        raise Exception('The analysis.endpoint_name variable can not have special characters')
    if not isinstance(analysis.open_api_endpoints_definition, str):
        raise Exception('The analysis.open_api_endpoints_definition must be of type string.')
    if analysis.id != 'analysis':
        raise Exception('The analysis.id variable must be analysis.')
    if not isinstance(analysis.name, str):
        raise Exception('The analysis.name must be of type string.')
    if not isinstance(analysis.ontology_id, str) and not re.match("[A-Za-z0-9]+:[A-Za-z0-9]", analysis.ontology_id):
        raise Exception('The analysis.ontology_id must be of type string and CURIE.')
    if not isinstance(analysis.ontology_name, str):
        raise Exception('The analysis.ontology_name must be of type string.')
    if not isinstance(analysis.specification, str):
        raise Exception('The analysis.specification must be of type string.')
    if not isinstance(analysis.description, str):
        raise Exception('The analysis.description must be of type string.')
    if not isinstance(analysis.defaultSchema_id, str):
        raise Exception('The analysis.defaultSchema_id must be of type string.')
    if not isinstance(analysis.defaultSchema_name, str):
        raise Exception('The analysis.defaultSchema_name must be of type string.')
    if not isinstance(analysis.defaultSchema_reference_to_schema_definition, str):
        raise Exception('The analysis.defaultSchema_reference_to_schema_definition must be of type string.')
    if not isinstance(analysis.defaultSchema_schema_version, str):
        raise Exception('The analysis.defaultSchema_schema_version must be of type string.')
    if not isinstance(analysis.aditionally_supported_schemas, list):
        raise Exception('The analysis.aditionally_supported_schemas must be of type list.')
    if not isinstance(analysis.allow_queries_without_filters, bool):
        raise Exception('The analysis.allow_queries_without_filters must be of type bool.')
    if not isinstance(analysis.singleEntryUrl, bool):
        raise Exception('The analysis.singleEntryUrl must be of type bool.')
    if not isinstance(analysis.biosample_lookup, bool):
        raise Exception('The analysis.biosample_lookup must be of type bool.')
    if not isinstance(analysis.cohort_lookup, bool):
        raise Exception('The analysis.cohort_lookup must be of type bool.')
    if not isinstance(analysis.dataset_lookup, bool):
        raise Exception('The analysis.dataset_lookup must be of type bool.')
    if not isinstance(analysis.genomicVariant_lookup, bool):
        raise Exception('The analysis.genomicVariant_lookup must be of type bool.')
    if not isinstance(analysis.individual_lookup, bool):
        raise Exception('The analysis.individual_lookup must be of type bool.')
    if not isinstance(analysis.run_lookup, bool):
        raise Exception('The analysis.run_lookup must be of type bool.')
    if not isinstance(biosample.open_api_endpoints_definition, str):
        raise Exception('The biosample.open_api_endpoints_definition must be of type string.')
    if biosample.id != 'biosample':
        raise Exception('The biosample.id variable must be biosample.')
    if not isinstance(biosample.name, str):
        raise Exception('The biosample.name must be of type string.')
    if not isinstance(biosample.ontology_id, str) and not re.match("[A-Za-z0-9]+:[A-Za-z0-9]", biosample.ontology_id):
        raise Exception('The biosample.ontology_id must be of type string and CURIE.')
    if not isinstance(biosample.ontology_name, str):
        raise Exception('The biosample.ontology_name must be of type string.')
    if not isinstance(biosample.specification, str):
        raise Exception('The biosample.specification must be of type string.')
    if not isinstance(biosample.description, str):
        raise Exception('The biosample.description must be of type string.')
    if not isinstance(biosample.defaultSchema_id, str):
        raise Exception('The biosample.defaultSchema_id must be of type string.')
    if not isinstance(biosample.defaultSchema_name, str):
        raise Exception('The biosample.defaultSchema_name must be of type string.')
    if not isinstance(biosample.defaultSchema_reference_to_schema_definition, str):
        raise Exception('The biosample.defaultSchema_reference_to_schema_definition must be of type string.')
    if not isinstance(biosample.defaultSchema_schema_version, str):
        raise Exception('The biosample.defaultSchema_schema_version must be of type string.')
    if not isinstance(biosample.aditionally_supported_schemas, list):
        raise Exception('The biosample.aditionally_supported_schemas must be of type list.')
    if not isinstance(biosample.allow_queries_without_filters, bool):
        raise Exception('The biosample.allow_queries_without_filters must be of type bool.')
    if not isinstance(biosample.singleEntryUrl, bool):
        raise Exception('The biosample.singleEntryUrl must be of type bool.')
    if not isinstance(biosample.analysis_lookup, bool):
        raise Exception('The biosample.analysis_lookup must be of type bool.')
    if not isinstance(biosample.cohort_lookup, bool):
        raise Exception('The biosample.cohort_lookup must be of type bool.')
    if not isinstance(biosample.dataset_lookup, bool):
        raise Exception('The biosample.dataset_lookup must be of type bool.')
    if not isinstance(biosample.genomicVariant_lookup, bool):
        raise Exception('The biosample.genomicVariant_lookup must be of type bool.')
    if not isinstance(biosample.individual_lookup, bool):
        raise Exception('The biosample.individual_lookup must be of type bool.')
    if not isinstance(biosample.run_lookup, bool):
        raise Exception('The biosample.run_lookup must be of type bool.')
    if not isinstance(cohort.open_api_endpoints_definition, str):
        raise Exception('The cohort.open_api_endpoints_definition must be of type string.')
    if cohort.id != 'cohort':
        raise Exception('The cohort.id variable must be cohort.')
    if not isinstance(cohort.name, str):
        raise Exception('The cohort.name must be of type string.')
    if not isinstance(cohort.ontology_id, str) and not re.match("[A-Za-z0-9]+:[A-Za-z0-9]", cohort.ontology_id):
        raise Exception('The cohort.ontology_id must be of type string and CURIE.')
    if not isinstance(cohort.ontology_name, str):
        raise Exception('The cohort.ontology_name must be of type string.')
    if not isinstance(cohort.specification, str):
        raise Exception('The cohort.specification must be of type string.')
    if not isinstance(cohort.description, str):
        raise Exception('The cohort.description must be of type string.')
    if not isinstance(cohort.defaultSchema_id, str):
        raise Exception('The cohort.defaultSchema_id must be of type string.')
    if not isinstance(cohort.defaultSchema_name, str):
        raise Exception('The cohort.defaultSchema_name must be of type string.')
    if not isinstance(cohort.defaultSchema_reference_to_schema_definition, str):
        raise Exception('The cohort.defaultSchema_reference_to_schema_definition must be of type string.')
    if not isinstance(cohort.defaultSchema_schema_version, str):
        raise Exception('The cohort.defaultSchema_schema_version must be of type string.')
    if not isinstance(cohort.aditionally_supported_schemas, list):
        raise Exception('The cohort.aditionally_supported_schemas must be of type list.')
    if not isinstance(cohort.allow_queries_without_filters, bool):
        raise Exception('The cohort.allow_queries_without_filters must be of type bool.')
    if not isinstance(cohort.singleEntryUrl, bool):
        raise Exception('The cohort.singleEntryUrl must be of type bool.')
    if not isinstance(cohort.analysis_lookup, bool):
        raise Exception('The cohort.analysis_lookup must be of type bool.')
    if not isinstance(cohort.biosample_lookup, bool):
        raise Exception('The cohort.biosample_lookup must be of type bool.')
    if not isinstance(cohort.dataset_lookup, bool):
        raise Exception('The cohort.dataset_lookup must be of type bool.')
    if not isinstance(cohort.genomicVariant_lookup, bool):
        raise Exception('The cohort.genomicVariant_lookup must be of type bool.')
    if not isinstance(cohort.individual_lookup, bool):
        raise Exception('The cohort.individual_lookup must be of type bool.')
    if not isinstance(cohort.run_lookup, bool):
        raise Exception('The cohort.run_lookup must be of type bool.')
    if not isinstance(dataset.open_api_endpoints_definition, str):
        raise Exception('The dataset.open_api_endpoints_definition must be of type string.')
    if dataset.id != 'dataset':
        raise Exception('The dataset.id variable must be dataset.')
    if not isinstance(dataset.name, str):
        raise Exception('The dataset.name must be of type string.')
    if not isinstance(dataset.ontology_id, str) and not re.match("[A-Za-z0-9]+:[A-Za-z0-9]", dataset.ontology_id):
        raise Exception('The dataset.ontology_id must be of type string and CURIE.')
    if not isinstance(dataset.ontology_name, str):
        raise Exception('The dataset.ontology_name must be of type string.')
    if not isinstance(dataset.specification, str):
        raise Exception('The dataset.specification must be of type string.')
    if not isinstance(dataset.description, str):
        raise Exception('The dataset.description must be of type string.')
    if not isinstance(dataset.defaultSchema_id, str):
        raise Exception('The dataset.defaultSchema_id must be of type string.')
    if not isinstance(dataset.defaultSchema_name, str):
        raise Exception('The dataset.defaultSchema_name must be of type string.')
    if not isinstance(dataset.defaultSchema_reference_to_schema_definition, str):
        raise Exception('The dataset.defaultSchema_reference_to_schema_definition must be of type string.')
    if not isinstance(dataset.defaultSchema_schema_version, str):
        raise Exception('The dataset.defaultSchema_schema_version must be of type string.')
    if not isinstance(dataset.aditionally_supported_schemas, list):
        raise Exception('The dataset.aditionally_supported_schemas must be of type list.')
    if not isinstance(dataset.allow_queries_without_filters, bool):
        raise Exception('The dataset.allow_queries_without_filters must be of type bool.')
    if not isinstance(dataset.singleEntryUrl, bool):
        raise Exception('The dataset.singleEntryUrl must be of type bool.')
    if not isinstance(dataset.analysis_lookup, bool):
        raise Exception('The dataset.analysis_lookup must be of type bool.')
    if not isinstance(dataset.biosample_lookup, bool):
        raise Exception('The dataset.biosample_lookup must be of type bool.')
    if not isinstance(dataset.cohort_lookup, bool):
        raise Exception('The dataset.cohort_lookup must be of type bool.')
    if not isinstance(dataset.genomicVariant_lookup, bool):
        raise Exception('The dataset.genomicVariant_lookup must be of type bool.')
    if not isinstance(dataset.individual_lookup, bool):
        raise Exception('The dataset.individual_lookup must be of type bool.')
    if not isinstance(dataset.run_lookup, bool):
        raise Exception('The dataset.run_lookup must be of type bool.')
    if not isinstance(genomicVariant.open_api_endpoints_definition, str):
        raise Exception('The genomicVariant.open_api_endpoints_definition must be of type string.')
    if genomicVariant.id != 'genomicVariant':
        raise Exception('The genomicVariant.id variable must be genomicVariant.')
    if not isinstance(genomicVariant.name, str):
        raise Exception('The genomicVariant.name must be of type string.')
    if not isinstance(genomicVariant.ontology_id, str) and not re.match("[A-Za-z0-9]+:[A-Za-z0-9]", genomicVariant.ontology_id):
        raise Exception('The genomicVariant.ontology_id must be of type string and CURIE.')
    if not isinstance(genomicVariant.ontology_name, str):
        raise Exception('The genomicVariant.ontology_name must be of type string.')
    if not isinstance(genomicVariant.specification, str):
        raise Exception('The genomicVariant.specification must be of type string.')
    if not isinstance(genomicVariant.description, str):
        raise Exception('The genomicVariant.description must be of type string.')
    if not isinstance(genomicVariant.defaultSchema_id, str):
        raise Exception('The genomicVariant.defaultSchema_id must be of type string.')
    if not isinstance(genomicVariant.defaultSchema_name, str):
        raise Exception('The genomicVariant.defaultSchema_name must be of type string.')
    if not isinstance(genomicVariant.defaultSchema_reference_to_schema_definition, str):
        raise Exception('The genomicVariant.defaultSchema_reference_to_schema_definition must be of type string.')
    if not isinstance(genomicVariant.defaultSchema_schema_version, str):
        raise Exception('The genomicVariant.defaultSchema_schema_version must be of type string.')
    if not isinstance(genomicVariant.aditionally_supported_schemas, list):
        raise Exception('The genomicVariant.aditionally_supported_schemas must be of type list.')
    if not isinstance(genomicVariant.allow_queries_without_filters, bool):
        raise Exception('The genomicVariant.allow_queries_without_filters must be of type bool.')
    if not isinstance(genomicVariant.singleEntryUrl, bool):
        raise Exception('The genomicVariant.singleEntryUrl must be of type bool.')
    if not isinstance(genomicVariant.analysis_lookup, bool):
        raise Exception('The genomicVariant.analysis_lookup must be of type bool.')
    if not isinstance(genomicVariant.biosample_lookup, bool):
        raise Exception('The genomicVariant.biosample_lookup must be of type bool.')
    if not isinstance(genomicVariant.cohort_lookup, bool):
        raise Exception('The genomicVariant.cohort_lookup must be of type bool.')
    if not isinstance(genomicVariant.dataset_lookup, bool):
        raise Exception('The genomicVariant.dataset_lookup must be of type bool.')
    if not isinstance(genomicVariant.individual_lookup, bool):
        raise Exception('The genomicVariant.individual_lookup must be of type bool.')
    if not isinstance(genomicVariant.run_lookup, bool):
        raise Exception('The genomicVariant.run_lookup must be of type bool.')
    if not isinstance(individual.open_api_endpoints_definition, str):
        raise Exception('The individual.open_api_endpoints_definition must be of type string.')
    if individual.id != 'individual':
        raise Exception('The individual.id variable must be individual.')
    if not isinstance(individual.name, str):
        raise Exception('The individual.name must be of type string.')
    if not isinstance(individual.ontology_id, str) and not re.match("[A-Za-z0-9]+:[A-Za-z0-9]", individual.ontology_id):
        raise Exception('The individual.ontology_id must be of type string and CURIE.')
    if not isinstance(individual.ontology_name, str):
        raise Exception('The individual.ontology_name must be of type string.')
    if not isinstance(individual.specification, str):
        raise Exception('The individual.specification must be of type string.')
    if not isinstance(individual.description, str):
        raise Exception('The individual.description must be of type string.')
    if not isinstance(individual.defaultSchema_id, str):
        raise Exception('The individual.defaultSchema_id must be of type string.')
    if not isinstance(individual.defaultSchema_name, str):
        raise Exception('The individual.defaultSchema_name must be of type string.')
    if not isinstance(individual.defaultSchema_reference_to_schema_definition, str):
        raise Exception('The individual.defaultSchema_reference_to_schema_definition must be of type string.')
    if not isinstance(individual.defaultSchema_schema_version, str):
        raise Exception('The individual.defaultSchema_schema_version must be of type string.')
    if not isinstance(individual.aditionally_supported_schemas, list):
        raise Exception('The individual.aditionally_supported_schemas must be of type list.')
    if not isinstance(individual.allow_queries_without_filters, bool):
        raise Exception('The individual.allow_queries_without_filters must be of type bool.')
    if not isinstance(individual.singleEntryUrl, bool):
        raise Exception('The individual.singleEntryUrl must be of type bool.')
    if not isinstance(individual.analysis_lookup, bool):
        raise Exception('The individual.analysis_lookup must be of type bool.')
    if not isinstance(individual.biosample_lookup, bool):
        raise Exception('The individual.biosample_lookup must be of type bool.')
    if not isinstance(individual.cohort_lookup, bool):
        raise Exception('The individual.cohort_lookup must be of type bool.')
    if not isinstance(individual.dataset_lookup, bool):
        raise Exception('The individual.dataset_lookup must be of type bool.')
    if not isinstance(individual.genomicVariant_lookup, bool):
        raise Exception('The individual.genomicVariant_lookup must be of type bool.')
    if not isinstance(individual.run_lookup, bool):
        raise Exception('The individual.run_lookup must be of type bool.')
    if not isinstance(run.open_api_endpoints_definition, str):
        raise Exception('The run.open_api_endpoints_definition must be of type string.')
    if run.id != 'run':
        raise Exception('The run.id variable must be run.')
    if not isinstance(run.name, str):
        raise Exception('The run.name must be of type string.')
    if not isinstance(run.ontology_id, str) and not re.match("[A-Za-z0-9]+:[A-Za-z0-9]", run.ontology_id):
        raise Exception('The run.ontology_id must be of type string and CURIE.')
    if not isinstance(run.ontology_name, str):
        raise Exception('The run.ontology_name must be of type string.')
    if not isinstance(run.specification, str):
        raise Exception('The run.specification must be of type string.')
    if not isinstance(run.description, str):
        raise Exception('The run.description must be of type string.')
    if not isinstance(run.defaultSchema_id, str):
        raise Exception('The run.defaultSchema_id must be of type string.')
    if not isinstance(run.defaultSchema_name, str):
        raise Exception('The run.defaultSchema_name must be of type string.')
    if not isinstance(run.defaultSchema_reference_to_schema_definition, str):
        raise Exception('The run.defaultSchema_reference_to_schema_definition must be of type string.')
    if not isinstance(run.defaultSchema_schema_version, str):
        raise Exception('The run.defaultSchema_schema_version must be of type string.')
    if not isinstance(run.aditionally_supported_schemas, list):
        raise Exception('The run.aditionally_supported_schemas must be of type list.')
    if not isinstance(run.allow_queries_without_filters, bool):
        raise Exception('The run.allow_queries_without_filters must be of type bool.')
    if not isinstance(run.singleEntryUrl, bool):
        raise Exception('The run.singleEntryUrl must be of type bool.')
    if not isinstance(run.analysis_lookup, bool):
        raise Exception('The run.analysis_lookup must be of type bool.')
    if not isinstance(run.biosample_lookup, bool):
        raise Exception('The run.biosample_lookup must be of type bool.')
    if not isinstance(run.cohort_lookup, bool):
        raise Exception('The run.cohort_lookup must be of type bool.')
    if not isinstance(run.dataset_lookup, bool):
        raise Exception('The run.dataset_lookup must be of type bool.')
    if not isinstance(run.genomicVariant_lookup, bool):
        raise Exception('The run.genomicVariant_lookup must be of type bool.')
    if not isinstance(run.individual_lookup, bool):
        raise Exception('The run.individual_lookup must be of type bool.')
    if conf.level not in [logging.NOTSET, logging.INFO, logging.DEBUG, logging.WARNING, logging.ERROR, logging.FATAL, logging.CRITICAL]:
        raise Exception('The config parameter level must be one possible logging library level (NOTSET, DEBUG, INFO, etc...')
    if not isinstance(conf.log_file, str):
        if conf.log_file != None:
            raise Exception('The config parameter log_file must be a string with the path to the dir where to store the logs or a variable None for not storing any log')
    if not isinstance(conf.beacon_name, str):
        raise Exception('The beacon_name config parameter must be a string')
    if not isinstance(conf.beacon_id, str):
        raise Exception('The beacon_id config parameter must be a string')
    if not isinstance(conf.api_version, str):
        raise Exception('The api_version config parameter must be a string')
    if not isinstance(conf.description, str):
        raise Exception('The description config parameter must be a string')
    if not isinstance(conf.welcome_url, str):
        raise Exception('The welcome_url config parameter must be a string')
    if not isinstance(conf.alternative_url, str):
        raise Exception('The alternative_url config parameter must be a string')
    if not isinstance(conf.create_datetime, str):
        raise Exception('The create_datetime config parameter must be a string')
    if not isinstance(conf.update_datetime, str):
        raise Exception('The update_datetime config parameter must be a string')
    if not isinstance(conf.documentation_url, str):
        raise Exception('The documentation_url config parameter must be a string')
    if not conf.welcome_url.startswith('http://'):
        if not conf.welcome_url.startswith('https://'):
            raise Exception('The url {} in cors_urls variable must start with http protocol'.format(conf.welcome_url))
    if not conf.alternative_url.startswith('http://'):
        if not conf.alternative_url.startswith('https://'):
            raise Exception('The url {} in cors_urls variable must start with http protocol'.format(conf.alternative_url))
    if not conf.documentation_url.startswith('http://'):
        if not conf.documentation_url.startswith('https://'):
            raise Exception('The url {} in cors_urls variable must start with http protocol'.format(conf.documentation_url))
    try:
        with open("/beacon/permissions/datasets/datasets_permissions.yml", 'r') as pfile:
            datasets = yaml.safe_load(pfile)
        pfile.close()
        for dataset_name, configuration in datasets.items():
            if not isinstance(configuration, bool):
                for security_level, securityconf in configuration.items():
                    if security_level not in ['public', 'registered', 'controlled']:
                        raise Exception("keys for datasets have to be public, registered, controlled for security level")
                    if not isinstance(securityconf, bool):
                        for parameters, paramsvalues in securityconf.items():
                            if parameters not in ['default_entry_types_granularity', 'entry_types_exceptions', 'user-list']:
                                raise Exception("entries for dataset settings have to be default_entry_types_granularity, entry_types_exceptions or user-list")
                            if dataset == 'controlled':
                                if parameters == 'user-list':
                                    for user in parameters:
                                        for confuser, valueuser in user.items():
                                            if confuser not in ['user_e-mail', 'default_entry_types_granularity', 'entry_types_exceptions']:
                                                raise Exception("entries for user settings in user-list must be be default_entry_types_granularity, entry_types_exceptions or user_e-mail")
    except Exception:
        raise
    try:
        with open("/beacon/conf/datasets/datasets_conf.yml", 'r') as pfile:
            datasets = yaml.safe_load(pfile)
        pfile.close()
        for dataset_name, configuration in datasets.items():
            for property, value in configuration.items():
                if property not in ['isTest', 'isSynthetic']:
                    raise Exception("keys for datasets properties in datasets_conf.yml have to be isTest or isSynthetic")
                if not isinstance(value, bool):
                    raise Exception("values for datasets properties in datasets_conf.yml have to be boolean")  
    except Exception:
        raise