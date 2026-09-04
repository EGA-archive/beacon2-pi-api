from django import forms
from django.forms import BaseFormSet, formset_factory

from adminbackend.forms.filtering_terms import get_all_entry_types


# ============================================================
# COMMON CHOICES
# ============================================================

GRANULARITY_CHOICES = [
    ("-", "-"),
    ("boolean", "Boolean"),
    ("count", "Count"),
    ("record", "Record"),
]


# ============================================================
# DATASET
# ============================================================

class PermitsForm(forms.Form):

    DatasetID = forms.CharField(
        help_text="Dataset ID",
    )


# ============================================================
# SECURITY LEVEL
# ============================================================

class SecurityLevelForm(forms.Form):

    SecurityLevel = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )

    granularity = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=GRANULARITY_CHOICES,
        help_text="Default Granularity",
        required=False,
    )


# ============================================================
# ENTRY TYPE GRANULARITY EXCEPTION
#
# Used by:
#
# public
# registered
#
# Example:
#
# entry_types_exceptions:
#   - individual: record
#   - dataset: count
# ============================================================

class EntryTypeGranularityForm(forms.Form):

    entry_type = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=[],
        help_text="Entry Type",
        required=False,
    )

    granularity = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=GRANULARITY_CHOICES,
        help_text="Granularity for this Entry Type",
        required=False,
    )

    def __init__(
        self,
        *args,
        entry_type_choices=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.fields["entry_type"].choices = (
            entry_type_choices
            if entry_type_choices is not None
            else get_all_entry_types()
        )


# ============================================================
# ENTRY TYPE FORMSET
#
# Used for public / registered security levels.
# ============================================================

class BaseEntryTypeGranularityFormSet(BaseFormSet):

    def clean(self):
        super().clean()

        if any(self.errors):
            return

        entry_types = set()

        for form in self.forms:

            if not form.cleaned_data:
                continue

            if form.cleaned_data.get("DELETE"):
                continue

            entry_type = form.cleaned_data.get(
                "entry_type"
            )

            if not entry_type:
                continue

            if entry_type in entry_types:
                raise forms.ValidationError(
                    "An entry type can only be added once "
                    "for each security level."
                )

            entry_types.add(entry_type)


EntryTypeGranularityFormSet = formset_factory(
    EntryTypeGranularityForm,
    formset=BaseEntryTypeGranularityFormSet,
    extra=1,
    can_delete=True,
)


# ============================================================
# USER PERMISSION
#
# Used by controlled security level.
#
# Example:
#
# - user-e-mail: jane.smith@beacon.ga4gh
#   default_entry_types_granularity: count
#   entry_types_exceptions:
#     - individual: record
# ============================================================

class UserPermissionForm(forms.Form):

    user = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=[],
        help_text="User",
        required=False,
    )

    user_granularity = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=GRANULARITY_CHOICES,
        help_text="Default Granularity for this User",
        required=False,
    )

    def __init__(
        self,
        *args,
        user_choices=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.fields["user"].choices = (
            user_choices
            if user_choices is not None
            else [
                (
                    "john.doe@beacon.ga4gh",
                    "john.doe@beacon.ga4gh",
                ),
                (
                    "jane.smith@beacon.ga4gh",
                    "jane.smith@beacon.ga4gh",
                ),
            ]
        )


# ============================================================
# USER FORMSET
# ============================================================

class BaseUserPermissionFormSet(BaseFormSet):

    def clean(self):
        super().clean()

        if any(self.errors):
            return

        users = set()

        for form in self.forms:

            if not form.cleaned_data:
                continue

            if form.cleaned_data.get("DELETE"):
                continue

            user = form.cleaned_data.get("user")

            if not user:
                continue

            if user in users:
                raise forms.ValidationError(
                    "A user can only be added once "
                    "for each controlled security level."
                )

            users.add(user)


UserPermissionFormSet = formset_factory(
    UserPermissionForm,
    formset=BaseUserPermissionFormSet,
    extra=1,
    can_delete=True,
)


# ============================================================
# USER ENTRY TYPE EXCEPTION
#
# Used inside each user's permissions.
#
# Example:
#
# entry_types_exceptions:
#   - individual: record
# ============================================================

class UserEntryTypeGranularityForm(forms.Form):

    entry_type = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=[],
        help_text="Entry Type",
        required=False,
    )

    granularity = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=GRANULARITY_CHOICES,
        help_text="Granularity for this Entry Type",
        required=False,
    )

    def __init__(
        self,
        *args,
        entry_type_choices=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.fields["entry_type"].choices = (
            entry_type_choices
            if entry_type_choices is not None
            else get_all_entry_types()
        )


# ============================================================
# USER ENTRY TYPE EXCEPTION FORMSET
# ============================================================

class BaseUserEntryTypeGranularityFormSet(BaseFormSet):

    def clean(self):
        super().clean()

        if any(self.errors):
            return

        entry_types = set()

        for form in self.forms:

            if not form.cleaned_data:
                continue

            if form.cleaned_data.get("DELETE"):
                continue

            entry_type = form.cleaned_data.get(
                "entry_type"
            )

            if not entry_type:
                continue

            if entry_type in entry_types:
                raise forms.ValidationError(
                    "An entry type can only be added once "
                    "for each user."
                )

            entry_types.add(entry_type)


UserEntryTypeGranularityFormSet = formset_factory(
    UserEntryTypeGranularityForm,
    formset=BaseUserEntryTypeGranularityFormSet,
    extra=1,
    can_delete=True,
)
