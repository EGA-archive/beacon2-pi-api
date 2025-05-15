from beacon.response.schemas import DefaultSchemas
from beacon.request.parameters import RequestParams
from beacon.request.classes import Granularity, ErrorClass
from beacon.conf import conf
from typing import Optional
from beacon.logs.logs import log_with_args
from beacon.conf.conf import level
from beacon.conf import analysis, biosample, cohort, dataset, genomicVariant, individual, run
from beacon.source.generator import get_entry_types, get_entry_types_map
from beacon.filtering_terms.resources import resources
from beacon.utils.handovers import list_of_handovers, list_of_handovers_per_dataset
import json

def build_response(self, data, num_total_results, qparams):
    """"Fills the `response` part with the correct format in `results`"""
    limit = qparams.query.pagination.limit
    include = qparams.query.include_resultset_responses
    if include == 'NONE':
            response = {
            'id': '', # TODO: Set the name of the dataset/cohort
            'setType': '', # TODO: Set the type of collection
            'exists': num_total_results > 0,
            'resultsCount': num_total_results,
            'results': data,
            # 'info': None,
            'resultsHandover': list_of_handovers,  # build_results_handover
        }
    elif limit != 0 and limit < num_total_results:# pragma: no cover
        response = {
            'id': '', # TODO: Set the name of the dataset/cohort
            'setType': '', # TODO: Set the type of collection
            'exists': num_total_results > 0,
            'resultsCount': limit,
            'results': data,
            # 'info': None,
            'resultsHandover': list_of_handovers,  # build_results_handover
        }
    else:# pragma: no cover
        response = {
            'id': '', # TODO: Set the name of the dataset/cohort
            'setType': '', # TODO: Set the type of collection
            'exists': num_total_results > 0,
            'resultsCount': num_total_results,
            'results': data,
            # 'info': None,
            'resultsHandover': list_of_handovers,  # build_results_handover
        }

    return response



@log_with_args(level)
def build_response_summary(self, exists, num_total_results):
    try:
        if num_total_results is None:# pragma: no cover
            return {
                'exists': exists
            }
        else:
            return {
                'exists': exists,
                'numTotalResults': num_total_results
            }
    except Exception as e:# pragma: no cover
        ErrorClass.error_code=500
        ErrorClass.error_message=str(e)
        raise

@log_with_args(level)
def build_response_summary_by_dataset(self, exists, num_total_results, data):
    try:
        count=num_total_results
        if count == 0:
            return {
                'exists': count > 0
            }
        else:
            return {
                'exists': count > 0,
                'numTotalResults': count
            }
    except Exception as e:# pragma: no cover
        ErrorClass.error_code=500
        ErrorClass.error_message=str(e)
        raise

@log_with_args(level)
def build_meta(self, qparams: RequestParams, entity_schema: Optional[DefaultSchemas], returned_granularity: Granularity):
    try:
        meta = {
            'beaconId': conf.beacon_id,
            'apiVersion': conf.api_version,
            'returnedGranularity': returned_granularity,
            'receivedRequestSummary': qparams.summary(),
            'returnedSchemas': [entity_schema.value] if entity_schema is not None else []
        }
        return meta
    except Exception:
        try:
            meta = {
                'beaconId': conf.beacon_id,
                'apiVersion': conf.api_version,
                'returnedGranularity': returned_granularity,
                'receivedRequestSummary': qparams,
                'returnedSchemas': [entity_schema.value] if entity_schema is not None else []
            }
            return meta
        except Exception as e:# pragma: no cover
            ErrorClass.error_code=500
            ErrorClass.error_message=str(e)
            raise

@log_with_args(level)
def build_info_meta(self, entity_schema: Optional[DefaultSchemas]):
    try:
        meta = {
            'beaconId': conf.beacon_id,
            'apiVersion': conf.api_version,
            'returnedSchemas': [entity_schema.value] if entity_schema is not None else []
        }
        return meta
    except Exception:# pragma: no cover
        try:
            meta = {
                'beaconId': conf.beacon_id,
                'apiVersion': conf.api_version,
                'returnedSchemas': [entity_schema.value] if entity_schema is not None else []
            }
            return meta
        except Exception as e:
            ErrorClass.error_code=500
            ErrorClass.error_message=str(e)
            raise

