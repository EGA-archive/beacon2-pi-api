from beacon.logs.logs import log_with_args, LOG
from beacon import conf
from beacon.conf.conf import level, uri_subpath
from beacon.conf import analysis, biosample, cohort, dataset, genomicVariant, individual, run
import asyncio
import aiohttp.web as web
from aiohttp.web_request import Request
from beacon.utils.txid import generate_txid
from beacon.permissions.__main__ import query_permissions
from beacon.exceptions.builder import error_builder
from bson import json_util
from beacon.request.classes import RequestAttributes
import time
import os
import signal
from threading import Thread
from beacon.utils.requests import deconstruct_request, RequestParams
from aiohttp_middlewares import cors_middleware
from aiohttp_cors import CorsViewMixin
from datetime import datetime
from beacon.conf import conf
import ssl
from beacon.budget.__main__ import insert_budget
from beacon.validator.configuration import check_configuration
from beacon.exceptions.exceptions import AppError
import aiohttp_autoreload
from beacon.validator.framework import (InfoBody, 
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
                                        Collections, 
                                        InformationalMeta,
                                        ConfigurationSchema,
                                        ConfigurationResponse,
                                        MapResponse,
                                        MapSchema,
                                        EntryTypesSchema,
                                        EntryTypesResponse,
                                        ServiceInfoResponse,
                                        FilteringTermsResults,
                                        FilteringTermsResponse,
                                        ErrorResponse,
                                        BeaconError)
from pydantic import create_model, Field, ValidationError
from typing import Optional
from beacon.exceptions.exceptions import InvalidData
from beacon.conf.templates import path, infoTemplate, resultSetsTemplate, countTemplate, booleanTemplate, collectionsTemplate, mapTemplate, configurationTemplate, entryTypesTemplate, serviceInfoTemplate, filteringTermsTemplate
import json

class EndpointView(web.View, CorsViewMixin):
    def __init__(self, request: Request):
        self._request = request
        self._id = generate_txid(self)
        RequestAttributes.ip = None
        RequestAttributes.headers=None
        RequestAttributes.entry_type=None
        RequestAttributes.entry_id=None
        RequestAttributes.pre_entry_type=None
        RequestAttributes.returned_schema=None
        RequestAttributes.returned_apiVersion="v2.0.0"
        RequestAttributes.qparams=RequestParams()
        RequestAttributes.returned_granularity="boolean"
        

    async def get(self):
        try:
            await deconstruct_request(self, self.request)
            self.template_path = path + '/' + RequestAttributes.returned_apiVersion + '/' # TODO: definir variable de forma diferent a la variable de path final. Cridar això en una funció.
            return await self.handler()
        except AppError as e:
            response_obj = await error_builder(self, e.status, e.message)
            return web.Response(text=json_util.dumps(response_obj), status=e.status, content_type='application/json')
        except Exception as e:
            response_obj = await error_builder(self, 500, "Unexpected internal error: {}".format(e))
            return web.Response(text=json_util.dumps(response_obj), status=500, content_type='application/json')

    async def post(self):
        try:
            await deconstruct_request(self, self.request)
            self.template_path = path + '/' + RequestAttributes.returned_apiVersion + '/' 
            return await self.handler()
        except AppError as e:
            response_obj = await error_builder(self, e.status, e.message)
            return web.Response(text=json_util.dumps(response_obj), status=e.status, content_type='application/json')
        except Exception as e:
            response_obj = await error_builder(self, 500, "Unexpected system error: {}".format(e))
            return web.Response(text=json_util.dumps(response_obj), status=500, content_type='application/json')


    def create_response(self): # TODO: Comentar cada línia de codi amb el que fem aquí.
        with open(self.template_path, 'r') as template:
            templateJSON = json.load(template)
        classtoJSON = self.classResponse.model_dump(exclude_none=True)
        modelFromTemplate = create_model('modelFromTemplate', **{k: (Optional[type(v)], None) for k, v in templateJSON.items()})
        responseClass = modelFromTemplate.model_validate(classtoJSON)
        JSONresponse = responseClass.model_dump(exclude_none=True)
        return JSONresponse

