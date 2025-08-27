
from django.shortcuts import render, redirect
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
    template = "general_configuration/verifier.html"
    return render(request, template)
