from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level
from beacon.request.classes import Granularity, RequestAttributes
from beacon.conf import analysis, biosample, cohort, dataset, genomicVariant, individual, run, filtering_terms as fterms, conf
import json
from beacon.validator.framework import (Info, 
                                        InfoResponse, 
                                        ResponseSummary, 
                                        ResultsetInstance, 
                                        Meta, 
                                        ResultsetsResponse, 
                                        Resultsets, 
                                        CountResponseSummary, 
                                        BooleanResponseSummary, 
                                        CountResponse, 
                                        BooleanResponse, 
                                        CollectionResponse, 
                                        Collection, 
                                        InformationalMeta,
                                        ConfigurationSchema,
                                        ConfigurationResponse,
                                        MapResponse,
                                        MapSchema,
                                        EntryTypesSchema,
                                        EntryTypesResponse,
                                        ServiceInfo,
                                        FilteringTermsResults,
                                        FilteringTermsResponse,
                                        ErrorResponse,
                                        BeaconError)
from pydantic import create_model, Field, ValidationError
from typing import Optional

@log_with_args(level)
async def builder(self, datasets):
    try:
        complete_module='beacon.connections.'+RequestAttributes.source+'.executor'
        import importlib
        module = importlib.import_module(complete_module, package=None)
        datasets_docs, datasets_count, count, include, datasets = await module.execute_function(self, datasets)
        if RequestAttributes.response_type == 'resultSet':
            with open('beacon/response/templates/{}/resultSetsResponse.json'.format(RequestAttributes.returned_apiVersion), 'r') as template:
                response = json.load(template)
            meta = Meta(receivedRequestSummary=RequestAttributes.qparams.summary(),returnedGranularity=RequestAttributes.returned_granularity,returnedSchemas=RequestAttributes.returned_schema,testMode=RequestAttributes.qparams.query.testMode)
            responseSummary = ResponseSummary.build_response_summary_by_dataset(ResponseSummary, datasets, datasets_count)
            list_of_resultSets=[]
            for dataset in datasets:
                resultSet = ResultsetInstance.build_response_by_dataset(ResultsetInstance,dataset, datasets_docs, datasets_count,RequestAttributes.allowed_granularity,RequestAttributes.qparams.query.requestedGranularity)
                list_of_resultSets.append(resultSet)
            resultSets = Resultsets.return_resultSets(Resultsets, list_of_resultSets)
            resultSetsResponse = ResultsetsResponse.return_response(ResultsetsResponse, meta, resultSets, responseSummary)
            resultSetsResponse = resultSetsResponse.model_dump(exclude_none=True)
            resultSetsFromTemplate = create_model('resultSetsFromTemplate', **{k: (Optional[type(v)], None) for k, v in response.items()})
            response = resultSetsFromTemplate.model_validate(resultSetsResponse)
            response = response.model_dump(exclude_none=True)
        elif RequestAttributes.response_type == 'count':
            with open('beacon/response/templates/{}/count.json'.format(RequestAttributes.returned_apiVersion), 'r') as template:
                response = json.load(template)
            meta = Meta(receivedRequestSummary=RequestAttributes.qparams.summary(),returnedGranularity=RequestAttributes.returned_granularity,returnedSchemas=RequestAttributes.returned_schema,testMode=RequestAttributes.qparams.query.testMode)
            responseSummary = CountResponseSummary.build_count_response_summary(CountResponseSummary, count)
            countResponse = CountResponse(meta=meta, responseSummary=responseSummary)
            countResponse = countResponse.model_dump(exclude_none=True)
            countsFromTemplate = create_model('countsFromTemplate', **{k: (Optional[type(v)], None) for k, v in response.items()})
            response = countsFromTemplate.model_validate(countResponse)
            response = response.model_dump(exclude_none=True)
        else:
            with open('beacon/response/templates/{}/boolean.json'.format(RequestAttributes.returned_apiVersion), 'r') as template:
                response = json.load(template)
            meta = Meta(receivedRequestSummary=RequestAttributes.qparams.summary(),returnedGranularity=RequestAttributes.returned_granularity,returnedSchemas=RequestAttributes.returned_schema,testMode=RequestAttributes.qparams.query.testMode)
            responseSummary = BooleanResponseSummary(exists=count>0)
            booleanResponse = BooleanResponse(meta=meta, responseSummary=responseSummary)
            booleanResponse = booleanResponse.model_dump(exclude_none=True)
            booleanFromTemplate = create_model('booleanFromTemplate', **{k: (Optional[type(v)], None) for k, v in response.items()})
            response = booleanFromTemplate.model_validate(booleanResponse)
            response = response.model_dump(exclude_none=True)
        return response
    except ValidationError as v:
        LOG.warning(v)
        self._error.handle_exception(v, None)
        raise
    except Exception as e:
        self._error.handle_exception(e, None)
        raise

