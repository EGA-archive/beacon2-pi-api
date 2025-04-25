from django.shortcuts import render, redirect
from django.views.generic import TemplateView
import subprocess
import time
from django.http import HttpResponseRedirect, HttpResponseBadRequest
import logging
import json
from pymongo.mongo_client import MongoClient
import imp
from django.urls import resolve
from adminbackend.forms import BamForm
import subprocess
import sys
from beacon.connections.mongo import conf
from beacon.conf import conf as basic_conf

client = MongoClient(
        "mongodb://{}:{}@{}:{}/{}?authSource={}".format(
            conf.database_user,
            conf.database_password,
            conf.database_host,
            conf.database_port,
            conf.database_name,
            conf.database_auth_source,
        )
    )




LOG = logging.getLogger(__name__)

def default_view(request):
    form =BamForm()
    context = {'form': form, "beacon_name": basic_conf.beacon_name}
    if request.method == 'POST':
        form = BamForm(request.POST)
        if form.is_valid():
            reference = form.cleaned_data['Datasets']
            with open("/beacon/conf/conf.py") as f:
                lines = f.readlines()
            with open("/beacon/conf/conf.py", "w") as f:
                new_lines =''
                j=0
                for line in lines:
                    if 'beacon_name' in str(line):
                        new_lines+="beacon_name="+"'"+reference+"'"+"\n"
                        #lines.insert(j, "beacon_name = provaaaaa")
                    else:
                        new_lines+=line
                    
                    j+=1
                f.write(new_lines)
            return redirect("adminclient:index")
    template = "home.html"
    return render(request, template, context)
