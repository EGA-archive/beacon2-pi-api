from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponseBadRequest
import logging
from pymongo.mongo_client import MongoClient
from django.urls import resolve
from beacon.connections.mongo.__init__ import client
from adminbackend.forms.permits import StreetForm
import yaml

import logging

LOG = logging.getLogger(__name__)
fmt = '%(levelname)s - %(asctime)s - %(message)s'
formatter = logging.Formatter(fmt)
sh = logging.StreamHandler()
sh.setLevel('NOTSET')
sh.setFormatter(formatter)
LOG.addHandler(sh)

def default_view(request):
    datasets=client["beacon"].datasets
    all_datasets=datasets.find({})
    dataset_list=[]
    form = StreetForm(request.POST)
    with open("adminui/beacon/permissions/datasets/datasets_permissions.yml") as f:
        datasets_permissions=yaml.safe_load(f)

    for dataset in all_datasets:
        dataset_dict={}
        dataset_dict["name"]=dataset["name"]
        dataset_dict["id"]=dataset["id"]
        for k,v in datasets_permissions.items():
            if k == dataset["id"]:
                dataset_dict["permissions"]=v
        dataset_list.append(dataset_dict)
        
    
    context={"datasets_found": dataset_list, "form": form}
    template = "general_configuration/permits.html"
    return render(request, template, context)