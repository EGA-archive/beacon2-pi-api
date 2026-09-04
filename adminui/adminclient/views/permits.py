from django.contrib import messages
from django.shortcuts import redirect, render

import copy
import yaml

from beacon.connections.mongo.__init__ import client

from adminbackend.forms.permits import (
    PermitsForm,
    SecurityLevelForm,
    EntryTypeGranularityFormSet,
    UserPermissionFormSet,
    UserEntryTypeGranularityFormSet,
)


SECURITY_LEVELS = (
    "public",
    "registered",
    "controlled",
)

PERMISSIONS_FILE = (
    "/home/app/web/beacon/permissions/datasets/"
    "datasets_permissions.yml"
)


# ============================================================
# HELPERS
# ============================================================

def _load_permissions():
    try:
        with open(PERMISSIONS_FILE) as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {}


def _get_users():
    return [
        (
            "jane.smith@beacon.ga4gh",
            "jane.smith@beacon.ga4gh",
        ),
        (
            "john.doe@beacon.ga4gh",
            "john.doe@beacon.ga4gh",
        ),
    ]


def _get_entry_types():
    return None


def _build_entry_type_initial(exceptions):
    initial = []

    for exception in exceptions or []:
        if not isinstance(exception, dict):
            continue

        for entry_type, granularity in exception.items():
            initial.append({
                "entry_type": entry_type,
                "granularity": granularity,
            })

    return initial


def _build_user_initial(user_list):
    initial = []

    for user_config in user_list or []:
        if not isinstance(user_config, dict):
            continue

        email = user_config.get("user_e-mail")

        if not email:
            continue

        initial.append({
            "user": email,
            "user_granularity": user_config.get(
                "default_entry_types_granularity",
                "-",
            ),
        })

    return initial






def _get_user_entry_type_initial(user_config):
    if not isinstance(user_config, dict):
        return []

    return _build_entry_type_initial(
        user_config.get(
            "entry_types_exceptions",
            [],
        )
    )


def _get_existing_user_config(user_list, email):
    for user_config in user_list or []:
        if not isinstance(user_config, dict):
            continue

        if user_config.get("user_e-mail") == email:
            return user_config

    return {}


# ============================================================
# BUILD USER ENTRY TYPE FORMSETS
# ============================================================

def _build_user_entry_type_formsets(
    request,
    user_formset,
    user_list,
    user_prefix,
    entry_type_choices,
):
    """
    Build one nested formset for every user form.

    IMPORTANT:
    We build a nested formset for EVERY user form index,
    regardless of whether the user has been filled in yet.

    This guarantees that the management form exists in the
    template for every possible user row.
    """

    nested_formsets = {}

    for user_index, user_form in enumerate(user_formset):

        user_entry_prefix = (
            f"{user_prefix}-"
            f"user-{user_index}-"
            f"entry-types"
        )

        # -----------------------------------------------
        # Determine initial data.
        #
        # For an existing GET form, use the existing
        # user's exceptions.
        #
        # For a POST, do NOT use cleaned_data here.
        # The POST itself supplies the values.
        # -----------------------------------------------

        initial = []

        if request.method != "POST":

            if user_index < len(user_list):

                user_config = user_list[user_index]

                initial = _get_user_entry_type_initial(
                    user_config
                )

        # -----------------------------------------------
        # Build nested formset
        # -----------------------------------------------

        nested_formset = (
            UserEntryTypeGranularityFormSet(
                request.POST or None,
                prefix=user_entry_prefix,
                initial=initial,
                form_kwargs={
                    "entry_type_choices":
                        entry_type_choices,
                },
            )
        )

        nested_formsets[user_index] = nested_formset

    return nested_formsets


# ============================================================
# VIEW
# ============================================================