@log_with_args(level)
def build_response_by_dataset(self, datasets, data, dict_counts, qparams):
    try:
        list_of_responses=[]
        for dataset in datasets:
            for handover in list_of_handovers_per_dataset:
                if handover["dataset"]==dataset:# pragma: no cover
                    response = {
                        'id': dataset, # TODO: Set the name of the dataset/cohort
                        'setType': 'dataset', # TODO: Set the type of collection
                        'exists': dict_counts[dataset] > 0,
                        'resultsCount': dict_counts[dataset],
                        'results': data[dataset],
                        # 'info': None,
                        'resultsHandover': handover["handover"]  # build_results_handover
                    }
                else:
                    response = {
                        'id': dataset, # TODO: Set the name of the dataset/cohort
                        'setType': 'dataset', # TODO: Set the type of collection
                        'exists': dict_counts[dataset] > 0,
                        'resultsCount': dict_counts[dataset],
                        'results': data[dataset]
                    }
            list_of_responses.append(response)

        return list_of_responses
    except Exception:# pragma: no cover
        raise

@log_with_args(level)
def build_beacon_record_response_by_dataset(self, datasets, data,
                                    dict_counts,
                                    num_total_results,
                                    qparams: RequestParams,
                                    entity_schema: DefaultSchemas):
    try:
        beacon_response = {
            'meta': build_meta(self, qparams, entity_schema, Granularity.RECORD),
            'responseSummary': build_response_summary_by_dataset(self, num_total_results > 0, num_total_results, data),
            'response': {
                'resultSets': build_response_by_dataset(self, datasets, data, dict_counts, qparams)
            },
            'beaconHandovers': list_of_handovers,
        }
        return beacon_response
    except Exception:# pragma: no cover
        raise

@log_with_args(level)
def build_beacon_boolean_response(self,
                                    num_total_results,
                                    qparams: RequestParams,
                                    entity_schema: DefaultSchemas):
    try:# pragma: no cover
        beacon_response = {
            'meta': build_meta(self, qparams, entity_schema, Granularity.BOOLEAN),
            'responseSummary': build_response_summary(self, num_total_results > 0, None),
            # TODO: 'extendedInfo': build_extended_info(),
            'beaconHandovers': list_of_handovers,
        }
        return beacon_response
    except Exception:# pragma: no cover
        raise

@log_with_args(level)
def build_beacon_count_response(self,
                                    num_total_results,
                                    qparams: RequestParams,
                                    entity_schema: DefaultSchemas):
    try:
        beacon_response = {
            'meta': build_meta(self, qparams, entity_schema, Granularity.COUNT),
            'responseSummary': build_response_summary(self, num_total_results > 0, num_total_results),
            # TODO: 'extendedInfo': build_extended_info(),
            'beaconHandovers': list_of_handovers,
        }
        return beacon_response
    except Exception:# pragma: no cover
        raise

@log_with_args(level)
def build_beacon_none_response(self, data,
                                    num_total_results,
                                    qparams: RequestParams,
                                    entity_schema: DefaultSchemas):
    try:
        beacon_response = {
            'meta': build_meta(self, qparams, entity_schema, Granularity.RECORD),
            'responseSummary': build_response_summary_by_dataset(self, num_total_results > 0, num_total_results, data),
            'response': {
                'resultSets': [build_response(self, data, num_total_results, qparams)]
            },
            'beaconHandovers': list_of_handovers,
        }
        return beacon_response
    except Exception:# pragma: no cover
        raise

@log_with_args(level)
def build_beacon_error_response(self, errorCode, qparams, errorMessage):
    try:
        beacon_response = {
            'meta': build_meta(self, qparams, None, Granularity.RECORD),
            'error': {
                'errorCode': str(errorCode),
                'errorMessage': str(errorMessage)
            }
        }
        return beacon_response
    except Exception:# pragma: no cover
        raise

