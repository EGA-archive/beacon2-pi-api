from django.shortcuts import render, redirect
from django.views.generic import TemplateView
import subprocess
import time
from django.http import HttpResponseRedirect, HttpResponseBadRequest
import logging
import json
from pymongo.mongo_client import MongoClient
import imp
from django.urls import resolve

# load a source module from a file
from . import conf

client = MongoClient(
        "mongodb://{}:{}@{}:{}/{}?authSource={}".format(
            conf.database_user,
            conf.database_password,
            conf.database_host,
            conf.database_port,
            conf.database_name,
            conf.database_auth_source,
        )
    )




LOG = logging.getLogger(__name__)

def default_view(request):
    template = "home.html"
    context={}
    return render(request, template, context)