class ServiceInfo(EndpointView):
    @log_with_args(level)
    async def handler(self):
        self.template_path = self.template_path + serviceInfoTemplate
        try:
            self.classResponse = ServiceInfoResponse()
            response_obj = self.create_response()
        except ValidationError as v:
            raise InvalidData('{} templates or data are not correct'.format(RequestAttributes.entry_type))
        return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')

class EntryTypes(EndpointView):
    @log_with_args(level)
    async def handler(self):
        self.template_path = self.template_path + entryTypesTemplate
        try:
            entry_types = EntryTypesSchema.return_schema(EntryTypesSchema)
            meta = InformationalMeta(returnedSchemas=[RequestAttributes.returned_schema])
            self.classResponse = EntryTypesResponse(meta=meta,response=entry_types)
            response_obj = self.create_response()
        except ValidationError as v:
            raise InvalidData('{} templates or data are not correct'.format(RequestAttributes.entry_type))
        return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')

class Map(EndpointView):
    @log_with_args(level)
    async def handler(self):
        self.template_path = self.template_path + mapTemplate
        try:
            map = MapSchema.populate_endpoints(MapSchema)
            meta = InformationalMeta(returnedSchemas=[RequestAttributes.returned_schema])
            self.classResponse = MapResponse(meta=meta,response=map)
            response_obj = self.create_response()
        except ValidationError as v:
            raise InvalidData('{} templates or data are not correct'.format(RequestAttributes.entry_type))
        return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')

class Configuration(EndpointView):
    @log_with_args(level)
    async def handler(self):
        self.template_path = self.template_path + configurationTemplate
        try:
            configuration = ConfigurationSchema.return_schema(ConfigurationSchema)
            meta = InformationalMeta(returnedSchemas=[RequestAttributes.returned_schema])
            self.classResponse = ConfigurationResponse(meta=meta,response=configuration)
            response_obj = self.create_response()
        except ValidationError as v:
            raise InvalidData('{} templates or data are not correct'.format(RequestAttributes.entry_type))
        return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')

class Info(EndpointView):        
    @log_with_args(level)
    async def handler(self):
        self.template_path = self.template_path + infoTemplate
        try:
            info = InfoBody()
            meta = InformationalMeta(returnedSchemas=[RequestAttributes.returned_schema])
            self.classResponse = InfoResponse(meta=meta,response=info)
            response_obj = self.create_response()
        except ValidationError as v:
            raise InvalidData('{} templates or data are not correct'.format(RequestAttributes.entry_type))
        return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')

class Collection(EndpointView):
    @log_with_args(level)
    async def handler(self):
        complete_module='beacon.connections.'+RequestAttributes.source+'.executor'
        import importlib
        module = importlib.import_module(complete_module, package=None)
        response_converted, count = await module.execute_collection_function(self)
        self.template_path = self.template_path + collectionsTemplate
        try:
            meta = Meta(receivedRequestSummary=RequestAttributes.qparams.summary(),returnedGranularity=RequestAttributes.returned_granularity,returnedSchemas=RequestAttributes.returned_schema,testMode=RequestAttributes.qparams.query.testMode)
            responseSummary = ResponseSummary(exists=count>0,numTotalResults=count)
            collections = Collections(collections=response_converted)
            self.classResponse = CollectionResponse(meta=meta,response=collections,responseSummary=responseSummary)
            response_obj = self.create_response()
        except ValidationError as v:
            LOG.error(str(v))
            raise InvalidData('{} templates or data are not correct'.format(RequestAttributes.entry_type))
        return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')
        
class FilteringTerms(EndpointView):
    @log_with_args(level)
    async def handler(self):
        complete_module='beacon.connections.'+RequestAttributes.source+'.filtering_terms'
        import importlib
        module = importlib.import_module(complete_module, package=None)
        count, records = module.get_filtering_terms(self)
        self.template_path = self.template_path + filteringTermsTemplate
        try:
            filteringterms = FilteringTermsResults(filteringTerms=records)
            meta = InformationalMeta(returnedSchemas=[RequestAttributes.returned_schema])
            self.classResponse = FilteringTermsResponse(meta=meta,response=filteringterms)
            response_obj = self.create_response()
        except ValidationError as v:
            raise InvalidData('{} templates or data are not correct'.format(RequestAttributes.entry_type))
        return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')

