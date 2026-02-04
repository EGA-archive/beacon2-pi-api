from beacon.logs.logs import log_with_args_mongo, LOG
from beacon.conf.conf_override import config
from datetime import datetime, timedelta
from beacon.request.classes import RequestAttributes
import aiohttp.web as web
from beacon.exceptions.exceptions import NumberOfQueriesExceeded, NoPermissionsAvailable

@log_with_args_mongo(config.level)
def check_budget(self, username):
    # Load the connection where the budget is stored
    complete_module='beacon.connections.'+config.query_budget_database+'.budget'
    import importlib
    module = importlib.import_module(complete_module, package=None)
    period_of_not_expired_time=config.query_budget_time_in_seconds
    time_now=datetime.now()
    start_budget_time=time_now+timedelta(seconds=-period_of_not_expired_time)
    # Check if there is username in case the budget is meant to be done by user and get the remaining budget
    if username is not None and username != 'public' and config.query_budget_per_user == True:
        remaining_budget=module.get_remaining_budget_by_user(self, username, start_budget_time)
        if len(remaining_budget)>=config.query_budget_amount: # Throw an exception if the query budget is exceeded for the user
            raise NumberOfQueriesExceeded("Number of queries exceeded for this user: {}".format(username))
        else: # Return the time to store in the database
            return time_now
    # Check if there is ip in case the budget is meant to be done by ip and get the remaining budget
    elif config.query_budget_per_ip == True and RequestAttributes.ip is not None:
        remaining_budget=module.get_remaining_budget_by_ip(self, start_budget_time)
        if len(remaining_budget)>=config.query_budget_amount:
            raise NumberOfQueriesExceeded("Number of queries exceeded for this ip: {}".format(RequestAttributes.ip))
        else: # Return the time to store in the database
            return time_now
    # Check if there is username in case the budget is meant to be done only by user and if there was no ip, then throw an exception
    elif config.query_budget_per_user == True and username is None or config.query_budget_per_user == True and username == 'public':
        raise NoPermissionsAvailable("Authentication failed. Please, log in to see results for the query")
    return time_now # Return the time to store in the database

@log_with_args_mongo(config.level)
def insert_budget(self, username, time_now):
    # Load the connection where the budget is stored
    complete_module='beacon.connections.'+config.query_budget_database+'.budget'
    import importlib
    module = importlib.import_module(complete_module, package=None)
    # Insert the budget with the username/ip and the time at the moment of the query was received
    module.insert_budget(self, username, time_now)