@log_with_args(level)
async def collection_builder(self):
    try:
        if RequestAttributes.entry_type == dataset.endpoint_name:
            source = dataset.database
        elif RequestAttributes.entry_type == cohort.endpoint_name:
            source = cohort.database
        complete_module='beacon.connections.'+source+'.executor'
        import importlib
        module = importlib.import_module(complete_module, package=None)
        response_converted, count = await module.execute_collection_function(self)
        with open('beacon/response/templates/{}/collections.json'.format(RequestAttributes.returned_apiVersion), 'r') as template:
            response = json.load(template)
        meta = Meta(receivedRequestSummary=RequestAttributes.qparams.summary(),returnedGranularity=RequestAttributes.returned_granularity,returnedSchemas=RequestAttributes.returned_schema,testMode=RequestAttributes.qparams.query.testMode)
        responseSummary = ResponseSummary(exists=count>0,numTotalResults=count)
        collections = Collection(collections=response_converted)
        collectionResponse = CollectionResponse(meta=meta,response=collections,responseSummary=responseSummary)
        collectionResponse = collectionResponse.model_dump(exclude_none=True)
        collectionFromTemplate = create_model('collectionFromTemplate', **{k: (Optional[type(v)], None) for k, v in response.items()})
        response = collectionFromTemplate.model_validate(collectionResponse)
        response = response.model_dump(exclude_none=True)
        return response
    except ValidationError as v:
        LOG.warning(v)
        self._error.handle_exception(v, None)
        raise
    except Exception as e:
        self._error.handle_exception(e, None)
        raise

@log_with_args(level)
async def info_builder(self):
    try:
        with open('beacon/response/templates/{}/info.json'.format(RequestAttributes.returned_apiVersion), 'r') as template:
            response = json.load(template)
        info = Info()
        meta = InformationalMeta(returnedSchemas=[{"schema": "info-v2.2.0"}])
        infoResponse = InfoResponse(meta=meta,response=info)
        infoResponse = infoResponse.model_dump(exclude_none=True)
        InfoFromTemplate = create_model('InfoFromTemplate', **{k: (Optional[type(v)], None) for k, v in response.items()})
        response = InfoFromTemplate.model_validate(infoResponse)
        response = response.model_dump(exclude_none=True)
        return response
    except Exception as e:
        self._error.handle_exception(e, None)
        raise

@log_with_args(level)
async def configuration_builder(self):
    try:
        with open('beacon/response/templates/{}/configuration.json'.format(RequestAttributes.returned_apiVersion), 'r') as template:
            response = json.load(template)
        configuration = ConfigurationSchema.return_schema(ConfigurationSchema)
        meta = InformationalMeta(returnedSchemas=[{"schema": "configuration-v2.2.0"}])
        configurationResponse = ConfigurationResponse(meta=meta,response=configuration)
        configurationResponse = configurationResponse.model_dump(exclude_none=True, by_alias=True)
        ConfigurationFromTemplate = create_model('ConfigurationFromTemplate', **{k: (Optional[type(v)], None) for k, v in response.items()})
        response = ConfigurationFromTemplate.model_validate(configurationResponse)
        response = response.model_dump(exclude_none=True)
        return response
    except Exception as e:
        self._error.handle_exception(e, None)
        raise