@log_with_args(level)
def build_beacon_collection_response(self, data, num_total_results, qparams: RequestParams, entity_schema: DefaultSchemas):
    try:
        beacon_response = {
            'meta': build_meta(self, qparams, entity_schema, Granularity.RECORD),
            'responseSummary': build_response_summary(self, num_total_results > 0, num_total_results),
            # TODO: 'info': build_extended_info(),
            'beaconHandovers': list_of_handovers,
            'response': {
                'collections': data
            }
        }
        return beacon_response
    except Exception:# pragma: no cover
        raise

@log_with_args(level)
def build_beacon_info_response(self):
    try:
        beacon_response = {
            'meta': build_info_meta(self, None),
            'response': {
                'id': conf.beacon_id,
                'name': conf.beacon_name,
                'apiVersion': conf.api_version,
                'environment': conf.environment,
                'organization': {
                    'id': conf.org_id,
                    'name': conf.org_name,
                    'description': conf.org_description,
                    'address': conf.org_adress,
                    'welcomeUrl': conf.org_welcome_url,
                    'contactUrl': conf.org_contact_url,
                    'logoUrl': conf.org_logo_url,
                },
                'description': conf.description,
                'version': conf.version,
                'welcomeUrl': conf.welcome_url,
                'alternativeUrl': conf.alternative_url,
                'createDateTime': conf.create_datetime,
                'updateDateTime': conf.update_datetime
            }
        }
        return beacon_response
    except Exception as e:# pragma: no cover
        ErrorClass.error_code=500
        ErrorClass.error_message=str(e)
        raise

