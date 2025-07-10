from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponseBadRequest
import logging
from pymongo.mongo_client import MongoClient
from django.urls import resolve
from beacon.connections.mongo.__init__ import client
from adminbackend.forms.datasets import DatasetsForm
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
    analyses=client["beacon"].analyses
    datasets=client["beacon"].datasets
    biosamples=client["beacon"].biosamples
    cohorts=client["beacon"].cohorts
    runs=client["beacon"].runs
    g_variants=client["beacon"].genomicVariations
    individuals=client["beacon"].individuals
    all_datasets=datasets.find({})
    dataset_list=[]
    for dataset in all_datasets:
        entry_types_included=["datasets"]
        dataset_dict={}
        dataset_dict["name"]=dataset["name"]
        dataset_dict["id"]=dataset["id"]
        dataset_dict["description"]=dataset["description"]
        total_ids=biosamples.find({"datasetId": dataset["id"]})
        total_ids=list(total_ids)
        dataset_dict["Total_IDs"]=len(total_ids)
        analyses_list=analyses.find_one({"datasetId": dataset["id"]})
        try:
            analyses_list=list(analyses_list)
        except Exception:
            analyses_list=[]
        cohorts_list=cohorts.find_one({"datasetId": dataset["id"]})
        try:
            cohorts_list=list(cohorts_list)
        except Exception:
            cohorts_list=[]
        runs_list=runs.find_one({"datasetId": dataset["id"]})
        try:
            runs_list=list(runs_list)
        except Exception:
            runs_list=[]
        g_variants_list=g_variants.find_one({"datasetId": dataset["id"]})
        try:
            g_variants_list=list(g_variants_list)
        except Exception:
            g_variants_list=[]
        individuals_list=individuals.find_one({"datasetId": dataset["id"]})
        try:
            individuals_list=list(individuals_list)
        except Exception:
            individuals_list=[]
        if len(total_ids) > 0:
            entry_types_included.append('biosamples')
        if len(analyses_list) > 0:
            entry_types_included.append('analyses')
        if len(cohorts_list) > 0:
            entry_types_included.append('cohorts')
        if len(individuals_list) > 0:
            entry_types_included.append('individuals')
        if len(runs_list) > 0:
            entry_types_included.append('runs')
        if len(g_variants_list) > 0:
            entry_types_included.append('g_variants')
        dataset_dict["entry_types_included"]=entry_types_included
        dataset_list.append(dataset_dict)
    with open("adminui/beacon/conf/datasets/datasets_conf.yml") as f:
        datasets_test=yaml.safe_load(f)
    if request.method == 'POST':
        form = DatasetsForm(request.POST)
        if form.is_valid():
            dataID = form.cleaned_data['DatasetID']
            if 'Test Mode' in request.POST:
                LOG.warning(request.POST)
                with open("adminui/beacon/conf/datasets/datasets_conf.yml") as f:
                    datasets_conf=yaml.safe_load(f)
                test_datasets=[]
                for key2, value2 in request.POST.items():
                    if value2 == 'on':
                        try:
                            datasets_conf[key2]['isTest']=True
                        except Exception:
                            datasets_conf[key2]={}
                            datasets_conf[key2]['isTest']=True
                        test_datasets.append(key2)
                for key, value in datasets_conf.items():
                    if key not in test_datasets:
                        try:
                            datasets_conf[key]['isTest']=False
                        except Exception:
                            datasets_conf[key]={}
                            datasets_conf[key]['isTest']=False
                with open('adminui/beacon/conf/datasets/datasets_conf.yml', 'w') as outfile:
                    yaml.dump(datasets_conf, outfile)
            elif 'Delete Dataset' in request.POST:
                LOG.warning('Delete dataset')
                LOG.warning(dataID)
            return redirect("adminclient:datasets")
    context={"datasets_found": dataset_list, "datasets_test": datasets_test}
    template = "general_configuration/datasets.html"
    return render(request, template, context)