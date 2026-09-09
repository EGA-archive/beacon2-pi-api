from django.shortcuts import render, redirect
import logging
from beacon.conf.conf_override import config
import subprocess
import os
import logging
import importlib
from django.contrib.auth.decorators import login_required, permission_required
import requests
from dotenv import load_dotenv, get_key, set_key

def test_api():
    try:
        response = requests.get(config.complete_url+'/health', timeout=5)
        api = response.json()
    except Exception as e:
        api = e
    context = {"api": api}
    return context

def test_ui():
    try:
        response = requests.get(config.welcome_url, timeout=5)
        ui = response.json()
    except Exception as e:
        ui = e
    context = {"ui": ui}
    return context

def test_idps():
    path="/home/app/web/beacon/auth/idp_providers/"
    idp_dict={}
    files = [
        f for f in os.listdir(path)
        if os.path.isfile(os.path.join(path, f))
    ]
    for file in files:
        print(file, flush=True)
        if file.endswith(".env"):
            issuer=get_key(dotenv_path=path + file, key_to_get="ISSUER")
            well_known_endpoint=issuer+".well-known/openid-configuration"
            try:
                idp_dict[file]=requests.get(well_known_endpoint, timeout=5)
            except Exception as e:
                idp_dict[file]=e
    context = {"idp": idp_dict}
    return context

#@login_required
#@permission_required('adminclient.can_see_view', raise_exception=True)
def default_view(request):
    context = {}
    if request.method == 'POST':
        for k in request.POST:
            if k == 'TestAPI':
                context = test_api()
            elif k == 'UserInterface':
                context = test_ui()
            elif k == 'IdentityProviders':
                context = test_idps()
            elif k == 'GeneralStatus':
                context_api = test_api()
                context_ui = test_ui()
                context_idps = test_idps()
                context = {**context_api, **context_ui, **context_idps}
        template = "general_configuration/service_status.html"
        return render(request, template, context)
    template = "general_configuration/service_status.html"
    return render(request, template, context)
