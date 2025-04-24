from pymongo.cursor import Cursor
from beacon.connections.mongo.__init__ import client
from pymongo.collection import Collection
from beacon.logs.logs import log_with_args_mongo, LOG
from beacon.conf.conf import level, query_budget_amount, query_budget_per_user, query_budget_per_ip, query_budget_time_in_seconds, query_budget_table
from datetime import datetime, timedelta
from beacon.request.classes import ErrorClass

@log_with_args_mongo(level)
def update_budget(self, username, ip):
    try:
        client.beacon.validate_collection(query_budget_table)
    except Exception:
        client.beacon.create_collection(name=query_budget_table)
    budget_query={}
    period_of_not_expired_time=query_budget_time_in_seconds
    time_now=datetime.now()
    start_budget_time=time_now+timedelta(seconds=-period_of_not_expired_time)

    if username is not None and username != 'public' and query_budget_per_user == True:
        budget_query["username"]=username
        budget_query["date"]={ "$gt": start_budget_time }
        budget_returned = client.beacon[query_budget_table].find(budget_query).max_time_ms(100 * 1000)
        budget_returned=list(budget_returned)
        if len(budget_returned)>=query_budget_amount:
            ErrorClass.error_code=429
            ErrorClass.error_message="Number of queries exceeded for this user: {}".format(username)
            raise
        else:
            budget_query["ip"]=ip
            budget_query["date"]=time_now
            client.beacon[query_budget_table].insert_one(budget_query)
    elif query_budget_per_ip == True:
        budget_query["ip"]=ip
        budget_query["date"]={ "$gt": start_budget_time }
        budget_returned = client.beacon[query_budget_table].find(budget_query).max_time_ms(100 * 1000)
        budget_returned=list(budget_returned)
        if len(budget_returned)>=query_budget_amount:
            ErrorClass.error_code=429
            ErrorClass.error_message="Number of queries exceeded for this ip: {}".format(ip)
            raise
        else:
            budget_query["username"]="public"
            budget_query["date"]=time_now
            client.beacon[query_budget_table].insert_one(budget_query)
    elif query_budget_per_user == True and username is None or query_budget_per_user == True and username == 'public':
        ErrorClass.error_code=401
        ErrorClass.error_message="Authentication failed. Please, log in to see results for the query"
        raise