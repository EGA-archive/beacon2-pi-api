from beacon.logs.logs import log_with_args_mongo, LOG
from beacon.conf.conf import query_budget_database, level

def check_budget(self, username, ip):
    try:
        complete_module='beacon.connections.'+query_budget_database+'.budget'
        import importlib
        module = importlib.import_module(complete_module, package=None)
        module.update_budget(self, username, ip)
    except Exception:
        raise