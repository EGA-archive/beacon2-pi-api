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
            initial.append(
                {
                    "entry_type": entry_type,
                    "granularity": granularity,
                }
            )
    return initial


def _build_user_initial(user_list):
    initial = []
    for user_config in user_list or []:
        if not isinstance(user_config, dict):
            continue
        email = user_config.get("user-e-mail")
        if not email:
            continue
        initial.append(
            {
                "user": email,
                "user_granularity": user_config.get(
                    "default_entry_types_granularity",
                    "-",
                ),
            }
        )
    return initial


def _get_user_entry_type_initial(user_config):
    exceptions = (
        user_config.get(
            "entry_types_exceptions",
            [],
        )
        if isinstance(user_config, dict)
        else []
    )
    return _build_entry_type_initial(exceptions)


def default_view(request):
    datasets = client["beacon"].datasets
    datasets_permissions = _load_permissions()
    dataset_ids = list(datasets_permissions.keys())
    user_choices = _get_users()
    entry_type_choices = _get_entry_types()
    forms_by_dataset = {}
    # =========================================================
    # BUILD FORMS
    # =========================================================

    for dataset_index, dataset_id in enumerate(dataset_ids):
        dataset_prefix = f"dataset-{dataset_index}"
        existing_dataset = (
            datasets_permissions.get(
                dataset_id,
                {},
            )
        )
        # =====================================================
        # DATASET FORM
        # =====================================================
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

        # =====================================================
        # SECURITY LEVELS
        # =====================================================

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
            existing_config = existing_dataset.get(
                security_level
            )
            # =================================================
            # SECURITY FORM
            # =================================================

            if existing_config:
                security_initial = {
                    "SecurityLevel": security_level,
                    "granularity": existing_config.get(
                        "default_entry_types_granularity",
                        "-",
                    ),
                    "user_granularity": existing_config.get(
                        "default_entry_types_granularity",
                        "-",
                    ),
                }

            else:
                security_initial = {
                    "SecurityLevel": security_level,
                    "granularity": "-",
                    "user_granularity": "-",
                }
            security_form = SecurityLevelForm(
                request.POST or None,
                prefix=security_prefix,
                initial=security_initial,
            )
            security_forms[security_level] = security_form

            # =================================================
            # PUBLIC / REGISTERED ENTRY TYPE FORMSET
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
            # CONTROLLED USERS
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
                user_initial = _build_user_initial(
                    user_list
                )
                user_formset = UserPermissionFormSet(
                    request.POST or None,
                    prefix=user_prefix,
                    initial=user_initial,
                    form_kwargs={
                        "user_choices": user_choices,
                    },
                )
                user_formsets[
                    security_level
                ] = user_formset
                entry_type_formsets[
                    security_level
                ] = None
                user_entry_type_formsets[
                    security_level
                ] = {}

                # -------------------------------------------------
                # Build an entry-type formset for every existing
                # user. These are keyed by user email.
                # -------------------------------------------------

                if request.method == "POST":
                    submitted_users = []
                    for form in user_formset:
                        user_value = request.POST.get(
                            form.add_prefix("user")
                        )
                        delete_value = request.POST.get(
                            form.add_prefix("DELETE")
                        )
                        if delete_value:
                            continue
                        if user_value:
                            submitted_users.append(user_value)
                    existing_user_configs = {
                        item.get("user-e-mail"): item
                        for item in user_list
                        if isinstance(item, dict)
                        and item.get("user-e-mail")
                    }
                    for user_index, email in enumerate(
                        submitted_users
                    ):
                        user_entry_prefix = (
                            f"{user_prefix}-"
                            f"user-{user_index}-"
                            f"entry-types"
                        )
                        existing_user_config = (
                            existing_user_configs.get(
                                email,
                                {},
                            )
                        )
                        user_exception_initial = (
                            _get_user_entry_type_initial(
                                existing_user_config
                            )
                        )
                        user_entry_formset = (
                            UserEntryTypeGranularityFormSet(
                                request.POST,
                                prefix=user_entry_prefix,
                                initial=user_exception_initial,
                                form_kwargs={
                                    "entry_type_choices":
                                        entry_type_choices,
                                },
                            )
                        )
                        user_entry_type_formsets[
                            security_level
                        ][email] = user_entry_formset
                else:
                    for user_index, user_config in enumerate(
                        user_list
                    ):
                        if not isinstance(
                            user_config,
                            dict,
                        ):
                            continue

                        email = user_config.get(
                            "user-e-mail"
                        )

                        if not email:
                            continue

                        user_entry_prefix = (
                            f"{user_prefix}-"
                            f"user-{user_index}-"
                            f"entry-types"
                        )

                        user_exception_initial = (
                            _get_user_entry_type_initial(
                                user_config
                            )
                        )

                        user_entry_formset = (
                            UserEntryTypeGranularityFormSet(
                                prefix=user_entry_prefix,
                                initial=user_exception_initial,
                                form_kwargs={
                                    "entry_type_choices":
                                        entry_type_choices,
                                },
                            )
                        )

                        user_entry_type_formsets[
                            security_level
                        ][email] = (
                            user_entry_formset
                        )

        # =====================================================
        # STORE EVERYTHING FOR TEMPLATE
        # =====================================================

        existing_security_levels = [
            level
            for level in SECURITY_LEVELS
            if level in existing_dataset
        ]

        forms_by_dataset[dataset_id] = {
            "permits": permits_form,
            "security": security_forms,
            "entry_types": entry_type_formsets,
            "users": user_formsets,
            "user_entry_types": user_entry_type_formsets,
            "existing_security_levels":
                existing_security_levels,
        }

    # =========================================================
    # POST
    # =========================================================

    if request.method == "POST":

        all_valid = True

        # =====================================================
        # VALIDATE ALL DATASETS
        # =====================================================

        for dataset_id, dataset_forms in (
            forms_by_dataset.items()
        ):

            # -------------------------------------------------
            # Dataset
            # -------------------------------------------------

            permits_form = dataset_forms["permits"]

            if not permits_form.is_valid():
                all_valid = False

            # -------------------------------------------------
            # Security levels
            # -------------------------------------------------

            for security_level in SECURITY_LEVELS:

                security_form = (
                    dataset_forms[
                        "security"
                    ][security_level]
                )

                if not security_form.is_valid():
                    all_valid = False

                # -------------------------------------------------
                # Public / registered
                # -------------------------------------------------

                if security_level != "controlled":

                    formset = (
                        dataset_forms[
                            "entry_types"
                        ][security_level]
                    )

                    if not formset.is_valid():
                        all_valid = False

                # -------------------------------------------------
                # Controlled
                # -------------------------------------------------

                else:

                    user_formset = (
                        dataset_forms[
                            "users"
                        ][security_level]
                    )

                    if not user_formset.is_valid():
                        all_valid = False

                    user_entry_formsets = (
                        dataset_forms[
                            "user_entry_types"
                        ][security_level]
                    )

                    for user_entry_formset in (
                        user_entry_formsets.values()
                    ):

                        if not user_entry_formset.is_valid():
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

                dataset_id = (
                    dataset_forms[
                        "permits"
                    ].cleaned_data[
                        "DatasetID"
                    ]
                )

                if dataset_id not in new_permissions:
                    new_permissions[dataset_id] = {}

                dataset_permissions = (
                    new_permissions[dataset_id]
                )

                # =================================================
                # SECURITY LEVELS
                # =================================================

                for security_level in SECURITY_LEVELS:

                    enabled_key = (
                        f"enabled-{dataset_id}-"
                        f"{security_level}"
                    )

                    enabled = request.POST.get(
                        enabled_key
                    )

                    # -------------------------------------------------
                    # Disabled
                    # -------------------------------------------------

                    if not enabled:

                        dataset_permissions.pop(
                            security_level,
                            None,
                        )

                        continue

                    security_form = (
                        dataset_forms[
                            "security"
                        ][security_level]
                    )

                    # =================================================
                    # PUBLIC / REGISTERED
                    # =================================================

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

                            exceptions.append(
                                {
                                    entry_type:
                                        granularity
                                }
                            )

                        dataset_permissions[
                            security_level
                        ] = {
                            "default_entry_types_granularity":
                                default_granularity,
                            "entry_types_exceptions":
                                exceptions,
                        }

                    # =================================================
                    # CONTROLLED
                    # =================================================

                    else:

                        user_formset = (
                            dataset_forms[
                                "users"
                            ][security_level]
                        )

                        user_entry_formsets = (
                            dataset_forms[
                                "user_entry_types"
                            ][security_level]
                        )

                        user_list = []

                        # -------------------------------------------------
                        # Build user configuration
                        # -------------------------------------------------

                        for user_index, form in enumerate(
                            user_formset
                        ):

                            if not form.cleaned_data:
                                continue

                            if form.cleaned_data.get(
                                "DELETE"
                            ):
                                continue

                            email = (
                                form.cleaned_data.get(
                                    "user"
                                )
                            )

                            if not email:
                                continue

                            default_granularity = (
                                form.cleaned_data.get(
                                    "user_granularity",
                                    "-",
                                )
                            )

                            # -------------------------------------------------
                            # Find corresponding user exception formset.
                            # The POST prefix is based on the user's position
                            # in the user formset.
                            # -------------------------------------------------

                            user_entry_prefix = (
                                f"dataset-"
                                f"{list(forms_by_dataset.keys()).index(dataset_id)}-"
                                f"users-{security_level}-"
                                f"user-{user_index}-entry-types"
                            )

                            user_entry_formset = None

                            for candidate_formset in (
                                user_entry_formsets.values()
                            ):

                                if (
                                    candidate_formset.prefix
                                    == user_entry_prefix
                                ):
                                    user_entry_formset = (
                                        candidate_formset
                                    )
                                    break

                            # -------------------------------------------------
                            # Entry type exceptions for this user
                            # -------------------------------------------------

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

                                    user_exceptions.append(
                                        {
                                            entry_type:
                                                granularity
                                        }
                                    )

                            user_list.append(
                                {
                                    "user-e-mail": email,
                                    "default_entry_types_granularity":
                                        default_granularity,
                                    "entry_types_exceptions":
                                        user_exceptions,
                                }
                            )

                        dataset_permissions[
                            security_level
                        ] = {
                            "user-list": user_list,
                        }

            # =====================================================
            # WRITE YAML
            # =====================================================

            with open(
                PERMISSIONS_FILE,
                "w"
            ) as outfile:
                print(new_permissions, flush=True)

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
        else:
            print('not_valid', flush=True)

    # =========================================================
    # RENDER
    # =========================================================

    return render(
        request,
        "general_configuration/permits.html",
        {
            "forms_by_dataset": forms_by_dataset,
            "security_levels": SECURITY_LEVELS,
        },
    )
