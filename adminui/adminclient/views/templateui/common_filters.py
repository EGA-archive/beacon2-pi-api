from django.shortcuts import render, redirect
import logging
from adminbackend.forms.templateui.common_filters import GroupForm, TEMPLATE_CONF
import yaml
import glob
import logging
import os
import subprocess
from dotenv import load_dotenv, set_key
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from beacon.connections.mongo.__init__ import client
import ast
import json

#@user_passes_test(lambda u: u.is_superuser)
#@login_required
#@permission_required('adminclient.can_see_view', raise_exception=True)
def default_view(request):
    
    groups = TEMPLATE_CONF["ui"]["commonFilters"]["filterCategories"]
    list_of_forms=[]
    for category in groups:
        list_of_forms.append(GroupForm(category=category))
    filtering_terms=client["beacon"].filtering_terms
    all_filtering_terms=filtering_terms.find({}).limit(0)
    final_fterm={}
    final_fterms_list=[]
    for fterm in all_filtering_terms:
        final_fterm=fterm
        final_fterms_list.append(final_fterm)
    if request.method == 'POST':
        print(request.POST, flush=True)
        filteringTerm= request.POST['FilteringTermLabel']
        ft_splitted = filteringTerm.split('_')
        category = request.POST['category']
        new_conf=TEMPLATE_CONF
        labels = request.POST.getlist('labels')
        new_category_dict_list=[]
        print(type(labels), flush=True)
        for label_dict in new_conf["ui"]["commonFilters"]["filterLabels"][category]:
            print(label_dict["key"], flush=True)
            if label_dict["key"] not in labels:
                continue
            else:
                new_category_dict_list.append(label_dict)
        new_conf["ui"]["commonFilters"]["filterLabels"][category]=new_category_dict_list
        new_dict={"key": ft_splitted[3], "id": ft_splitted[1], "label": ft_splitted[3], "type": "ontology", "scopes": ast.literal_eval(ft_splitted[5])}
        print(new_dict, flush=True)
        if new_dict["key"] not in labels:
            new_conf["ui"]["commonFilters"]["filterLabels"][category].append(new_dict)
        

        with open("/home/app/web/template-ui-config.json", "w") as f:
            json.dump(new_conf, f)
        return redirect("adminclient:common_filters")
        

    context={"fterms_list": final_fterms_list, "list_of_forms": list_of_forms}
    template = "templateui/common_filters.html"
    return render(request, template, context)
