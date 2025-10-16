from aiohttp.test_utils import TestClient, TestServer, loop_context
import unittest
from aiohttp import web
from unittest.mock import MagicMock
from beacon.request.classes import RequestAttributes

def create_test_app():
    app = web.Application()
    return app

class TestBudget(unittest.TestCase):
    def setUp(self):
        self.app = create_test_app()

    def test_insert_and_check_budget_by_user(self):
        from beacon.conf.conf import query_budget_per_user, query_budget_per_ip
        query_budget_per_user=True
        query_budget_per_ip=True
        from beacon.budget.__main__ import check_budget, insert_budget
        with loop_context() as loop:
            client = TestClient(TestServer(self.app), loop=loop)
            loop.run_until_complete(client.start_server())
            MagicClass = MagicMock(_id='hohoho')
            async def test_insert_and_check_budget_by_user():
                RequestAttributes.ip="172.0.0.1"
                time_now = check_budget(self=MagicClass, username="jane")
                insert_budget(self=MagicClass, username="jane", time_now=time_now)
                insert_budget(self=MagicClass, username="jane", time_now=time_now)
                insert_budget(self=MagicClass, username="jane", time_now=time_now)
                try:
                    resp = check_budget(self=MagicClass, username="jane")
                except Exception as e:
                    assert e.status == 429
                
            loop.run_until_complete(test_insert_and_check_budget_by_user())
            loop.run_until_complete(client.close())

    def test_insert_and_check_budget_by_unauthorized_user(self):
        from beacon.conf.conf import query_budget_per_user, query_budget_per_ip
        query_budget_per_user=True
        query_budget_per_ip=True
        from beacon.budget.__main__ import check_budget, insert_budget
        with loop_context() as loop:
            client = TestClient(TestServer(self.app), loop=loop)
            loop.run_until_complete(client.start_server())
            MagicClass = MagicMock(_id='hohoho')
            async def test_insert_and_check_budget_by_unauthorized_user():
                try:
                    RequestAttributes.ip=None
                    resp = check_budget(self=MagicClass, username="public")
                except Exception:
                    pass
            loop.run_until_complete(test_insert_and_check_budget_by_unauthorized_user())
            loop.run_until_complete(client.close())
    def test_insert_and_check_budget_by_ip(self):
        from beacon.conf.conf import query_budget_per_user, query_budget_per_ip
        query_budget_per_user=True
        query_budget_per_ip=True
        from beacon.budget.__main__ import check_budget, insert_budget
        with loop_context() as loop:
            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            MagicClass = MagicMock(_id='hohoho')
            async def test_insert_and_check_budget_by_ip():
                RequestAttributes.ip="172.0.0.1"
                time_now = check_budget(self=MagicClass, username="public")
                insert_budget(self=MagicClass, username="public", time_now=time_now)
                insert_budget(self=MagicClass, username="public", time_now=time_now)
                insert_budget(self=MagicClass, username="public", time_now=time_now)
                try:
                    resp = check_budget(self=MagicClass, username="public")
                except Exception as e:
                    assert e.status == 429
            loop.run_until_complete(test_insert_and_check_budget_by_ip())
            loop.run_until_complete(client.close())

def suite():
    """
        Gather all the tests from this module in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestBudget))
    return test_suite


mySuit=suite()


runner=unittest.TextTestRunner()
runner.run(mySuit)



