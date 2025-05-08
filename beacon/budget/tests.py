from aiohttp.test_utils import TestClient, TestServer, loop_context
import unittest
import asyncio
from aiohttp import web
from unittest.mock import MagicMock
from beacon.budget.budget import check_budget, insert_budget
from datetime import datetime, timedelta
from beacon.logs.logs import LOG
from beacon.request.classes import ErrorClass
from beacon.conf.conf import query_budget_per_user, query_budget_per_ip, query_budget_amount, query_budget_time_in_seconds

#dummy test anonymous
#dummy test login
#add test coverage
#audit --> agafar informació molt específica que ens interessa guardar per sempre (de quins individuals ha obtingut resultats positius)

def create_test_app():
    app = web.Application()
    #app.on_startup.append(initialize)
    return app

class TestBudget(unittest.TestCase):
    def test_insert_and_check_budget_by_ip(self):
        with loop_context() as loop:
            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            MagicClass = MagicMock(_id='hohoho')
            async def test_insert_and_check_budget_by_ip():
                time_now = check_budget(self=MagicClass, ip="172.0.0.1", username="public")
                insert_budget(self=MagicClass, username="public", ip="172.0.0.1", time_now=time_now)
                insert_budget(self=MagicClass, username="public", ip="172.0.0.1", time_now=time_now)
                insert_budget(self=MagicClass, username="public", ip="172.0.0.1", time_now=time_now)
                try:
                    resp = check_budget(self=MagicClass, ip="172.0.0.1", username="public")
                except Exception:
                    pass
                assert ErrorClass.error_code == 429
            loop.run_until_complete(test_insert_and_check_budget_by_ip())
            loop.run_until_complete(client.close())
    def test_insert_and_check_budget_by_user(self):
        with loop_context() as loop:
            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            MagicClass = MagicMock(_id='hohoho')
            async def test_insert_and_check_budget_by_user():
                time_now = check_budget(self=MagicClass, ip="172.0.0.1", username="jane")
                insert_budget(self=MagicClass, username="jane", ip="172.0.0.1", time_now=time_now)
                insert_budget(self=MagicClass, username="jane", ip="172.0.0.1", time_now=time_now)
                insert_budget(self=MagicClass, username="jane", ip="172.0.0.1", time_now=time_now)
                try:
                    resp = check_budget(self=MagicClass, ip="172.0.0.1", username="jane")
                except Exception:
                    pass
                assert ErrorClass.error_code == 429
            loop.run_until_complete(test_insert_and_check_budget_by_user())
            loop.run_until_complete(client.close())
    def test_insert_and_check_budget_by_unauthorized_user(self):
        with loop_context() as loop:
            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            MagicClass = MagicMock(_id='hohoho')
            async def test_insert_and_check_budget_by_unauthorized_user():
                try:
                    resp = check_budget(self=MagicClass, ip=None, username="public")
                except Exception:
                    pass
                assert ErrorClass.error_code == 401
            loop.run_until_complete(test_insert_and_check_budget_by_unauthorized_user())
            loop.run_until_complete(client.close())

if __name__ == '__main__':
    unittest.main()# pragma: no cover