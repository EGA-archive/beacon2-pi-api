from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponseBadRequest
import logging
from pymongo.mongo_client import MongoClient
from django.urls import resolve
from adminbackend.forms.budget import BudgetForm
from adminbackend.forms.entry_types import EntryTypesForm

import logging

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
