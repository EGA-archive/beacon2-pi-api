from beacon.logs.logs import log_with_args, LOG
from beacon import conf
from beacon.conf.conf import level, uri_subpath
from beacon.conf import analysis, biosample, cohort, dataset, genomicVariant, individual, run
import asyncio
import aiohttp.web as web
from aiohttp.web_request import Request
from beacon.utils.txid import generate_txid
from beacon.permissions.__main__ import query_permissions
from beacon.response.builder import builder, collection_builder, info_builder, configuration_builder, map_builder, entry_types_builder, service_info_builder, filtering_terms_builder
from bson import json_util
from beacon.response.catalog import build_beacon_error_response
from beacon.request.classes import ErrorClass, RequestAttributes
import time
import os
import signal
from threading import Thread
from beacon.utils.requests import get_qparams, deconstruct_request
from aiohttp_middlewares import cors_middleware
from aiohttp_cors import CorsViewMixin
from datetime import datetime
from beacon.conf import conf
import ssl
from beacon.request.parameters import RequestMeta, RequestQuery, Pagination
from beacon.budget.__main__ import insert_budget
from beacon.validator.configuration import check_configuration
import aiohttp_autoreload

class EndpointView(web.View, CorsViewMixin):
    def __init__(self, request: Request):
        self._request = request
        self._id = generate_txid(self)
        ErrorClass.error_code = None
        ErrorClass.error_message = None
        RequestAttributes.ip = None
        RequestAttributes.headers=None
        RequestAttributes.entry_type=None
        RequestAttributes.entry_id=None
        RequestAttributes.pre_entry_type=None

class ServiceInfo(EndpointView):
    @log_with_args(level)
    async def service_info(self, request):
        try:
            response_obj = await service_info_builder(self)
            return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')
        except Exception as e:# pragma: no cover
            raise

    async def get(self):
        try:
            return await self.service_info(self.request)
        except Exception as e:# pragma: no cover
            response_obj = build_beacon_error_response(self, ErrorClass.error_code, ErrorClass.error_message)
            return web.Response(text=json_util.dumps(response_obj), status=ErrorClass.error_code, content_type='application/json')

    async def post(self):
        try:
            return await self.service_info(self.request)
        except Exception as e:# pragma: no cover
            response_obj = build_beacon_error_response(self, ErrorClass.error_code, ErrorClass.error_message)
            return web.Response(text=json_util.dumps(response_obj), status=ErrorClass.error_code, content_type='application/json')

class EntryTypes(EndpointView):
    @log_with_args(level)
    async def entry_types(self, request):
        try:
            response_obj = await entry_types_builder(self)
            return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')
        except Exception:# pragma: no cover
            raise

    async def get(self):
        try:
            return await self.entry_types(self.request)
        except Exception as e:# pragma: no cover
            response_obj = build_beacon_error_response(self, ErrorClass.error_code, ErrorClass.error_message)
            return web.Response(text=json_util.dumps(response_obj), status=ErrorClass.error_code, content_type='application/json')

    async def post(self):
        try:
            return await self.entry_types(self.request)
        except Exception as e:# pragma: no cover
            response_obj = build_beacon_error_response(self, ErrorClass.error_code, ErrorClass.error_message)
            return web.Response(text=json_util.dumps(response_obj), status=ErrorClass.error_code, content_type='application/json')

class Map(EndpointView):
    @log_with_args(level)
    async def map(self, request):
        try:
            response_obj = await map_builder(self)
            return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')
        except Exception:# pragma: no cover
            raise

    async def get(self):
        try:
            return await self.map(self.request)
        except Exception as e:# pragma: no cover
            response_obj = build_beacon_error_response(self, ErrorClass.error_code, ErrorClass.error_message)
            return web.Response(text=json_util.dumps(response_obj), status=ErrorClass.error_code, content_type='application/json')

    async def post(self):
        try:
            return await self.map(self.request)
        except Exception as e:# pragma: no cover
            response_obj = build_beacon_error_response(self, ErrorClass.error_code, ErrorClass.error_message)
            return web.Response(text=json_util.dumps(response_obj), status=ErrorClass.error_code, content_type='application/json')

