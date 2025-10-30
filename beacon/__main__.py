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
from beacon.utils.shutters import _graceful_shutdown_ctx, initialize

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