from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponseBadRequest
import logging
from pymongo.mongo_client import MongoClient
from django.urls import resolve
from adminbackend.forms.beacon import BamForm
from adminbackend.forms.entry_types_dyn import EntryTypeForm, LookupsForm
from django.contrib.auth.decorators import login_required, permission_required
import yaml
import os
import logging
import ast

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
    form =BamForm()
    context = {'form': form}
    if request.method == 'POST':
        form = BamForm(request.POST)
        if form.is_valid():
            beaconName = form.cleaned_data['BeaconName']
            beaconId = form.cleaned_data['BeaconId']
            beaconDescription = form.cleaned_data['BeaconDescription']
            environment = form.cleaned_data['Environment']
            org_id = form.cleaned_data['OrgId']
            org_name = form.cleaned_data['OrgName']
            org_description = form.cleaned_data['OrgDescription']
            org_address = form.cleaned_data['OrgAddress']
            org_welcome_url = form.cleaned_data['OrgWelcomeUrl']
            org_contact_url = form.cleaned_data['OrgContactUrl']
            org_logo_url = form.cleaned_data['OrgLogoUrl']
            granularity = form.cleaned_data['granularity']
            security_level = form.cleaned_data['SecurityLevel']
            max_limit_of_records_per_dataset_in_a_page = form.cleaned_data['MaxLimitRecords']
            pending_requests_timeout_in_seconds = form.cleaned_data['PendingRequestsTimeout']
            with open("/home/app/web/beacon/conf/conf.py") as f:
                entry_type_conf = f.readentry_type_conf()
            with open("/home/app/web/beacon/conf/conf.py", "w") as f:
                new_entry_type_conf =''
                for line in entry_type_conf:
                    if 'beacon_name' in str(line):
                        new_entry_type_conf+="beacon_name="+'"'+beaconName+'"'+"\n"
                    elif 'beacon_id' in str(line):
                        new_entry_type_conf+="beacon_id="+'"'+beaconId+'"'+"\n"
                    elif 'description' in str(line) and '_' not in str(line)[0:12]:
                        new_entry_type_conf+="beacon_id="+'"'+beaconDescription+'"'+"\n"
                    elif 'environment' in str(line):
                        new_entry_type_conf+="environment="+'"'+environment+'"'+"\n"
                    elif 'org_id' in str(line):
                        new_entry_type_conf+="org_id="+'"'+org_id+'"'+"\n"
                    elif 'org_name' in str(line):
                        new_entry_type_conf+="org_name="+'"'+org_name+'"'+"\n"
                    elif 'org_description' in str(line):
                        new_entry_type_conf+="org_description="+'"'+org_description+'"'+"\n"
                    elif 'org_address' in str(line):
                        new_entry_type_conf+="org_address="+'"'+org_address+'"'+"\n"
                    elif 'org_welcome_url' in str(line):
                        new_entry_type_conf+="org_welcome_url="+'"'+org_welcome_url+'"'+"\n"
                    elif 'org_contact_url' in str(line):
                        new_entry_type_conf+="org_contact_url="+'"'+org_contact_url+'"'+"\n"
                    elif 'org_logo_url' in str(line):
                        new_entry_type_conf+="org_logo_url="+'"'+org_logo_url+'"'+"\n"
                    elif 'security_levels' in str(line):
                        new_entry_type_conf+="security_levels="+str(security_level)+"\n"
                    elif 'default_beacon_granularity' in str(line):
                        new_entry_type_conf+="default_beacon_granularity="+'"'+granularity+'"'+"\n"
                    elif 'max_limit_of_records_per_dataset_in_a_page' in str(line):
                        new_entry_type_conf+="max_limit_of_records_per_dataset_in_a_page="+str(max_limit_of_records_per_dataset_in_a_page)+"\n"
                    elif 'pending_requests_timeout_in_seconds' in str(line):
                        new_entry_type_conf+="pending_requests_timeout_in_seconds="+str(pending_requests_timeout_in_seconds)+"\n"
                    else:
                        new_entry_type_conf+=line
                    
                f.write(new_entry_type_conf)
            f.close()
            return redirect("adminclient:index")
    template = "home.html"
    return render(request, template, context)


#@login_required
#@permission_required('adminclient.can_see_view', raise_exception=True)


