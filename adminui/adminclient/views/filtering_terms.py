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
    filtering_terms=client["beacon"].filtering_terms
    synonyms=client["beacon"].synonyms
    similarities=client["beacon"].similarities
    all_filtering_terms=filtering_terms.find({})
    all_similarities=similarities.find({})
    all_synonyms=synonyms.find({})
    final_fterm={}
    final_fterms_list=[]
    for fterm in all_filtering_terms:
        final_fterm=fterm
        for synonym in all_synonyms:
            if fterm["id"] in synonym:
                final_fterm["synonyms"]=synonym[fterm["id"]]
        for similarity in all_similarities:
            if fterm["id"] in similarity:
                final_fterm["similarities"]=similarity[fterm["id"]]
        final_fterms_list.append(final_fterm)
        
    if request.method == 'POST':
        form = DatasetsForm(request.POST)
        if form.is_valid():

            return redirect("adminclient:filtering_terms")
    context={"filtering_terms": list(all_filtering_terms)}
    template = "general_configuration/filtering_terms.html"
    return render(request, template, context)