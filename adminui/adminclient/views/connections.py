from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponseBadRequest
import logging
from pymongo.mongo_client import MongoClient
from django.urls import resolve
from adminbackend.forms.connections import ConnectionsForm, APIConnection, UIConnection
from beacon.conf.conf_override import config
import subprocess
from django.contrib.auth.decorators import login_required, permission_required
import os
import logging
from dotenv import load_dotenv, get_key, set_key

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
    dict_of_forms["API"]=APIConnection
    dict_of_forms["UI"]=UIConnection
    context = {'non_db_forms': dict_of_forms, 'db_forms': connections_dict}

    if request.method == 'POST':
        form = ConnectionsForm(request.POST)
        if 'Test Connection' in request.POST:
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
                    if Cluster:
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

                    if Certificate != '' and CAFile != '':
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
                        


            template = "general_configuration/connections.html"
            return render(request, template, context)
        elif form.is_valid() and 'Save' in request.POST:
            folder=request.POST.get('Save')
            Host = form.cleaned_data['Host']
            Port = form.cleaned_data['Port']
            User = form.cleaned_data['User']
            Password = form.cleaned_data['Password']
            Name = form.cleaned_data['Name']
            Auth = form.cleaned_data['Auth']
            Certificate = form.cleaned_data['Certificate']
            CAFile = form.cleaned_data['CAFile']
            Cluster = form.cleaned_data['Cluster']
            #set_key(dotenv_path="/home/app/web/beacon/connections/" + folder + "/conf.env", key_to_set="database_host", value_to_set=Host)
            #set_key(dotenv_path="/home/app/web/beacon/connections/" + folder + "/conf.env", key_to_set="database_port", value_to_set=Port)
            #set_key(dotenv_path="/home/app/web/beacon/connections/" + folder + "/conf.env", key_to_set="database_user", value_to_set=User)
            #set_key(dotenv_path="/home/app/web/beacon/connections/" + folder + "/conf.env", key_to_set="database_password", value_to_set=Password)
            #set_key(dotenv_path="/home/app/web/beacon/connections/" + folder + "/conf.env", key_to_set="database_name", value_to_set=Name)
            #set_key(dotenv_path="/home/app/web/beacon/connections/" + folder + "/conf.env", key_to_set="database_auth_source", value_to_set=Auth)
            #set_key(dotenv_path="/home/app/web/beacon/connections/" + folder + "/conf.env", key_to_set="database_certificate", value_to_set=Certificate)
            #set_key(dotenv_path="/home/app/web/beacon/connections/" + folder + "/conf.env", key_to_set="database_cafile", value_to_set=CAFile)
            #set_key(dotenv_path="/home/app/web/beacon/connections/" + folder + "/conf.env", key_to_set="database_cluster", value_to_set=Cluster)
            return redirect("adminclient:connections")

    template = "general_configuration/connections.html"
    return render(request, template, context)
