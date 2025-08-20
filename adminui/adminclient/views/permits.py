from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponseBadRequest
import logging
from pymongo.mongo_client import MongoClient
from django.urls import resolve
from beacon.connections.mongo.__init__ import client
from adminbackend.forms.permits import PermitsForm, UserPermitsForm
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
    form = PermitsForm(request.POST)
    userform = UserPermitsForm(request.POST)
    with open("adminui/beacon/permissions/datasets/datasets_permissions.yml") as f:
        datasets_permissions=yaml.safe_load(f)

    for dataset in all_datasets:
        dataset_dict={}
        dataset_dict["name"]=dataset["name"]
        dataset_dict["id"]=dataset["id"]
        for k,v in datasets_permissions.items():
            if k == dataset["id"]:
                for security_level, exceptions in v.items():
                    dataset_dict["security_level"]=security_level
                    for exception, value in exceptions.items():
                        if exception == 'default_entry_types_granularity':
                            dataset_dict["granularity"]=value
                        elif exception == 'entry_types_exceptions':
                            dataset_dict["exceptions"]={}
                            for entry_type in value:
                                for entrytype, granularity in entry_type.items():
                                    dataset_dict["exceptions"][entrytype]=granularity
                        elif exception == 'user-list' and security_level == 'controlled':
                            dataset_dict["users"]=value
        dataset_list.append(dataset_dict)
        
    
    context={"datasets_found": dataset_list, "form": form, "userform": userform}
    template = "general_configuration/permits.html"
    return render(request, template, context)