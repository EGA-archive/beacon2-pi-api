from django.shortcuts import render, redirect
import logging
from adminbackend.forms.identity_provider import IDPForm
import yaml
import glob
import logging
import os
import subprocess
from dotenv import load_dotenv, set_key
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test

#@user_passes_test(lambda u: u.is_superuser)
#@login_required
#@permission_required('adminclient.can_see_view', raise_exception=True)
def default_view(request):
    form = IDPForm()
    
    identity_provider_list=[]
    
    for env_filename in glob.glob("/home/app/web/beacon/auth/idp_providers/*.env"):
        load_dotenv(env_filename, override=True)
        identity_provider_dict={}
        env_id = env_filename.split('/')
        env_id = env_id[-1]
        env_id = env_id.split('.')
        env_id = env_id[0]
        identity_provider_dict["IdentityProvider"]=env_id
        identity_provider_dict["Issuer"] = os.getenv('ISSUER')
        identity_provider_dict["ClientID"] = os.getenv('CLIENT_ID')
        identity_provider_dict["WellKnown"] = os.getenv('WELL_KNOWN_ENDPOINT')
        identity_provider_dict["BeaconInAudience"] = os.getenv('MUST_INCLUDE_BEACON_URL_IN_AUDIENCE')
        identity_provider_list.append(identity_provider_dict)
        
    if request.method == 'POST':
        form = IDPForm(request.POST)
        if form.is_valid():
            idp = form.cleaned_data['IdentityProvider']
            issuer = form.cleaned_data['Issuer']
            client_id = form.cleaned_data['ClientID']
            well_known = form.cleaned_data['WellKnown']
            beacon_in_aud = form.cleaned_data['BeaconInAudience']
            load_dotenv("/home/app/web/beacon/auth/idp_providers/" + idp + '.env', override=True)
            if 'Save' in request.POST:
                if isinstance(beacon_in_aud, bool):
                    if beacon_in_aud == True:
                        beacon_in_aud = 'True'
                    elif beacon_in_aud == False:
                        beacon_in_aud = 'False'
                set_key(dotenv_path="/home/app/web/beacon/auth/idp_providers/" + idp + '.env', key_to_set="CLIENT_ID", value_to_set=client_id)
                set_key(dotenv_path="/home/app/web/beacon/auth/idp_providers/" + idp + '.env', key_to_set="WELL_KNOWN_ENDPOINT", value_to_set=well_known)
                set_key(dotenv_path="/home/app/web/beacon/auth/idp_providers/" + idp + '.env', key_to_set="MUST_INCLUDE_BEACON_URL_IN_AUDIENCE", value_to_set=beacon_in_aud)
                set_key(dotenv_path="/home/app/web/beacon/auth/idp_providers/" + idp + '.env', key_to_set="ISSUER", value_to_set=issuer)
            elif 'Add' in request.POST:
                if isinstance(beacon_in_aud, bool):
                    if beacon_in_aud == True:
                        beacon_in_aud = 'True'
                    elif beacon_in_aud == False:
                        beacon_in_aud = 'False'
                create_idp = subprocess.check_output("touch /home/app/web/beacon/auth/idp_providers/{}.env".format(idp), shell=True)
                load_dotenv("/home/app/web/beacon/auth/idp_providers/" + idp + '.env', override=True)
                set_key(dotenv_path="/home/app/web/beacon/auth/idp_providers/" + idp + '.env', key_to_set="CLIENT_ID", value_to_set=client_id)
                set_key(dotenv_path="/home/app/web/beacon/auth/idp_providers/" + idp + '.env', key_to_set="WELL_KNOWN_ENDPOINT", value_to_set=well_known)
                set_key(dotenv_path="/home/app/web/beacon/auth/idp_providers/" + idp + '.env', key_to_set="MUST_INCLUDE_BEACON_URL_IN_AUDIENCE", value_to_set=beacon_in_aud)
                set_key(dotenv_path="/home/app/web/beacon/auth/idp_providers/" + idp + '.env', key_to_set="ISSUER", value_to_set=issuer)
            elif 'Delete' in request.POST:
                os.remove("/home/app/web/beacon/auth/idp_providers/" + idp +'.env')
            return redirect("adminclient:identity_provider")
    context={"identity_provider_list": identity_provider_list ,"form": form}
    template = "general_configuration/identity_provider.html"
    return render(request, template, context)