def entry_types(request):
    LOG.warning('starting')

    models = {}
    context = {'models': models}

    with open(
        "/home/app/web/beacon/conf/models/models_conf.yml"
    ) as f:
        models_conf = yaml.safe_load(f)


    for model, config in models_conf.items():

        if config['model_enabled']:

            

            path = (
                "/home/app/web/beacon/models/"
                f"{model}/conf/entry_types"
            )

            for filename in os.listdir(path):
                entry_types = {}

                if filename.endswith(".yml"):
                    entry_type = filename[:-4]

                    entry_types['basic']=EntryTypeForm(
                            request.POST or None,
                            prefix=f"{model}_{entry_type}",
                            model=model,
                            entry_type=entry_type
                        )
                    with open(path+'/'+filename) as f:
                        entry_type_yaml = yaml.safe_load(f)

                    for k, v in entry_type_yaml[entry_type].items():
                        if k == 'lookups':
                            entry_types['lookups']=[]
                            for k2, v2 in v.items():
                                entry_types['lookups'].append(
                                    LookupsForm(
                                        request.POST or None,
                                        prefix=f"{model}_{entry_type}_{k2}",
                                        model=model,
                                        entry_type=entry_type,
                                        lookup = k2
                                    )
                                )

                    try:
                        models[model][entry_type] = entry_types
                    except Exception:
                        models[model]={}
                        models[model][entry_type] = entry_types



    LOG.warning('finished')
    if request.method == "POST":
        valid = True

        for model, entry_types in models.items():
            path = (
            "/home/app/web/beacon/models/"
            f"{model}/conf/entry_types/"
            )
            final_path=""

            for entry_type, type_of_forms in entry_types.items():
                if type_of_forms['basic'].is_valid():
                    LOG.warning('is valiiiid')
                    entry_type_name=type_of_forms['basic'].cleaned_data["entry_type_name"]
                    LOG.warning(entry_type_name)
                    LOG.warning(request.POST)
                    LOG.warning(request.POST.get('entry_type_name'))
                    if entry_type_name == request.POST.get('entry_type_name'):
                        LOG.warning('yesss')
                        for filename in os.listdir(path):
                            if entry_type_name in filename:
                                final_path=str(path)+filename

                        if final_path != "":
                            entry_type_conf={}
                            entry_type_conf[entry_type_name]={}
                            entry_type_conf[entry_type_name]['connection']={}
                            entry_type_conf[entry_type_name]['info']={}
                            entry_type_conf[entry_type_name]['schema']={}
                            entry_type_enabled=type_of_forms['basic'].cleaned_data['entry_type']
                            entry_type_open_api_definition=type_of_forms['basic'].cleaned_data['entry_type_open_api_definition']
                            entry_type_allow_queries_without_filters=type_of_forms['basic'].cleaned_data['entry_typeNonFiltered']
                            entry_type_id= type_of_forms['basic'].cleaned_data['entry_type_id']
                            entry_type_response_type=type_of_forms['basic'].cleaned_data['entry_type_response_type']
                            entry_type_endpoint_name = type_of_forms['basic'].cleaned_data['entry_typeEndpointName']
                            entry_type_granularity = type_of_forms['basic'].cleaned_data['entry_type_granularity']
                            entry_type_engine = type_of_forms['basic'].cleaned_data['entry_type_engine']
                            entry_type_dbname= type_of_forms['basic'].cleaned_data['entry_type_dbname']
                            entry_type_tablename= type_of_forms['basic'].cleaned_data['entry_type_tablename']
                            entry_type_function= type_of_forms['basic'].cleaned_data['entry_type_function']
                            entry_type_id_function= type_of_forms['basic'].cleaned_data['entry_type_id_function']
                            entry_type_info_name= type_of_forms['basic'].cleaned_data['entry_type_info_name']
                            entry_type_info_ontology_id= type_of_forms['basic'].cleaned_data['entry_type_info_ontology_id']
                            entry_type_info_ontology_name= type_of_forms['basic'].cleaned_data['entry_type_info_ontology_name']
                            entry_type_info_description= type_of_forms['basic'].cleaned_data['entry_type_info_description']
                            entry_type_schema_specification= type_of_forms['basic'].cleaned_data['entry_type_schema_specification']
                            entry_type_schema_id= type_of_forms['basic'].cleaned_data['entry_type_schema_id']
                            entry_type_schema_name= type_of_forms['basic'].cleaned_data['entry_type_schema_name']
                            entry_type_schema_version= type_of_forms['basic'].cleaned_data['entry_type_schema_version']
                            entry_type_supported_schemas= type_of_forms['basic'].cleaned_data['entry_type_supported_schemas']
                            entry_type_schema_reference= type_of_forms['basic'].cleaned_data['entry_type_schema_reference']
                            entry_type_conf[entry_type_name]['entry_type_enabled']=entry_type_enabled
                            entry_type_conf[entry_type_name]['max_granularity']=entry_type_granularity
                            entry_type_conf[entry_type_name]['endpoint_name']=entry_type_endpoint_name
                            entry_type_conf[entry_type_name]['open_api_definition']=entry_type_open_api_definition
                            entry_type_conf[entry_type_name]['allow_queries_without_filters']=entry_type_allow_queries_without_filters
                            entry_type_conf[entry_type_name]['allow_id_query']=entry_type_id
                            entry_type_conf[entry_type_name]['response_type']=entry_type_response_type
                            entry_type_conf[entry_type_name]['connection']['functions']={}
                            entry_type_conf[entry_type_name]['connection']['name']=entry_type_engine
                            entry_type_conf[entry_type_name]['connection']['database']=entry_type_dbname
                            entry_type_conf[entry_type_name]['connection']['table']=entry_type_tablename
                            entry_type_conf[entry_type_name]['connection']['functions']['function_name_assigned']=entry_type_function
                            entry_type_conf[entry_type_name]['connection']['functions']['id_query_function_name_assigned']=entry_type_id_function
                            entry_type_conf[entry_type_name]['info']['name']=entry_type_info_name
                            entry_type_conf[entry_type_name]['info']['ontology_id']=entry_type_info_ontology_id
                            entry_type_conf[entry_type_name]['info']['ontology_name']=entry_type_info_ontology_name
                            entry_type_conf[entry_type_name]['info']['description']=entry_type_info_description
                            entry_type_conf[entry_type_name]['schema']['specification']=entry_type_schema_specification
                            entry_type_conf[entry_type_name]['schema']['default_schema_id']=entry_type_schema_id
                            entry_type_conf[entry_type_name]['schema']['default_schema_name']=entry_type_schema_name
                            entry_type_conf[entry_type_name]['schema']['reference_to_default_schema_definition']=entry_type_schema_reference
                            entry_type_conf[entry_type_name]['schema']['default_schema_version']=entry_type_schema_version
                            entry_type_conf[entry_type_name]['schema']['supported_schemas']=entry_type_supported_schemas
                            entry_type_conf['lookups']={}
                            for form in type_of_forms['lookups']:
                                if form.is_valid():
                                    lookup_name=form.cleaned_data['lookup_name']
                                    entry_type_conf['lookups'][lookup_name]={}
                                    entry_type_conf['lookups'][lookup_name]['connection']={}
                                    entry_type_conf['lookups'][lookup_name]['connection']['functions']={}
                                    entry_type_conf['lookups'][lookup_name]['endpoint_name']=form.cleaned_data['lookup_endpoint_name']
                                    entry_type_conf['lookups'][lookup_name]['response_type']=form.cleaned_data['lookup_response_type']
                                    entry_type_conf['lookups'][lookup_name]['endpoint_enabled']=form.cleaned_data['lookup']
                                    entry_type_conf['lookups'][lookup_name]['connection']['name']=form.cleaned_data['lookup_engine']
                                    entry_type_conf['lookups'][lookup_name]['connection']['database']=form.cleaned_data['lookup_dbname']
                                    entry_type_conf['lookups'][lookup_name]['connection']['table']=form.cleaned_data['lookup_tablename']
                                    entry_type_conf['lookups'][lookup_name]['connection']['functions']['function_name_assigned']=form.cleaned_data['lookup_function']

                            with open(final_path, 'w') as outfile:
                                yaml.dump(entry_type_conf, outfile)

                        return redirect("adminclient:entry_types")
                    else:
                        context = {'models': models}
    if request.method == "GET":
        params =request.GET.urlencode()
        params_splitted = params.split("&")
        for param in params_splitted:
            if 'New_Schema' in param:
                final_params=param.replace("%3A", ":")
                new_schema=final_params.split("=")
                new_schema_found=new_schema[1]
    template = "general_configuration/entry_types.html"
    return render(request, template, context)