@log_with_args(level)
def build_configuration(self):
    try:
        entry_types=get_entry_types(self)
    except Exception:# pragma: no cover
        raise
    try:
        meta = {
            '$schema': 'https://raw.githubusercontent.com/ga4gh-beacon/beacon-framework-v2/main/responses/sections/beaconInformationalResponseMeta.json',
            'beaconId': conf.beacon_id,
            'apiVersion': conf.api_version,
            'returnedSchemas': []
        }

        with open('beacon/response/templates/configuration.json', 'r') as template:
            response = json.load(template)

        response['securityAttributes']['defaultGranularity']=conf.max_beacon_granularity
        response['securityAttributes']['securityLevels']=conf.security_levels
        response['maturityAttributes']['productionStatus']=conf.environment.upper()

        if analysis.boolean!=False and analysis.count!=False and analysis.record!=False:
            response['entryTypes'][analysis.id]==response['entryTypes']['analysis']
            del response['entryTypes']['analysis']
            response['entryTypes'][analysis.id]={}
            response['entryTypes'][analysis.id]["id"]=analysis.id
            response['entryTypes'][analysis.id]["name"]=analysis.name
            response['entryTypes'][analysis.id]['ontologyTermForThisType']={}
            response['entryTypes'][analysis.id]['ontologyTermForThisType']['id']=analysis.ontology_id
            response['entryTypes'][analysis.id]['ontologyTermForThisType']['name']=analysis.ontology_name
            response['entryTypes'][analysis.id]['partOfSpecification']=analysis.specification
            response['entryTypes'][analysis.id]['description']=analysis.description
            response['entryTypes'][analysis.id]['defaultSchema']={}
            response['entryTypes'][analysis.id]['defaultSchema']['id']=analysis.defaultSchema_id
            response['entryTypes'][analysis.id]['defaultSchema']['name']=analysis.defaultSchema_name
            response['entryTypes'][analysis.id]['defaultSchema']['referenceToSchemaDefinition']=analysis.defaultSchema_reference_to_schema_definition
            response['entryTypes'][analysis.id]['defaultSchema']['schemaVersion']=analysis.defaultSchema_schema_version
            response['entryTypes'][analysis.id]['additionallySupportedSchemas']=analysis.aditionally_supported_schemas
            response['entryTypes'][analysis.id]['nonFilteredQueriesAllowed']=analysis.allow_queries_without_filters
        if biosample.boolean!=False and biosample.count!=False and biosample.record!=False:
            response['entryTypes'][biosample.id]==response['entryTypes']['biosample']
            del response['entryTypes']['biosample']
            response['entryTypes'][biosample.id]={}
            response['entryTypes'][biosample.id]["id"]=biosample.id
            response['entryTypes'][biosample.id]["name"]=biosample.name
            response['entryTypes'][biosample.id]['ontologyTermForThisType']={}
            response['entryTypes'][biosample.id]['ontologyTermForThisType']['id']=biosample.ontology_id
            response['entryTypes'][biosample.id]['ontologyTermForThisType']['name']=biosample.ontology_name
            response['entryTypes'][biosample.id]['partOfSpecification']=biosample.specification
            response['entryTypes'][biosample.id]['description']=biosample.description
            response['entryTypes'][biosample.id]['defaultSchema']={}
            response['entryTypes'][biosample.id]['defaultSchema']['id']=biosample.defaultSchema_id
            response['entryTypes'][biosample.id]['defaultSchema']['name']=biosample.defaultSchema_name
            response['entryTypes'][biosample.id]['defaultSchema']['referenceToSchemaDefinition']=biosample.defaultSchema_reference_to_schema_definition
            response['entryTypes'][biosample.id]['defaultSchema']['schemaVersion']=biosample.defaultSchema_schema_version
            response['entryTypes'][biosample.id]['additionallySupportedSchemas']=biosample.aditionally_supported_schemas
            response['entryTypes'][biosample.id]['nonFilteredQueriesAllowed']=biosample.allow_queries_without_filters
        if cohort.boolean!=False and cohort.count!=False and cohort.record!=False:
            response['entryTypes'][cohort.id]==response['entryTypes']['cohort']
            del response['entryTypes']['cohort']
            response['entryTypes'][cohort.id]={}
            response['entryTypes'][cohort.id]["id"]=cohort.id
            response['entryTypes'][cohort.id]["name"]=cohort.name
            response['entryTypes'][cohort.id]['ontologyTermForThisType']={}
            response['entryTypes'][cohort.id]['ontologyTermForThisType']['id']=cohort.ontology_id
            response['entryTypes'][cohort.id]['ontologyTermForThisType']['name']=cohort.ontology_name
            response['entryTypes'][cohort.id]['partOfSpecification']=cohort.specification
            response['entryTypes'][cohort.id]['description']=cohort.description
            response['entryTypes'][cohort.id]['defaultSchema']={}
            response['entryTypes'][cohort.id]['defaultSchema']['id']=cohort.defaultSchema_id
            response['entryTypes'][cohort.id]['defaultSchema']['name']=cohort.defaultSchema_name
            response['entryTypes'][cohort.id]['defaultSchema']['referenceToSchemaDefinition']=cohort.defaultSchema_reference_to_schema_definition
            response['entryTypes'][cohort.id]['defaultSchema']['schemaVersion']=cohort.defaultSchema_schema_version
            response['entryTypes'][cohort.id]['additionallySupportedSchemas']=cohort.aditionally_supported_schemas
            response['entryTypes'][cohort.id]['nonFilteredQueriesAllowed']=cohort.allow_queries_without_filters
        if dataset.boolean!=False and dataset.count!=False and dataset.record!=False:
            response['entryTypes'][dataset.id]==response['entryTypes']['dataset']
            del response['entryTypes']['dataset']
            response['entryTypes'][dataset.id]={}
            response['entryTypes'][dataset.id]["id"]=dataset.id
            response['entryTypes'][dataset.id]["name"]=dataset.name
            response['entryTypes'][dataset.id]['ontologyTermForThisType']={}
            response['entryTypes'][dataset.id]['ontologyTermForThisType']['id']=dataset.ontology_id
            response['entryTypes'][dataset.id]['ontologyTermForThisType']['name']=dataset.ontology_name
            response['entryTypes'][dataset.id]['partOfSpecification']=dataset.specification
            response['entryTypes'][dataset.id]['description']=dataset.description
            response['entryTypes'][dataset.id]['defaultSchema']={}
            response['entryTypes'][dataset.id]['defaultSchema']['id']=dataset.defaultSchema_id
            response['entryTypes'][dataset.id]['defaultSchema']['name']=dataset.defaultSchema_name
            response['entryTypes'][dataset.id]['defaultSchema']['referenceToSchemaDefinition']=dataset.defaultSchema_reference_to_schema_definition
            response['entryTypes'][dataset.id]['defaultSchema']['schemaVersion']=dataset.defaultSchema_schema_version
            response['entryTypes'][dataset.id]['additionallySupportedSchemas']=dataset.aditionally_supported_schemas
            response['entryTypes'][dataset.id]['nonFilteredQueriesAllowed']=dataset.allow_queries_without_filters
        if genomicVariant.boolean!=False and genomicVariant.count!=False and genomicVariant.record!=False:
            response['entryTypes'][genomicVariant.id]==response['entryTypes']['genomicVariant']
            del response['entryTypes']['genomicVariant']
            response['entryTypes'][genomicVariant.id]={}
            response['entryTypes'][genomicVariant.id]["id"]=genomicVariant.id
            response['entryTypes'][genomicVariant.id]["name"]=genomicVariant.name
            response['entryTypes'][genomicVariant.id]['ontologyTermForThisType']={}
            response['entryTypes'][genomicVariant.id]['ontologyTermForThisType']['id']=genomicVariant.ontology_id
            response['entryTypes'][genomicVariant.id]['ontologyTermForThisType']['name']=genomicVariant.ontology_name
            response['entryTypes'][genomicVariant.id]['partOfSpecification']=genomicVariant.specification
            response['entryTypes'][genomicVariant.id]['description']=genomicVariant.description
            response['entryTypes'][genomicVariant.id]['defaultSchema']={}
            response['entryTypes'][genomicVariant.id]['defaultSchema']['id']=genomicVariant.defaultSchema_id
            response['entryTypes'][genomicVariant.id]['defaultSchema']['name']=genomicVariant.defaultSchema_name
            response['entryTypes'][genomicVariant.id]['defaultSchema']['referenceToSchemaDefinition']=genomicVariant.defaultSchema_reference_to_schema_definition
            response['entryTypes'][genomicVariant.id]['defaultSchema']['schemaVersion']=genomicVariant.defaultSchema_schema_version
            response['entryTypes'][genomicVariant.id]['additionallySupportedSchemas']=genomicVariant.aditionally_supported_schemas
            response['entryTypes'][genomicVariant.id]['nonFilteredQueriesAllowed']=genomicVariant.allow_queries_without_filters
        if individual.boolean!=False and individual.count!=False and individual.record!=False:
            response['entryTypes'][individual.id]==response['entryTypes']['individual']
            del response['entryTypes']['individual']
            response['entryTypes'][individual.id]={}
            response['entryTypes'][individual.id]["id"]=individual.id
            response['entryTypes'][individual.id]["name"]=individual.name
            response['entryTypes'][individual.id]['ontologyTermForThisType']={}
            response['entryTypes'][individual.id]['ontologyTermForThisType']['id']=individual.ontology_id
            response['entryTypes'][individual.id]['ontologyTermForThisType']['name']=individual.ontology_name
            response['entryTypes'][individual.id]['partOfSpecification']=individual.specification
            response['entryTypes'][individual.id]['description']=individual.description
            response['entryTypes'][individual.id]['defaultSchema']={}
            response['entryTypes'][individual.id]['defaultSchema']['id']=individual.defaultSchema_id
            response['entryTypes'][individual.id]['defaultSchema']['name']=individual.defaultSchema_name
            response['entryTypes'][individual.id]['defaultSchema']['referenceToSchemaDefinition']=individual.defaultSchema_reference_to_schema_definition
            response['entryTypes'][individual.id]['defaultSchema']['schemaVersion']=individual.defaultSchema_schema_version
            response['entryTypes'][individual.id]['additionallySupportedSchemas']=individual.aditionally_supported_schemas
            response['entryTypes'][individual.id]['nonFilteredQueriesAllowed']=individual.allow_queries_without_filters
        if run.boolean!=False and run.count!=False and run.record!=False:
            response['entryTypes'][run.id]==response['entryTypes']['run']
            del response['entryTypes']['run']
            response['entryTypes'][run.id]={}
            response['entryTypes'][run.id]["id"]=run.id
            response['entryTypes'][run.id]["name"]=run.name
            response['entryTypes'][run.id]['ontologyTermForThisType']={}
            response['entryTypes'][run.id]['ontologyTermForThisType']['id']=run.ontology_id
            response['entryTypes'][run.id]['ontologyTermForThisType']['name']=run.ontology_name
            response['entryTypes'][run.id]['partOfSpecification']=run.specification
            response['entryTypes'][run.id]['description']=run.description
            response['entryTypes'][run.id]['defaultSchema']={}
            response['entryTypes'][run.id]['defaultSchema']['id']=run.defaultSchema_id
            response['entryTypes'][run.id]['defaultSchema']['name']=run.defaultSchema_name
            response['entryTypes'][run.id]['defaultSchema']['referenceToSchemaDefinition']=run.defaultSchema_reference_to_schema_definition
            response['entryTypes'][run.id]['defaultSchema']['schemaVersion']=run.defaultSchema_schema_version
            response['entryTypes'][run.id]['additionallySupportedSchemas']=run.aditionally_supported_schemas
            response['entryTypes'][run.id]['nonFilteredQueriesAllowed']=run.allow_queries_without_filters

        configuration_json = {
            '$schema': 'https://raw.githubusercontent.com/ga4gh-beacon/beacon-framework-v2/main/responses/beaconConfigurationResponse.json',
            'meta': meta,
            'response': response
        }

        return configuration_json
    except Exception as e:# pragma: no cover
        ErrorClass.error_code=500
        ErrorClass.error_message=str(e)
        raise

