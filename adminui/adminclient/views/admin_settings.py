
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model



import logging

LOG = logging.getLogger(__name__)
fmt = '%(levelname)s - %(asctime)s - %(message)s'
formatter = logging.Formatter(fmt)
sh = logging.StreamHandler()
sh.setLevel('NOTSET')
sh.setFormatter(formatter)
LOG.addHandler(sh)

#my_group = Group.objects.get(name='my_group_name') 
#my_group.user_set.add(your_user)

@login_required
def default_view(request):
    User = get_user_model()
    users = User.objects.all()
    users_list=[]
    for user in users:
        userdict={}
        userdict["email"]=user.email
        userdict["username"]=user.email
        userdict["name"]=user.first_name
        userdict["group"]=user.groups
        users_list.append(userdict)
    context = {"users": users_list}
    template = "general_configuration/admin_settings.html"
    return render(request, template, context)
