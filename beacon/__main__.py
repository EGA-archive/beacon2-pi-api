import asyncio
import aiohttp.web as web
import os
from aiohttp_middlewares import cors_middleware
from beacon.conf.conf_override import config
import ssl
from beacon.validator.configuration import check_configuration, check_logs_configuration
from beacon.utils.routes import append_routes
from beacon.utils.middlewares import error_middleware, track_requests_middleware
from beacon.utils.shutters import _graceful_shutdown_ctx, on_startup as on_start
from beacon.logs.logs import initialize_logger
from beacon.utils.modules import check_database_connections
import datetime
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

async def create_api(port):
    try:
        print('INFO - {}Z - Preparing the logs'.format(datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3], flush=True))
        # We first check if the logging configuration is correct
        check_logs_configuration()
        # We initialize the logger
        LOG = initialize_logger(config.level)
        # Before standing up the app, check that the configuration makes sense
        check_configuration(LOG=LOG)
        await check_database_connections(LOG=LOG)

        # Create the web app with middlewares for allowing CORS for the specific urls and to handle Not Found and other non related app errors with error_middleware
        app = web.Application(
            middlewares=[
                cors_middleware(origins=config.cors_urls), error_middleware, track_requests_middleware
            ]
        )
        app['logger'] = LOG
        app['pending_requests'] = set()
        app['state'] = 'initializing'

        # Add initialization and graceful shutdown
        app.on_startup.append(on_start) # Added for file conf restart, not conflicting with asynchronous requests handling
        app.cleanup_ctx.append(_graceful_shutdown_ctx)

        # Add routes
        app = append_routes(app=app)

        # Optional: add ssl certificates to encrypt communication from the app
        ssl_context = None
        if (os.path.isfile(config.beacon_server_key)) and (os.path.isfile(config.beacon_server_crt)):
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(certfile=config.beacon_server_crt, keyfile=config.beacon_server_key)
        
        # Add a reloader in case any file is modified, so the app is restarted automatically
        #aiohttp_autoreload.start()

        # Starting app with AppRunner, that is able to handle requests in parallel
        app['state'] = 'ok'
        LOG.info("API ready. Listening to requests")
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