class Configuration(EndpointView):
    @log_with_args(level)
    async def configuration(self, request):
        try:
            response_obj = await configuration_builder(self)
            return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')
        except Exception:# pragma: no cover
            raise

    async def get(self):
        try:
            return await self.configuration(self.request)
        except Exception as e:# pragma: no cover
            response_obj = build_beacon_error_response(self, ErrorClass.error_code, ErrorClass.error_message)
            return web.Response(text=json_util.dumps(response_obj), status=ErrorClass.error_code, content_type='application/json')

    async def post(self):
        try:
            return await self.configuration(self.request)
        except Exception as e:# pragma: no cover
            response_obj = build_beacon_error_response(self, ErrorClass.error_code, ErrorClass.error_message)
            return web.Response(text=json_util.dumps(response_obj), status=ErrorClass.error_code, content_type='application/json')

class Info(EndpointView):
    @log_with_args(level)
    async def info(self, request):
        try:
            response_obj = await info_builder(self)
            return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')
        except Exception:# pragma: no cover
            raise

    async def get(self):
        try:
            return await self.info(self.request)
        except Exception as e:# pragma: no cover
            response_obj = build_beacon_error_response(self, ErrorClass.error_code, ErrorClass.error_message)
            return web.Response(text=json_util.dumps(response_obj), status=ErrorClass.error_code, content_type='application/json')

    async def post(self):
        try:
            return await self.info(self.request)
        except Exception as e:# pragma: no cover
            response_obj = build_beacon_error_response(self, ErrorClass.error_code, ErrorClass.error_message)
            return web.Response(text=json_util.dumps(response_obj), status=ErrorClass.error_code, content_type='application/json')

class Collection(EndpointView):
    @log_with_args(level)
    async def collection(self, qparams):
        try:
            response_obj = await collection_builder(self, qparams)
            return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')
        except Exception:# pragma: no cover
            raise

    async def get(self):
        try:
            qparams = await deconstruct_request(self, self.request)
            return await self.collection(qparams)
        except Exception as e:# pragma: no cover
            response_obj = build_beacon_error_response(self, ErrorClass.error_code, ErrorClass.error_message)
            return web.Response(text=json_util.dumps(response_obj), status=ErrorClass.error_code, content_type='application/json')

    async def post(self):
        try:
            qparams = await deconstruct_request(self, self.request)
            return await self.collection(qparams)
        except Exception as e:# pragma: no cover
            response_obj = build_beacon_error_response(self, ErrorClass.error_code, ErrorClass.error_message)
            return web.Response(text=json_util.dumps(response_obj), status=ErrorClass.error_code, content_type='application/json')
        
class FilteringTerms(EndpointView):
    @log_with_args(level)
    async def filteringTerms(self, qparams):
        try:
            response_obj = await filtering_terms_builder(self, qparams)
            return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')
        except Exception:# pragma: no cover
            raise

    async def get(self):
        try:
            qparams = await deconstruct_request(self, self.request)
            return await self.filteringTerms(qparams)
        except Exception as e:# pragma: no cover
            response_obj = build_beacon_error_response(self, ErrorClass.error_code, ErrorClass.error_message)
            return web.Response(text=json_util.dumps(response_obj), status=ErrorClass.error_code, content_type='application/json')

    async def post(self):
        try:
            qparams = await deconstruct_request(self, self.request)
            return await self.filteringTerms( qparams)
        except Exception as e:# pragma: no cover
            response_obj = build_beacon_error_response(self, ErrorClass.error_code, ErrorClass.error_message)
            return web.Response(text=json_util.dumps(response_obj), status=ErrorClass.error_code, content_type='application/json')

