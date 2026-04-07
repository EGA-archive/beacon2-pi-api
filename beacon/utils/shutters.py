import logging
import os
import time
import asyncio
from datetime import datetime
from beacon.conf.conf_override import config
import signal
from threading import Thread

from beacon.logs.logs import initialize_logger

async def _graceful_shutdown(app, LOG, runner, stop_event=None):
    LOG.info("API ready. Listening to requests")

    if stop_event is None:
        stop_event = asyncio.Event()
        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGINT, stop_event.set)
        loop.add_signal_handler(signal.SIGTERM, stop_event.set)

    await stop_event.wait()

    LOG.warning("Shutting down...")

    app['shutting_down'] = True
    app['state'] = 'Shutting down'

    pending = list(app['pending_requests'])

    if pending:
        LOG.warning(f"Waiting for {len(pending)} requests to finish...")

        try:
            await asyncio.wait_for(
                asyncio.gather(*pending, return_exceptions=True),
                timeout=config.pending_requests_timeout_in_seconds
            )
        except asyncio.TimeoutError:
            LOG.warning("Timeout reached, forcing shutdown")
            for task in pending:
                task.cancel()
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
    if len(app['pending_requests'])>0:
        LOG.warning("Waiting for {} requests to finish...".format(len(app['pending_requests'])))
    while len(app['pending_requests']) >0:
        await asyncio.sleep(1)


async def config_watcher(app, new_initial_times, paths_to_restart=PATHS_TO_RESTART, exit_fn=None, sleep_interval=2):
    LOG = app['logger']
    exit_fn = exit_fn or os._exit

    # Take initial snapshot
    initial_times = {}
    for path in paths_to_restart:
        if os.path.isfile(path):
            initial_times[path] = os.path.getmtime(path)
        elif os.path.isdir(path):
            for root, _, files in os.walk(path):
                for f in files:
                    if "__pycache__" in root:
                        continue
                    if not (f.endswith(".py") or f.endswith(".yml")):
                        continue
                    full = os.path.join(root, f)
                    initial_times[full] = os.path.getmtime(full)

    LOG.info(f"Watcher started for paths: {paths_to_restart}")
    await monitor_pending(app)

    while True:
        await asyncio.sleep(sleep_interval)
        changed = False
        current_times = {}

        # Scan paths
        for path in paths_to_restart:
            if os.path.isfile(path):
                current_times[path] = os.path.getmtime(path)
            elif os.path.isdir(path):
                for root, _, files in os.walk(path):
                    if "__pycache__" in root:
                        continue
                    for f in files:
                        if not (f.endswith(".py") or f.endswith(".yml")):
                            continue
                        full = os.path.join(root, f)
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