def default_view(request):

    datasets = client["beacon"].datasets

    datasets_permissions = _load_permissions()

    dataset_ids = list(
        datasets_permissions.keys()
    )

    user_choices = _get_users()
    entry_type_choices = _get_entry_types()

    forms_by_dataset = {}

    # ========================================================
    # BUILD FORMS
    # ========================================================

    for dataset_index, dataset_id in enumerate(
        dataset_ids
    ):

        dataset_prefix = (
            f"dataset-{dataset_index}"
        )

        existing_dataset = (
            datasets_permissions.get(
                dataset_id,
                {},
            )
        )

        # ====================================================
        # DATASET FORM
        # ====================================================

        permits_form = PermitsForm(
            request.POST or None,
            prefix=f"{dataset_prefix}-permits",
            initial={
                "DatasetID": dataset_id,
            },
        )

        security_forms = {}
        entry_type_formsets = {}
        user_formsets = {}
        user_entry_type_formsets = {}

        # ====================================================
        # SECURITY LEVELS
        # ====================================================

        for security_level in SECURITY_LEVELS:

            security_prefix = (
                f"{dataset_prefix}-"
                f"security-{security_level}"
            )

            entry_type_prefix = (
                f"{dataset_prefix}-"
                f"entry-types-{security_level}"
            )

            user_prefix = (
                f"{dataset_prefix}-"
                f"users-{security_level}"
            )

            existing_config = (
                existing_dataset.get(
                    security_level
                )
            )

            # =================================================
            # SECURITY FORM INITIAL
            # =================================================

            if security_level == "controlled":

                security_initial = {
                    "SecurityLevel": security_level,
                }

            else:

                if existing_config:

                    security_initial = {
                        "SecurityLevel": security_level,
                        "granularity": existing_config.get(
                            "default_entry_types_granularity",
                            "-",
                        ),
                    }

                else:

                    security_initial = {
                        "SecurityLevel": security_level,
                        "granularity": "-",
                    }


            # =================================================
            # SECURITY FORM
            # =================================================

            security_form = SecurityLevelForm(
                request.POST or None,
                prefix=security_prefix,
                initial=security_initial,
            )

            security_forms[
                security_level
            ] = security_form

            # =================================================
            # PUBLIC / REGISTERED
            # =================================================

            if security_level != "controlled":

                existing_exceptions = []

                if existing_config:

                    existing_exceptions = (
                        existing_config.get(
                            "entry_types_exceptions",
                            [],
                        )
                    )

                entry_type_initial = (
                    _build_entry_type_initial(
                        existing_exceptions
                    )
                )

                entry_type_formset = (
                    EntryTypeGranularityFormSet(
                        request.POST or None,
                        prefix=entry_type_prefix,
                        initial=entry_type_initial,
                        form_kwargs={
                            "entry_type_choices":
                                entry_type_choices,
                        },
                    )
                )

                entry_type_formsets[
                    security_level
                ] = entry_type_formset

                user_formsets[
                    security_level
                ] = None

                user_entry_type_formsets[
                    security_level
                ] = {}

            # =================================================
            # CONTROLLED
            # =================================================

            else:

                user_list = []

                if existing_config:

                    user_list = (
                        existing_config.get(
                            "user-list",
                            [],
                        )
                    )

                user_initial = (
                    _build_user_initial(
                        user_list
                    )
                )

                # ---------------------------------------------
                # User formset
                # ---------------------------------------------

                user_formset = (
                    UserPermissionFormSet(
                        request.POST or None,
                        prefix=user_prefix,
                        initial=user_initial,
                        form_kwargs={
                            "user_choices":
                                user_choices,
                        },
                    )
                )

                user_formsets[
                    security_level
                ] = user_formset

                entry_type_formsets[
                    security_level
                ] = None

                # ---------------------------------------------
                # ALWAYS BUILD ALL NESTED FORMSETS
                # ---------------------------------------------

                user_entry_type_formsets[
                    security_level
                ] = _build_user_entry_type_formsets(
                    request=request,
                    user_formset=user_formset,
                    user_list=user_list,
                    user_prefix=user_prefix,
                    entry_type_choices=entry_type_choices,
                )

        # ====================================================
        # EXISTING SECURITY LEVELS
        # ====================================================

        existing_security_levels = [
            level
            for level in SECURITY_LEVELS
            if level in existing_dataset
        ]

        # ====================================================
        # STORE FORMS
        # ====================================================

        forms_by_dataset[
            dataset_id
        ] = {
            "permits":
                permits_form,

            "security":
                security_forms,

            "entry_types":
                entry_type_formsets,

            "users":
                user_formsets,

            "user_entry_types":
                user_entry_type_formsets,

            "existing_security_levels":
                existing_security_levels,
        }

    # ========================================================
    # POST
    # ========================================================

    if request.method == "POST":

        all_valid = True

        # ====================================================
        # VALIDATE EVERYTHING
        # ====================================================

        for dataset_id, dataset_forms in (
            forms_by_dataset.items()
        ):

            # ------------------------------------------------
            # Dataset
            # ------------------------------------------------

            permits_form = (
                dataset_forms[
                    "permits"
                ]
            )

            if not permits_form.is_valid():
                all_valid = False

            # ------------------------------------------------
            # Security levels
            # ------------------------------------------------

            for security_level in SECURITY_LEVELS:

                security_form = (
                    dataset_forms[
                        "security"
                    ][security_level]
                )

                if not security_form.is_valid():
                    all_valid = False

                # ============================================
                # PUBLIC / REGISTERED
                # ============================================

                if security_level != "controlled":

                    formset = (
                        dataset_forms[
                            "entry_types"
                        ][security_level]
                    )

                    if not formset.is_valid():
                        all_valid = False

                # ============================================
                # CONTROLLED
                # ============================================

                else:

                    user_formset = (
                        dataset_forms[
                            "users"
                        ][security_level]
                    )

                    if not user_formset.is_valid():
                        all_valid = False

                    nested_formsets = (
                        dataset_forms[
                            "user_entry_types"
                        ][security_level]
                    )

                    # ----------------------------------------
                    # Validate EVERY nested formset.
                    #
                    # Because the view now creates a nested
                    # formset for every user index, Django
                    # will always have its ManagementForm.
                    # ----------------------------------------

                    for user_index, user_entry_formset in (
                        nested_formsets.items()
                    ):

                        if not user_entry_formset.is_valid():
                            all_valid = False

        # ====================================================
        # SAVE
        # ====================================================

        if all_valid:

            new_permissions = copy.deepcopy(
                datasets_permissions
            )

            # =================================================
            # DATASETS
            # =================================================

            for original_dataset_id, dataset_forms in (
                forms_by_dataset.items()
            ):

                permits_form = (
                    dataset_forms[
                        "permits"
                    ]
                )

                dataset_id = (
                    permits_form.cleaned_data[
                        "DatasetID"
                    ]
                )

                if dataset_id not in new_permissions:

                    new_permissions[
                        dataset_id
                    ] = {}

                dataset_permissions = (
                    new_permissions[
                        dataset_id
                    ]
                )

                # =============================================
                # SECURITY LEVELS
                # =============================================

                for security_level in SECURITY_LEVELS:

                    # -----------------------------------------
                    # Enabled checkbox
                    # -----------------------------------------

                    enabled_key = (
                        f"enabled-{original_dataset_id}-"
                        f"{security_level}"
                    )

                    enabled = request.POST.get(
                        enabled_key
                    )

                    if not enabled:

                        dataset_permissions.pop(
                            security_level,
                            None
                        )

                        continue

                    security_form = (
                        dataset_forms[
                            "security"
                        ][security_level]
                    )

                    # =========================================
                    # PUBLIC / REGISTERED
                    # =========================================

                    if security_level != "controlled":

                        default_granularity = (
                            security_form.cleaned_data.get(
                                "granularity",
                                "-",
                            )
                        )

                        formset = (
                            dataset_forms[
                                "entry_types"
                            ][security_level]
                        )

                        exceptions = []

                        for form in formset:

                            if not form.cleaned_data:
                                continue

                            if form.cleaned_data.get(
                                "DELETE"
                            ):
                                continue

                            entry_type = (
                                form.cleaned_data.get(
                                    "entry_type"
                                )
                            )

                            granularity = (
                                form.cleaned_data.get(
                                    "granularity"
                                )
                            )

                            if not entry_type:
                                continue

                            exceptions.append({
                                entry_type:
                                    granularity
                            })

                        dataset_permissions[
                            security_level
                        ] = {
                            "default_entry_types_granularity":
                                default_granularity,

                            "entry_types_exceptions":
                                exceptions,
                        }

                    # =========================================
                    # CONTROLLED
                    # =========================================

                    else:

                        user_formset = (
                            dataset_forms[
                                "users"
                            ][security_level]
                        )

                        nested_formsets = (
                            dataset_forms[
                                "user_entry_types"
                            ][security_level]
                        )

                        user_list = []

                        # -------------------------------------
                        # USERS
                        # -------------------------------------

                        for user_index, user_form in enumerate(
                            user_formset
                        ):

                            if not user_form.cleaned_data:
                                continue

                            if user_form.cleaned_data.get(
                                "DELETE"
                            ):
                                continue

                            email = (
                                user_form.cleaned_data.get(
                                    "user"
                                )
                            )

                            user_granularity = user_form.cleaned_data.get(
                                "user_granularity",
                                "-",
                            )


                            if not email:
                                continue


                            # ---------------------------------
                            # Nested exceptions
                            # ---------------------------------

                            user_entry_formset = (
                                nested_formsets.get(
                                    user_index
                                )
                            )

                            user_exceptions = []

                            if user_entry_formset:

                                for exception_form in (
                                    user_entry_formset
                                ):

                                    if not exception_form.cleaned_data:
                                        continue

                                    if exception_form.cleaned_data.get(
                                        "DELETE"
                                    ):
                                        continue

                                    entry_type = (
                                        exception_form.cleaned_data.get(
                                            "entry_type"
                                        )
                                    )

                                    granularity = (
                                        exception_form.cleaned_data.get(
                                            "granularity"
                                        )
                                    )



                                    if not entry_type:
                                        continue

                                    user_exceptions.append({
                                        entry_type:
                                            granularity
                                    })

                            # ---------------------------------
                            # Build YAML user
                            # ---------------------------------

                            user_list.append({
                                "user-e-mail": email,
                                "default_entry_types_granularity": user_granularity,
                                "entry_types_exceptions": user_exceptions,
                            })


                        # -------------------------------------
                        # Controlled configuration
                        # -------------------------------------

                        dataset_permissions[
                            security_level
                        ] = {
                            "user-list":
                                user_list,
                        }

            # =================================================
            # WRITE YAML
            # =================================================

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
                "Permissions saved successfully.",
            )

            return redirect(
                "adminclient:permits"
            )

    # ========================================================
    # GET / INVALID POST
    # ========================================================

    return render(
        request,
        "general_configuration/permits.html",
        {
            "forms_by_dataset":
                forms_by_dataset,

            "security_levels":
                SECURITY_LEVELS,
        },
    )