class PhenoGeno(EndpointView):
    @query_permissions
    @log_with_args(level)
    async def handler(self, datasets, username, time_now):
        complete_module='beacon.connections.'+RequestAttributes.source+'.executor'# TODO: Comentar.
        import importlib
        module = importlib.import_module(complete_module, package=None)
        datasets_docs, datasets_count, count, include, datasets = await module.execute_function(self, datasets) # TODO: Això s'ha de retornar en una classe.
        try:
            meta = Meta(receivedRequestSummary=RequestAttributes.qparams.summary(),returnedGranularity=RequestAttributes.returned_granularity,returnedSchemas=RequestAttributes.returned_schema,testMode=RequestAttributes.qparams.query.testMode)
            if RequestAttributes.response_type == 'resultSet':
                self.template_path = self.template_path + resultSetsTemplate
                list_of_resultSets=[]
                new_datasets=[]
                for dataset in datasets:
                    try:
                        resultSet = ResultsetInstance.build_response_by_dataset(ResultsetInstance,dataset, datasets_docs, datasets_count,RequestAttributes.allowed_granularity,RequestAttributes.qparams.query.requestedGranularity)
                        list_of_resultSets.append(resultSet)
                        new_datasets.append(dataset)
                    except ValidationError as v:
                        LOG.error('{} dataset is invalid: {}'.format(dataset.dataset, str(v)))
                responseSummary = ResponseSummary.build_response_summary_by_dataset(ResponseSummary, new_datasets, datasets_count)
                resultSets = Resultsets.return_resultSets(Resultsets, list_of_resultSets)
                self.classResponse = ResultsetsResponse.return_response(ResultsetsResponse, meta, resultSets, responseSummary)
                response_obj = self.create_response()
            elif RequestAttributes.response_type == 'count':
                self.template_path = self.template_path + countTemplate
                responseSummary = CountResponseSummary.build_count_response_summary(CountResponseSummary, count)
                self.classResponse = CountResponse(meta=meta, responseSummary=responseSummary)
                response_obj = self.create_response()
            else:
                self.template_path = self.template_path + booleanTemplate
                responseSummary = BooleanResponseSummary(exists=count>0)
                self.classResponse = BooleanResponse(meta=meta, responseSummary=responseSummary)
                response_obj = self.create_response()
        except ValidationError as v:
            raise InvalidData('{} templates or data are not correct'.format(RequestAttributes.entry_type))
        if time_now is not None:
            insert_budget(self, username, time_now)
        return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')

@web.middleware
async def error_middleware(request, handler):
    try:
        response = await handler(request)
        if response.status != 404:
            return response
    except web.HTTPException as ex:
        if ex.status != 404:
            response_obj = await error_builder(EndpointView(request), ex.status, "Unexpected system error: {}".format(ex))
            return web.Response(text=json_util.dumps(response_obj), status=ex.status, content_type='application/json')
        else:
            response_obj = await error_builder(EndpointView(request), 404, "Not found")
            return web.Response(text=json_util.dumps(response_obj), status=404, content_type='application/json')

async def initialize(app):
    setattr(conf, 'update_datetime', datetime.now().isoformat())

    LOG.info("Initialization done.")

def _on_shutdown(pid):
    time.sleep(6)

    #  Sending SIGINT to close server
    os.kill(pid, signal.SIGINT)

    LOG.info('Shutting down beacon v2')

async def _graceful_shutdown_ctx(app):
    def graceful_shutdown_sigterm_handler():
        nonlocal thread
        thread = Thread(target=_on_shutdown, args=(os.getpid(),))
        thread.start()

    thread = None

    loop = asyncio.get_event_loop()
    loop.add_signal_handler(
        signal.SIGTERM, graceful_shutdown_sigterm_handler,
    )

    yield

    loop.remove_signal_handler(signal.SIGTERM)

    if thread is not None:
        thread.join()

