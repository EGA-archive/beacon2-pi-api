from beacon.logs.logs import log_with_args, LOG
from beacon import conf
import asyncio
import aiohttp.web as web
import os
from aiohttp_middlewares import cors_middleware
from beacon.conf import conf
import ssl
from beacon.validator.configuration import check_configuration
import aiohttp_autoreload
from beacon.utils.routes import append_routes
from beacon.utils.middlewares import error_middleware
from beacon.utils.shutters import _graceful_shutdown_ctx, on_startup as on_start

async def create_api(port):
    try:
        # Before standing up the app, check that the configuration makes sense
        check_configuration()

        # Create the web app with middlewares for allowing CORS for the specific urls and to handle Not Found and other non related app errors with error_middleware
        app = web.Application(
            middlewares=[
                cors_middleware(origins=conf.cors_urls), error_middleware
            ]
        )

        # Add initialization and graceful shutdown
        app.on_startup.append(on_start) # Added for file conf restart, not conflicting with asynchronous requests handling
        app.cleanup_ctx.append(_graceful_shutdown_ctx)

        # Add routes
        app = append_routes(app)

        # Optional: add ssl certificates to encrypt communication from the app
        ssl_context = None
        if (os.path.isfile(conf.beacon_server_key)) and (os.path.isfile(conf.beacon_server_crt)):
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(certfile=conf.beacon_server_crt, keyfile=conf.beacon_server_key)
        
        # Add a reloader in case any file is modified, so the app is restarted automatically
        aiohttp_autoreload.start()

        # Starting app with AppRunner, that is able to handle requests in parallel
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