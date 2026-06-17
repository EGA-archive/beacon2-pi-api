import asyncio
import aiohttp.web as web
import sys
from aiohttp_middlewares import cors_middleware
from beacon.conf.conf_override import config
from beacon.validator.configuration import check_configuration, check_logs_configuration
from beacon.utils.routes import append_routes
from beacon.utils.middlewares import error_middleware, track_requests_middleware
from beacon.utils.shutters import _graceful_shutdown, on_startup as on_start
from beacon.logs.logs import initialize_logger
from beacon.utils.modules import check_database_connections
import datetime
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

async def create_api(port):
    try:
        # Stdout the initial logs, as we still haven't got the logger ready
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


        # Create the aiohttp object that will be used to run the API
        app = web.Application(
            middlewares=[
                cors_middleware(origins=config.cors_urls),
                error_middleware,
                track_requests_middleware
            ]
        )
        # Add the different attributes to the app object that will be needed for logger and status checks
        app['logger'] = LOG
        app['pending_requests'] = set()
        app['shutting_down'] = False
        app['state'] = 'Running - healthy'

        # Generate the initial routes that the app will initially come with. This regenerates if conf for entry types is modified.
        app = append_routes(app=app)

        # Add the property for the app, when started, to hot-reload every time a config change occurs. 
        app.on_startup.append(on_start)

        # Define what runner will be used to launch the app. Using AppRunner for asynchronous request handling purposes.
        runner = web.AppRunner(app)
        # Prepare and wait for runner to launch
        await runner.setup()
        # Assign a TCP connection to the local system of the launched runner, in this case in all the IPs inside the Docker container and attached to the internal 5050 port.
        site = web.TCPSite(runner, '0.0.0.0', port)
        # Start listening to the TCP site established.
        await site.start()
        # Run the app continuously until an event that makes the app to shut down gracefully happens.
        await _graceful_shutdown(app, LOG, runner)
    # Handle the exceptions that come from an external agent out of the app.
    except Exception as e:
        # Stdout the reason and datetime of the external error that provoked the app to go down.
        print('INFO - {}Z - {}'.format(datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3],'Shutdown because of {} error'.format(e), flush=True))
        # Exit but indicating the app didn't error out, that it was something broader that made the app to go down (that's why we use a 0 instead of a 1)
        sys.exit(0)

# When module initialized with the name beacon, execute creation of the API
if __name__ == '__main__':
    try:
        # Using asyncio to be able to create multiple threads within the app execution.
        asyncio.run(create_api(5050))
    # Catch the exceptions caused by a manual stop of the application.
    except KeyboardInterrupt:
        # Stdout the reason and datetime of the manual stoppage that provoked the app to go down.
        print('INFO - {}Z - {}'.format(datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3],'No pending requests - Shutting down now', flush=True))
    except Exception:
        raise # TODO: The crucial system exceptions must be codified here.