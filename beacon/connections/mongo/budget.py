from beacon.connections.mongo.__init__ import client
from beacon.logs.logs import log_with_args_mongo, LOG
from beacon.conf.conf_override import config
from beacon.request.classes import RequestAttributes

@log_with_args_mongo(config.level)
def get_remaining_budget_by_user(self, username, start_budget_time):
    # Validate if there is any budget table initiated and create one if there isn't
    try:
        client[config.query_budget_db_name].validate_collection(config.query_budget_table)
    except Exception:
        client[config.query_budget_db_name].create_collection(name=config.query_budget_table)
    # Initiate the dictionary to create the query syntax for getting the remaining budget of the user that is performing the query
    budget_query={}
    budget_query["username"]=username
    budget_query["date"]={ "$gt": start_budget_time }
    remaining_budget = client[config.query_budget_db_name][config.query_budget_table].find(budget_query).max_time_ms(100 * 1000)
    remaining_budget=list(remaining_budget)
    return remaining_budget

@log_with_args_mongo(config.level)
def insert_budget(self, username, time_now):
    # Insert in the database one of the uses of the budget for the user/ip performing the query
    budget_query={}
    budget_query["username"]=username
    budget_query["ip"]=RequestAttributes.ip
    budget_query["date"]=time_now
    client[config.query_budget_db_name][config.query_budget_table].insert_one(budget_query)

@log_with_args_mongo(config.level)
def get_remaining_budget_by_ip(self, start_budget_time):
    # Initiate the dictionary to create the query syntax for getting the remaining budget of the ip that is performing the query
    budget_query={}
    budget_query["ip"]=RequestAttributes.ip
    budget_query["date"]={ "$gt": start_budget_time }
    remaining_budget = client[config.query_budget_db_name][config.query_budget_table].find(budget_query).max_time_ms(100 * 1000)
    remaining_budget=list(remaining_budget)
    return remaining_budget