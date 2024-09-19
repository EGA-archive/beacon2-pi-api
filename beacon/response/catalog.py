from beacon.response.schemas import DefaultSchemas
from beacon.request.parameters import RequestParams
from beacon.request.classes import Granularity
from beacon.conf import conf
from typing import Optional
from beacon.logs.logs import log_with_args
from beacon.conf.conf import level
from beacon.source.generator import get_entry_types, get_entry_types_map
from beacon.filtering_terms.resources import resources
from beacon.exceptions.exceptions import raise_exception

@log_with_args(level)
def build_response_summary(self, exists, num_total_results):
    try:
        if num_total_results is None:
            return {
                'exists': exists
            }
        else:
            return {
                'exists': exists,
                'numTotalResults': num_total_results
            }
    except Exception as e:
        err = str(e)
        errcode=500
        raise_exception(err, errcode)

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
    except Exception as e:
        err = str(e)
        errcode=500
        raise_exception(err, errcode)

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
        except Exception as e:
            err = str(e)
            errcode=500
            raise_exception(err, errcode)

@log_with_args(level)
def build_info_meta(self, entity_schema: Optional[DefaultSchemas]):
    try:
        meta = {
            'beaconId': conf.beacon_id,
            'apiVersion': conf.api_version,
            'returnedSchemas': [entity_schema.value] if entity_schema is not None else []
        }
        return meta
    except Exception:
        try:
            meta = {
                'beaconId': conf.beacon_id,
                'apiVersion': conf.api_version,
                'returnedSchemas': [entity_schema.value] if entity_schema is not None else []
            }
            return meta
        except Exception as e:
            err = str(e)
            errcode=500
            raise_exception(err, errcode)

@log_with_args(level)
def build_response_by_dataset(self, data, dict_counts, qparams):
    try:
        list_of_responses=[]
        for k,v in data.items():
            if v:
                response = {
                    'id': k, # TODO: Set the name of the dataset/cohort
                    'setType': 'dataset', # TODO: Set the type of collection
                    'exists': dict_counts[k] > 0,
                    'resultsCount': dict_counts[k],
                    'results': v,
                    # 'info': None,
                    'resultsHandover': 'beacon_handovers_by_dataset(k)',  # build_results_handover
                }
                
                list_of_responses.append(response)

        return list_of_responses
    except Exception:
        raise

@log_with_args(level)
def build_beacon_boolean_response_by_dataset(self, data,
                                    dict_counts,
                                    num_total_results,
                                    qparams: RequestParams,
                                    entity_schema: DefaultSchemas):
    try:
        beacon_response = {
            'meta': build_meta(self, qparams, entity_schema, Granularity.BOOLEAN),
            'responseSummary': build_response_summary_by_dataset(self, num_total_results > 0, num_total_results, data),
            'response': {
                'resultSets': build_response_by_dataset(self, data, dict_counts, qparams)
            },
            'beaconHandovers': 'beacon_handovers()',
        }
        return beacon_response
    except Exception:
        raise

@log_with_args(level)
def build_beacon_boolean_response(self, data,
                                    num_total_results,
                                    qparams: RequestParams,
                                    entity_schema: DefaultSchemas):
    try:
        beacon_response = {
            'meta': build_meta(self, qparams, entity_schema, Granularity.BOOLEAN),
            'responseSummary': build_response_summary(self, num_total_results > 0, None),
            # TODO: 'extendedInfo': build_extended_info(),
            'beaconHandovers': 'beacon_handovers()',
        }
        return beacon_response
    except Exception:
        raise

@log_with_args(level)
def build_beacon_count_response(self, data,
                                    num_total_results,
                                    qparams: RequestParams,
                                    entity_schema: DefaultSchemas):
    try:
        beacon_response = {
            'meta': build_meta(self, qparams, entity_schema, Granularity.COUNT),
            'responseSummary': build_response_summary(self, num_total_results > 0, num_total_results),
            # TODO: 'extendedInfo': build_extended_info(),
            'beaconHandovers': 'beacon_handovers()',
        }
        return beacon_response
    except Exception:
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
    except Exception:
        raise

@log_with_args(level)
def build_beacon_collection_response(self, data, num_total_results, qparams: RequestParams, entity_schema: DefaultSchemas):
    try:
        beacon_response = {
            'meta': build_meta(self, qparams, entity_schema, Granularity.RECORD),
            'responseSummary': build_response_summary(self, num_total_results > 0, num_total_results),
            # TODO: 'info': build_extended_info(),
            'beaconHandovers': "beacon_handovers()",
            'response': {
                'collections': data
            }
        }
        return beacon_response
    except Exception:
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
    except Exception as e:
        err = str(e)
        errcode=500
        raise_exception(err, errcode)

@log_with_args(level)
def build_configuration(self):
    try:
        entry_types=get_entry_types(self)
    except Exception:
        raise
    try:
        meta = {
            '$schema': 'https://raw.githubusercontent.com/ga4gh-beacon/beacon-framework-v2/main/responses/sections/beaconInformationalResponseMeta.json',
            'beaconId': conf.beacon_id,
            'apiVersion': conf.api_version,
            'returnedSchemas': []
        }

        response = {
            '$schema': 'https://raw.githubusercontent.com/ga4gh-beacon/beacon-framework-v2/main/configuration/beaconConfigurationSchema.json',
            'maturityAttributes': {
                'productionStatus': conf.environment.upper()
            },
            'securityAttributes': {
                'defaultGranularity': conf.default_beacon_granularity,
                'securityLevels': conf.security_levels
            },
            'entryTypes': entry_types
        }

        configuration_json = {
            '$schema': 'https://raw.githubusercontent.com/ga4gh-beacon/beacon-framework-v2/main/responses/beaconConfigurationResponse.json',
            'meta': meta,
            'response': response
        }

        return configuration_json
    except Exception as e:
        err = str(e)
        errcode=500
        raise_exception(err, errcode)

@log_with_args(level)
def build_map(self):
    try:
        response = get_entry_types_map(self)
    except Exception:
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
    except Exception as e:
        err = str(e)
        errcode=500
        raise_exception(err, errcode)

@log_with_args(level)
def build_entry_types(self):
    try:
        response = get_entry_types(self)
    except Exception:
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
    except Exception as e:
        err = str(e)
        errcode=500
        raise_exception(err, errcode)

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
    except Exception as e:
        err = str(e)
        errcode=500
        raise_exception(err, errcode)

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
            'beaconHandovers': "beacon_handovers()",
        }
        return beacon_response
    except Exception:
        raise