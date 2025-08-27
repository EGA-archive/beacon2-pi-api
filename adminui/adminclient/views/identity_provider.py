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


LOG = logging.getLogger(__name__)
fmt = '%(levelname)s - %(asctime)s - %(message)s'
formatter = logging.Formatter(fmt)
sh = logging.StreamHandler()
sh.setLevel('NOTSET')
sh.setFormatter(formatter)
LOG.addHandler(sh)

@user_passes_test(lambda u: u.is_superuser)
@login_required
@permission_required('adminclient.can_see_view', raise_exception=True)
def default_view(request):
    form = IDPForm()
    
    identity_provider_list=[]
    
    for env_filename in glob.glob("adminui/beacon/auth/idp_providers/*.env"):
        load_dotenv(env_filename, override=True)
        identity_provider_dict={}
        env_id = env_filename.split('/')
        env_id = env_id[-1]
        env_id = env_id.split('.')
        env_id = env_id[0]
        identity_provider_dict["IdentityProvider"]=env_id
        identity_provider_dict["Issuer"] = os.getenv('ISSUER')
        identity_provider_dict["ClientID"] = os.getenv('CLIENT_ID')
        identity_provider_dict["ClientSecret"] = os.getenv('CLIENT_SECRET')
        identity_provider_dict["UserInfo"] = os.getenv('USER_INFO')
        identity_provider_dict["Introspection"] = os.getenv('INTROSPECTION')
        identity_provider_dict["JWKSURL"] = os.getenv('JWKS_URL')
        identity_provider_list.append(identity_provider_dict)
        
    if request.method == 'POST':
        form = IDPForm(request.POST)
        if form.is_valid():
            idp = form.cleaned_data['IdentityProvider']
            issuer = form.cleaned_data['Issuer']
            client_id = form.cleaned_data['ClientID']
            client_secret = form.cleaned_data['ClientSecret']
            user_info = form.cleaned_data['UserInfo']
            introspection = form.cleaned_data['Introspection']
            jwks_url = form.cleaned_data['JWKSURL']
            load_dotenv("adminui/beacon/auth/idp_providers/" + idp + '.env', override=True)
            if 'Save' in request.POST:
                set_key(dotenv_path="adminui/beacon/auth/idp_providers/" + idp + '.env', key_to_set="CLIENT_ID", value_to_set=client_id)
                set_key(dotenv_path="adminui/beacon/auth/idp_providers/" + idp + '.env', key_to_set="CLIENT_SECRET", value_to_set=client_secret)
                set_key(dotenv_path="adminui/beacon/auth/idp_providers/" + idp + '.env', key_to_set="USER_INFO", value_to_set=user_info)
                set_key(dotenv_path="adminui/beacon/auth/idp_providers/" + idp + '.env', key_to_set="INTROSPECTION", value_to_set=introspection)
                set_key(dotenv_path="adminui/beacon/auth/idp_providers/" + idp + '.env', key_to_set="JWKS_URL", value_to_set=jwks_url)
                set_key(dotenv_path="adminui/beacon/auth/idp_providers/" + idp + '.env', key_to_set="ISSUER", value_to_set=issuer)
            elif 'Add' in request.POST:
                create_idp = subprocess.check_output("touch adminui/beacon/auth/idp_providers/{}.env".format(idp), shell=True)
                load_dotenv("adminui/beacon/auth/idp_providers/" + idp + '.env', override=True)
                set_key(dotenv_path="adminui/beacon/auth/idp_providers/" + idp + '.env', key_to_set="CLIENT_ID", value_to_set=client_id)
                set_key(dotenv_path="adminui/beacon/auth/idp_providers/" + idp + '.env', key_to_set="CLIENT_SECRET", value_to_set=client_secret)
                set_key(dotenv_path="adminui/beacon/auth/idp_providers/" + idp + '.env', key_to_set="USER_INFO", value_to_set=user_info)
                set_key(dotenv_path="adminui/beacon/auth/idp_providers/" + idp + '.env', key_to_set="INTROSPECTION", value_to_set=introspection)
                set_key(dotenv_path="adminui/beacon/auth/idp_providers/" + idp + '.env', key_to_set="JWKS_URL", value_to_set=jwks_url)
                set_key(dotenv_path="adminui/beacon/auth/idp_providers/" + idp + '.env', key_to_set="ISSUER", value_to_set=issuer)
            elif 'Delete' in request.POST:
                os.remove("adminui/beacon/auth/idp_providers/" + idp)
            return redirect("adminclient:identity_provider")
    context={"identity_provider_list": identity_provider_list ,"form": form}
    template = "general_configuration/identity_provider.html"
    return render(request, template, context)