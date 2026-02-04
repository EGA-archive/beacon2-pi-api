from beacon.logs.logs import LOG
import os
import time
import asyncio
from datetime import datetime
from beacon import conf
import signal
from threading import Thread

async def initialize(app):
    # Set the time when standing up the app and log a message.
    setattr(conf, 'update_datetime', datetime.now().isoformat())

    LOG.info("Initialization done.")

def _on_shutdown(pid):
    time.sleep(6)

    #  Sending SIGINT to close server
    os.kill(pid, signal.SIGINT)

    LOG.info('Shutting down beacon v2')

async def _graceful_shutdown_ctx(app):
    def graceful_shutdown_sigterm_handler():
        # Get the process where the app is running in the system.
        nonlocal thread
        thread = Thread(target=_on_shutdown, args=(os.getpid(),))
        thread.start()

    thread = None
    # Catch the process where the app is running.
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(
        signal.SIGTERM, graceful_shutdown_sigterm_handler,
    )
    #TODO: Haig de donar-te un temps d'espera + afegir un brute force shutdown (que també ha d'anar a tancar connexions)
    yield
    # Stop the process where the app is running
    loop.remove_signal_handler(signal.SIGTERM)

    if thread is not None:
        thread.join()

PATHS_TO_RESTART = [
    "/beacon/conf/conf.py",
    "/beacon/models",
    "/beacon/conf/models",
    "/beacon/connections/mongo/conf.py"
]

async def monitor_pending(app):
    LOG.warning("Waiting for requests to finish...")
    while len(app['pending_requests']) >0:
        await asyncio.sleep(1)


async def config_watcher(app):
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
                await monitor_pending(app)
                LOG.warning("Restarting app")
                os._exit(0)

        initial_times = new_initial_times

async def on_startup(app):
    app["config_watcher"] = asyncio.create_task(config_watcher(app))