from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponseBadRequest
import logging
from pymongo.mongo_client import MongoClient
from django.urls import resolve
from adminbackend.forms.beacon import BamForm
from adminbackend.forms.entry_types import EntryTypesForm
from adminbackend.forms.entry_types_dyn import EntryTypeForm, ModelsForm
from django.contrib.auth.decorators import login_required, permission_required
import yaml
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
                lines = f.readlines()
            with open("/home/app/web/beacon/conf/conf.py", "w") as f:
                new_lines =''
                for line in lines:
                    if 'beacon_name' in str(line):
                        new_lines+="beacon_name="+'"'+beaconName+'"'+"\n"
                    elif 'beacon_id' in str(line):
                        new_lines+="beacon_id="+'"'+beaconId+'"'+"\n"
                    elif 'description' in str(line) and '_' not in str(line)[0:12]:
                        new_lines+="beacon_id="+'"'+beaconDescription+'"'+"\n"
                    elif 'environment' in str(line):
                        new_lines+="environment="+'"'+environment+'"'+"\n"
                    elif 'org_id' in str(line):
                        new_lines+="org_id="+'"'+org_id+'"'+"\n"
                    elif 'org_name' in str(line):
                        new_lines+="org_name="+'"'+org_name+'"'+"\n"
                    elif 'org_description' in str(line):
                        new_lines+="org_description="+'"'+org_description+'"'+"\n"
                    elif 'org_address' in str(line):
                        new_lines+="org_address="+'"'+org_address+'"'+"\n"
                    elif 'org_welcome_url' in str(line):
                        new_lines+="org_welcome_url="+'"'+org_welcome_url+'"'+"\n"
                    elif 'org_contact_url' in str(line):
                        new_lines+="org_contact_url="+'"'+org_contact_url+'"'+"\n"
                    elif 'org_logo_url' in str(line):
                        new_lines+="org_logo_url="+'"'+org_logo_url+'"'+"\n"
                    elif 'security_levels' in str(line):
                        new_lines+="security_levels="+str(security_level)+"\n"
                    elif 'default_beacon_granularity' in str(line):
                        new_lines+="default_beacon_granularity="+'"'+granularity+'"'+"\n"
                    elif 'max_limit_of_records_per_dataset_in_a_page' in str(line):
                        new_lines+="max_limit_of_records_per_dataset_in_a_page="+str(max_limit_of_records_per_dataset_in_a_page)+"\n"
                    elif 'pending_requests_timeout_in_seconds' in str(line):
                        new_lines+="pending_requests_timeout_in_seconds="+str(pending_requests_timeout_in_seconds)+"\n"
                    else:
                        new_lines+=line
                    
                f.write(new_lines)
            f.close()
            return redirect("adminclient:index")
    template = "home.html"
    return render(request, template, context)

#@login_required
#@permission_required('adminclient.can_see_view', raise_exception=True)


def entry_types(request):

    models = {}
    context = {'models': models}

    with open(
        "/home/app/web/beacon/conf/models/models_conf.yml"
    ) as f:
        models_conf = yaml.safe_load(f)


    for model, config in models_conf.items():

        if config['model_enabled']:

            entry_types = []

            path = (
                "/home/app/web/beacon/models/"
                f"{model}/conf/entry_types"
            )

            for filename in os.listdir(path):

                if filename.endswith(".yml"):
                    entry_type = filename[:-4]

                    entry_types.append(
                        EntryTypeForm(
                            request.POST or None,
                            prefix=f"{model}_{entry_type}",
                            model=model,
                            entry_type=entry_type
                        )
                    )

            models[model] = entry_types


    if request.method == "POST":

        valid = True

        for model, forms in models.items():

            for form in forms:

                if not form.is_valid():
                    valid = False


        if valid:
            for model, forms in models.items():

                for form in forms:
                    print(
                        model,
                        form.entry_type,
                        form.cleaned_data
                    )

            # save here
            return redirect("adminclient:entry_types")
        else:
            context = {'models': models}
            
    template = "general_configuration/entry_types.html"
    return render(request, template, context)

    return render(
        request,
        "entry_types.html",
        {
            "models": models
        }
    )

