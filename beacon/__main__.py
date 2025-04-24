from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf import level
import asyncio
import aiohttp.web as web
from aiohttp.web_request import Request
from beacon.utils.txid import generate_txid
from beacon.permissions.__main__ import dataset_permissions
from beacon.response.builder import builder, collection_builder, info_builder, configuration_builder, map_builder, entry_types_builder, service_info_builder, filtering_terms_builder
from bson import json_util
from beacon.response.catalog import build_beacon_error_response
from beacon.request.classes import ErrorClass
import time
import os
import signal
from threading import Thread
from beacon.utils.requests import get_qparams
from aiohttp_middlewares import cors_middleware
from aiohttp_cors import CorsViewMixin
from datetime import datetime
from beacon.conf import conf
import ssl
from beacon.request.parameters import RequestMeta, RequestQuery

class EndpointView(web.View, CorsViewMixin):
    def __init__(self, request: Request):
        self._request = request
        self._id = generate_txid(self)
        ErrorClass.error_code = None
        ErrorClass.error_message = None

class ServiceInfo(EndpointView):
    @log_with_args(level)
    async def service_info(self, request):
        try:
            response_obj = await service_info_builder(self, request)
            return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')
        except Exception as e:# pragma: no cover
            raise

    async def get(self):
        try:
            return await self.service_info(self.request)
        except Exception as e:# pragma: no cover
            response_obj = build_beacon_error_response(self, ErrorClass.error_code, {}, ErrorClass.error_message)
            return web.Response(text=json_util.dumps(response_obj), status=ErrorClass.error_code, content_type='application/json')

    async def post(self):
        try:
            return await self.service_info(self.request)
        except Exception as e:# pragma: no cover
            response_obj = build_beacon_error_response(self, ErrorClass.error_code, {}, ErrorClass.error_message)
            return web.Response(text=json_util.dumps(response_obj), status=ErrorClass.error_code, content_type='application/json')

class EntryTypes(EndpointView):
    @log_with_args(level)
    async def entry_types(self, request):
        try:
            response_obj = await entry_types_builder(self, request)
            return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')
        except Exception:# pragma: no cover
            raise

    async def get(self):
        try:
            return await self.entry_types(self.request)
        except Exception as e:# pragma: no cover
            response_obj = build_beacon_error_response(self, ErrorClass.error_code, {}, ErrorClass.error_message)
            return web.Response(text=json_util.dumps(response_obj), status=ErrorClass.error_code, content_type='application/json')

    async def post(self):
        try:
            return await self.entry_types(self.request)
        except Exception as e:# pragma: no cover
            response_obj = build_beacon_error_response(self, ErrorClass.error_code, {}, ErrorClass.error_message)
            return web.Response(text=json_util.dumps(response_obj), status=ErrorClass.error_code, content_type='application/json')

class Map(EndpointView):
    @log_with_args(level)
    async def map(self, request):
        try:
            response_obj = await map_builder(self, request)
            return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')
        except Exception:# pragma: no cover
            raise

    async def get(self):
        try:
            return await self.map(self.request)
        except Exception as e:# pragma: no cover
            response_obj = build_beacon_error_response(self, ErrorClass.error_code, {}, ErrorClass.error_message)
            return web.Response(text=json_util.dumps(response_obj), status=ErrorClass.error_code, content_type='application/json')

    async def post(self):
        try:
            return await self.map(self.request)
        except Exception as e:# pragma: no cover
            response_obj = build_beacon_error_response(self, ErrorClass.error_code, {}, ErrorClass.error_message)
            return web.Response(text=json_util.dumps(response_obj), status=ErrorClass.error_code, content_type='application/json')

class Configuration(EndpointView):
    @log_with_args(level)
    async def configuration(self, request):
        try:
            response_obj = await configuration_builder(self, request)
            return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')
        except Exception:# pragma: no cover
            raise

    async def get(self):
        try:
            return await self.configuration(self.request)
        except Exception as e:# pragma: no cover
            response_obj = build_beacon_error_response(self, ErrorClass.error_code, {}, ErrorClass.error_message)
            return web.Response(text=json_util.dumps(response_obj), status=ErrorClass.error_code, content_type='application/json')

    async def post(self):
        try:
            return await self.configuration(self.request)
        except Exception as e:# pragma: no cover
            response_obj = build_beacon_error_response(self, ErrorClass.error_code, {}, ErrorClass.error_message)
            return web.Response(text=json_util.dumps(response_obj), status=ErrorClass.error_code, content_type='application/json')

