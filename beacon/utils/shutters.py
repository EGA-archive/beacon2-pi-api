import logging
import os
import time
import asyncio
from datetime import datetime
from beacon.conf.conf_override import config
import signal
from threading import Thread

from beacon.logs.logs import initialize_logger

async def initialize(app):
    LOG = app['logger']

    # Set the time when standing up the app and log a message.
    setattr(config, 'update_datetime', datetime.now().isoformat())

    LOG.info("Initialization done.")

def _on_shutdown(pid, app):

    time.sleep(6)

    #  Sending SIGINT to close server
    os.kill(pid, signal.SIGINT)

    LOG = app['logger']
    LOG.info('Shutting down beacon v2')


async def _graceful_shutdown(app, LOG, runner):
    LOG.info("API ready. Listening to requests")

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()

    loop.add_signal_handler(signal.SIGINT, stop_event.set)
    loop.add_signal_handler(signal.SIGTERM, stop_event.set)

    # Wait until signal
    await stop_event.wait()

    LOG.warning("Shutting down...")

    app['shutting_down'] = True
    app['state']='Shutting down'

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

PATHS_TO_RESTART = [
    "/beacon/conf/conf.py",
    "/beacon/models",
    "/beacon/conf/models",
    "/beacon/connections/mongo/conf.py"
]

async def monitor_pending(app):
    LOG = app['logger']
    LOG.warning("Waiting for {} requests to finish...".format(len(app['pending_requests'])))
    while len(app['pending_requests']) >0:
        await asyncio.sleep(1)


async def config_watcher(app):
    LOG = app['logger']

    initial_times = {}

    # Let's add all the snapshot times for the folders to restart when changed
    for path in PATHS_TO_RESTART:
        if os.path.isfile(path):
            initial_times[path] = os.path.getmtime(path)
        elif os.path.isdir(path):
            for root, _, files in os.walk(path):
                for f in files:
                    full = os.path.join(root, f)
                    initial_times[full] = os.path.getmtime(full)
    # We give a time to the server to start
    await asyncio.sleep(5) 

    while True:
        await asyncio.sleep(2)

        new_initial_times = {}

        # We check again for any change
        for path in PATHS_TO_RESTART:
            if os.path.isfile(path):
                new_initial_times[path] = os.path.getmtime(path)
            elif os.path.isdir(path):
                for root, _, files in os.walk(path):
                    if "__pycache__" in root:
                        continue

                    for f in files:
                        if not (f.endswith(".py") or f.endswith(".yml")):
                            continue


                        full = os.path.join(root, f)
                        new_initial_times[full] = os.path.getmtime(full)









        # If there is a change then, restart again the app
        for file_path, new_m in new_initial_times.items():
            old_m = initial_times.get(file_path)
            if old_m is None or new_m != old_m:
                LOG.warning(id(app))
                app['state'] = 'Draining'
                await monitor_pending(app)
                LOG.info("Restarting app")
                os._exit(1)

        initial_times = new_initial_times

async def on_startup(app):
    app["config_watcher"] = asyncio.create_task(config_watcher(app))