class Resultset(EndpointView):
    @query_permissions
    @log_with_args(level)
    async def resultset(self, qparams, datasets, username, time_now):
        try:
            response_obj = await builder(self, datasets, qparams)
            if time_now is not None:
                insert_budget(self, username, time_now)
            return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')
        except Exception:# pragma: no cover
            raise

    async def get(self):
        try: # Crear funció comuna
            # Afegir classe per la request
            qparams = await deconstruct_request(self, self.request)
            return await self.resultset(qparams)
        except Exception as e:# pragma: no cover
            response_obj = build_beacon_error_response(self, ErrorClass.error_code, ErrorClass.error_message)
            return web.Response(text=json_util.dumps(response_obj), status=ErrorClass.error_code, content_type='application/json')

    async def post(self):
        try:
            qparams = await deconstruct_request(self, self.request)
            return await self.resultset(qparams)
        except Exception as e:# pragma: no cover
            response_obj = build_beacon_error_response(self, ErrorClass.error_code, ErrorClass.error_message)
            return web.Response(text=json_util.dumps(response_obj), status=ErrorClass.error_code, content_type='application/json')
        

async def initialize(app):# pragma: no cover
    setattr(conf, 'update_datetime', datetime.now().isoformat())

    LOG.info("Initialization done.")

def _on_shutdown(pid):# pragma: no cover
    time.sleep(6)

    #  Sending SIGINT to close server
    os.kill(pid, signal.SIGINT)

    LOG.info('Shutting down beacon v2')

async def _graceful_shutdown_ctx(app):# pragma: no cover
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

