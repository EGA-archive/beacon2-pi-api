from aiohttp.web_request import Request
from beacon.response.catalog import build_beacon_record_response_by_dataset, build_beacon_count_response, build_beacon_collection_response, build_beacon_info_response, build_map, build_configuration, build_entry_types, build_beacon_service_info_response, build_filtering_terms_response, build_beacon_boolean_response
from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level
from beacon.request.classes import Granularity, RequestAttributes
from beacon.conf import analysis, biosample, cohort, dataset, genomicVariant, individual, run, filtering_terms

@log_with_args(level)
async def builder(self, datasets, qparams):
    granularity = qparams.query.requestedGranularity
    try:
        complete_module='beacon.connections.'+RequestAttributes.source+'.executor'
        import importlib
        module = importlib.import_module(complete_module, package=None)
        datasets_docs, datasets_count, count, entity_schema, include, datasets = await module.execute_function(self, datasets, qparams)
        if qparams.query.includeResultsetResponses != 'NONE':
            response = build_beacon_record_response_by_dataset(self, datasets, datasets_docs, datasets_count, count, qparams, entity_schema)
        elif qparams.query.includeResultsetResponses == 'NONE' and RequestAttributes.allowed_granularity in ['count','record'] and granularity in ['count', 'record']:
            response = build_beacon_count_response(self, datasets, datasets_docs, datasets_count, count, qparams, entity_schema)
        else:# pragma: no cover
            response = build_beacon_boolean_response(self, count, qparams, entity_schema)
        return response
    except Exception:# pragma: no cover
        raise

@log_with_args(level)
async def collection_builder(self, qparams):
    try:
        if RequestAttributes.entry_type == dataset.endpoint_name:
            source = dataset.database
        elif RequestAttributes.entry_type == cohort.endpoint_name:
            source = cohort.database
        complete_module='beacon.connections.'+source+'.executor'
        import importlib
        module = importlib.import_module(complete_module, package=None)
        response_converted, count, entity_schema = await module.execute_collection_function(self, qparams)
        response = build_beacon_collection_response(
                    self, response_converted, count, qparams, entity_schema
                )
        return response
    except Exception:# pragma: no cover
        raise

@log_with_args(level)
async def info_builder(self):
    try:
        response = build_beacon_info_response(
                    self
                )
        return response
    except Exception:# pragma: no cover
        raise

@log_with_args(level)
async def configuration_builder(self):
    try:
        response = build_configuration(
                    self
                )
        return response
    except Exception:# pragma: no cover
        raise

@log_with_args(level)
async def map_builder(self):
    try:
        response = build_map(
                    self
                )
        return response
    except Exception:# pragma: no cover
        raise

@log_with_args(level)
async def entry_types_builder(self):
    try:
        response = build_entry_types(
                    self
                )
        return response
    except Exception:# pragma: no cover
        raise

@log_with_args(level)
async def service_info_builder(self):
    try:
        response = build_beacon_service_info_response(
                    self
                )
        return response
    except Exception:# pragma: no cover
        raise

@log_with_args(level)
async def filtering_terms_builder(self, qparams):
    source=filtering_terms.database
    complete_module='beacon.connections.'+source+'.filtering_terms'
    import importlib
    module = importlib.import_module(complete_module, package=None)
    try:
        entity_schema, count, records = module.get_filtering_terms(self, qparams)
        response = build_filtering_terms_response(
                    self, records, count, qparams, entity_schema
                )
        return response
    except Exception:# pragma: no cover
        raise