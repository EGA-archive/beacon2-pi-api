from beacon.logs.logs import log_with_args, LOG
from beacon import conf
import asyncio
import aiohttp.web as web
from beacon.exceptions.builder import error_builder
from bson import json_util
import time
import os
import signal
from threading import Thread
from aiohttp_middlewares import cors_middleware
from datetime import datetime
from beacon.conf import conf
import ssl
from beacon.validator.configuration import check_configuration
import aiohttp_autoreload
from beacon.views.endpoint import EndpointView
from beacon.utils.routes import append_routes

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
        app = append_routes(app)

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