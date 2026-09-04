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


import copy

from django.contrib import messages




SECURITY_LEVELS = (
    "public",
    "registered",
    "controlled",
)

PERMISSIONS_FILE = (
    "/home/app/web/beacon/permissions/datasets/"
    "datasets_permissions.yml"
)


def default_view(request):

    datasets = client["beacon"].datasets

    try:
        with open(PERMISSIONS_FILE) as f:
            datasets_permissions = (
                yaml.safe_load(f) or {}
            )
    except FileNotFoundError:
        datasets_permissions = {}

    # ---------------------------------------------------------
    # Get datasets
    # ---------------------------------------------------------

    dataset_ids = [k for k,v in datasets_permissions.items()]

    # ---------------------------------------------------------
    # Load existing permissions
    # ---------------------------------------------------------



    forms_by_dataset = {}

    # =========================================================
    # BUILD FORMS
    # =========================================================

    for dataset_index, dataset_id in enumerate(
        dataset_ids
    ):

        dataset_prefix = (
            f"dataset-{dataset_index}"
        )

        # -----------------------------------------------------
        # Existing configuration for this dataset
        # -----------------------------------------------------

        existing_dataset = (
            datasets_permissions.get(
                dataset_id,
                {}
            )
        )

        # =====================================================
        # Dataset ID form
        # =====================================================

        permits_form = PermitsForm(
            request.POST or None,
            prefix=f"{dataset_prefix}-permits",
            initial={
                "DatasetID": dataset_id,
            },
        )

        # =====================================================
        # Security level forms
        # =====================================================

        security_forms = {}

        granularity_formsets = {}

        for security_level in SECURITY_LEVELS:

            security_prefix = (
                f"{dataset_prefix}-"
                f"security-{security_level}"
            )

            granularity_prefix = (
                f"{dataset_prefix}-"
                f"granularity-{security_level}"
            )

            existing_config = (
                existing_dataset.get(
                    security_level
                )
            )

            # -------------------------------------------------
            # Determine whether this security level exists
            # -------------------------------------------------

            if existing_config is not None:

                default_granularity = (
                    existing_config.get(
                        "default_entry_types_granularity",
                        "-"
                    )
                )

                security_initial = {
                    "SecurityLevel": security_level,
                    "granularity": default_granularity,
                }

            else:

                security_initial = {
                    "SecurityLevel": security_level,
                    "granularity": "-",
                }

            # -------------------------------------------------
            # Security level form
            # -------------------------------------------------

            security_form = SecurityLevelForm(
                request.POST or None,
                prefix=security_prefix,
                initial=security_initial,
            )


            security_forms[security_level] = (
                security_form
            )

            # -------------------------------------------------
            # Existing entry type exceptions
            # -------------------------------------------------

            initial_exceptions = []

            if existing_config:

                existing_exceptions = (
                    existing_config.get(
                        "entry_types_exceptions",
                        []
                    )
                )

                for exception in existing_exceptions:

                    if not isinstance(
                        exception,
                        dict
                    ):
                        continue

                    for entry_type, granularity in (
                        exception.items()
                    ):

                        initial_exceptions.append({
                            "entry_type": entry_type,
                            "granularity": granularity,
                        })

            # -------------------------------------------------
            # Granularity formset
            # -------------------------------------------------

            if request.method == "POST":

                granularity_formset = (
                    GranularityFormSet(
                        request.POST,
                        prefix=granularity_prefix,
                        form_kwargs={
                            "dataset_id": dataset_id,
                            "security_level": security_level,
                        },
                    )
                )

            else:

                granularity_formset = (
                    GranularityFormSet(
                        prefix=granularity_prefix,
                        initial=initial_exceptions,
                        form_kwargs={
                            "dataset_id": dataset_id,
                            "security_level": security_level,
                        },
                    )
                )

            granularity_formsets[
                security_level
            ] = granularity_formset

        # =====================================================
        # Store forms
        # =====================================================
        existing_security_levels = [
    level
    for level in SECURITY_LEVELS
    if level in existing_dataset
]

        forms_by_dataset[dataset_id] = {
            "permits": permits_form,
            "security": security_forms,
            "granularity": granularity_formsets,
            "existing_security_levels": existing_security_levels,
        }


    # =========================================================
    # POST
    # =========================================================

    if request.method == "POST":

        all_valid = True

        # -----------------------------------------------------
        # Validate all datasets
        # -----------------------------------------------------

        for dataset_id, dataset_forms in (
            forms_by_dataset.items()
        ):

            # ================================================
            # Permits
            # ================================================

            permits_form = (
                dataset_forms["permits"]
            )

            if not permits_form.is_valid():
                all_valid = False

            # ================================================
            # Security levels
            # ================================================

            for security_level in SECURITY_LEVELS:

                security_form = (
                    dataset_forms["security"][
                        security_level
                    ]
                )

                if not security_form.is_valid():
                    all_valid = False

                # ============================================
                # Granularity formset
                # ============================================

                granularity_formset = (
                    dataset_forms["granularity"][
                        security_level
                    ]
                )

                if not granularity_formset.is_valid():
                    all_valid = False

        # =====================================================
        # SAVE
        # =====================================================

        if all_valid:

            new_permissions = copy.deepcopy(
                datasets_permissions
            )

            for dataset_id, dataset_forms in (
                forms_by_dataset.items()
            ):

                # =================================================
                # Dataset ID
                # =================================================

                datasetID = (
                    dataset_forms[
                        "permits"
                    ].cleaned_data[
                        "DatasetID"
                    ]
                )

                # =================================================
                # Make sure dataset exists
                # =================================================

                if datasetID not in new_permissions:

                    new_permissions[
                        datasetID
                    ] = {}

                dataset_permissions = (
                    new_permissions[
                        datasetID
                    ]
                )

                # =================================================
                # Rebuild security-level configuration
                # =================================================

                for security_level in SECURITY_LEVELS:

                    security_form = (
                        dataset_forms[
                            "security"
                        ][security_level]
                    )

                    granularity_formset = (
                        dataset_forms[
                            "granularity"
                        ][security_level]
                    )

                    # ------------------------------------------------
                    # Determine if security level is enabled.
                    #
                    # We use the checkbox submitted by JavaScript.
                    # ------------------------------------------------

                    enabled_key = (
                        f"enabled-{datasetID}-"
                        f"{security_level}"
                    )

                    enabled = request.POST.get(
                        enabled_key
                    )

                    # ------------------------------------------------
                    # If not enabled, remove it.
                    # ------------------------------------------------

                    if not enabled:

                        dataset_permissions.pop(
                            security_level,
                            None
                        )

                        continue

                    # ------------------------------------------------
                    # Security level
                    # ------------------------------------------------

                    default_granularity = (
                        security_form.cleaned_data[
                            "granularity"
                        ]
                    )

                    # ------------------------------------------------
                    # Entry type exceptions
                    # ------------------------------------------------

                    exceptions = []

                    for form in granularity_formset:

                        if not form.cleaned_data:
                            continue

                        if form.cleaned_data.get(
                            "DELETE"
                        ):
                            continue

                        entry_type = (
                            form.cleaned_data[
                                "entry_type"
                            ]
                        )

                        granularity = (
                            form.cleaned_data[
                                "granularity"
                            ]
                        )

                        exceptions.append({
                            entry_type:
                                granularity
                        })

                    # ------------------------------------------------
                    # Save security-level configuration
                    # ------------------------------------------------

                    dataset_permissions[
                        security_level
                    ] = {
                        "default_entry_types_granularity":
                            default_granularity,

                        "entry_types_exceptions":
                            exceptions,
                    }

            # =====================================================
            # Save YAML
            # =====================================================

            with open(
                PERMISSIONS_FILE,
                "w"
            ) as outfile:

                yaml.safe_dump(
                    new_permissions,
                    outfile,
                    sort_keys=False,
                )

            messages.success(
                request,
                "Permissions saved successfully."
            )

            return redirect(
                "adminclient:permits"
            )

    # =========================================================
    # GET / invalid POST
    # =========================================================

    return render(
        request,
        "general_configuration/permits.html",
        {
            "forms_by_dataset": forms_by_dataset,
            "security_levels": SECURITY_LEVELS,
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