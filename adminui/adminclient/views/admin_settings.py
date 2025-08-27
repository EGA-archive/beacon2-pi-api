
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth import get_user_model
from adminbackend.forms.admin_settings import AdminForm
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission


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

@user_passes_test(lambda u: u.is_superuser)
@login_required
@permission_required('adminclient.can_see_view', raise_exception=True)
def default_view(request):
    User = get_user_model()
    users = User.objects.all()
    users_list=[]
    form = AdminForm()
    for user in users:
        userdict={}
        userdict["email"]=user.email
        for g in user.groups.all():
            userdict["group"]=str(g)
        try:
            if userdict["group"] == "":
                userdict["group"] = None
        except Exception:
            userdict["group"]=None
        users_list.append(userdict)
    if request.method == 'POST':
        form = AdminForm(request.POST)
        if form.is_valid():
            Email = form.cleaned_data['Email']
            Groups = form.cleaned_data['Groups']
            user = User.objects.get(email=Email)
            user.groups.clear()
            my_group = Group.objects.get(name=Groups)
            my_group.user_set.add(user)
            '''
            if Groups == 'Owner':
                user.is_superuser = True
                user.is_staff = True
                user.save()
            '''
            return redirect("adminclient:admin_settings")
    context = {"users": users_list, "form": form}
    template = "general_configuration/admin_settings.html"
    return render(request, template, context)
