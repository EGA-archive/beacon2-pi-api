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

import logging

LOG = logging.getLogger(__name__)
fmt = '%(levelname)s - %(asctime)s - %(message)s'
formatter = logging.Formatter(fmt)
sh = logging.StreamHandler()
sh.setLevel('NOTSET')
sh.setFormatter(formatter)
LOG.addHandler(sh)

def default_view(request):
    headers = ['id', 'label', 'type', 'synonyms', 'similarities', 'scopes']
    similarities_headers = ['id', 'label', 'similarities']
    filtering_terms=client["beacon"].filtering_terms
    synonyms=client["beacon"].synonyms
    similarities=client["beacon"].similarities
    all_similarities=similarities.find({}).limit(0)
    all_filtering_terms=filtering_terms.find({}).limit(0)
    final_fterm={}
    final_fterms_list=[]
    for fterm in all_filtering_terms:
        final_fterm=fterm
        synonym=synonyms.find_one({"id": fterm["id"]})
        similarity=similarities.find_one({"id": fterm["id"]})
        final_fterm["synonyms"]=synonym
        final_fterm["similarities"]=similarity
        final_fterms_list.append(final_fterm)
    
    if request.method == 'POST':
        form = FilteringTermsForm(request.POST, request.FILES)
        form2 = AddFilteringTerm(request.POST)
        if form.is_valid():
            filteringTermID = form.cleaned_data['FilteringTermID']
            if 'Delete Filtering Term' in request.POST:
                filtering_terms.delete_many({"id": filteringTermID})
            elif 'Delete All' in request.POST:
                filtering_terms.delete_many({})
            elif 'Upload a List' in request.POST:
                hola = json.load(request.FILES["FilteringTermsList"])
                filtering_terms.insert_many(hola)
        elif form2.is_valid():
            filteringTermID = form.cleaned_data['FilteringTermID']
            filteringTermType = form.cleaned_data['FilteringTermType']

        return redirect("adminclient:filtering_terms")
    context={"filtering_terms": final_fterms_list, "headers": headers, "all_similarities": list(all_similarities), "similarities_headers": similarities_headers}
    template = "general_configuration/filtering_terms.html"
    return render(request, template, context)