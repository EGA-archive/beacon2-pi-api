from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponseBadRequest
import logging
from pymongo.mongo_client import MongoClient
from django.urls import resolve
from beacon.connections.mongo.__init__ import client
from adminbackend.forms.filtering_terms import FilteringTermsForm, AddFilteringTerm
import yaml
import json
from django.contrib.auth.decorators import login_required, permission_required

import logging

LOG = logging.getLogger(__name__)
fmt = '%(levelname)s - %(asctime)s - %(message)s'
formatter = logging.Formatter(fmt)
sh = logging.StreamHandler()
sh.setLevel('NOTSET')
sh.setFormatter(formatter)
LOG.addHandler(sh)

@login_required
@permission_required('adminclient.can_see_view', raise_exception=True)
def default_view(request):

    params =request.GET.urlencode()
    params_splitted = params.split("&")
    for param in params_splitted:
        if 'Synonym_FilteringTermID' in param:
            final_params=param.replace("%3A", ":")
            ft_queried=final_params.split("=")
            ft_found=ft_queried[1]
        elif 'Descendant' in param:
            final_params=param.replace("%3A", ":")
            descendant_queried=final_params.split("=")
            descendant_found=descendant_queried[1]


    predescendants=client["beacon"].predescendants
    predescendants.insert_one({"id": ft_found, "descendants": descendant_found})
    
    descendants_found=predescendants.find({"id": ft_found })
    
    descendants_list=[]
    for descendant_found in descendants_found:
        descendants_list.append(descendant_found["descendants"])

    context={"descendants": descendants_list}
    template = "general_configuration/descendants.html"
    return render(request, template, context)