class Info(EndpointView):
    @log_with_args(level)
    async def info(self, request):
        try:
            response_obj = await info_builder(self, request)
            return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')
        except Exception:# pragma: no cover
            raise

    async def get(self):
        try:
            return await self.info(self.request)
        except Exception as e:# pragma: no cover
            response_obj = build_beacon_error_response(self, ErrorClass.error_code, {}, ErrorClass.error_message)
            return web.Response(text=json_util.dumps(response_obj), status=ErrorClass.error_code, content_type='application/json')

    async def post(self):
        try:
            return await self.info(self.request)
        except Exception as e:# pragma: no cover
            response_obj = build_beacon_error_response(self, ErrorClass.error_code, {}, ErrorClass.error_message)
            return web.Response(text=json_util.dumps(response_obj), status=ErrorClass.error_code, content_type='application/json')

class Collection(EndpointView):
    @log_with_args(level)
    async def collection(self, request, qparams, entry_type, entry_id):
        try:
            response_obj = await collection_builder(self, request, qparams, entry_type, entry_id)
            return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')
        except Exception:# pragma: no cover
            raise

    async def get(self):
        try:
            post_data = None
            qparams = await get_qparams(self, post_data, self.request) 
            path_list = self.request.path.split('/')
            if len(path_list) > 4:
                entry_type=path_list[2]+'_'+path_list[4]# pragma: no cover
            else:
                entry_type=path_list[2]
            entry_id = self.request.match_info.get('id', None)
            if entry_id == None:
                entry_id = self.request.match_info.get('variantInternalId', None)
            return await self.collection(self.request, qparams, entry_type, entry_id)
        except Exception as e:# pragma: no cover
            response_obj = build_beacon_error_response(self, ErrorClass.error_code, {
                "apiVersion": RequestMeta().api_version,
                "requestedSchemas": RequestMeta().requested_schemas,
                "pagination": {"skip": 0,"limit": 10 },
                "requestedGranularity": RequestQuery().requested_granularity,
            }, ErrorClass.error_message)
            return web.Response(text=json_util.dumps(response_obj), status=ErrorClass.error_code, content_type='application/json')

    async def post(self):
        try:
            request = await self.request.json() if self.request.has_body else {}
            post_data = request
            qparams = await get_qparams(self, post_data, request) 
            path_list = self.request.path.split('/')
            if len(path_list) > 4:
                entry_type=path_list[2]+'_'+path_list[4]# pragma: no cover
            else:
                entry_type=path_list[2]
            entry_id = self.request.match_info.get('id', None)
            if entry_id == None:
                entry_id = self.request.match_info.get('variantInternalId', None)
            return await self.collection(request, qparams, entry_type, entry_id)
        except Exception as e:# pragma: no cover
            response_obj = build_beacon_error_response(self, ErrorClass.error_code, {
                "apiVersion": RequestMeta().api_version,
                "requestedSchemas": RequestMeta().requested_schemas,
                "pagination": {"skip": 0,"limit": 10 },
                "requestedGranularity": RequestQuery().requested_granularity,
            }, ErrorClass.error_message)
            return web.Response(text=json_util.dumps(response_obj), status=ErrorClass.error_code, content_type='application/json')
        
class FilteringTerms(EndpointView):
    @log_with_args(level)
    async def filteringTerms(self, request, qparams):
        try:
            response_obj = await filtering_terms_builder(self, request, qparams)
            return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')
        except Exception:# pragma: no cover
            raise

    async def get(self):
        try:
            post_data = None
            qparams = await get_qparams(self, post_data, self.request) 
            return await self.filteringTerms(self.request, qparams)
        except Exception as e:# pragma: no cover
            response_obj = build_beacon_error_response(self, ErrorClass.error_code, {
                "apiVersion": RequestMeta().api_version,
                "requestedSchemas": RequestMeta().requested_schemas,
                "pagination": {"skip": 0,"limit": 10 },
                "requestedGranularity": RequestQuery().requested_granularity,
            }, ErrorClass.error_message)
            return web.Response(text=json_util.dumps(response_obj), status=ErrorClass.error_code, content_type='application/json')

    async def post(self):
        try:
            post_data = None
            qparams = await get_qparams(self, post_data, self.request) 
            return await self.filteringTerms(self.request, qparams)
        except Exception as e:# pragma: no cover
            response_obj = build_beacon_error_response(self, ErrorClass.error_code, {
                "apiVersion": RequestMeta().api_version,
                "requestedSchemas": RequestMeta().requested_schemas,
                "pagination": {"skip": 0,"limit": 10 },
                "requestedGranularity": RequestQuery().requested_granularity,
            }, ErrorClass.error_message)
            return web.Response(text=json_util.dumps(response_obj), status=ErrorClass.error_code, content_type='application/json')

