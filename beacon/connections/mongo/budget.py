from pymongo.cursor import Cursor
from beacon.connections.mongo.__init__ import client
from pymongo.collection import Collection
from beacon.logs.logs import log_with_args_mongo, LOG
from beacon.conf.conf import level, query_budget_amount, query_budget_per_user, query_budget_per_ip, query_budget_time, query_budget_table
from datetime import datetime
from beacon.exceptions.exceptions import raise_exception

@log_with_args_mongo(level)
def update_budget(self, username, ip):
    try:
        client.beacon.validate_collection(query_budget_table)
    except Exception:
        client.beacon.create_collection(name=query_budget_table)
    budget_query={}
    period_of_not_expired_time=query_budget_time
    time_now=datetime.now().timestamp()
    start_budget_time=time_now-period_of_not_expired_time

    if username is not None and username != 'public':
        budget_query["username"]=username
        budget_query["timestamp"]={ "$gt": start_budget_time }
        budget_returned = client.beacon[query_budget_table].find(budget_query).max_time_ms(100 * 1000)
        budget_returned=list(budget_returned)
        if len(budget_returned)>=query_budget_amount:
            raise_exception("Number of queries exceeded for this user: {}".format(username), 429)
        else:
            budget_query["ip"]=ip
            budget_query["timestamp"]=time_now
            client.beacon[query_budget_table].insert_one(budget_query)
    else:
        budget_query["ip"]=ip
        budget_query["timestamp"]={ "$gt": start_budget_time }
        budget_returned = client.beacon[query_budget_table].find(budget_query).max_time_ms(100 * 1000)
        budget_returned=list(budget_returned)
        if len(budget_returned)>=query_budget_amount:
            raise_exception("Number of queries exceeded for this ip: {}".format(ip), 429)
        else:
            budget_query["timestamp"]=time_now
            client.beacon[query_budget_table].insert_one(budget_query)