@log_with_args(level)
async def map_builder(self):
    try:
        with open('beacon/response/templates/{}/map.json'.format(RequestAttributes.returned_apiVersion), 'r') as template:
            response = json.load(template)
        map = MapSchema.populate_endpoints(MapSchema)
        meta = InformationalMeta(returnedSchemas=[{"schema": "map-v2.2.0"}])
        mapResponse = MapResponse(meta=meta,response=map)
        mapResponse = mapResponse.model_dump(exclude_none=True, by_alias=True)
        MapFromTemplate = create_model('MapFromTemplate', **{k: (Optional[type(v)], None) for k, v in response.items()})
        response = MapFromTemplate.model_validate(mapResponse)
        response = response.model_dump(exclude_none=True)
        return response
    except Exception as e:
        self._error.handle_exception(e, None)
        raise

@log_with_args(level)
async def entry_types_builder(self):
    try:
        with open('beacon/response/templates/{}/entry_types.json'.format(RequestAttributes.returned_apiVersion), 'r') as template:
            response = json.load(template)
        entry_types = EntryTypesSchema.return_schema(EntryTypesSchema)
        meta = InformationalMeta(returnedSchemas=[{"schema": "entry_types-v2.2.0"}])
        entryTypesResponse = EntryTypesResponse(meta=meta,response=entry_types)
        entryTypesResponse = entryTypesResponse.model_dump(exclude_none=True)
        EntryTypesFromTemplate = create_model('EntryTypesFromTemplate', **{k: (Optional[type(v)], None) for k, v in response.items()})
        response = EntryTypesFromTemplate.model_validate(entryTypesResponse)
        response = response.model_dump(exclude_none=True)
        return response
    except Exception as e:
        self._error.handle_exception(e, None)
        raise

@log_with_args(level)
async def service_info_builder(self):
    try:
        with open('beacon/response/templates/{}/service-info.json'.format(RequestAttributes.returned_apiVersion), 'r') as template:
            response = json.load(template)
        service_info = ServiceInfo()
        serviceInfoResponse = service_info.model_dump(exclude_none=True)
        ServiceInfoFromTemplate = create_model('ServiceInfoFromTemplate', **{k: (Optional[type(v)], None) for k, v in response.items()})
        response = ServiceInfoFromTemplate.model_validate(serviceInfoResponse)
        response = response.model_dump(exclude_none=True)
        return response
    except Exception as e:
        self._error.handle_exception(e, None)
        raise

@log_with_args(level)
async def filtering_terms_builder(self):
    source=fterms.database
    complete_module='beacon.connections.'+source+'.filtering_terms'
    import importlib
    module = importlib.import_module(complete_module, package=None)
    try:
        count, records = module.get_filtering_terms(self)
        with open('beacon/response/templates/{}/filtering_terms.json'.format(RequestAttributes.returned_apiVersion), 'r') as template:
            response = json.load(template)
        filteringterms = FilteringTermsResults(filteringTerms=records)
        meta = InformationalMeta(returnedSchemas=[{"schema": "filtering_terms-v2.2.0"}])
        filteringTermsResponse = FilteringTermsResponse(meta=meta,response=filteringterms)
        filteringTermsResponse = filteringTermsResponse.model_dump(exclude_none=True)
        FilteringTermsFromTemplate = create_model('FilteringTermsFromTemplate', **{k: (Optional[type(v)], None) for k, v in response.items()})
        response = FilteringTermsFromTemplate.model_validate(filteringTermsResponse)
        response = response.model_dump(exclude_none=True)
        return response
    except Exception as e:
        self._error.handle_exception(e, None)
        raise

@log_with_args(level)
async def error_builder(self, status, message):
    try:
        with open('beacon/response/templates/{}/error.json'.format(RequestAttributes.returned_apiVersion), 'r') as template:
            response = json.load(template)
        error = BeaconError(errorCode=status,errorMessage=message)
        meta = Meta(receivedRequestSummary=RequestAttributes.qparams.summary(),returnedGranularity=RequestAttributes.returned_granularity,returnedSchemas=[{"schema": "error-v2.2.0"}],testMode=RequestAttributes.qparams.query.testMode)
        errorResponse = ErrorResponse(meta=meta,error=error)
        errorResponse = errorResponse.model_dump(exclude_none=True)
        ErrorFromTemplate = create_model('ErrorFromTemplate', **{k: (Optional[type(v)], None) for k, v in response.items()})
        response = ErrorFromTemplate.model_validate(errorResponse)
        response = response.model_dump(exclude_none=True)
        return response
    except Exception as e:
        self._error.handle_exception(e, None)
        raise

