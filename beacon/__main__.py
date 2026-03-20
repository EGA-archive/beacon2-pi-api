import asyncio
import aiohttp.web as web
import os
from aiohttp_middlewares import cors_middleware
from beacon.conf.conf_override import config
import ssl
from beacon.validator.configuration import check_configuration, check_logs_configuration
from beacon.utils.routes import append_routes
from beacon.utils.middlewares import error_middleware, track_requests_middleware
from beacon.utils.shutters import _graceful_shutdown_ctx, on_startup as on_start, monitor_pending
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
        app = web.Application(
            middlewares=[
                cors_middleware(origins=config.cors_urls), error_middleware, track_requests_middleware
            ]
        )
        try:
            await check_database_connections(LOG=LOG)
            app['state'] = 'Running - healthy'
        except DatabaseIsDown as e:
            app['state'] = 'Running - degraded'



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

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', port)
        await site.start()

        LOG.warning("API running...")

        stop_event = asyncio.Event()
        loop = asyncio.get_running_loop()

        loop.add_signal_handler(signal.SIGINT, stop_event.set)
        loop.add_signal_handler(signal.SIGTERM, stop_event.set)

        # Wait until signal
        await stop_event.wait()

        LOG.warning("Shutdown signal received")

        app['shutting_down'] = True

        pending = list(app['pending_requests'])

        if pending:
            LOG.warning("Waiting for {} requests to finish...".format(len(pending)))

            try:
                await asyncio.wait_for(
                    asyncio.gather(*pending, return_exceptions=True),
                    timeout=config.pending_requests_timeout_in_seconds
                )
            except asyncio.TimeoutError:
                LOG.warning("Timeout reached, forcing shutdown")

        else:
            LOG.warning("No pending requests")

        await runner.cleanup()

        LOG.warning("Shutdown complete")
    except DatabaseIsDown as e:
        print('INFO - {}Z - {}'.format(datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3],'Restarting', flush=True))
    except Exception:
        raise

if __name__ == '__main__':
    try:
        asyncio.run(create_api(5050))
    except KeyboardInterrupt:
        print('INFO - {}Z - {}'.format(datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3],'No pending requests - Shutting down now', flush=True))
    except Exception:
        raise # TODO: Les excepcions més greus han d'estar codificades aquí.