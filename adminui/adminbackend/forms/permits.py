from django import forms
from django.forms import BaseFormSet, formset_factory
from adminbackend.forms.filtering_terms import get_all_entry_types


class PermitsForm(forms.Form):
    DatasetID = forms.CharField(
        help_text="Dataset ID"
    )


class SecurityLevelForm(forms.Form):
    security_level_choices = [
        ("public", "Public"),
        ("registered", "Registered"),
        ("controlled", "Controlled"),
    ]

    SecurityLevel = forms.ChoiceField(
        choices=security_level_choices,
        widget=forms.RadioSelect,
        help_text="Security Level",
        required=True,
    )

    granularity_choices = [
        ("-", "-"),
        ("boolean", "Boolean"),
        ("count", "Count"),
        ("record", "Record"),
    ]

    granularity = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=granularity_choices,
        help_text="Default Granularity",
        required=True,
    )

    def __init__(self, *args, dataset_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.dataset_id = dataset_id


class GranularityForm(forms.Form):
    entry_type = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=[],
        help_text="Entry Type",
        required=True,
    )

    granularity_choices = [
        ("-", "-"),
        ("boolean", "Boolean"),
        ("count", "Count"),
        ("record", "Record"),
    ]

    granularity = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=granularity_choices,
        help_text="Granularity for this Entry Type",
        required=True,
    )

    def __init__(
        self,
        *args,
        dataset_id=None,
        security_level=None,
        entry_type_choices=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.dataset_id = dataset_id
        self.security_level = security_level

        self.fields["entry_type"].choices = (
            entry_type_choices
            if entry_type_choices is not None
            else get_all_entry_types()
        )
        
class BaseGranularityFormSet(BaseFormSet):

    def clean(self):
        super().clean()

        entry_types = set()

        for form in self.forms:

            if not form.cleaned_data:
                continue

            if form.cleaned_data.get("DELETE"):
                continue

            entry_type = form.cleaned_data.get("entry_type")

            if not entry_type:
                continue

            if entry_type in entry_types:
                raise forms.ValidationError(
                    "An entry type can only be added once "
                    "for each security level."
                )

            entry_types.add(entry_type)



GranularityFormSet = formset_factory(
    GranularityForm,
    formset=BaseGranularityFormSet,
    extra=1,
    can_delete=True,
)