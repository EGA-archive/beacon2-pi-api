from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponseBadRequest
import logging
from pymongo.mongo_client import MongoClient
from django.urls import resolve
from adminbackend.forms import BamForm
from beacon.connections.mongo import conf
from beacon.conf import conf as basic_conf

def default_view(request):
    form =BamForm()
    context = {'form': form}
    if request.method == 'POST':
        form = BamForm(request.POST)
        if form.is_valid():
            beaconName = form.cleaned_data['BeaconName']
            beaconId = form.cleaned_data['BeaconId']
            environment = form.cleaned_data['Environment']
            with open("adminui/beacon/conf/conf.py") as f:
                lines = f.readlines()
            with open("adminui/beacon/conf/conf.py", "w") as f:
                new_lines =''
                for line in lines:
                    if 'beacon_name' in str(line):
                        new_lines+="beacon_name="+"'"+beaconName+"'"+"\n"
                    elif 'beacon_id' in str(line):
                        new_lines+="beacon_id="+"'"+beaconId+"'"+"\n"
                    elif 'environment' in str(line):
                        new_lines+="environment="+"'"+environment+"'"+"\n"
                    else:
                        new_lines+=line
                    
                f.write(new_lines)
            f.close()
            return redirect("adminclient:index")
    template = "home.html"
    return render(request, template, context)
