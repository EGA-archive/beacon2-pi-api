from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponseBadRequest
import logging
from pymongo.mongo_client import MongoClient
from django.urls import resolve
from adminbackend.forms.budget import BudgetForm
from beacon.conf.conf import query_budget_database

import logging

complete_module='beacon.connections.'+query_budget_database
import importlib
module = importlib.import_module(complete_module, package=None)

LOG = logging.getLogger(__name__)
fmt = '%(levelname)s - %(asctime)s - %(message)s'
formatter = logging.Formatter(fmt)
sh = logging.StreamHandler()
sh.setLevel('NOTSET')
sh.setFormatter(formatter)
LOG.addHandler(sh)

def default_view(request):
    form =BudgetForm()
    context = {'form': form}
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if 'Test Budget Connection' in request.POST:
            if 'mongo' in query_budget_database:
                try:
                    client = module.client.server_info()
                    client = "Ok and running in a mongo " + client["version"] + "version"
                except Exception:
                    client = 'Connection could not be established'
            #client = module.client.admin.command('ismaster')
            template = "general_configuration/budget.html"
            context = {'form': form, 'client': client}
            return render(request, template, context)
        if form.is_valid():
            budgetUser = form.cleaned_data['BudgetUser']
            budgetIP = form.cleaned_data['BudgetIP']
            budgetAmount = form.cleaned_data['BudgetAmount']
            budgetTime = form.cleaned_data['BudgetTime']
            budgetDB = form.cleaned_data['BudgetDB']
            budgetDBname = form.cleaned_data['BudgetDBName']
            budgetTable = form.cleaned_data['BudgetTable']
            with open("adminui/beacon/conf/conf.py") as f:
                lines = f.readlines()
            with open("adminui/beacon/conf/conf.py", "w") as f:
                new_lines =''
                for line in lines:
                    if 'query_budget_per_user' in str(line):
                        new_lines+="query_budget_per_user="+str(budgetUser)+"\n"
                    elif 'query_budget_per_ip' in str(line):
                        new_lines+="query_budget_per_ip="+str(budgetIP)+"\n"
                    elif 'query_budget_amount' in str(line):
                        new_lines+="query_budget_amount="+str(budgetAmount)+"\n"
                    elif 'query_budget_time_in_seconds' in str(line):
                        new_lines+="query_budget_time_in_seconds="+str(budgetTime)+"\n"
                    elif 'query_budget_database' in str(line):
                        new_lines+="query_budget_database="+'"'+budgetDB+'"'+"\n"
                    elif 'query_budget_db_name' in str(line):
                        new_lines+="query_budget_db_name="+'"'+budgetDBname+'"'+"\n"
                    elif 'query_budget_table' in str(line):
                        new_lines+="query_budget_table="+'"'+budgetTable+'"'+"\n"
                    else:
                        new_lines+=line
                    
                f.write(new_lines)
            f.close()
            return redirect("adminclient:budget")
    template = "general_configuration/budget.html"
    return render(request, template, context)
