from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponseBadRequest
import logging
from pymongo.mongo_client import MongoClient
from django.urls import resolve
from beacon.connections.mongo.__init__ import client
from adminbackend.forms.permits import PermitsForm, SecurityLevelForm, GranularityFormSet
import yaml
from django.contrib.auth.decorators import login_required, permission_required

from django.shortcuts import render


def default_view(request):
    datasets = client["beacon"].datasets

    # Materialize the MongoDB cursor because we need to iterate
    # over the datasets more than once.
    all_datasets = list(datasets.find({}))

    dataset_ids = [
        dataset["id"]
        for dataset in all_datasets
    ]

    security_levels = (
        "public",
        "registered",
        "controlled",
    )

    forms_by_dataset = {}

    # ---------------------------------------------------------
    # BUILD ALL FORMS
    # ---------------------------------------------------------

    for dataset_index, dataset_id in enumerate(dataset_ids):

        # Use a safe prefix based on the dataset index.
        #
        # Dataset IDs may contain "/", spaces, etc., which can
        # make them awkward as HTML form prefixes.
        dataset_prefix = f"dataset-{dataset_index}"

        forms_by_dataset[dataset_id] = {
            # -------------------------------------------------
            # Dataset ID form
            # -------------------------------------------------

            "permits": PermitsForm(
                request.POST or None,
                prefix=f"{dataset_prefix}-permits",
                initial={
                    "DatasetID": dataset_id,
                },
            ),

            # -------------------------------------------------
            # Security level + default granularity
            # -------------------------------------------------

            "security": SecurityLevelForm(
                request.POST or None,
                dataset_id=dataset_id,
                prefix=f"{dataset_prefix}-security",
            ),

            # -------------------------------------------------
            # Granularity formsets
            #
            # One formset for each security level.
            # -------------------------------------------------

            "granularity": {
                security_level: GranularityFormSet(
                    request.POST or None,
                    prefix=(
                        f"{dataset_prefix}-"
                        f"{security_level}-granularity"
                    ),
                    form_kwargs={
                        "dataset_id": dataset_id,
                        "security_level": security_level,
                    },
                )
                for security_level in security_levels
            },
        }

    # ---------------------------------------------------------
    # POST
    # ---------------------------------------------------------

    if request.method == "POST":

        all_valid = True

        # -----------------------------------------------------
        # Validate PermitsForm, SecurityLevelForm AND all
        # GranularityFormSets.
        # -----------------------------------------------------

        for dataset_id, dataset_forms in forms_by_dataset.items():

            permits_form = dataset_forms["permits"]
            security_form = dataset_forms["security"]

            if not permits_form.is_valid():
                all_valid = False

            if not security_form.is_valid():
                all_valid = False

            # Validate every security-level formset.
            #
            # We validate all of them rather than only the
            # selected security level. This is important because
            # a user may have added exception rows under several
            # security levels.
            for security_level, formset in (
                dataset_forms["granularity"].items()
            ):
                if not formset.is_valid():
                    all_valid = False

        # -----------------------------------------------------
        # PROCESS DATA
        # -----------------------------------------------------

        if all_valid:

            permissions_file = (
                "/home/app/web/beacon/permissions/datasets/"
                "datasets_permissions.yml"
            )

            # Load existing permissions.
            with open(permissions_file) as f:
                datasets_permissions = yaml.safe_load(f) or {}

            # Work on a copy.
            new_permissions = datasets_permissions.copy()

            # -------------------------------------------------
            # Process every dataset
            # -------------------------------------------------

            for dataset_id, dataset_forms in forms_by_dataset.items():

                # =================================================
                # 1. DATASET ID
                # =================================================

                permits_data = (
                    dataset_forms["permits"].cleaned_data
                )

                datasetID = permits_data["DatasetID"]

                # =================================================
                # 2. SECURITY LEVEL + DEFAULT GRANULARITY
                # =================================================

                security_data = (
                    dataset_forms["security"].cleaned_data
                )

                SecurityLevel = (
                    security_data["SecurityLevel"]
                )

                default_granularity = (
                    security_data["granularity"]
                )

                # =================================================
                # 3. MAKE SURE DATASET EXISTS
                # =================================================

                if datasetID not in new_permissions:
                    new_permissions[datasetID] = {}

                dataset_permissions = (
                    new_permissions[datasetID]
                )

                # =================================================
                # 4. FIND EXISTING SECURITY-LEVEL CONFIGURATION
                # =================================================

                existing_config = None

                for level in security_levels:

                    if level in dataset_permissions:

                        existing_config = (
                            dataset_permissions[level]
                        )

                        break

                if existing_config is None:
                    existing_config = {}

                # =================================================
                # 5. REMOVE EXISTING SECURITY LEVELS
                # =================================================

                for level in security_levels:
                    dataset_permissions.pop(level, None)

                # =================================================
                # 6. PUT CONFIGURATION UNDER SELECTED SECURITY
                #    LEVEL
                # =================================================

                dataset_permissions[SecurityLevel] = (
                    existing_config
                )

                selected_config = (
                    dataset_permissions[SecurityLevel]
                )

                # =================================================
                # 7. SET DEFAULT GRANULARITY
                # =================================================

                selected_config[
                    "default_entry_types_granularity"
                ] = default_granularity

                # =================================================
                # 8. SET ENTRY-TYPE EXCEPTIONS
                # =================================================

                exceptions = []

                # Get the formset for the selected security level.
                selected_formset = (
                    dataset_forms["granularity"][SecurityLevel]
                )

                for form in selected_formset:

                    # Empty forms can occur because formsets have
                    # extra forms.
                    if not form.cleaned_data:
                        continue

                    # Ignore forms marked for deletion.
                    if form.cleaned_data.get("DELETE"):
                        continue

                    entry_type = (
                        form.cleaned_data["entry_type"]
                    )

                    entry_type_granularity = (
                        form.cleaned_data["granularity"]
                    )

                    exceptions.append(
                        {
                            entry_type: entry_type_granularity
                        }
                    )

                selected_config[
                    "entry_types_exceptions"
                ] = exceptions

            # -----------------------------------------------------
            # SAVE YAML ONCE
            # -----------------------------------------------------

            with open(permissions_file, "w") as outfile:
                yaml.safe_dump(
                    new_permissions,
                    outfile,
                    sort_keys=False,
                )

            return redirect("adminclient:permits")

    # ---------------------------------------------------------
    # GET OR INVALID POST
    # ---------------------------------------------------------

    template = "general_configuration/permits.html"

    return render(
        request,
        template,
        {
            "forms_by_dataset": forms_by_dataset,
            "security_levels": security_levels,
        },
    )



