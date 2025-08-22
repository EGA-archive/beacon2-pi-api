from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponseBadRequest
import logging
from pymongo.mongo_client import MongoClient
from django.urls import resolve
from adminbackend.forms.connections import ConnectionsForm, ChooseConnection, LinkConnection
from beacon.conf.conf import query_budget_database
import subprocess

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
    formchoose= ChooseConnection()
    form = None
    linkform = None
    context = {'form': form, 'formchoose': formchoose}
    if request.method == 'POST':
        formchoose= ChooseConnection()
        LOG.warning(request.POST)
        try:
            if request.POST['ChooseConnection']:
                Database = request.POST['Connection']
                if Database !='API' and Database != 'UI':
                    form = ConnectionsForm(dire=Database)
                else:
                    form = LinkConnection()
                template = "general_configuration/connections.html"
                context = {'form': form, 'formchoose': formchoose}
                return render(request, template, context)
        except Exception:
            try:
                form = ConnectionsForm(request.POST,dire=request.POST['Host'])
                
                if form.is_valid():
                    Host = form.cleaned_data['Host']
                    Port = form.cleaned_data['Port']
                    User = form.cleaned_data['User']
                    Password = form.cleaned_data['Password']
                    Name = form.cleaned_data['Name']
                    Auth = form.cleaned_data['Auth']
                    Certificate = form.cleaned_data['Certificate']
                    CAFile = form.cleaned_data['CAFile']
                    Cluster = form.cleaned_data['Cluster']
                    with open("adminui/beacon/connections/"+form.dire+"/conf.py") as f:
                        lines = f.readlines()
                    with open("adminui/beacon/connections/"+form.dire+"/conf.py", "w") as f:
                        new_lines =''
                        for line in lines:
                            if 'database_host' in str(line):
                                new_lines+="database_host="+'"'+Host+'"'+"\n"
                            elif 'host' in str(line):
                                new_lines+="host="+'"'+Host+'"'+"\n"
                            elif 'database_port' in str(line):
                                new_lines+="database_port="+str(Port)+"\n"
                            elif 'database_user' in str(line):
                                new_lines+="database_user="+'"'+User+'"'+"\n"
                            elif 'username' in str(line):
                                new_lines+="username="+'"'+User+'"'+"\n"
                            elif 'database_password' in str(line):
                                new_lines+="database_password="+'"'+Password+'"'+"\n"
                            elif 'password' in str(line):
                                new_lines+="password="+'"'+Password+'"'+"\n"
                            elif 'database_name' in str(line):
                                new_lines+="database_name="+'"'+Name+'"'+"\n"
                            elif 'database_auth_source' in str(line):
                                new_lines+="database_auth_source="+'"'+Auth+'"'+"\n"
                            elif 'database_certificate' in str(line):
                                new_lines+="database_certificate="+'"'+Certificate+'"'+"\n"
                            elif 'database_cafile' in str(line):
                                new_lines+="database_cafile="+'"'+CAFile+'"'+"\n"
                            elif 'database_cluster' in str(line):
                                new_lines+="database_cluster="+'"'+str(Cluster)+'"'+"\n"
                            else:
                                new_lines+=line
                            
                        f.write(new_lines)
                    f.close()
            except Exception:
                linkform = LinkConnection(request.POST)
                if linkform.is_valid():
                    LOG.warning('o')
        return redirect("adminclient:connections")
    template = "general_configuration/connections.html"
    return render(request, template, context)
