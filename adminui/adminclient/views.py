from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponseBadRequest
import logging
from pymongo.mongo_client import MongoClient
from django.urls import resolve
from adminbackend.forms.beacon import BamForm
from adminbackend.forms.entry_types import EntryTypesForm

import logging

LOG = logging.getLogger(__name__)
fmt = '%(levelname)s - %(asctime)s - %(message)s'
formatter = logging.Formatter(fmt)
sh = logging.StreamHandler()
sh.setLevel('NOTSET')
sh.setFormatter(formatter)
LOG.addHandler(sh)

def default_view(request):
    form =BamForm()
    context = {'form': form}
    if request.method == 'POST':
        form = BamForm(request.POST)
        if form.is_valid():
            beaconName = form.cleaned_data['BeaconName']
            beaconId = form.cleaned_data['BeaconId']
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
            with open("adminui/beacon/conf/conf.py") as f:
                lines = f.readlines()
            with open("adminui/beacon/conf/conf.py", "w") as f:
                new_lines =''
                for line in lines:
                    if 'beacon_name' in str(line):
                        new_lines+="beacon_name="+'"'+beaconName+'"'+"\n"
                    elif 'beacon_id' in str(line):
                        new_lines+="beacon_id="+'"'+beaconId+'"'+"\n"
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
                    else:
                        new_lines+=line
                    
                f.write(new_lines)
            f.close()
            return redirect("adminclient:index")
    template = "home.html"
    return render(request, template, context)

def entry_types(request):
    form =EntryTypesForm()
    context = {'form': form}
    if request.method == 'POST':
        form = EntryTypesForm(request.POST)
        if form.is_valid():
            analysis=form.cleaned_data['Analysis']
            analysis_endpoint_name = form.cleaned_data['AnalysisEndpointName']
            biosample=form.cleaned_data['Biosample']
            biosample_endpoint_name = form.cleaned_data['BiosampleEndpointName']
            cohort=form.cleaned_data['Cohort']
            cohort_endpoint_name = form.cleaned_data['CohortEndpointName']
            dataset=form.cleaned_data['Dataset']
            dataset_endpoint_name = form.cleaned_data['DatasetEndpointName']
            genomicVariant=form.cleaned_data['GenomicVariant']
            genomicVariant_endpoint_name = form.cleaned_data['GenomicVariantEndpointName']
            individual=form.cleaned_data['Individual']
            individual_endpoint_name = form.cleaned_data['IndividualEndpointName']
            run=form.cleaned_data['Run']
            run_endpoint_name = form.cleaned_data['RunEndpointName']
            if analysis != None:
                analysis_endpoints=form.cleaned_data['AnalysisEndpoints']
                analysis_non_filtered = form.cleaned_data['AnalysisNonFiltered']
                with open("adminui/beacon/conf/" + 'analysis' + ".py") as f:
                    lines = f.readlines()
                with open("adminui/beacon/conf/"+ 'analysis' + ".py", "w") as f:
                    new_lines =''
                    for line in lines:
                        if 'endpoint_name' in str(line):
                            new_lines+="endpoint_name="+'"'+analysis_endpoint_name+'"'+"\n"
                        elif 'allow_queries_without_filters' in str(line):
                            if "True" in str(line):
                                new_line=line.replace("True",str(analysis_non_filtered))
                                new_lines+=new_line
                            elif "False" in str(line):
                                new_line=line.replace("False",str(analysis_non_filtered))
                                new_lines+=new_line
                        elif 'singleEntryUrl' in str(line):
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
                        elif 'biosample_lookup' in str(line):
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
                        elif 'cohort_lookup' in str(line):
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
                        elif 'genomicVariant_lookup' in str(line):
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
                        elif 'individual_lookup' in str(line):
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
                        elif 'run_lookup' in str(line):
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
                        else:
                            new_lines+=line
                    f.write(new_lines)
                f.close()


        
            return redirect("adminclient:entry_types")
        else:
            context = {'form': form}
            
    template = "general_configuration/entry_types.html"
    return render(request, template, context)
