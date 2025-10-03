from aiohttp.test_utils import TestClient, TestServer, loop_context
import unittest
import asyncio
from aiohttp import web
from unittest.mock import MagicMock, patch
from beacon.logs.logs import LOG
import beacon
from beacon.request.classes import ErrorClass
import os
import time
import signal
from threading import Thread
from beacon.request.classes import RequestAttributes

def create_test_app():
    app = web.Application()
    #app.on_startup.append(initialize)
    return app

def _on_shutdown(pid):
    time.sleep(6)

    #  Sending SIGINT to close server
    os.kill(pid, signal.SIGINT)

    LOG.info('Shutting down beacon v2')

async def _graceful_shutdown_ctx(app):
    def graceful_shutdown_sigterm_handler():
        nonlocal thread
        thread = Thread(target=_on_shutdown, args=(os.getpid(),))
        thread.start()

    thread = None

    loop = asyncio.get_event_loop()
    loop.add_signal_handler(
        signal.SIGTERM, graceful_shutdown_sigterm_handler,
    )

    yield

    loop.remove_signal_handler(signal.SIGTERM)

    if thread is not None:
        thread.join()

class TestBudget(unittest.TestCase):
    def setUp(self):
        self.app = create_test_app()

    def tearDown(self):
        _graceful_shutdown_ctx(self.app)

    def test_insert_and_check_budget_by_user(self):
        beacon.conf.conf.query_budget_per_user=True
        beacon.conf.conf.query_budget_per_ip=True
        from beacon.budget.__main__ import check_budget, insert_budget
        with loop_context() as loop:
            client = TestClient(TestServer(self.app), loop=loop)
            loop.run_until_complete(client.start_server())
            MagicClass = MagicMock(_id='hohoho', _error=ErrorClass())
            async def test_insert_and_check_budget_by_user():
                RequestAttributes.ip="172.0.0.1"
                time_now = check_budget(self=MagicClass, username="jane")
                insert_budget(self=MagicClass, username="jane", time_now=time_now)
                insert_budget(self=MagicClass, username="jane", time_now=time_now)
                insert_budget(self=MagicClass, username="jane", time_now=time_now)
                try:
                    resp = check_budget(self=MagicClass, username="jane")
                except Exception:
                    pass
                assert MagicClass._error.error_code == 429
                
            loop.run_until_complete(test_insert_and_check_budget_by_user())
            loop.run_until_complete(client.close())

    def test_insert_and_check_budget_by_unauthorized_user(self):
        beacon.conf.conf.query_budget_per_user=True
        beacon.conf.conf.query_budget_per_ip=True
        from beacon.budget.__main__ import check_budget, insert_budget
        with loop_context() as loop:
            client = TestClient(TestServer(self.app), loop=loop)
            loop.run_until_complete(client.start_server())
            MagicClass = MagicMock(_id='hohoho', _error=ErrorClass())
            async def test_insert_and_check_budget_by_unauthorized_user():
                try:
                    RequestAttributes.ip=None
                    resp = check_budget(self=MagicClass, username="public")
                except Exception:
                    pass
                assert MagicClass._error.error_code == 401
            loop.run_until_complete(test_insert_and_check_budget_by_unauthorized_user())
            loop.run_until_complete(client.close())
    def test_insert_and_check_budget_by_ip(self):
        beacon.conf.conf.query_budget_per_user=True
        beacon.conf.conf.query_budget_per_ip=True
        from beacon.budget.__main__ import check_budget, insert_budget
        with loop_context() as loop:
            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            MagicClass = MagicMock(_id='hohoho', _error=ErrorClass())
            async def test_insert_and_check_budget_by_ip():
                RequestAttributes.ip="172.0.0.1"
                time_now = check_budget(self=MagicClass, username="public")
                insert_budget(self=MagicClass, username="public", time_now=time_now)
                insert_budget(self=MagicClass, username="public", time_now=time_now)
                insert_budget(self=MagicClass, username="public", time_now=time_now)
                try:
                    resp = check_budget(self=MagicClass, username="public")
                except Exception:
                    pass
                assert MagicClass._error.error_code == 429
                _graceful_shutdown_ctx(app)
            loop.run_until_complete(test_insert_and_check_budget_by_ip())
            loop.run_until_complete(client.close())

def suite():
    """
        Gather all the tests from this module in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestBudget))
    #test_suite.addTest(unittest.makeSuite(TestBudget2))
    return test_suite


mySuit=suite()


runner=unittest.TextTestRunner()
runner.run(mySuit)



