from django.shortcuts import render
from beacon.connections.mongo.__init__ import client
import yaml

PERMISSIONS_FILE = (
    "/home/app/web/beacon/permissions/datasets/"
    "datasets_permissions.yml"
)

#@login_required
#@permission_required('adminclient.can_see_view', raise_exception=True)
def default_view(request):
    params =request.GET.urlencode()
    params_splitted = params.split("&")
    for param in params_splitted:
        if 'New_Dataset' in param:
            new_dataset_name=param.split("=")[1]

    try:
        with open(PERMISSIONS_FILE) as f:
            datasets_permissions = (
                yaml.safe_load(f) or {}
            )
    except FileNotFoundError:
        datasets_permissions = {}

    datasets_permissions[new_dataset_name]={"public": {"default_entry_types_granularity": "boolean"}}

    with open(PERMISSIONS_FILE, 'w') as outfile:
        yaml.dump(datasets_permissions, outfile)

    context={"new_dataset": new_dataset_name}
    template = "general_configuration/new_permit.html"
    return render(request, template, context)