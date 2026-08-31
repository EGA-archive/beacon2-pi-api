from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponseBadRequest
import logging
from pymongo.mongo_client import MongoClient
from django.urls import resolve
from beacon.connections.mongo.__init__ import client
from adminbackend.forms.datasets import DatasetsForm
import yaml
from django.contrib.auth.decorators import login_required, permission_required
import os

import logging

LOG = logging.getLogger(__name__)
fmt = '%(levelname)s - %(asctime)s - %(message)s'
formatter = logging.Formatter(fmt)
sh = logging.StreamHandler()
sh.setLevel('NOTSET')
sh.setFormatter(formatter)
LOG.addHandler(sh)

#@login_required
#@permission_required('adminclient.can_see_view', raise_exception=True)
def default_view(request):
    LOG.warning('starting')

    models = {}
    context = {'models': models}

    with open(
        "/home/app/web/beacon/conf/models/models_conf.yml"
    ) as f:
        models_conf = yaml.safe_load(f)

    connections = {}
    datasets_connections = {}
    datasets_forms = []
    for model, config in models_conf.items():
        if model not in models:
            models[model]={}

        if config['model_enabled']:

            

            path = (
                "/home/app/web/beacon/models/"
                f"{model}/conf/entry_types"
            )
            
            for filename in os.listdir(path):
                

                if filename.endswith(".yml"):
                    entry_type = filename[:-4]
                
                    with open(path+'/'+filename) as f:
                        entry_type_yaml = yaml.safe_load(f)

                    database_name=entry_type_yaml[entry_type]['connection']['database']
                    collection_name=entry_type_yaml[entry_type]['connection']['table']
                    endpoint_name=entry_type_yaml[entry_type]['endpoint_name']
                    print(entry_type, flush=True)
                    if 'data set' in entry_type_yaml[entry_type]['info']['ontology_name'].lower() or 'dataset' in entry_type_yaml[entry_type]['info']['ontology_name'].lower():
                        datasets_connections[endpoint_name]=client[database_name][collection_name]
                    else:
                        connections[endpoint_name]=client[database_name][collection_name]

        print(model, flush=True)
        print(datasets_connections, flush=True)
        caseLevelData=client["beacon"].caseLevelData
        connections['caseLevelData']=caseLevelData
        targets=client["beacon"].targets
        connections['targets']=targets

        models[model]['connections']= connections
        models[model]['dataset_connections']= datasets_connections

        for endpoint, dataset_connection in datasets_connections.items():
            all_datasets=dataset_connection.find({})
            dataset_list=[]
            for dataset in all_datasets:
                entry_types_included=["datasets"]
                dataset_dict={}
                dataset_dict["Total_IDs"]={}
                dataset_dict["name"]=dataset["name"]
                dataset_dict["id"]=dataset["id"]
                dataset_dict["description"]=dataset["description"]
                datasets_forms.append(
                    DatasetsForm(
                        request.POST or None,
                        prefix=f"{model}_{dataset["id"]}",
                        model=model,
                        dataset=dataset["id"]
                    )
                )
                
                for endpoint_connection, connection in connections.items():
                    if endpoint_connection not in ['targets', 'caseLevelData']:
                        total_ids=connection.find({"datasetId": dataset["id"]})
                        total_ids=list(total_ids)
                        if len(total_ids) > 0:
                            dataset_dict["Total_IDs"][endpoint_connection]=len(total_ids)
                            entry_types_included.append(endpoint_connection)
                dataset_dict["entry_types_included"]=entry_types_included
                dataset_list.append(dataset_dict)
            models[model]['forms']= datasets_forms
            models[model]['dataset_list']= dataset_list
    with open("beacon/conf/datasets/datasets_conf.yml") as f:
        datasets_test=yaml.safe_load(f)
    if request.method == 'POST':
        for model, key_model in models['forms'].items():
            for dataset_form in key_model['forms']:
                dataID = dataset_form.cleaned_data['DatasetID']
                if 'Test Mode' in request.POST:
                    with open("beacon/conf/datasets/datasets_conf.yml") as f:
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
                    with open('/home/app/web/beacon/conf/datasets/datasets_conf.yml', 'w') as outfile:
                        yaml.dump(datasets_conf, outfile)
                elif 'Delete Dataset' in request.POST:
                    for connections in key_model['connections']:
                        for endpoint_connection, connection in connections:
                            connection.delete_many({"datasetId": dataID})
                    for datasets_connections in key_model['dataset_connections']:
                        for endpoint, dataset_connection in datasets_connections:
                            dataset_connection.delete_many({"id": dataID})
            return redirect("adminclient:datasets")
    context={"models": models, "datasets_test": datasets_test}
    template = "general_configuration/datasets.html"
    return render(request, template, context)