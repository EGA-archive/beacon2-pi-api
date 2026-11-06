import asyncio
import aiohttp.web as web
import sys
import datetime
import warnings
from concurrent.futures import ThreadPoolExecutor
from aiohttp_middlewares import cors_middleware
from beacon.conf.conf_override import config
from beacon.validator.configuration import check_configuration, check_logs_configuration
from beacon.utils.routes import append_routes
from beacon.utils.middlewares import error_middleware, track_requests_middleware
from beacon.utils.shutters import _graceful_shutdown, on_startup as on_start
from beacon.logs.logs import initialize_logger
from beacon.utils.modules import check_database_connections

warnings.filterwarnings("ignore", category=UserWarning)

async def close_pools(app):
    for name in ('db_pool', 'cpu_pool'):
        pool = app.get(name)
        if pool is not None:
            await asyncio.to_thread(pool.shutdown, wait=True)


async def create_api(port):
    try:
        print(
            'INFO - {}Z - Initializing Beacon Production Implementation'.format(
                datetime.datetime.now(datetime.timezone.utc)
                .strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
            ),
            flush=True,
        )

        print(
            'INFO - {}Z - Preparing the logs'.format(
                datetime.datetime.now(datetime.timezone.utc)
                .strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
            ),
            flush=True,
        )

        check_logs_configuration()
        LOG = initialize_logger(config.level)
        check_configuration(LOG=LOG)

        await check_database_connections(LOG=LOG)

        app = web.Application(
            middlewares=[
                cors_middleware(origins=config.cors_urls),
                error_middleware,
                track_requests_middleware,
            ]
        )

        app['logger'] = LOG
        app['pending_requests'] = set()
        app['shutting_down'] = False
        app['state'] = 'Running - healthy'

        app['db_pool'] = ThreadPoolExecutor(max_workers=config.max_num_of_concurrent_threads)

        app = append_routes(app=app)

        app.on_startup.append(on_start)


        runner = web.AppRunner(app)
        app.on_cleanup.append(close_pools)

        await runner.setup()

        site = web.TCPSite(runner, '0.0.0.0', port)
        await site.start()

        await _graceful_shutdown(app, LOG, runner)

    except Exception as e:
        print(
            'INFO - {}Z - {}'.format(
                datetime.datetime.now(datetime.timezone.utc)
                .strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3],
                'Shutdown because of {} error'.format(e),
            ),
            flush=True,
        )
        sys.exit(0)


if __name__ == '__main__':
    try:
        asyncio.run(create_api(5050))
    except KeyboardInterrupt:
        print(
            'INFO - {}Z - {}'.format(
                datetime.datetime.now(datetime.timezone.utc)
                .strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3],
                'No pending requests - Shutting down now',
            ),
            flush=True,
        )
    except Exception:
        raise