"""
def entry_types(request):
    models_form = ModelsForm()
    form = EntryTypeForm()

    context = {'models_form': models_form}
    if request.method == 'POST':
        if "models" in request.POST:
            model_name=models_form.cleaned_data['models_tabs']
            with open("/home/app/web/beacon/conf/models/models_conf.yml") as f:
                models_conf = yaml.safe_load(f)
            for k, v in models_conf.items():
                if k == model_name:
                    dirs = os.listdir("/home/app/web/beacon/models"+k+"/conf/entry_types")
            for entrytype in dirs:
                with open("/home/app/web/beacon/models/"+model_name+"/conf/entry_types/"+entrytype+".yml") as entrytypeyaml:
                    yamlfile = yaml.safe_load(entrytypeyaml)
        form = EntryTypeForm(request.POST)
        if form.is_valid():
            analysis=form.cleaned_data['Analysis']
            analysis_endpoint_name = form.cleaned_data['AnalysisEndpointName']
            analysis_granularity = form.cleaned_data['analysis_granularity']
            analysis_engine = form.cleaned_data['analysis_engine']
            analysis_dbname= form.cleaned_data['analysis_dbname']
            analysis_tablename= form.cleaned_data['analysis_tablename']
            analysis_function= form.cleaned_data['analysis_function']
            analysis_id_function= form.cleaned_data['analysis_id_function']
            analysis_info_name= form.cleaned_data['analysis_info_name']
            analysis_info_ontology_id= form.cleaned_data['analysis_info_ontology_id']
            analysis_info_ontology_name= form.cleaned_data['analysis_info_ontology_name']
            analysis_info_description= form.cleaned_data['analysis_info_description']
            analysis_schema_specification= form.cleaned_data['analysis_schema_specification']
            analysis_schema_id= form.cleaned_data['analysis_schema_id']
            analysis_schema_name= form.cleaned_data['analysis_schema_name']
            analysis_schema_version= form.cleaned_data['analysis_schema_version']
            analysis_supported_schemas= form.cleaned_data['analysis_supported_schemas']
            analysis_schema_reference= form.cleaned_data['analysis_schema_reference']

            if analysis != None:
                analysis_endpoints=form.cleaned_data['AnalysisEndpoints']
                analysis_non_filtered = form.cleaned_data['AnalysisNonFiltered']
                with open("/home/app/web/beacon/conf/" + 'analysis' + ".py") as f:
                    lines = f.readlines()
                with open("/home/app/web/beacon/conf/"+ 'analysis' + ".py", "w") as f:
                    new_lines =''
                    for line in lines:
                        if 'endpoint_name=' in str(line):
                            new_lines+="endpoint_name="+'"'+analysis_endpoint_name+'"'+"\n"
                        elif 'allow_queries_without_filters=' in str(line):
                            if "True" in str(line):
                                new_line=line.replace("True",str(analysis_non_filtered))
                                new_lines+=new_line
                            elif "False" in str(line):
                                new_line=line.replace("False",str(analysis_non_filtered))
                                new_lines+=new_line
                        elif 'singleEntryUrl=' in str(line):
                            endpoint_to_look=analysis_endpoint_name + '/{id}'
                            if endpoint_to_look in analysis_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'biosample_lookup=' in str(line):
                            endpoint_to_look=analysis_endpoint_name + '/{id}/'+biosample_endpoint_name
                            if endpoint_to_look in analysis_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'cohort_lookup=' in str(line):
                            endpoint_to_look=analysis_endpoint_name + '/{id}/'+cohort_endpoint_name
                            if endpoint_to_look in analysis_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'dataset_lookup' in str(line):
                            endpoint_to_look = analysis_endpoint_name + '/{id}/'+dataset_endpoint_name
                            if endpoint_to_look in analysis_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'genomicVariant_lookup=' in str(line):
                            endpoint_to_look=analysis_endpoint_name + '/{id}/'+genomicVariant_endpoint_name
                            if endpoint_to_look in analysis_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'individual_lookup=' in str(line):
                            endpoint_to_look=analysis_endpoint_name + '/{id}/'+individual_endpoint_name
                            if endpoint_to_look in analysis_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'run_lookup=' in str(line):
                            endpoint_to_look=analysis_endpoint_name + '/{id}/'+run_endpoint_name
                            if endpoint_to_look in analysis_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'granularity=' in str(line):
                            new_lines+="granularity="+'"'+analysis_granularity+'"'+"\n"
                        elif 'database=' in str(line):
                            new_lines+="database="+'"'+analysis_engine+'"'+"\n"
                        else:
                            new_lines+=line
                    f.write(new_lines)
                f.close()
            if biosample != None:
                biosample_endpoints=form.cleaned_data['BiosampleEndpoints']
                biosample_non_filtered = form.cleaned_data['BiosampleNonFiltered']
                with open("/home/app/web/beacon/conf/" + 'biosample' + ".py") as f:
                    lines = f.readlines()
                with open("/home/app/web/beacon/conf/"+ 'biosample' + ".py", "w") as f:
                    new_lines =''
                    for line in lines:
                        if 'endpoint_name=' in str(line):
                            new_lines+="endpoint_name="+'"'+biosample_endpoint_name+'"'+"\n"
                        elif 'allow_queries_without_filters=' in str(line):
                            if "True" in str(line):
                                new_line=line.replace("True",str(biosample_non_filtered))
                                new_lines+=new_line
                            elif "False" in str(line):
                                new_line=line.replace("False",str(biosample_non_filtered))
                                new_lines+=new_line
                        elif 'singleEntryUrl=' in str(line):
                            endpoint_to_look=biosample_endpoint_name + '/{id}'
                            if endpoint_to_look in biosample_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'analysis_lookup=' in str(line):
                            endpoint_to_look=biosample_endpoint_name + '/{id}/'+analysis_endpoint_name
                            if endpoint_to_look in biosample_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'cohort_lookup=' in str(line):
                            endpoint_to_look=biosample_endpoint_name + '/{id}/'+cohort_endpoint_name
                            if endpoint_to_look in biosample_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'dataset_lookup' in str(line):
                            endpoint_to_look = biosample_endpoint_name + '/{id}/'+dataset_endpoint_name
                            if endpoint_to_look in biosample_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'genomicVariant_lookup=' in str(line):
                            endpoint_to_look=biosample_endpoint_name + '/{id}/'+genomicVariant_endpoint_name
                            if endpoint_to_look in biosample_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'individual_lookup=' in str(line):
                            endpoint_to_look=biosample_endpoint_name + '/{id}/'+individual_endpoint_name
                            if endpoint_to_look in biosample_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'run_lookup=' in str(line):
                            endpoint_to_look=biosample_endpoint_name + '/{id}/'+run_endpoint_name
                            if endpoint_to_look in biosample_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'granularity=' in str(line):
                            new_lines+="granularity="+'"'+biosample_granularity+'"'+"\n"
                        elif 'database=' in str(line):
                            new_lines+="database="+'"'+biosample_engine+'"'+"\n"
                        else:
                            new_lines+=line
                    f.write(new_lines)
                f.close()
            if cohort != None:
                cohort_endpoints=form.cleaned_data['CohortEndpoints']
                cohort_non_filtered = form.cleaned_data['CohortNonFiltered']
                with open("/home/app/web/beacon/conf/" + 'cohort' + ".py") as f:
                    lines = f.readlines()
                with open("/home/app/web/beacon/conf/"+ 'cohort' + ".py", "w") as f:
                    new_lines =''
                    for line in lines:
                        if 'endpoint_name=' in str(line):
                            new_lines+="endpoint_name="+'"'+cohort_endpoint_name+'"'+"\n"
                        elif 'allow_queries_without_filters=' in str(line):
                            if "True" in str(line):
                                new_line=line.replace("True",str(cohort_non_filtered))
                                new_lines+=new_line
                            elif "False" in str(line):
                                new_line=line.replace("False",str(cohort_non_filtered))
                                new_lines+=new_line
                        elif 'singleEntryUrl=' in str(line):
                            endpoint_to_look=cohort_endpoint_name + '/{id}'
                            if endpoint_to_look in cohort_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'analysis_lookup=' in str(line):
                            endpoint_to_look=cohort_endpoint_name + '/{id}/'+analysis_endpoint_name
                            if endpoint_to_look in cohort_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'biosample_lookup=' in str(line):
                            endpoint_to_look=cohort_endpoint_name + '/{id}/'+biosample_endpoint_name
                            if endpoint_to_look in cohort_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'dataset_lookup' in str(line):
                            endpoint_to_look = cohort_endpoint_name + '/{id}/'+dataset_endpoint_name
                            if endpoint_to_look in cohort_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'genomicVariant_lookup=' in str(line):
                            endpoint_to_look=cohort_endpoint_name + '/{id}/'+genomicVariant_endpoint_name
                            if endpoint_to_look in cohort_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'individual_lookup=' in str(line):
                            endpoint_to_look=cohort_endpoint_name + '/{id}/'+individual_endpoint_name
                            if endpoint_to_look in cohort_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'run_lookup=' in str(line):
                            endpoint_to_look=cohort_endpoint_name + '/{id}/'+run_endpoint_name
                            if endpoint_to_look in cohort_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'granularity=' in str(line):
                            new_lines+="granularity="+'"'+cohort_granularity+'"'+"\n"
                        elif 'database=' in str(line):
                            new_lines+="database="+'"'+cohort_engine+'"'+"\n"
                        else:
                            new_lines+=line
                    f.write(new_lines)
                f.close()
            if dataset != None:
                dataset_endpoints=form.cleaned_data['DatasetEndpoints']
                dataset_non_filtered = form.cleaned_data['DatasetNonFiltered']
                with open("/home/app/web/beacon/conf/" + 'dataset' + ".py") as f:
                    lines = f.readlines()
                with open("/home/app/web/beacon/conf/"+ 'dataset' + ".py", "w") as f:
                    new_lines =''
                    for line in lines:
                        if 'endpoint_name=' in str(line):
                            new_lines+="endpoint_name="+'"'+dataset_endpoint_name+'"'+"\n"
                        elif 'allow_queries_without_filters=' in str(line):
                            if "True" in str(line):
                                new_line=line.replace("True",str(dataset_non_filtered))
                                new_lines+=new_line
                            elif "False" in str(line):
                                new_line=line.replace("False",str(dataset_non_filtered))
                                new_lines+=new_line
                        elif 'singleEntryUrl=' in str(line):
                            endpoint_to_look=dataset_endpoint_name + '/{id}'
                            if endpoint_to_look in dataset_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'analysis_lookup=' in str(line):
                            endpoint_to_look=dataset_endpoint_name + '/{id}/'+analysis_endpoint_name
                            if endpoint_to_look in dataset_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'biosample_lookup=' in str(line):
                            endpoint_to_look=dataset_endpoint_name + '/{id}/'+biosample_endpoint_name
                            if endpoint_to_look in dataset_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'cohort_lookup=' in str(line):
                            endpoint_to_look = dataset_endpoint_name + '/{id}/'+cohort_endpoint_name
                            if endpoint_to_look in dataset_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'genomicVariant_lookup=' in str(line):
                            endpoint_to_look=dataset_endpoint_name + '/{id}/'+genomicVariant_endpoint_name
                            if endpoint_to_look in dataset_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'individual_lookup=' in str(line):
                            endpoint_to_look=dataset_endpoint_name + '/{id}/'+individual_endpoint_name
                            if endpoint_to_look in dataset_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'run_lookup=' in str(line):
                            endpoint_to_look=dataset_endpoint_name + '/{id}/'+run_endpoint_name
                            if endpoint_to_look in dataset_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'granularity=' in str(line):
                            new_lines+="granularity="+'"'+dataset_granularity+'"'+"\n"
                        elif 'database=' in str(line):
                            new_lines+="database="+'"'+dataset_engine+'"'+"\n"
                        else:
                            new_lines+=line
                    f.write(new_lines)
                f.close()
            if genomicVariant != None:
                genomicVariant_endpoints=form.cleaned_data['GenomicVariantEndpoints']
                genomicVariant_non_filtered = form.cleaned_data['GenomicVariantNonFiltered']
                with open("/home/app/web/beacon/conf/" + 'genomicVariant' + ".py") as f:
                    lines = f.readlines()
                with open("/home/app/web/beacon/conf/"+ 'genomicVariant' + ".py", "w") as f:
                    new_lines =''
                    for line in lines:
                        if 'endpoint_name=' in str(line):
                            new_lines+="endpoint_name="+'"'+genomicVariant_endpoint_name+'"'+"\n"
                        elif 'allow_queries_without_filters=' in str(line):
                            if "True" in str(line):
                                new_line=line.replace("True",str(genomicVariant_non_filtered))
                                new_lines+=new_line
                            elif "False" in str(line):
                                new_line=line.replace("False",str(genomicVariant_non_filtered))
                                new_lines+=new_line
                        elif 'singleEntryUrl=' in str(line):
                            endpoint_to_look=genomicVariant_endpoint_name + '/{id}'
                            if endpoint_to_look in genomicVariant_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'analysis_lookup=' in str(line):
                            endpoint_to_look=genomicVariant_endpoint_name + '/{id}/'+analysis_endpoint_name
                            if endpoint_to_look in genomicVariant_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'biosample_lookup=' in str(line):
                            endpoint_to_look=genomicVariant_endpoint_name + '/{id}/'+biosample_endpoint_name
                            if endpoint_to_look in genomicVariant_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'cohort_lookup=' in str(line):
                            endpoint_to_look = genomicVariant_endpoint_name + '/{id}/'+cohort_endpoint_name
                            if endpoint_to_look in genomicVariant_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'dataset_lookup' in str(line):
                            endpoint_to_look=genomicVariant_endpoint_name + '/{id}/'+dataset_endpoint_name
                            if endpoint_to_look in genomicVariant_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'individual_lookup=' in str(line):
                            endpoint_to_look=genomicVariant_endpoint_name + '/{id}/'+individual_endpoint_name
                            if endpoint_to_look in genomicVariant_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'run_lookup=' in str(line):
                            endpoint_to_look=genomicVariant_endpoint_name + '/{id}/'+run_endpoint_name
                            if endpoint_to_look in genomicVariant_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'granularity=' in str(line):
                            new_lines+="granularity="+'"'+genomicVariation_granularity+'"'+"\n"
                        elif 'database=' in str(line):
                            new_lines+="database="+'"'+genomicVariation_engine+'"'+"\n"
                        else:
                            new_lines+=line
                    f.write(new_lines)
                f.close()
            if individual != None:
                individual_endpoints=form.cleaned_data['IndividualEndpoints']
                individual_non_filtered = form.cleaned_data['IndividualNonFiltered']
                with open("/home/app/web/beacon/conf/" + 'individual' + ".py") as f:
                    lines = f.readlines()
                with open("/home/app/web/beacon/conf/"+ 'individual' + ".py", "w") as f:
                    new_lines =''
                    for line in lines:
                        if 'endpoint_name=' in str(line):
                            new_lines+="endpoint_name="+'"'+individual_endpoint_name+'"'+"\n"
                        elif 'allow_queries_without_filters=' in str(line):
                            if "True" in str(line):
                                new_line=line.replace("True",str(individual_non_filtered))
                                new_lines+=new_line
                            elif "False" in str(line):
                                new_line=line.replace("False",str(individual_non_filtered))
                                new_lines+=new_line
                        elif 'singleEntryUrl=' in str(line):
                            endpoint_to_look=individual_endpoint_name + '/{id}'
                            if endpoint_to_look in individual_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'analysis_lookup=' in str(line):
                            endpoint_to_look=individual_endpoint_name + '/{id}/'+analysis_endpoint_name
                            if endpoint_to_look in individual_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'biosample_lookup=' in str(line):
                            endpoint_to_look=individual_endpoint_name + '/{id}/'+biosample_endpoint_name
                            if endpoint_to_look in individual_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'cohort_lookup=' in str(line):
                            endpoint_to_look = individual_endpoint_name + '/{id}/'+cohort_endpoint_name
                            if endpoint_to_look in individual_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'dataset_lookup' in str(line):
                            endpoint_to_look=individual_endpoint_name + '/{id}/'+dataset_endpoint_name
                            if endpoint_to_look in individual_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'genomicVariant_lookup=' in str(line):
                            endpoint_to_look=individual_endpoint_name + '/{id}/'+genomicVariant_endpoint_name
                            if endpoint_to_look in individual_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'run_lookup=' in str(line):
                            endpoint_to_look=individual_endpoint_name + '/{id}/'+run_endpoint_name
                            if endpoint_to_look in individual_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'granularity=' in str(line):
                            new_lines+="granularity="+'"'+individual_granularity+'"'+"\n"
                        elif 'database=' in str(line):
                            new_lines+="database="+'"'+individual_engine+'"'+"\n"
                        else:
                            new_lines+=line
                    f.write(new_lines)
                f.close()
            if run != None:
                run_endpoints=form.cleaned_data['RunEndpoints']
                run_non_filtered = form.cleaned_data['RunNonFiltered']
                with open("/home/app/web/beacon/conf/" + 'run' + ".py") as f:
                    lines = f.readlines()
                with open("/home/app/web/beacon/conf/"+ 'run' + ".py", "w") as f:
                    new_lines =''
                    for line in lines:
                        if 'endpoint_name=' in str(line):
                            new_lines+="endpoint_name="+'"'+run_endpoint_name+'"'+"\n"
                        elif 'allow_queries_without_filters=' in str(line):
                            if "True" in str(line):
                                new_line=line.replace("True",str(run_non_filtered))
                                new_lines+=new_line
                            elif "False" in str(line):
                                new_line=line.replace("False",str(run_non_filtered))
                                new_lines+=new_line
                        elif 'singleEntryUrl=' in str(line):
                            endpoint_to_look=run_endpoint_name + '/{id}'
                            if endpoint_to_look in run_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'analysis_lookup=' in str(line):
                            endpoint_to_look=run_endpoint_name + '/{id}/'+analysis_endpoint_name
                            if endpoint_to_look in run_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'biosample_lookup=' in str(line):
                            endpoint_to_look=run_endpoint_name + '/{id}/'+biosample_endpoint_name
                            if endpoint_to_look in run_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'cohort_lookup=' in str(line):
                            endpoint_to_look = run_endpoint_name + '/{id}/'+cohort_endpoint_name
                            if endpoint_to_look in run_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'dataset_lookup' in str(line):
                            endpoint_to_look=run_endpoint_name + '/{id}/'+dataset_endpoint_name
                            if endpoint_to_look in run_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'genomicVariant_lookup=' in str(line):
                            endpoint_to_look=run_endpoint_name + '/{id}/'+genomicVariant_endpoint_name
                            if endpoint_to_look in run_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'individual_lookup=' in str(line):
                            endpoint_to_look=run_endpoint_name + '/{id}/'+individual_endpoint_name
                            if endpoint_to_look in run_endpoints:
                                if 'False' in str(line):
                                    new_line=line.replace("False","True")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                            else:
                                if 'True' in str(line):
                                    new_line=line.replace("True","False")
                                    new_lines+=new_line
                                else:
                                    new_lines+=line
                        elif 'granularity=' in str(line):
                            new_lines+="granularity="+'"'+run_granularity+'"'+"\n"
                        elif 'database=' in str(line):
                            new_lines+="database="+'"'+run_engine+'"'+"\n"
                        else:
                            new_lines+=line
                    f.write(new_lines)
                f.close()


        
            return redirect("adminclient:entry_types")
        else:
            context = {'form': form}
            
    template = "general_configuration/entry_types.html"
    return render(request, template, context)
"""