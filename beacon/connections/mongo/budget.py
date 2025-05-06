from beacon.connections.mongo.__init__ import client
from beacon.logs.logs import log_with_args_mongo, LOG
from beacon.conf.conf import level, query_budget_table

@log_with_args_mongo(level)
def get_remaining_budget_by_user(self, username, ip, start_budget_time, time_now):
    try:
        client.beacon.validate_collection(query_budget_table)
    except Exception:
        client.beacon.create_collection(name=query_budget_table)
    budget_query={}
    budget_query["username"]=username
    budget_query["date"]={ "$gt": start_budget_time }
    remaining_budget = client.beacon[query_budget_table].find(budget_query).max_time_ms(100 * 1000)
    remaining_budget=list(remaining_budget)
    return remaining_budget

@log_with_args_mongo(level)
def insert_budget(self, username, ip, start_budget_time, time_now):
    budget_query={}
    budget_query["username"]=username
    budget_query["date"]={ "$gt": start_budget_time }
    budget_query["ip"]=ip
    budget_query["date"]=time_now
    client.beacon[query_budget_table].insert_one(budget_query)

@log_with_args_mongo(level)
def get_remaining_budget_by_ip(self, ip, start_budget_time, time_now):
    budget_query={}
    budget_query["ip"]=ip
    budget_query["date"]={ "$gt": start_budget_time }
    remaining_budget = client.beacon[query_budget_table].find(budget_query).max_time_ms(100 * 1000)
    remaining_budget=list(remaining_budget)
    return remaining_budget