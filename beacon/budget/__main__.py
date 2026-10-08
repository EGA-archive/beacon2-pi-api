from beacon.logs.logs import log_with_args_mongo
from beacon.conf.conf_override import config
from datetime import datetime, timedelta
from beacon.exceptions.exceptions import NumberOfQueriesExceeded, NoPermissionsAvailable

@log_with_args_mongo(config.level)
def check_budget(self, user_id):
    # Load the connection where the budget is stored
    complete_module='beacon.connections.'+config.query_budget_database+'.budget'
    import importlib
    module = importlib.import_module(complete_module, package=None)
    period_of_not_expired_time=config.query_budget_time_in_seconds
    time_now=datetime.now()
    start_budget_time=time_now+timedelta(seconds=-period_of_not_expired_time)
    # Check if there is user_id in case the budget is meant to be done by user and get the remaining budget
    if user_id is not None and user_id != None and config.query_budget_per_user == True:
        remaining_budget=module.get_remaining_budget_by_user(self, user_id, start_budget_time)
        if len(remaining_budget)>=config.query_budget_amount: # Throw an exception if the query budget is exceeded for the user
            raise NumberOfQueriesExceeded("Number of queries exceeded for this user: {}".format(user_id))
        else: # Return the time to store in the database
            return time_now
    # Check if there is ip in case the budget is meant to be done by ip and get the remaining budget
    elif config.query_budget_per_ip == True and self.request_attributes.ip is not None:
        remaining_budget=module.get_remaining_budget_by_ip(self, start_budget_time)
        if len(remaining_budget)>=config.query_budget_amount:
            raise NumberOfQueriesExceeded("Number of queries exceeded for this ip: {}".format(self.request_attributes.ip))
        else: # Return the time to store in the database
            return time_now
    # Check if there is user_id in case the budget is meant to be done only by user and if there was no ip, then throw an exception
    elif config.query_budget_per_user == True and user_id is None or config.query_budget_per_user == True and user_id == None:
        raise NoPermissionsAvailable("Authentication failed. Please, log in to see results for the query")
    return time_now # Return the time to store in the database

@log_with_args_mongo(config.level)
def load_module_to_insert_budget(self, user_id, time_now):
    # Load the connection where the budget is stored
    complete_module='beacon.connections.'+config.query_budget_database+'.budget'
    import importlib
    module = importlib.import_module(complete_module, package=None)
    # Insert the budget with the user_id/ip and the time at the moment of the query was received
    module.insert_budget(self, user_id, time_now)
