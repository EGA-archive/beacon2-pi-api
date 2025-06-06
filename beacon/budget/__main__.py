from beacon.logs.logs import log_with_args_mongo, LOG
from beacon.conf.conf import query_budget_database, level
from datetime import datetime, timedelta
from beacon.request.classes import ErrorClass, RequestAttributes
from beacon.conf.conf import level, query_budget_amount, query_budget_per_user, query_budget_per_ip, query_budget_time_in_seconds

@log_with_args_mongo(level)
def check_budget(self, username):
    try:
        complete_module='beacon.connections.'+query_budget_database+'.budget'
        import importlib
        module = importlib.import_module(complete_module, package=None)
        period_of_not_expired_time=query_budget_time_in_seconds
        time_now=datetime.now()
        start_budget_time=time_now+timedelta(seconds=-period_of_not_expired_time)
        if username is not None and username != 'public' and query_budget_per_user == True:
            remaining_budget=module.get_remaining_budget_by_user(self, username, start_budget_time)
            if len(remaining_budget)>=query_budget_amount:
                ErrorClass.error_code=429
                ErrorClass.error_message="Number of queries exceeded for this user: {}".format(username)
                raise
            else:
                return time_now
        elif query_budget_per_ip == True and RequestAttributes.ip is not None:
            remaining_budget=module.get_remaining_budget_by_ip(self, start_budget_time)
            if len(remaining_budget)>=query_budget_amount:
                ErrorClass.error_code=429
                ErrorClass.error_message="Number of queries exceeded for this ip: {}".format(RequestAttributes.ip)
                raise
            else:
                return time_now
        elif query_budget_per_user == True and username is None or query_budget_per_user == True and username == 'public':
            ErrorClass.error_code=401
            ErrorClass.error_message="Authentication failed. Please, log in to see results for the query"
            raise
        return time_now # pragma: no cover
    except Exception as e:
        raise

@log_with_args_mongo(level)
def insert_budget(self, username, time_now):
    complete_module='beacon.connections.'+query_budget_database+'.budget'
    import importlib
    module = importlib.import_module(complete_module, package=None)
    module.insert_budget(self, username, time_now)