class Resultset(EndpointView):
    @dataset_permissions
    @log_with_args(level)
    async def resultset(self, post_data, request, qparams, entry_type, entry_id, datasets, headers, ip):
        try:
            response_obj = await builder(self, request, datasets, qparams, entry_type, entry_id)
            return web.Response(text=json_util.dumps(response_obj), status=200, content_type='application/json')
        except Exception:# pragma: no cover
            raise

    async def get(self):
        try:
            ip = self.request.remote
            post_data = None
            headers = None
            qparams = await get_qparams(self, post_data, self.request) 
            path_list = self.request.path.split('/')
            if len(path_list) > 4:
                entry_type=path_list[2]+'_'+path_list[4]
            else:
                entry_type=path_list[2]
            entry_id = self.request.match_info.get('id', None)
            if entry_id == None:
                entry_id = self.request.match_info.get('variantInternalId', None)
            return await self.resultset(post_data, self.request, qparams, entry_type, entry_id, ip, headers)
        except Exception as e:# pragma: no cover
            response_obj = build_beacon_error_response(self, ErrorClass.error_code, {
                "apiVersion": RequestMeta().api_version,
                "requestedSchemas": RequestMeta().requested_schemas,
                "pagination": {"skip": 0,"limit": 10 },
                "requestedGranularity": RequestQuery().requested_granularity,
            }, ErrorClass.error_message)
            return web.Response(text=json_util.dumps(response_obj), status=ErrorClass.error_code, content_type='application/json')

    async def post(self):
        try:
            ip = self.request.remote
            request = await self.request.json() if self.request.has_body else {}
            headers = self.request.headers
            post_data = request
            qparams = await get_qparams(self, post_data, request) 
            path_list = self.request.path.split('/')
            if len(path_list) > 4:
                entry_type=path_list[2]+'_'+path_list[4]# pragma: no cover
            else:
                entry_type=path_list[2]
            entry_id = self.request.match_info.get('id', None)
            if entry_id == None:
                entry_id = self.request.match_info.get('variantInternalId', None)
            return await self.resultset(post_data, request, qparams, entry_type, entry_id, ip, headers)
        except Exception as e:# pragma: no cover
            response_obj = build_beacon_error_response(self, ErrorClass.error_code, {
                "apiVersion": RequestMeta().api_version,
                "requestedSchemas": RequestMeta().requested_schemas,
                "pagination": {"skip": 0,"limit": 10 },
                "requestedGranularity": RequestQuery().requested_granularity,
            }, ErrorClass.error_message)
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
    app = web.Application(
        middlewares=[
            cors_middleware(origins=conf.cors_urls)
        ]
    )
    app.on_startup.append(initialize)
    app.cleanup_ctx.append(_graceful_shutdown_ctx)
    
    app.add_routes([web.post('/api', Info)])
    app.add_routes([web.post('/api/info', Info)])
    app.add_routes([web.post('/api/entry_types', EntryTypes)])
    app.add_routes([web.post('/api/service-info', ServiceInfo)])
    app.add_routes([web.post('/api/configuration', Configuration)])
    app.add_routes([web.post('/api/map', Map)])
    app.add_routes([web.post('/api/filtering_terms', FilteringTerms)])
    app.add_routes([web.post('/api/datasets', Collection)])
    app.add_routes([web.post('/api/datasets/{id}', Collection)])
    app.add_routes([web.post('/api/datasets/{id}/g_variants', Resultset)])
    app.add_routes([web.post('/api/datasets/{id}/biosamples', Resultset)])
    app.add_routes([web.post('/api/datasets/{id}/analyses', Resultset)])
    app.add_routes([web.post('/api/datasets/{id}/runs', Resultset)])
    app.add_routes([web.post('/api/datasets/{id}/individuals', Resultset)])
    app.add_routes([web.post('/api/cohorts', Collection)])
    app.add_routes([web.post('/api/cohorts/{id}', Collection)])
    app.add_routes([web.post('/api/cohorts/{id}/individuals', Resultset)])
    app.add_routes([web.post('/api/cohorts/{id}/g_variants', Resultset)])
    app.add_routes([web.post('/api/cohorts/{id}/biosamples', Resultset)])
    app.add_routes([web.post('/api/cohorts/{id}/analyses', Resultset)])
    app.add_routes([web.post('/api/cohorts/{id}/runs', Resultset)])
    app.add_routes([web.post('/api/g_variants', Resultset)])
    app.add_routes([web.post('/api/g_variants/{id}', Resultset)])
    app.add_routes([web.post('/api/g_variants/{id}/analyses', Resultset)])
    app.add_routes([web.post('/api/g_variants/{id}/biosamples', Resultset)])
    app.add_routes([web.post('/api/g_variants/{id}/individuals', Resultset)])
    app.add_routes([web.post('/api/g_variants/{id}/runs', Resultset)])
    app.add_routes([web.post('/api/individuals', Resultset)])
    app.add_routes([web.post('/api/individuals/{id}', Resultset)])
    app.add_routes([web.post('/api/individuals/{id}/g_variants', Resultset)])
    app.add_routes([web.post('/api/individuals/{id}/biosamples', Resultset)])
    app.add_routes([web.post('/api/analyses', Resultset)])
    app.add_routes([web.post('/api/analyses/{id}', Resultset)])
    app.add_routes([web.post('/api/analyses/{id}/g_variants', Resultset)])
    app.add_routes([web.post('/api/biosamples', Resultset)])
    app.add_routes([web.post('/api/biosamples/{id}', Resultset)])
    app.add_routes([web.post('/api/biosamples/{id}/g_variants', Resultset)])
    app.add_routes([web.post('/api/biosamples/{id}/analyses', Resultset)])
    app.add_routes([web.post('/api/biosamples/{id}/runs', Resultset)])
    app.add_routes([web.post('/api/runs', Resultset)])
    app.add_routes([web.post('/api/runs/{id}', Resultset)])
    app.add_routes([web.post('/api/runs/{id}/analyses', Resultset)])
    app.add_routes([web.post('/api/runs/{id}/g_variants', Resultset)])
    app.add_routes([web.get('/api', Info)])
    app.add_routes([web.get('/api/info', Info)])
    app.add_routes([web.get('/api/entry_types', EntryTypes)])
    app.add_routes([web.get('/api/service-info', ServiceInfo)])
    app.add_routes([web.get('/api/configuration', Configuration)])
    app.add_routes([web.get('/api/map', Map)])
    app.add_routes([web.get('/api/filtering_terms', FilteringTerms)])
    app.add_routes([web.get('/api/datasets', Collection)])
    app.add_routes([web.get('/api/datasets/{id}', Collection)])
    app.add_routes([web.get('/api/datasets/{id}/g_variants', Resultset)])
    app.add_routes([web.get('/api/datasets/{id}/biosamples', Resultset)])
    app.add_routes([web.get('/api/datasets/{id}/analyses', Resultset)])
    app.add_routes([web.get('/api/datasets/{id}/runs', Resultset)])
    app.add_routes([web.get('/api/datasets/{id}/individuals', Resultset)])
    app.add_routes([web.get('/api/cohorts', Collection)])
    app.add_routes([web.get('/api/cohorts/{id}', Collection)])
    app.add_routes([web.get('/api/cohorts/{id}/individuals', Resultset)])
    app.add_routes([web.get('/api/cohorts/{id}/g_variants', Resultset)])
    app.add_routes([web.get('/api/cohorts/{id}/biosamples', Resultset)])
    app.add_routes([web.get('/api/cohorts/{id}/analyses', Resultset)])
    app.add_routes([web.get('/api/cohorts/{id}/runs', Resultset)])
    app.add_routes([web.get('/api/g_variants', Resultset)])
    app.add_routes([web.get('/api/g_variants/{id}', Resultset)])
    app.add_routes([web.get('/api/g_variants/{id}/analyses', Resultset)])
    app.add_routes([web.get('/api/g_variants/{id}/biosamples', Resultset)])
    app.add_routes([web.get('/api/g_variants/{id}/individuals', Resultset)])
    app.add_routes([web.get('/api/g_variants/{id}/runs', Resultset)])
    app.add_routes([web.get('/api/individuals', Resultset)])
    app.add_routes([web.get('/api/individuals/{id}', Resultset)])
    app.add_routes([web.get('/api/individuals/{id}/g_variants', Resultset)])
    app.add_routes([web.get('/api/individuals/{id}/biosamples', Resultset)])
    app.add_routes([web.get('/api/analyses', Resultset)])
    app.add_routes([web.get('/api/analyses/{id}', Resultset)])
    app.add_routes([web.get('/api/analyses/{id}/g_variants', Resultset)])
    app.add_routes([web.get('/api/biosamples', Resultset)])
    app.add_routes([web.get('/api/biosamples/{id}', Resultset)])
    app.add_routes([web.get('/api/biosamples/{id}/g_variants', Resultset)])
    app.add_routes([web.get('/api/biosamples/{id}/analyses', Resultset)])
    app.add_routes([web.get('/api/biosamples/{id}/runs', Resultset)])
    app.add_routes([web.get('/api/runs', Resultset)])
    app.add_routes([web.get('/api/runs/{id}', Resultset)])
    app.add_routes([web.get('/api/runs/{id}/analyses', Resultset)])
    app.add_routes([web.get('/api/runs/{id}/g_variants', Resultset)])

    ssl_context = None
    if (os.path.isfile(conf.beacon_server_key)) and (os.path.isfile(conf.beacon_server_crt)):
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(certfile=conf.beacon_server_crt, keyfile=conf.beacon_server_key)

    LOG.debug("Starting app")
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 5050,  ssl_context=ssl_context)
    await site.start()

    while True:
        await asyncio.sleep(3600)

if __name__ == '__main__':# pragma: no cover
    asyncio.run(create_api())