@log_with_args(level)
def build_map(self):
    try:
        response = get_entry_types_map(self)
    except Exception:# pragma: no cover
        raise
    try:
        meta = {
            '$schema': 'https://raw.githubusercontent.com/ga4gh-beacon/beacon-framework-v2/main/responses/sections/beaconInformationalResponseMeta.json',
            'beaconId': conf.beacon_id,
            'apiVersion': conf.api_version,
            'returnedSchemas': []
        }

        response['$schema'] ='https://raw.githubusercontent.com/ga4gh-beacon/beacon-framework-v2/main/configuration/beaconMapSchema.json'

        beacon_map_json = {
            'meta': meta,
            'response': response
        }

        return beacon_map_json
    except Exception as e:# pragma: no cover
        ErrorClass.error_code=500
        ErrorClass.error_message=str(e)
        raise

@log_with_args(level)
def build_entry_types(self):
    try:
        response = get_entry_types(self)
    except Exception:# pragma: no cover
        raise
    try:
        meta = {
            'beaconId': conf.beacon_id,
            'apiVersion': conf.api_version,
            'returnedSchemas': []
        }

        entry_types_json = {
            'meta': meta,
            'response': response
        }

        return entry_types_json
    except Exception as e:# pragma: no cover
        ErrorClass.error_code=500
        ErrorClass.error_message=str(e)
        raise

