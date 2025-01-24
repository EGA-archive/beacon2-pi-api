from aiohttp.web_request import Request
from beacon.response.catalog import build_beacon_record_response_by_dataset, build_beacon_count_response, build_beacon_collection_response, build_beacon_info_response, build_map, build_configuration, build_entry_types, build_beacon_service_info_response, build_filtering_terms_response, build_beacon_boolean_response, build_beacon_none_response
from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level, max_beacon_granularity, test_datasetId
from beacon.request.classes import Granularity
from beacon.source.manage import analyses, biosamples, cohorts, datasets, g_variants, individuals, runs, filtering_terms

@log_with_args(level)
async def builder(self, request: Request, datasets, qparams, entry_type, entry_id):
    granularity = qparams.query.requested_granularity
    try:
        if '_' in entry_type and 'g_variants' not in entry_type:
            source_entry_type = entry_type.split('_')
            source_entry_type = source_entry_type[1]
            if source_entry_type == 'analyses':
                source = analyses['database']
                source_granularity = analyses['granularity']
            elif source_entry_type == 'biosamples':
                source = biosamples['database']
                source_granularity = biosamples['granularity']
            elif source_entry_type == 'individuals':
                source = individuals['database']
                source_granularity = individuals['granularity']
            elif source_entry_type == 'runs':
                source = runs['database']
                source_granularity = runs['granularity']
        elif entry_type == 'g_variants':
            source = g_variants['database']
            source_granularity = g_variants['granularity']
        elif '_' in entry_type:
            source = g_variants['database']
            source_granularity = g_variants['granularity']
        elif entry_type == 'analyses':
            source = analyses['database']
            source_granularity = analyses['granularity']
        elif entry_type == 'biosamples':
            source = biosamples['database']
            source_granularity = biosamples['granularity']
        elif entry_type == 'individuals':
            source = individuals['database']
            source_granularity = individuals['granularity']
        elif entry_type == 'runs':
            source = runs['database']
            source_granularity = runs['granularity']
        if source_granularity['record']==True:
            allowed_granularity='record'
        elif source_granularity['count']==True:# pragma: no cover
            allowed_granularity='count'
        else:# pragma: no cover
            allowed_granularity='boolean'
        complete_module='beacon.connections.'+source+'.executor'
        import importlib
        module = importlib.import_module(complete_module, package=None)
        testMode = qparams.query.test_mode
        if testMode == True:
            datasets = [test_datasetId]
        datasets_docs, datasets_count, count, entity_schema, include, datasets = await module.execute_function(self, entry_type, datasets, qparams, entry_id)
        if include != 'NONE' and granularity == Granularity.RECORD and max_beacon_granularity == 'record' and allowed_granularity=='record':
            response = build_beacon_record_response_by_dataset(self, datasets, datasets_docs, datasets_count, count, qparams, entity_schema)
        elif include == 'NONE' and granularity == Granularity.RECORD and max_beacon_granularity == 'record' and allowed_granularity=='record':
            response = build_beacon_none_response(self, datasets_docs["NONE"], count, qparams, entity_schema)
        elif granularity == Granularity.COUNT and max_beacon_granularity in ['count', 'record'] and allowed_granularity in ['count', 'record']:
            response = build_beacon_count_response(self, count, qparams, entity_schema)
        elif granularity == Granularity.RECORD and max_beacon_granularity in ['count'] and allowed_granularity in ['count', 'record']:# pragma: no cover
            response = build_beacon_count_response(self, count, qparams, entity_schema)
        elif granularity == Granularity.RECORD and allowed_granularity in ['count'] and max_beacon_granularity in ['count', 'record']:# pragma: no cover
            response = build_beacon_count_response(self, count, qparams, entity_schema)
        else:# pragma: no cover
            response = build_beacon_boolean_response(self, count, qparams, entity_schema)
        return response
    except Exception:# pragma: no cover
        raise

@log_with_args(level)
async def collection_builder(self, request: Request, qparams, entry_type, entry_id):
    try:
        if entry_type == 'datasets':
            source = datasets['database']
        elif entry_type == 'cohorts':
            source = cohorts['database']
        complete_module='beacon.connections.'+source+'.executor'
        import importlib
        module = importlib.import_module(complete_module, package=None)
        response_converted, count, entity_schema = await module.execute_collection_function(self, entry_type, qparams, entry_id)
        response = build_beacon_collection_response(
                    self, response_converted, count, qparams, entity_schema
                )
        return response
    except Exception:# pragma: no cover
        raise

@log_with_args(level)
async def info_builder(self, request: Request):
    try:
        response = build_beacon_info_response(
                    self
                )
        return response
    except Exception:# pragma: no cover
        raise

@log_with_args(level)
async def configuration_builder(self, request: Request):
    try:
        response = build_configuration(
                    self
                )
        return response
    except Exception:# pragma: no cover
        raise

@log_with_args(level)
async def map_builder(self, request: Request):
    try:
        response = build_map(
                    self
                )
        return response
    except Exception:# pragma: no cover
        raise

@log_with_args(level)
async def entry_types_builder(self, request: Request):
    try:
        response = build_entry_types(
                    self
                )
        return response
    except Exception:# pragma: no cover
        raise

@log_with_args(level)
async def service_info_builder(self, request: Request):
    try:
        response = build_beacon_service_info_response(
                    self
                )
        return response
    except Exception:# pragma: no cover
        raise

@log_with_args(level)
async def filtering_terms_builder(self, request: Request, qparams):
    source=filtering_terms['database']
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