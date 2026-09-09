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

#@user_passes_test(lambda u: u.is_superuser)
#@login_required
#@permission_required('adminclient.can_see_view', raise_exception=True)
def default_view(request):
    groups = TEMPLATE_CONF["ui"]["commonFilters"]["filterCategories"]
    list_of_forms=[]
    for category in groups:
        list_of_forms.append(GroupForm(category=category))
    context={"list_of_forms": list_of_forms }
    template = "templateui/common_filters.html"
    return render(request, template, context)