@log_with_args(level)
def build_beacon_service_info_response(self):
    try:
        beacon_response = {
            'id': conf.beacon_id,
            'name': conf.beacon_name,
            'type': {
                'group': conf.ga4gh_service_type_group,
                'artifact': conf.ga4gh_service_type_artifact,
                'version': conf.ga4gh_service_type_version
            },
            'description': conf.description,
            'organization': {
                'name': conf.org_name,
                'url': conf.org_welcome_url
            },
            'contactUrl': conf.org_contact_url,
            'documentationUrl': conf.documentation_url,
            'createdAt': conf.create_datetime,
            'updatedAt': conf.update_datetime,
            'environment': conf.environment,
            'version': conf.version,
        }
        return beacon_response
    except Exception as e:# pragma: no cover
        ErrorClass.error_code=500
        ErrorClass.error_message=str(e)
        raise

@log_with_args(level)
def build_filtering_terms_response(self, data,
                                    num_total_results,
                                    qparams: RequestParams,
                                    entity_schema: DefaultSchemas):
    try:
        beacon_response = {
            'meta': build_meta(self, qparams, entity_schema, Granularity.RECORD),
            'responseSummary': build_response_summary(self, num_total_results > 0, num_total_results),
            # TODO: 'extendedInfo': build_extended_info(),
            'response': {
                'filteringTerms': data,
                'resources': resources
            },
            'beaconHandovers': list_of_handovers,
        }
        return beacon_response
    except Exception:# pragma: no cover
        raise