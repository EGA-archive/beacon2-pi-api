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
from django.contrib.auth.decorators import login_required

import logging

LOG = logging.getLogger(__name__)
fmt = '%(levelname)s - %(asctime)s - %(message)s'
formatter = logging.Formatter(fmt)
sh = logging.StreamHandler()
sh.setLevel('NOTSET')
sh.setFormatter(formatter)
LOG.addHandler(sh)

@login_required
def default_view(request):

    params =request.GET.urlencode()
    params_splitted = params.split("&")
    for param in params_splitted:
        if 'Synonym_FilteringTermID' in param:
            final_params=param.replace("%3A", ":")
            ft_queried=final_params.split("=")
            ft_found=ft_queried[1]
        elif 'Synonym' in param:
            final_params=param.replace("%3A", ":")
            synonym_queried=final_params.split("=")
            synonym_found=synonym_queried[1]


    presynonyms=client["beacon"].presynonyms
    presynonyms.insert_one({"id": ft_found, "synonym": synonym_found})
    
    synonyms_found=presynonyms.find({"id": ft_found })
    
    synonyms_list=[]
    for synonym_found in synonyms_found:
        synonyms_list.append(synonym_found["synonym"])

    context={"synonyms": synonyms_list}
    template = "general_configuration/synonyms.html"
    return render(request, template, context)