async def create_api():# pragma: no cover
    check_configuration()
    app = web.Application(
        middlewares=[
            cors_middleware(origins=conf.cors_urls)
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
            app.add_routes([web.post(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+analysis.endpoint_name, Resultset)])
            app.add_routes([web.get(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+analysis.endpoint_name, Resultset)])
        if dataset.biosample_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+biosample.endpoint_name, Resultset)])
            app.add_routes([web.get(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+biosample.endpoint_name, Resultset)])
        if dataset.cohort_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+cohort.endpoint_name, Collection)])
            app.add_routes([web.get(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+cohort.endpoint_name, Collection)])
        if dataset.genomicVariant_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, Resultset)])
            app.add_routes([web.get(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, Resultset)])
        if dataset.individual_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+individual.endpoint_name, Resultset)])
            app.add_routes([web.get(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+individual.endpoint_name, Resultset)])
        if dataset.run_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+run.endpoint_name, Resultset)])
            app.add_routes([web.get(uri_subpath+'/'+dataset.endpoint_name+'/{id}/'+run.endpoint_name, Resultset)])
    if cohort.endpoint_name != '':
        app.add_routes([web.post(uri_subpath+'/'+cohort.endpoint_name, Collection)])
        app.add_routes([web.get(uri_subpath+'/'+cohort.endpoint_name, Collection)])
        if cohort.singleEntryUrl == True:
            app.add_routes([web.post(uri_subpath+'/'+cohort.endpoint_name+'/{id}', Collection)])
            app.add_routes([web.get(uri_subpath+'/'+cohort.endpoint_name+'/{id}', Collection)])
        if cohort.analysis_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+analysis.endpoint_name, Resultset)])
            app.add_routes([web.get(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+analysis.endpoint_name, Resultset)])
        if cohort.biosample_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+biosample.endpoint_name, Resultset)])
            app.add_routes([web.get(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+biosample.endpoint_name, Resultset)])
        if cohort.dataset_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+dataset.endpoint_name, Collection)])
            app.add_routes([web.get(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+dataset.endpoint_name, Collection)])
        if cohort.genomicVariant_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, Resultset)])
            app.add_routes([web.get(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, Resultset)])
        if cohort.individual_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+individual.endpoint_name, Resultset)])
            app.add_routes([web.get(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+individual.endpoint_name, Resultset)])
        if cohort.run_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+run.endpoint_name, Resultset)])
            app.add_routes([web.get(uri_subpath+'/'+cohort.endpoint_name+'/{id}/'+run.endpoint_name, Resultset)])
    if analysis.endpoint_name != '':
        app.add_routes([web.post(uri_subpath+'/'+analysis.endpoint_name, Resultset)])
        app.add_routes([web.get(uri_subpath+'/'+analysis.endpoint_name, Resultset)])
        if analysis.singleEntryUrl == True:
            app.add_routes([web.post(uri_subpath+'/'+analysis.endpoint_name+'/{id}', Resultset)])
            app.add_routes([web.get(uri_subpath+'/'+analysis.endpoint_name+'/{id}', Resultset)])
        if analysis.cohort_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+cohort.endpoint_name, Collection)])
            app.add_routes([web.get(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+cohort.endpoint_name, Collection)])
        if analysis.biosample_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+biosample.endpoint_name, Resultset)])
            app.add_routes([web.get(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+biosample.endpoint_name, Resultset)])
        if analysis.dataset_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+dataset.endpoint_name, Collection)])
            app.add_routes([web.get(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+dataset.endpoint_name, Collection)])
        if analysis.genomicVariant_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, Resultset)])
            app.add_routes([web.get(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, Resultset)])
        if analysis.individual_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+individual.endpoint_name, Resultset)])
            app.add_routes([web.get(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+individual.endpoint_name, Resultset)])
        if analysis.run_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+run.endpoint_name, Resultset)])
            app.add_routes([web.get(uri_subpath+'/'+analysis.endpoint_name+'/{id}/'+run.endpoint_name, Resultset)])
    if biosample.endpoint_name != '':
        app.add_routes([web.post(uri_subpath+'/'+biosample.endpoint_name, Resultset)])
        app.add_routes([web.get(uri_subpath+'/'+biosample.endpoint_name, Resultset)])
        if biosample.singleEntryUrl == True:
            app.add_routes([web.post(uri_subpath+'/'+biosample.endpoint_name+'/{id}', Resultset)])
            app.add_routes([web.get(uri_subpath+'/'+biosample.endpoint_name+'/{id}', Resultset)])
        if biosample.cohort_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+cohort.endpoint_name, Collection)])
            app.add_routes([web.get(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+cohort.endpoint_name, Collection)])
        if biosample.analysis_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+analysis.endpoint_name, Resultset)])
            app.add_routes([web.get(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+analysis.endpoint_name, Resultset)])
        if biosample.dataset_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+dataset.endpoint_name, Collection)])
            app.add_routes([web.get(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+dataset.endpoint_name, Collection)])
        if biosample.genomicVariant_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, Resultset)])
            app.add_routes([web.get(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, Resultset)])
        if biosample.individual_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+individual.endpoint_name, Resultset)])
            app.add_routes([web.get(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+individual.endpoint_name, Resultset)])
        if biosample.run_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+run.endpoint_name, Resultset)])
            app.add_routes([web.get(uri_subpath+'/'+biosample.endpoint_name+'/{id}/'+run.endpoint_name, Resultset)])
    if genomicVariant.endpoint_name != '':
        app.add_routes([web.post(uri_subpath+'/'+genomicVariant.endpoint_name, Resultset)])
        app.add_routes([web.get(uri_subpath+'/'+genomicVariant.endpoint_name, Resultset)])
        if genomicVariant.singleEntryUrl == True:
            app.add_routes([web.post(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}', Resultset)])
            app.add_routes([web.get(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}', Resultset)])
        if genomicVariant.cohort_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+cohort.endpoint_name, Collection)])
            app.add_routes([web.get(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+cohort.endpoint_name, Collection)])
        if genomicVariant.analysis_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+analysis.endpoint_name, Resultset)])
            app.add_routes([web.get(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+analysis.endpoint_name, Resultset)])
        if genomicVariant.dataset_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+dataset.endpoint_name, Collection)])
            app.add_routes([web.get(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+dataset.endpoint_name, Collection)])
        if genomicVariant.biosample_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+biosample.endpoint_name, Resultset)])
            app.add_routes([web.get(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+biosample.endpoint_name, Resultset)])
        if genomicVariant.individual_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+individual.endpoint_name, Resultset)])
            app.add_routes([web.get(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+individual.endpoint_name, Resultset)])
        if genomicVariant.run_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+run.endpoint_name, Resultset)])
            app.add_routes([web.get(uri_subpath+'/'+genomicVariant.endpoint_name+'/{id}/'+run.endpoint_name, Resultset)])
    if individual.endpoint_name != '':
        app.add_routes([web.post(uri_subpath+'/'+individual.endpoint_name, Resultset)])
        app.add_routes([web.get(uri_subpath+'/'+individual.endpoint_name, Resultset)])
        if individual.singleEntryUrl == True:
            app.add_routes([web.post(uri_subpath+'/'+individual.endpoint_name+'/{id}', Resultset)])
            app.add_routes([web.get(uri_subpath+'/'+individual.endpoint_name+'/{id}', Resultset)])
        if individual.cohort_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+cohort.endpoint_name, Collection)])
            app.add_routes([web.get(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+cohort.endpoint_name, Collection)])
        if individual.analysis_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+analysis.endpoint_name, Resultset)])
            app.add_routes([web.get(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+analysis.endpoint_name, Resultset)])
        if individual.dataset_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+dataset.endpoint_name, Collection)])
            app.add_routes([web.get(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+dataset.endpoint_name, Collection)])
        if individual.biosample_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+biosample.endpoint_name, Resultset)])
            app.add_routes([web.get(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+biosample.endpoint_name, Resultset)])
        if individual.genomicVariant_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, Resultset)])
            app.add_routes([web.get(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, Resultset)])
        if individual.run_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+run.endpoint_name, Resultset)])
            app.add_routes([web.get(uri_subpath+'/'+individual.endpoint_name+'/{id}/'+run.endpoint_name, Resultset)])
    if run.endpoint_name != '':
        app.add_routes([web.post(uri_subpath+'/'+run.endpoint_name, Resultset)])
        app.add_routes([web.get(uri_subpath+'/'+run.endpoint_name, Resultset)])
        if run.singleEntryUrl == True:
            app.add_routes([web.post(uri_subpath+'/'+run.endpoint_name+'/{id}', Resultset)])
            app.add_routes([web.get(uri_subpath+'/'+run.endpoint_name+'/{id}', Resultset)])
        if run.cohort_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+run.endpoint_name+'/{id}/'+cohort.endpoint_name, Collection)])
            app.add_routes([web.get(uri_subpath+'/'+run.endpoint_name+'/{id}/'+cohort.endpoint_name, Collection)])
        if run.analysis_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+run.endpoint_name+'/{id}/'+analysis.endpoint_name, Resultset)])
            app.add_routes([web.get(uri_subpath+'/'+run.endpoint_name+'/{id}/'+analysis.endpoint_name, Resultset)])
        if run.dataset_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+run.endpoint_name+'/{id}/'+dataset.endpoint_name, Collection)])
            app.add_routes([web.get(uri_subpath+'/'+run.endpoint_name+'/{id}/'+dataset.endpoint_name, Collection)])
        if run.biosample_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+run.endpoint_name+'/{id}/'+biosample.endpoint_name, Resultset)])
            app.add_routes([web.get(uri_subpath+'/'+run.endpoint_name+'/{id}/'+biosample.endpoint_name, Resultset)])
        if run.genomicVariant_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+run.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, Resultset)])
            app.add_routes([web.get(uri_subpath+'/'+run.endpoint_name+'/{id}/'+genomicVariant.endpoint_name, Resultset)])
        if run.individual_lookup == True:
            app.add_routes([web.post(uri_subpath+'/'+run.endpoint_name+'/{id}/'+individual.endpoint_name, Resultset)])
            app.add_routes([web.get(uri_subpath+'/'+run.endpoint_name+'/{id}/'+individual.endpoint_name, Resultset)])

    ssl_context = None
    if (os.path.isfile(conf.beacon_server_key)) and (os.path.isfile(conf.beacon_server_crt)):
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(certfile=conf.beacon_server_crt, keyfile=conf.beacon_server_key)
    
    aiohttp_autoreload.start()
    LOG.debug("Starting app")
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 5050,  ssl_context=ssl_context)
    await site.start()

    while True:
        await asyncio.sleep(3600)

if __name__ == '__main__':# pragma: no cover
    asyncio.run(create_api())