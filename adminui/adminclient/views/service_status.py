from django.shortcuts import render, redirect
import logging
from beacon.connections.mongo.__init__ import query_budget_database
from beacon.conf.conf import uri, uri_subpath
import subprocess
import os
import logging
import importlib


LOG = logging.getLogger(__name__)
fmt = '%(levelname)s - %(asctime)s - %(message)s'
formatter = logging.Formatter(fmt)
sh = logging.StreamHandler()
sh.setLevel('NOTSET')
sh.setFormatter(formatter)
LOG.addHandler(sh)

def default_view(request):
    context = {}
    if request.method == 'POST':
        for k in request.POST:

            if k == 'TestDatabase':
                dirs = os.listdir("adminui/beacon/connections")
                for dir in dirs:
                    if 'mongo' in dir:
                        try:
                            complete_module='beacon.connections.'+dir
                            module = importlib.import_module(complete_module, package=None)
                            client = module.client.server_info()
                            client = "Ok and running in a mongo " + client["version"] + "version"
                        except Exception:
                            client = 'Connection could not be established'
                context = {"client": client}
            elif k == 'TestAPI':
                try:
                    client = subprocess.check_output("curl -s -o /dev/null -v {}".format(uri+uri_subpath), shell=True)
                    client = 'Connection successful'
                except Exception:
                    client = 'Connection could not be established'
                context = {"client": client}
            elif k == 'BudgetDatabase':
                if 'mongo' in query_budget_database:
                    try:
                        complete_module='beacon.connections.'+query_budget_database
                        module = importlib.import_module(complete_module, package=None)
                        client = module.client.server_info()
                        client = "Ok and running in a mongo " + client["version"] + "version"
                    except Exception:
                        client = 'Connection could not be established'
                context = {"client": client}
            elif k == 'UserInterface':
                pass
            elif k == 'GeneralStatus':
                dirs = os.listdir("adminui/beacon/connections")
                for dir in dirs:
                    if 'mongo' in dir:
                        try:
                            complete_module='beacon.connections.'+dir
                            module = importlib.import_module(complete_module, package=None)
                            database = module.client.server_info()
                            database = "Ok and running in a mongo " + database["version"] + "version"
                        except Exception:
                            database = 'Connection could not be established'
                try:
                    api = subprocess.check_output("curl -s -o /dev/null -v {}".format(uri+uri_subpath), shell=True)
                    api = 'Connection successful'
                except Exception:
                    api = 'Connection could not be established'
                if 'mongo' in query_budget_database:
                    try:
                        complete_module='beacon.connections.'+query_budget_database
                        module = importlib.import_module(complete_module, package=None)
                        budget = module.client.server_info()
                        budget = "Ok and running in a mongo " + budget["version"] + "version"
                    except Exception:
                        budget = 'Connection could not be established'
                context = {"database": database, "budget": budget, "api": api}
                

        template = "general_configuration/service_status.html"
        return render(request, template, context)
    template = "general_configuration/service_status.html"
    return render(request, template, context)