async def create_api(port):
    try:
        check_configuration()
        app = web.Application(
            middlewares=[
                cors_middleware(origins=conf.cors_urls), error_middleware
            ]
        )
        app.on_startup.append(initialize)
        app.cleanup_ctx.append(_graceful_shutdown_ctx)
        # base_path del /api a la configuració
        app.add_routes([web.post(uri_subpath, Info)])
        app.add_routes([web.post(uri_subpath+'/info', Info)])
        app.add_routes([web.post(uri_subpath+'/entry_types', EntryTypes)])
        app.add_routes([web.post(uri_subpath+'/service-info', ServiceInfo)])
        app.add_routes([web.post(uri_subpath+'/configuration', Configuration)])
        app.add_routes([web.post(uri_subpath+'/map', Map)])
        app.add_routes([web.post(uri_subpath+'/filtering_terms', FilteringTerms)])
        app.add_routes([web.get(uri_subpath, Info)])
        app.add_routes([web.get(uri_subpath+'/info', Info)])
        app.add_routes([web.get(uri_subpath+'/entry_types', EntryTypes)])
        app.add_routes([web.get(uri_subpath+'/service-info', ServiceInfo)])
        app.add_routes([web.get(uri_subpath+'/configuration', Configuration)])
        app.add_routes([web.get(uri_subpath+'/map', Map)])
        app.add_routes([web.get(uri_subpath+'/filtering_terms', FilteringTerms)])
        if dataset.endpoint_name != '':
            app.add_routes([web.post(uri_subpath+'/'+dataset.endpoint_name, Collection)])
            app.add_routes([web.get(uri_subpath+'/'+dataset.endpoint_name, Collection)])
            if dataset.singleEntryUrl == True:
                app.add_routes([web.post(uri_subpath+'/'+dataset.endpoint_name+'/{id}', Collection)])
                app.add_routes([web.get(uri_subpath+'/'+dataset.endpoint_name+'/{id}', Collection)])
            if dataset.analysis_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+analysis.endpoint_name, PhenoGeno)])
                app.add_routes([web.get(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+analysis.endpoint_name, PhenoGeno)])
            if dataset.biosample_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+biosample.endpoint_name, PhenoGeno)])
                app.add_routes([web.get(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+biosample.endpoint_name, PhenoGeno)])
            if dataset.cohort_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+cohort.endpoint_name, Collection)])
                app.add_routes([web.get(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+cohort.endpoint_name, Collection)])
            if dataset.genomicVariant_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, PhenoGeno)])
                app.add_routes([web.get(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, PhenoGeno)])
            if dataset.individual_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+individual.endpoint_name, PhenoGeno)])
                app.add_routes([web.get(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+individual.endpoint_name, PhenoGeno)])
            if dataset.run_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+run.endpoint_name, PhenoGeno)])
                app.add_routes([web.get(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+run.endpoint_name, PhenoGeno)])
        if cohort.endpoint_name != '':
            app.add_routes([web.post(uri_subpath+'/'+cohort.endpoint_name, Collection)])
            app.add_routes([web.get(uri_subpath+'/'+cohort.endpoint_name, Collection)])
            if cohort.singleEntryUrl == True:
                app.add_routes([web.post(uri_subpath+'/'+cohort.endpoint_name+'/{id}', Collection)])
                app.add_routes([web.get(uri_subpath+'/'+cohort.endpoint_name+'/{id}', Collection)])
            if cohort.analysis_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+analysis.endpoint_name, PhenoGeno)])
                app.add_routes([web.get(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+analysis.endpoint_name, PhenoGeno)])
            if cohort.biosample_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+biosample.endpoint_name, PhenoGeno)])
                app.add_routes([web.get(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+biosample.endpoint_name, PhenoGeno)])
            if cohort.dataset_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+dataset.endpoint_name, Collection)])
                app.add_routes([web.get(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+dataset.endpoint_name, Collection)])
            if cohort.genomicVariant_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, PhenoGeno)])
                app.add_routes([web.get(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, PhenoGeno)])
            if cohort.individual_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+individual.endpoint_name, PhenoGeno)])
                app.add_routes([web.get(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+individual.endpoint_name, PhenoGeno)])
            if cohort.run_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+run.endpoint_name, PhenoGeno)])
                app.add_routes([web.get(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+run.endpoint_name, PhenoGeno)])
        if analysis.endpoint_name != '':
            app.add_routes([web.post(uri_subpath+'/'+analysis.endpoint_name, PhenoGeno)])
            app.add_routes([web.get(uri_subpath+'/'+analysis.endpoint_name, PhenoGeno)])
            if analysis.singleEntryUrl == True:
                app.add_routes([web.post(uri_subpath+'/'+analysis.endpoint_name+'/{id}', PhenoGeno)])
                app.add_routes([web.get(uri_subpath+'/'+analysis.endpoint_name+'/{id}', PhenoGeno)])
            if analysis.cohort_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+cohort.endpoint_name, Collection)])
                app.add_routes([web.get(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+cohort.endpoint_name, Collection)])
            if analysis.biosample_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+biosample.endpoint_name, PhenoGeno)])
                app.add_routes([web.get(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+biosample.endpoint_name, PhenoGeno)])
            if analysis.dataset_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+dataset.endpoint_name, Collection)])
                app.add_routes([web.get(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+dataset.endpoint_name, Collection)])
            if analysis.genomicVariant_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, PhenoGeno)])
                app.add_routes([web.get(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, PhenoGeno)])
            if analysis.individual_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+individual.endpoint_name, PhenoGeno)])
                app.add_routes([web.get(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+individual.endpoint_name, PhenoGeno)])
            if analysis.run_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+run.endpoint_name, PhenoGeno)])
                app.add_routes([web.get(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+run.endpoint_name, PhenoGeno)])
        if biosample.endpoint_name != '':
            app.add_routes([web.post(uri_subpath+'/'+biosample.endpoint_name, PhenoGeno)])
            app.add_routes([web.get(uri_subpath+'/'+biosample.endpoint_name, PhenoGeno)])
            if biosample.singleEntryUrl == True:
                app.add_routes([web.post(uri_subpath+'/'+biosample.endpoint_name+'/{id}', PhenoGeno)])
                app.add_routes([web.get(uri_subpath+'/'+biosample.endpoint_name+'/{id}', PhenoGeno)])
            if biosample.cohort_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+cohort.endpoint_name, Collection)])
                app.add_routes([web.get(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+cohort.endpoint_name, Collection)])
            if biosample.analysis_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+analysis.endpoint_name, PhenoGeno)])
                app.add_routes([web.get(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+analysis.endpoint_name, PhenoGeno)])
            if biosample.dataset_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+dataset.endpoint_name, Collection)])
                app.add_routes([web.get(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+dataset.endpoint_name, Collection)])
            if biosample.genomicVariant_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, PhenoGeno)])
                app.add_routes([web.get(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, PhenoGeno)])
            if biosample.individual_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+individual.endpoint_name, PhenoGeno)])
                app.add_routes([web.get(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+individual.endpoint_name, PhenoGeno)])
            if biosample.run_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+run.endpoint_name, PhenoGeno)])
                app.add_routes([web.get(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+run.endpoint_name, PhenoGeno)])
        if genomicVariant.endpoint_name != '':
            app.add_routes([web.post(uri_subpath+'/'+genomicVariant.endpoint_name, PhenoGeno)])
            app.add_routes([web.get(uri_subpath+'/'+genomicVariant.endpoint_name, PhenoGeno)])
            if genomicVariant.singleEntryUrl == True:
                app.add_routes([web.post(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}', PhenoGeno)])
                app.add_routes([web.get(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}', PhenoGeno)])
            if genomicVariant.cohort_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+cohort.endpoint_name, Collection)])
                app.add_routes([web.get(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+cohort.endpoint_name, Collection)])
            if genomicVariant.analysis_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+analysis.endpoint_name, PhenoGeno)])
                app.add_routes([web.get(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+analysis.endpoint_name, PhenoGeno)])
            if genomicVariant.dataset_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+dataset.endpoint_name, Collection)])
                app.add_routes([web.get(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+dataset.endpoint_name, Collection)])
            if genomicVariant.biosample_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+biosample.endpoint_name, PhenoGeno)])
                app.add_routes([web.get(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+biosample.endpoint_name, PhenoGeno)])
            if genomicVariant.individual_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+individual.endpoint_name, PhenoGeno)])
                app.add_routes([web.get(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+individual.endpoint_name, PhenoGeno)])
            if genomicVariant.run_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+run.endpoint_name, PhenoGeno)])
                app.add_routes([web.get(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+run.endpoint_name, PhenoGeno)])
        if individual.endpoint_name != '':
            app.add_routes([web.post(uri_subpath+'/'+individual.endpoint_name, PhenoGeno)])
            app.add_routes([web.get(uri_subpath+'/'+individual.endpoint_name, PhenoGeno)])
            if individual.singleEntryUrl == True:
                app.add_routes([web.post(uri_subpath+'/'+individual.endpoint_name+'/{id}', PhenoGeno)])
                app.add_routes([web.get(uri_subpath+'/'+individual.endpoint_name+'/{id}', PhenoGeno)])
            if individual.cohort_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+cohort.endpoint_name, Collection)])
                app.add_routes([web.get(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+cohort.endpoint_name, Collection)])
            if individual.analysis_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+analysis.endpoint_name, PhenoGeno)])
                app.add_routes([web.get(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+analysis.endpoint_name, PhenoGeno)])
            if individual.dataset_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+dataset.endpoint_name, Collection)])
                app.add_routes([web.get(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+dataset.endpoint_name, Collection)])
            if individual.biosample_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+biosample.endpoint_name, PhenoGeno)])
                app.add_routes([web.get(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+biosample.endpoint_name, PhenoGeno)])
            if individual.genomicVariant_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, PhenoGeno)])
                app.add_routes([web.get(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, PhenoGeno)])
            if individual.run_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+run.endpoint_name, PhenoGeno)])
                app.add_routes([web.get(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+run.endpoint_name, PhenoGeno)])
        if run.endpoint_name != '':
            app.add_routes([web.post(uri_subpath+'/'+run.endpoint_name, PhenoGeno)])
            app.add_routes([web.get(uri_subpath+'/'+run.endpoint_name, PhenoGeno)])
            if run.singleEntryUrl == True:
                app.add_routes([web.post(uri_subpath+'/'+run.endpoint_name+'/{id}', PhenoGeno)])
                app.add_routes([web.get(uri_subpath+'/'+run.endpoint_name+'/{id}', PhenoGeno)])
            if run.cohort_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+run.endpoint_name+'/{id}/'+cohort.endpoint_name, Collection)])
                app.add_routes([web.get(uri_subpath+'/'+run.endpoint_name+'/{id}/'+cohort.endpoint_name, Collection)])
            if run.analysis_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+run.endpoint_name+'/{id}/'+analysis.endpoint_name, PhenoGeno)])
                app.add_routes([web.get(uri_subpath+'/'+run.endpoint_name+'/{id}/'+analysis.endpoint_name, PhenoGeno)])
            if run.dataset_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+run.endpoint_name+'/{id}/'+dataset.endpoint_name, Collection)])
                app.add_routes([web.get(uri_subpath+'/'+run.endpoint_name+'/{id}/'+dataset.endpoint_name, Collection)])
            if run.biosample_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+run.endpoint_name+'/{id}/'+biosample.endpoint_name, PhenoGeno)])
                app.add_routes([web.get(uri_subpath+'/'+run.endpoint_name+'/{id}/'+biosample.endpoint_name, PhenoGeno)])
            if run.genomicVariant_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+run.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, PhenoGeno)])
                app.add_routes([web.get(uri_subpath+'/'+run.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, PhenoGeno)])
            if run.individual_lookup == True:
                app.add_routes([web.post(uri_subpath+'/'+run.endpoint_name+'/{id}/'+individual.endpoint_name, PhenoGeno)])
                app.add_routes([web.get(uri_subpath+'/'+run.endpoint_name+'/{id}/'+individual.endpoint_name, PhenoGeno)])

        ssl_context = None
        if (os.path.isfile(conf.beacon_server_key)) and (os.path.isfile(conf.beacon_server_crt)):
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(certfile=conf.beacon_server_crt, keyfile=conf.beacon_server_key)
        
        aiohttp_autoreload.start()
        LOG.debug("Starting app")
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', port,  ssl_context=ssl_context)
        await site.start()

        while True:
            await asyncio.sleep(3600)
            
    except Exception:
        raise

if __name__ == '__main__':
    try:
        asyncio.run(create_api(5050))
    except Exception:
        raise # TODO: Les excepcions més greus han d'estar codificades aquí.


# TODO: Posar classes Endpoint en arxius diferents (com model i framework) i també routes. Només deixar les línies de crida.