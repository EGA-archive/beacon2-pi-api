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
import subprocess
from django.contrib.auth.decorators import login_required


LOG = logging.getLogger(__name__)
fmt = '%(levelname)s - %(asctime)s - %(message)s'
formatter = logging.Formatter(fmt)
sh = logging.StreamHandler()
sh.setLevel('NOTSET')
sh.setFormatter(formatter)
LOG.addHandler(sh)

@login_required
def default_view(request):
    form2 = AddFilteringTerm(request.POST)
    headers = ['id', 'label', 'type', 'synonyms', 'similarities', 'scopes']
    similarities_headers = ['id', 'label', 'similarities']
    filtering_terms=client["beacon"].filtering_terms
    presynonyms=client["beacon"].presynonyms
    predescendants=client["beacon"].predescendants
    synonyms=client["beacon"].synonyms
    similarities=client["beacon"].similarities
    all_similarities=similarities.find({}).limit(0)

    
    if request.method == 'POST':
        form = FilteringTermsForm(request.POST, request.FILES)
        if form2.is_valid():
            filteringTermID = form2.cleaned_data['Synonym_FilteringTermID']
            ft_type = form2.cleaned_data['FilteringTermType']
            ft_label = form2.cleaned_data['FilteringTermLabel']
            ft_scope = form2.cleaned_data['Scope']
            ft_synonyms = presynonyms.find({"id": filteringTermID})
            ft_synonyms_list=[]
            for ft_synonym in ft_synonyms:
                ft_synonyms_list.append(ft_synonym)
            if ft_synonyms_list != []:
                synonyms.insert_many(ft_synonyms_list)
            ft_descendants = predescendants.find({"id": filteringTermID})
            ft_descendants_list=[]
            for ft_descendant in ft_descendants:
                ft_descendants_list.append(ft_descendant["descendants"])
            if ft_descendants_list != []:
                similarities.insert_one({"id": filteringTermID, "descendants": ft_descendants_list})
            presynonyms.delete_many({})
            predescendants.delete_many({})
            ft_dict={}
            ft_dict["id"]=filteringTermID
            ft_dict["type"]=ft_type.lower()
            if ft_label is not None:
                ft_dict["label"]=ft_label.lower()
            if ft_scope is not None:
                ft_dict["scopes"]=ft_scope
            filtering_terms.update_one({"id": filteringTermID},{"$set":ft_dict},upsert=True)
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
            context={"filtering_terms": final_fterms_list, "headers": headers, "all_similarities": list(all_similarities), "similarities_headers": similarities_headers, "form2": form2}
            template = "general_configuration/filtering_terms.html"
            return render(request, template, context)
            
        elif form.is_valid():
            LOG.warning('here I am')
            filteringTermID = form.cleaned_data['FilteringTermID']
            if 'Delete Filtering Term' in request.POST:
                filtering_terms.delete_many({"id": filteringTermID})
            elif 'Delete All' in request.POST:
                filtering_terms.delete_many({})
            elif 'Upload a List' in request.POST:
                hola = json.load(request.FILES["FilteringTermsList"])
                filtering_terms.insert_many(hola)
            elif 'SearchAscendant' in request.POST:
                bash_string = 'python -m beacon.connections.mongo.get_descendants'
                bash = subprocess.check_output([bash_string], shell=True)

            presynonyms.delete_many({})
            predescendants.delete_many({})
            return redirect("adminclient:filtering_terms")
    elif request.method == 'GET':
        if form2.is_valid():
            pass
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
    presynonyms.delete_many({})
    predescendants.delete_many({})
    context={"filtering_terms": final_fterms_list, "headers": headers, "all_similarities": list(all_similarities), "similarities_headers": similarities_headers, "form2": form2}
    template = "general_configuration/filtering_terms.html"
    return render(request, template, context)