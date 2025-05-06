from beacon.logs.logs import log_with_args_mongo, LOG
from beacon.conf.conf import query_budget_database, level
from datetime import datetime, timedelta
from beacon.request.classes import ErrorClass
from beacon.conf.conf import level, query_budget_amount, query_budget_per_user, query_budget_per_ip, query_budget_time_in_seconds, query_budget_table

@log_with_args_mongo(level)
def check_budget(self, username, ip):
    try:
        complete_module='beacon.connections.'+query_budget_database+'.budget'
        import importlib
        module = importlib.import_module(complete_module, package=None)
        period_of_not_expired_time=query_budget_time_in_seconds
        time_now=datetime.now()
        start_budget_time=time_now+timedelta(seconds=-period_of_not_expired_time)
        if username is not None and username != 'public' and query_budget_per_user == True:
            remaining_budget=module.get_remaining_budget_by_user(self, username, ip, start_budget_time, time_now)
            if len(remaining_budget)>=query_budget_amount:
                ErrorClass.error_code=429
                ErrorClass.error_message="Number of queries exceeded for this user: {}".format(username)
                raise
            else:
                module.insert_budget(self, username, ip, start_budget_time, time_now)
        elif query_budget_per_ip == True:
            remaining_budget=module.get_remaining_budget_by_ip(self, ip, start_budget_time, time_now)
            if len(remaining_budget)>=query_budget_amount:
                ErrorClass.error_code=429
                ErrorClass.error_message="Number of queries exceeded for this ip: {}".format(ip)
                raise
            else:
                module.insert_budget(self, username, ip, start_budget_time, time_now)
        elif query_budget_per_user == True and username is None or query_budget_per_user == True and username == 'public':
            ErrorClass.error_code=401
            ErrorClass.error_message="Authentication failed. Please, log in to see results for the query"
            raise
    except Exception as e:
        raise