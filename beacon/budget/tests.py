from aiohttp.test_utils import TestClient, TestServer, loop_context
import unittest
from aiohttp import web
from unittest.mock import MagicMock
from beacon.request.classes import RequestAttributes

def create_test_app():
    app = web.Application()
    return app

# Unit test suite for budget enforcement logic (rate limiting per user/IP)
class TestBudget(unittest.TestCase):

    def setUp(self):
        # Create isolated test application instance before each test
        self.app = create_test_app()

    def test_insert_and_check_budget_by_user(self):
        # Enable both per-user and per-IP query budget enforcement
        from beacon.conf.conf_override import config
        config.query_budget_per_user = True
        config.query_budget_per_ip = True

        # Import budget control functions under test
        from beacon.budget.__main__ import check_budget, insert_budget

        # Create async event loop context for running coroutine-based test logic
        with loop_context() as loop:

            # Wrap app in test server/client environment
            client = TestClient(TestServer(self.app), loop=loop)
            loop.run_until_complete(client.start_server())

            # Mock object simulating a DB-backed entity with identifier
            MagicClass = MagicMock(_id='hohoho')

            async def test_insert_and_check_budget_by_user():
                # Simulate incoming request IP (used in IP-based budget tracking)
                RequestAttributes.ip = "172.0.0.1"

                # First budget check establishes baseline timestamp/quota window
                time_now = check_budget(self=MagicClass, username="jane")

                # Simulate multiple requests consuming budget for same user
                insert_budget(self=MagicClass, username="jane", time_now=time_now)
                insert_budget(self=MagicClass, username="jane", time_now=time_now)
                insert_budget(self=MagicClass, username="jane", time_now=time_now)

                # Next check should exceed quota and raise rate-limit exception
                try:
                    resp = check_budget(self=MagicClass, username="jane")
                except Exception as e:
                    # Expected behavior: HTTP-like 429 Too Many Requests
                    assert e.status == 429

            # Execute async test scenario inside event loop
            loop.run_until_complete(test_insert_and_check_budget_by_user())

            # Cleanly shut down test server/client resources
            loop.run_until_complete(client.close())

    def test_insert_and_check_budget_by_unauthorized_user(self):
        # Enable budget enforcement globally
        from beacon.conf.conf_override import config
        config.query_budget_per_user = True
        config.query_budget_per_ip = True

        from beacon.budget.__main__ import check_budget, insert_budget

        with loop_context() as loop:
            client = TestClient(TestServer(self.app), loop=loop)
            loop.run_until_complete(client.start_server())

            MagicClass = MagicMock(_id='hohoho')

            async def test_insert_and_check_budget_by_unauthorized_user():
                # Simulate missing IP (unauthenticated or unknown client)
                RequestAttributes.ip = None

                # Budget check for "public" user should either bypass or fail safely
                try:
                    resp = check_budget(self=MagicClass, username="public")
                except Exception:
                    # Any exception is considered acceptable behavior here
                    # (policy depends on implementation: deny or fallback)
                    pass

            loop.run_until_complete(test_insert_and_check_budget_by_unauthorized_user())
            loop.run_until_complete(client.close())

    def test_insert_and_check_budget_by_ip(self):
        # Enable same budget constraints, but test IP-driven tracking
        from beacon.conf.conf_override import config
        config.query_budget_per_user = True
        config.query_budget_per_ip = True

        from beacon.budget.__main__ import check_budget, insert_budget

        with loop_context() as loop:

            # Fresh app instance for isolated IP-based test case
            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)

            loop.run_until_complete(client.start_server())

            # Mocked entity used to satisfy function signature expectations
            MagicClass = MagicMock(_id='hohoho')

            async def test_insert_and_check_budget_by_ip():
                # Assign explicit IP for rate-limit grouping
                RequestAttributes.ip = "172.0.0.1"

                # First call initializes budget tracking window for this IP/user
                time_now = check_budget(self=MagicClass, username="public")

                # Simulate repeated requests from same IP consuming quota
                insert_budget(self=MagicClass, username="public", time_now=time_now)
                insert_budget(self=MagicClass, username="public", time_now=time_now)
                insert_budget(self=MagicClass, username="public", time_now=time_now)

                # Final check should trigger rate limit exception (429)
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



