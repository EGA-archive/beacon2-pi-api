from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponseBadRequest
import logging
from pymongo.mongo_client import MongoClient
from django.urls import resolve
from adminbackend.forms.rounding_counts import RoundingCountsForm
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
    form =RoundingCountsForm()
    context = {'form': form}
    if request.method == 'POST':
        form = RoundingCountsForm(request.POST)
        if form.is_valid():
            rounding = form.cleaned_data['Rounding']
            imprecise = form.cleaned_data['Imprecise']
            type = form.cleaned_data['Type']
            with open("/home/app/web/beacon/conf/conf.py") as f:
                lines = f.readlines()
            with open("/home/app/web/beacon/conf/conf.py", "w") as f:
                new_lines =''
                for line in lines:
                    if 'imprecise_count=' in str(line):
                        new_lines+="imprecise_count="+str(imprecise)+"\n"
                    elif 'round_to_tens=' in str(line):
                        if rounding == 'tenths' and type == 'rounded':
                            new_lines+="round_to_tens="+str(True)+"\n"
                        else:
                            new_lines+="round_to_tens="+str(False)+"\n"
                    elif 'round_to_hundreds=' in str(line):
                        if rounding == 'hundredths' and type == 'rounded':
                            new_lines+="round_to_hundreds="+str(True)+"\n"
                        else:
                            new_lines+="round_to_hundreds="+str(False)+"\n"
                    else:
                        new_lines+=line
                    
                f.write(new_lines)
            f.close()
            return redirect("adminclient:rounding_counts")
    template = "general_configuration/rounding_counts.html"
    return render(request, template, context)
