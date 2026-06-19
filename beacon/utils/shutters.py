import os
import asyncio
from beacon.conf.conf_override import config
import signal

from beacon.logs.logs import initialize_logger

async def _graceful_shutdown(app, LOG, runner, stop_event=None):
    """Stop the app in case of receiving signal for shutdown, handling pending requests in case any is alive"""
    LOG.info("API ready. Listening to requests")

    # If there is no ongoing event in this thread
    if stop_event is None:
        # Start an asyncio event
        stop_event = asyncio.Event()
        # Add it to the current thread where the app is being run
        loop = asyncio.get_running_loop()
        # Add the signals for terminating the event
        loop.add_signal_handler(signal.SIGINT, stop_event.set)
        loop.add_signal_handler(signal.SIGTERM, stop_event.set)
    # Wait until the event is finished
    await stop_event.wait()
    # In case the event is finished, we start logging that the app is shutting down
    LOG.warning("Shutting down...")

    # Create the variables for state checks
    app['shutting_down'] = True
    app['state'] = 'Shutting down'

    # Generate a list with the requests that are yet to be processd
    pending = list(app['pending_requests'])


    # If there are any pending requests
    if pending:
        # Stdout how many requests there are pending
        LOG.warning(f"Waiting for {len(pending)} requests to finish...")

        # Start an asyncio concurrent task gathering the pending requests and set a timeout for them
        try:
            await asyncio.wait_for(
                asyncio.gather(*pending, return_exceptions=True),
                timeout=config.pending_requests_timeout_in_seconds
            )
        # If the timeout expires before requests are processed, cancel the request
        except asyncio.TimeoutError:
            LOG.warning("Timeout reached, forcing shutdown")
            for task in pending:
                task.cancel()
    # If there aren't any pending requests
    else:
        LOG.warning("No pending requests")

    # Once pending requests are finished, clean the executer of the app
    await runner.cleanup()

    LOG.warning("Shutdown complete")

# List that will trigger the hot-reload of the app in case any is modified

PATHS_TO_RESTART = [
    "/beacon/conf/conf.py",
    "/beacon/conf/conf_default.py",
    "/beacon/models",
    "/beacon/conf/models",
    "/beacon/connections/mongo/conf.py"
]

async def monitor_pending(app):
    """This will stdout how many requests there are pending when draining or shutting down"""
    LOG = app['logger']
    # If there are any pending requests, stdout the number of pending requests
    if len(app['pending_requests'])>0:
        LOG.warning("Waiting for {} requests to finish...".format(len(app['pending_requests'])))
    # In case there are yet requests to be processed, wait for them to finish
    while len(app['pending_requests']) >0:
        await asyncio.sleep(1)

async def config_watcher(app, new_initial_times, paths_to_restart=PATHS_TO_RESTART, exit_fn=None, sleep_interval=2):
    """Get the date where the files were last added/modified and then trigger the reload in case the new modification is newer"""
    LOG = app['logger']
    exit_fn = exit_fn or os._exit

    # Take initial snapshot
    initial_times = {}
    # Store the file as path with the time they were last modified
    for path in paths_to_restart:
        # If the file already exists just add it to the object
        if os.path.isfile(path):
            initial_times[path] = os.path.getmtime(path)
        # If the file does not exists
        elif os.path.isdir(path):
            for root, _, files in os.walk(path):
                for f in files:
                    #Discard them if they are a pycache type of file
                    if "__pycache__" in root:
                        continue
                    #Discard them if they are not python scripts or yaml files
                    if not (f.endswith(".py") or f.endswith(".yml")):
                        continue
                    full = os.path.join(root, f)
                    # Then, add them to the object
                    initial_times[full] = os.path.getmtime(full)

    LOG.info(f"Watcher started for paths: {paths_to_restart}")
    await monitor_pending(app)

    # Start non-stopping loop 
    while True:
        # Give a time for the files to be stored/modified and the date changed
        await asyncio.sleep(sleep_interval)
        changed = False
        current_times = {}

        # Scan paths
        for path in paths_to_restart:
            # In case a path of the file is found, store it with the datetime
            if os.path.isfile(path):
                current_times[path] = os.path.getmtime(path)
            # On the contrary, start doing the triage of the files
            elif os.path.isdir(path):
                for root, _, files in os.walk(path):
                    #Discard them if they are a pycache type of file
                    if "__pycache__" in root:
                        continue
                    #Discard them if they are not python scripts or yaml files
                    for f in files:
                        if not (f.endswith(".py") or f.endswith(".yml")):
                            continue
                        full = os.path.join(root, f)
                        # Then, add them to the current times object
                        current_times[full] = os.path.getmtime(full)
        # Compare with snapshot
        for file_path, new_m in current_times.items():
            old_m = initial_times.get(file_path)
            if old_m is None or new_m != old_m:
                LOG.info(f"Change detected: {file_path}")
                app['state'] = 'Draining'
                changed = True
                break  # stop on first change

        # Update snapshots
        initial_times = dict(current_times)
        new_initial_times.clear()
        new_initial_times.update(current_times)

        if changed:
            exit_fn(1)
            return  # stop watcher after detecting a change

async def on_startup(app):
    app["config_watcher"] = asyncio.create_task(config_watcher(app, {}))