"""
#@login_required
#@permission_required('adminclient.can_see_view', raise_exception=True)
def default_view(request):
    datasets=client["beacon"].datasets
    all_datasets=datasets.find({})
    dataset_list=[]
    form = PermitsForm(request.POST)
    userform = UserPermitsForm(request.POST)
    with open("/home/app/web/beacon/permissions/datasets/datasets_permissions.yml") as f:
        datasets_permissions=yaml.safe_load(f)


    if request.method == 'POST':
        userform = UserPermitsForm(request.POST)
        form = PermitsForm(request.POST)
        if userform.is_valid():
            if 'User' in request.POST:
                datasetID = userform.cleaned_data['DatasetID']
                user_email = userform.cleaned_data['UserEmail']
                userindividual = userform.cleaned_data['userindividualgranularity']
                userbiosample = userform.cleaned_data['userbiosamplegranularity']
                usercohort = userform.cleaned_data['usercohortgranularity']
                userdataset = userform.cleaned_data['userdatasetgranularity']
                useranalysis = userform.cleaned_data['useranalysisgranularity']
                uservariant = userform.cleaned_data['usergenomicVariationgranularity']
                userrun = userform.cleaned_data['userrungranularity']
                usergranularity = userform.cleaned_data['usergranularity']
                
                with open("/home/app/web/beacon/permissions/datasets/datasets_permissions.yml") as f:
                    datasets_permissions=yaml.safe_load(f)

                user_list = datasets_permissions[datasetID]["controlled"]["user-list"]
                new_user_list=[]
                new_user={}
                new_user["user_e-mail"]=user_email
                if usergranularity == '':
                    new_user["default_entry_types_granularity"]='boolean'
                else:
                    new_user["default_entry_types_granularity"]=usergranularity
                new_user["entry_types_exceptions"]=[]
                if userindividual != '-':
                    new_user["entry_types_exceptions"].append({"individual": userindividual})
                if userbiosample != '-':
                    new_user["entry_types_exceptions"].append({"biosample": userbiosample})
                if usercohort != '-':
                    new_user["entry_types_exceptions"].append({"cohort": usercohort})
                if userdataset != '-':
                    new_user["entry_types_exceptions"].append({"dataset": userdataset})
                if useranalysis != '-':
                    new_user["entry_types_exceptions"].append({"analysis": useranalysis})
                if uservariant != '-':
                    new_user["entry_types_exceptions"].append({"genomicVariant": uservariant})
                if userrun != '-':
                    new_user["entry_types_exceptions"].append({"run": userrun})
                if new_user["entry_types_exceptions"] == []:
                    new_user.pop("entry_types_exceptions")
                
                new_user_list.append(new_user)
                
                for user in user_list:
                    if user["user_e-mail"]==user_email:
                        pass
                    else:
                        new_user_list.append(user)
                datasets_permissions[datasetID]["controlled"]["user-list"]=new_user_list
                with open('/home/app/web/beacon/permissions/datasets/datasets_permissions.yml', 'w') as outfile:
                    yaml.dump(datasets_permissions, outfile)
                return redirect("adminclient:permits")
            elif 'Remove' in request.POST:
                datasetID = userform.cleaned_data['DatasetID']
                user_email = userform.cleaned_data['UserEmail']

                new_user_list=[]
                
                with open("/home/app/web/beacon/permissions/datasets/datasets_permissions.yml") as f:
                    datasets_permissions=yaml.safe_load(f)
                user_list = datasets_permissions[datasetID]["controlled"]["user-list"]
                
                for user in user_list:
                    if user["user_e-mail"]==user_email:
                        pass
                    else:
                        new_user_list.append(user)
                datasets_permissions[datasetID]["controlled"]["user-list"]=new_user_list
                with open('/home/app/web/beacon/permissions/datasets/datasets_permissions.yml', 'w') as outfile:
                    yaml.dump(datasets_permissions, outfile)
                return redirect("adminclient:permits")
        elif form.is_valid():
            if 'Save' in request.POST:
                datasetID = userform.cleaned_data['DatasetID']
                individual = form.cleaned_data['individualgranularity']
                biosample = form.cleaned_data['biosamplegranularity']
                cohort = form.cleaned_data['cohortgranularity']
                dataset = form.cleaned_data['datasetgranularity']
                analysis = form.cleaned_data['analysisgranularity']
                variant = form.cleaned_data['genomicVariationgranularity']
                run = form.cleaned_data['rungranularity']
                granularity = form.cleaned_data['granularity']
                SecurityLevel = form.cleaned_data['SecurityLevel']

                if SecurityLevel == '' or SecurityLevel == None:
                    SecurityLevel = 'controlled'
                if granularity == '' or granularity == None:
                    granularity = 'boolean'
            
                with open("/home/app/web/beacon/permissions/datasets/datasets_permissions.yml") as f:
                    datasets_permissions=yaml.safe_load(f)
                new_permissions=datasets_permissions
                try:
                    new_permissions[datasetID][SecurityLevel]=datasets_permissions[datasetID]["public"]
                    if SecurityLevel != 'public':
                        del new_permissions[datasetID]['public']
                except Exception:
                    try:
                        new_permissions[datasetID][SecurityLevel]=datasets_permissions[datasetID]["registered"]
                        if SecurityLevel != 'registered':
                            del new_permissions[datasetID]['registered']
                    except Exception:
                        new_permissions[datasetID][SecurityLevel]=datasets_permissions[datasetID]["controlled"]
                        if SecurityLevel != 'controlled':
                            del new_permissions[datasetID]['controlled']
                new_permissions[datasetID][SecurityLevel]["default_entry_types_granularity"]=granularity
                new_permissions[datasetID][SecurityLevel]["entry_types_exceptions"]=[]
                if individual != '-':
                    new_permissions[datasetID][SecurityLevel]["entry_types_exceptions"].append({"individual": individual})
                if biosample != '-':
                    new_permissions[datasetID][SecurityLevel]["entry_types_exceptions"].append({"biosample": biosample})
                if cohort != '-':
                    new_permissions[datasetID][SecurityLevel]["entry_types_exceptions"].append({"cohort": cohort})
                if dataset != '-':
                    new_permissions[datasetID][SecurityLevel]["entry_types_exceptions"].append({"dataset": dataset})
                if analysis != '-':
                    new_permissions[datasetID][SecurityLevel]["entry_types_exceptions"].append({"analysis": analysis})
                if variant != '-':
                    new_permissions[datasetID][SecurityLevel]["entry_types_exceptions"].append({"genomicVariant": variant})
                if run != '-':
                    new_permissions[datasetID][SecurityLevel]["entry_types_exceptions"].append({"run": run})
                if new_permissions[datasetID][SecurityLevel]["entry_types_exceptions"] == []:
                    new_permissions[datasetID][SecurityLevel].pop("entry_types_exceptions")
                
                datasets_permissions=new_permissions

                with open('/home/app/web/beacon/permissions/datasets/datasets_permissions.yml', 'w') as outfile:
                    yaml.dump(datasets_permissions, outfile)
                return redirect("adminclient:permits")


    for dataset in all_datasets:
        dataset_dict={}
        dataset_dict["name"]=dataset["name"]
        dataset_dict["id"]=dataset["id"]
        for k,v in datasets_permissions.items():
            if k == dataset["id"]:
                for security_level, exceptions in v.items():
                    dataset_dict["security_level"]=security_level
                    for exception, value in exceptions.items():
                        if exception == 'default_entry_types_granularity':
                            dataset_dict["granularity"]=value
                        elif exception == 'entry_types_exceptions':
                            dataset_dict["exceptions"]={}
                            for entry_type in value:
                                for entrytype, granularity in entry_type.items():
                                    dataset_dict["exceptions"][entrytype]=granularity
                        elif exception == 'user-list' and security_level == 'controlled':
                            dataset_dict["users"]=value
        dataset_list.append(dataset_dict)      
    
    context={"datasets_found": dataset_list, "form": form, "userform": userform}
    template = "general_configuration/permits.html"
    return render(request, template, context)
"""