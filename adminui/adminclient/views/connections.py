from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponseBadRequest
import logging
from pymongo.mongo_client import MongoClient
from django.urls import resolve
from adminbackend.forms.connections import ConnectionsForm, ChooseConnection, LinkConnection
from beacon.conf.conf import query_budget_database
import subprocess
from django.contrib.auth.decorators import login_required, permission_required

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

@login_required
@permission_required('adminclient.can_see_view', raise_exception=True)
def default_view(request):
    formchoose= ChooseConnection()
    form = None
    linkform = None
    context = {'form': form, 'formchoose': formchoose}
    if request.method == 'POST':
        formchoose= ChooseConnection()
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
                    
                if 'Test Connection' in request.POST:
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


                            try:
                                if Cluster:# pragma: no cover
                                    uri = "mongodb+srv://{}:{}@{}/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000".format(
                                        User,
                                        Password,
                                        Host
                                    )
                                else:
                                    uri = "mongodb://{}:{}@{}:{}/{}?authSource={}".format(
                                        User,
                                        Password,
                                        Host,
                                        Port,
                                        Name,
                                        Auth
                                    )

                                if Certificate != '' and CAFile != '':# pragma: no cover
                                    uri += '&tls=true&tlsCertificateKeyFile={}&tlsCAFile={}'.format(Certificate, CAFile)
                            except Exception:
                                uri = "mongodb://{}:{}@{}:{}/{}?authSource={}".format(
                                        User,
                                        Password,
                                        Host,
                                        Port,
                                        Name,
                                        Auth
                                    )


                        
                            
                            try:
                                client = MongoClient(uri)
                                client = module.client.server_info()
                                client = "Ok and running in a mongo " + client["version"] + "version"
                            except Exception:
                                client = 'Connection could not be established'
                            #client = module.client.admin.command('ismaster')
                    except Exception:
                        linkform = LinkConnection(request.POST)
                        if linkform.is_valid():
                            Connection = linkform.cleaned_data['Connection']
                            try:
                                client = subprocess.check_output("curl -s -o /dev/null -v {}".format(Connection), shell=True)
                                client = 'Connection successful'
                            except Exception:
                                client = 'Connection could not be established'
                                


                    template = "general_configuration/connections.html"
                    context = {'form': form, 'client': client, 'formchoose': formchoose}
                    return render(request, template, context)
                elif form.is_valid():
                    Host = form.cleaned_data['Host']
                    Port = form.cleaned_data['Port']
                    User = form.cleaned_data['User']
                    Password = form.cleaned_data['Password']
                    Name = form.cleaned_data['Name']
                    Auth = form.cleaned_data['Auth']
                    Certificate = form.cleaned_data['Certificate']
                    CAFile = form.cleaned_data['CAFile']
                    Cluster = form.cleaned_data['Cluster']
                    with open("/home/app/web/beacon/connections/"+form.dire+"/conf.py") as f:
                        lines = f.readlines()
                    with open("/home/app/web/beacon/connections/"+form.dire+"/conf.py", "w") as f:
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
                if 'Test Connection' in request.POST:
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


                        try:
                            if Cluster:# pragma: no cover
                                uri = "mongodb+srv://{}:{}@{}/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000".format(
                                    User,
                                    Password,
                                    Host
                                )
                            else:
                                uri = "mongodb://{}:{}@{}:{}/{}?authSource={}".format(
                                    User,
                                    Password,
                                    Host,
                                    Port,
                                    Name,
                                    Auth
                                )

                            if Certificate != '' and CAFile != '':# pragma: no cover
                                uri += '&tls=true&tlsCertificateKeyFile={}&tlsCAFile={}'.format(Certificate, CAFile)
                        except Exception:
                            uri = "mongodb://{}:{}@{}:{}/{}?authSource={}".format(
                                    User,
                                    Password,
                                    Host,
                                    Port,
                                    Name,
                                    Auth
                                )
                    else:
                        client = 'Configuration not valid'
                    #client = module.client.admin.command('ismaster')
                    client = MongoClient(uri)
                        
                    try:
                        client = module.client.server_info()
                        client = "Ok and running in a mongo " + client["version"] + "version"
                    except Exception:
                        client = 'Connection could not be established'
                    template = "general_configuration/connections.html"
                    context = {'form': form, 'client': client, 'formchoose': formchoose}
                    return render(request, template, context)
                else:
                    linkform = LinkConnection(request.POST)
        return redirect("adminclient:connections")
    template = "general_configuration/connections.html"
    return render(request, template, context)
