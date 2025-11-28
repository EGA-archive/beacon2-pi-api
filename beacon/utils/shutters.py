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

    yield
    # Stop the process where the app is running
    loop.remove_signal_handler(signal.SIGTERM)

    if thread is not None:
        thread.join()