import asyncio
import aiohttp.web as web
import sys
from aiohttp_middlewares import cors_middleware
from beacon.conf.conf_override import config
import ssl
from beacon.validator.configuration import check_configuration, check_logs_configuration
from beacon.utils.routes import append_routes
from beacon.utils.middlewares import error_middleware, track_requests_middleware
from beacon.utils.shutters import _graceful_shutdown, on_startup as on_start
from beacon.logs.logs import initialize_logger
from beacon.utils.modules import check_database_connections
from beacon.exceptions.exceptions import DatabaseIsDown
import datetime
import warnings
import signal

warnings.filterwarnings("ignore", category=UserWarning)

async def create_api(port):
    try:
        print('INFO - {}Z - Initializing Beacon Production Implementation'.format(datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3], flush=True))
        print('INFO - {}Z - Preparing the logs'.format(datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3], flush=True))
        # We first check if the logging configuration is correct
        check_logs_configuration()
        # We initialize the logger
        LOG = initialize_logger(config.level)
        # Before standing up the app, check that the configuration makes sense
        check_configuration(LOG=LOG)

            

        # Create the web app with middlewares for allowing CORS for the specific urls and to handle Not Found and other non related app errors with error_middleware

        await check_database_connections(LOG=LOG)



        app = web.Application(
            middlewares=[
                cors_middleware(origins=config.cors_urls),
                error_middleware,
                track_requests_middleware
            ]
        )
        app['logger'] = LOG
        app['pending_requests'] = set()
        app['shutting_down'] = False

        app = append_routes(app=app)

        app.on_startup.append(on_start)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', port)
        await site.start()
        await _graceful_shutdown(app, LOG, runner)

    except Exception:
        print('INFO - {}Z - {}'.format(datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3],'Shutting down...', flush=True))
        sys.exit(0)

if __name__ == '__main__':
    try:
        asyncio.run(create_api(5050))
    except KeyboardInterrupt:
        print('INFO - {}Z - {}'.format(datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3],'No pending requests - Shutting down now', flush=True))
    except Exception:
        raise # TODO: Les excepcions més greus han d'estar codificades aquí.