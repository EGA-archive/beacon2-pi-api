from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponseBadRequest
import logging
from pymongo.mongo_client import MongoClient
from django.urls import resolve
from adminbackend.forms.connections import ConnectionsForm, LinkConnection
from beacon.conf.conf_override import config
from beacon.conf.conf import complete_url, welcome_url
import subprocess
from django.contrib.auth.decorators import login_required, permission_required
import os
import logging
from dotenv import load_dotenv, get_key, set_key
import requests

#@login_required
#@permission_required('adminclient.can_see_view', raise_exception=True)
def default_view(request):
    form=ConnectionsForm()
    connections_dict={}
    dict_of_forms = {}
    dirs = os.listdir("/home/app/web/beacon/connections")
    for dir in dirs:
        load_dotenv("/home/app/web/beacon/connections/" + dir + "/conf.env", override=True)
        connection_dict={}        
        connection_dict['Host']=get_key(dotenv_path="/home/app/web/beacon/connections/" + dir + "/conf.env", key_to_get="database_host")
        connection_dict['Port']=get_key(dotenv_path="/home/app/web/beacon/connections/" + dir + "/conf.env", key_to_get="database_port")
        connection_dict['User']=get_key(dotenv_path="/home/app/web/beacon/connections/" + dir + "/conf.env", key_to_get="database_user")
        connection_dict['Password']=get_key(dotenv_path="/home/app/web/beacon/connections/" + dir + "/conf.env", key_to_get="database_password")
        connection_dict['Name']=get_key(dotenv_path="/home/app/web/beacon/connections/" + dir + "/conf.env", key_to_get="database_name")
        connection_dict['Auth']=get_key(dotenv_path="/home/app/web/beacon/connections/" + dir + "/conf.env", key_to_get="database_auth_source")
        connection_dict['Certificate']=get_key(dotenv_path="/home/app/web/beacon/connections/" + dir + "/conf.env", key_to_get="database_certificate")
        connection_dict['CAFile']=get_key(dotenv_path="/home/app/web/beacon/connections/" + dir + "/conf.env", key_to_get="database_cafile")
        connection_dict['Cluster']=get_key(dotenv_path="/home/app/web/beacon/connections/" + dir + "/conf.env", key_to_get="database_cluster")
        connections_dict[dir]=connection_dict
    dict_of_forms["API"]=LinkConnection(link=complete_url)
    dict_of_forms["UI"]=LinkConnection(link=welcome_url)
    context = {'non_db_forms': dict_of_forms, 'db_forms': connections_dict}

    if request.method == 'POST':
        form = ConnectionsForm(request.POST)
        api_form = LinkConnection(request.POST)
        ui_form = LinkConnection(request.POST)
        if 'Test Connection' in request.POST:
            if form.is_valid():
                for dir in dirs:
                    if dir in request.POST:
                        complete_client_module='beacon.connections.'+dir+'.client'
                        import importlib
                        module = importlib.import_module(complete_client_module, package=None)
                        client_from_module = getattr(module, 'get_client')
                        # Perform the ping of each of the connections with a timeout
                        try:
                            ping=client_from_module.admin.command("ping")
                            context["ping"]=ping
                            context["ping_title"]=dir
                        # In case of timeout or ping not successful, raise an error of the database being down
                        except Exception as e:
                            context["ping"]=e
                            context["ping_title"]=dir
            elif api_form.is_valid():
                print('here I am', flush=True)
                url=api_form.cleaned_data.get('Connection')
                try:
                    ping=requests.get(url,  timeout=5)
                    context["ping"]=ping.status_code
                    context["ping_title"]="API"
                except Exception as e:
                    context["ping"]=e
                    context["ping_title"]="API"
            elif ui_form.is_valid():
                print('here I am', flush=True)
                url=api_form.cleaned_data.get('Connection')
                try:
                    ping=requests.get(url,  timeout=5)
                    context["ping"]=ping.status_code
                    context["ping_title"]="UI"
                except Exception as e:
                    context["ping"]=e
                    context["ping_title"]="UI"
            template = "general_configuration/connections.html"
            return render(request, template, context)
        elif form.is_valid() and 'Save' in request.POST:
            folder=request.POST.get('Save')
            load_dotenv("/home/app/web/beacon/connections/" + folder + "/conf.env", override=True)
            Host = form.cleaned_data['Host']
            Port = form.cleaned_data['Port']
            User = form.cleaned_data['User']
            Password = form.cleaned_data['Password']
            Name = form.cleaned_data['Name']
            Auth = form.cleaned_data['Auth']
            Certificate = form.cleaned_data['Certificate']
            CAFile = form.cleaned_data['CAFile']
            Cluster = form.cleaned_data['Cluster']
            set_key(dotenv_path="/home/app/web/beacon/connections/" + folder + "/conf.env", key_to_set="database_host", value_to_set=Host)
            set_key(dotenv_path="/home/app/web/beacon/connections/" + folder + "/conf.env", key_to_set="database_port", value_to_set=str(Port))
            set_key(dotenv_path="/home/app/web/beacon/connections/" + folder + "/conf.env", key_to_set="database_user", value_to_set=User)
            set_key(dotenv_path="/home/app/web/beacon/connections/" + folder + "/conf.env", key_to_set="database_password", value_to_set=Password)
            set_key(dotenv_path="/home/app/web/beacon/connections/" + folder + "/conf.env", key_to_set="database_name", value_to_set=Name)
            set_key(dotenv_path="/home/app/web/beacon/connections/" + folder + "/conf.env", key_to_set="database_auth_source", value_to_set=Auth)
            set_key(dotenv_path="/home/app/web/beacon/connections/" + folder + "/conf.env", key_to_set="database_certificate", value_to_set=Certificate)
            set_key(dotenv_path="/home/app/web/beacon/connections/" + folder + "/conf.env", key_to_set="database_cafile", value_to_set=CAFile)
            if Cluster == True:
                set_key(dotenv_path="/home/app/web/beacon/connections/" + folder + "/conf.env", key_to_set="database_cluster", value_to_set='True')
            else:
                set_key(dotenv_path="/home/app/web/beacon/connections/" + folder + "/conf.env", key_to_set="database_cluster", value_to_set='False')
            return redirect("adminclient:connections")
        elif form.is_valid() and 'Save' in request.POST:
            folder=request.POST.get('Save')
            load_dotenv("/home/app/web/beacon/connections/" + folder + "/conf.env", override=True)
            Host = form.cleaned_data['Host']
            Port = form.cleaned_data['Port']
            User = form.cleaned_data['User']
            Password = form.cleaned_data['Password']
            Name = form.cleaned_data['Name']
            Auth = form.cleaned_data['Auth']
            Certificate = form.cleaned_data['Certificate']
            CAFile = form.cleaned_data['CAFile']
            Cluster = form.cleaned_data['Cluster']
            set_key(dotenv_path="/home/app/web/beacon/connections/" + folder + "/conf.env", key_to_set="database_host", value_to_set=Host)
            set_key(dotenv_path="/home/app/web/beacon/connections/" + folder + "/conf.env", key_to_set="database_port", value_to_set=str(Port))
            set_key(dotenv_path="/home/app/web/beacon/connections/" + folder + "/conf.env", key_to_set="database_user", value_to_set=User)
            set_key(dotenv_path="/home/app/web/beacon/connections/" + folder + "/conf.env", key_to_set="database_password", value_to_set=Password)
            set_key(dotenv_path="/home/app/web/beacon/connections/" + folder + "/conf.env", key_to_set="database_name", value_to_set=Name)
            set_key(dotenv_path="/home/app/web/beacon/connections/" + folder + "/conf.env", key_to_set="database_auth_source", value_to_set=Auth)
            set_key(dotenv_path="/home/app/web/beacon/connections/" + folder + "/conf.env", key_to_set="database_certificate", value_to_set=Certificate)
            set_key(dotenv_path="/home/app/web/beacon/connections/" + folder + "/conf.env", key_to_set="database_cafile", value_to_set=CAFile)
            if Cluster == True:
                set_key(dotenv_path="/home/app/web/beacon/connections/" + folder + "/conf.env", key_to_set="database_cluster", value_to_set='True')
            else:
                set_key(dotenv_path="/home/app/web/beacon/connections/" + folder + "/conf.env", key_to_set="database_cluster", value_to_set='False')
            return redirect("adminclient:connections")
        elif api_form.is_valid() and 'API' in request.POST:
            print('here I am', flush=True)
            API_link = api_form.cleaned_data['Connection']
            API_link_splitted = API_link.split('/')
            print(API_link_splitted, flush=True)
            with open("/home/app/web/beacon/conf/conf.py") as f:
                lines = f.readlines()
            with open("/home/app/web/beacon/conf/conf.py", "w") as f:
                new_lines =''
                for line in lines:
                    if 'uri_subpath' in str(line) and 'complete_url' not in str(line) and 'security_levels' not in str(line):
                        new_lines+="uri_subpath="+"'/"+str(API_link_splitted[-1])+"'"+"\n"
                    elif 'uri' in str(line) and 'complete_url' not in str(line) and 'security_levels' not in str(line):
                        new_lines+="uri="+"'"+'http://'+str(API_link_splitted[2])+"'"+"\n"
                    else:
                        new_lines+=line
                f.write(new_lines)
            f.close()
            dict_of_forms["API"]=LinkConnection(link=API_link)
            context = {'non_db_forms': dict_of_forms, 'db_forms': connections_dict}
        elif ui_form.is_valid() and 'UI' in request.POST:
            UI_link = api_form.cleaned_data['Connection']
            with open("/home/app/web/beacon/conf/conf.py") as f:
                lines = f.readlines()
            with open("/home/app/web/beacon/conf/conf.py", "w") as f:
                new_lines =''
                for line in lines:
                    if 'welcome_url' in str(line) and 'org_' not in str(line):
                        new_lines+="welcome_url="+"'"+str(UI_link)+"'"+"\n"
                    else:
                        new_lines+=line
                    
                f.write(new_lines)
            f.close()
            dict_of_forms["UI"]=LinkConnection(link=UI_link)
            context = {'non_db_forms': dict_of_forms, 'db_forms': connections_dict}
        else:
            print(request.POST, flush=True)
    template = "general_configuration/connections.html"
    return render(request, template, context)
