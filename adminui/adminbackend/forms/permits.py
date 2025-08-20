from django import forms
import yaml
import logging

LOG = logging.getLogger(__name__)
fmt = '%(levelname)s - %(asctime)s - %(message)s'
formatter = logging.Formatter(fmt)
sh = logging.StreamHandler()
sh.setLevel('NOTSET')
sh.setFormatter(formatter)
LOG.addHandler(sh)

def formatting_field(self, line):
    linestring=str(line)
    splitted_line=linestring.split("=")
    placeholder=splitted_line[1].replace('"', '')
    placeholder=str(placeholder)
    placeholder=placeholder.strip()
    if "#" in placeholder:
        placeholder_def=placeholder.split('#')
        placeholder=placeholder_def[0]
        placeholder=placeholder.strip()
    if placeholder.startswith("'"):
        placeholder=placeholder[1:]
    if placeholder.endswith("'"):
        placeholder=placeholder[0:-1]
    return placeholder


class PermitsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(PermitsForm, self).__init__(*args, **kwargs)
        # assign a (computed, I assume) default value to the choice field
        self.fields['DatasetID'].widget.attrs['readonly'] = True
        self.fields['User'].widget.attrs['readonly'] = True

    DatasetID= forms.CharField(help_text='DatasetId')
    User= forms.EmailField(help_text='User')
    granularity_choices = [
        ('boolean', 'Boolean'),
        ('count', 'Count'),
        ('record', 'Record'),
    ]
    granularity= forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=granularity_choices
    )
    security_level_choices = [
        ('public', 'Public'),
        ('registered', 'Registered'),
        ('controlled', 'Controlled'),
    ]
    SecurityLevel= forms.MultipleChoiceField(
        choices=security_level_choices, 
        widget=forms.CheckboxSelectMultiple
    )
    individuals= forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=granularity_choices,
        required=False
    )
    datasets= forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=granularity_choices,
        required=False
    )
    analyses= forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=granularity_choices,
        required=False
    )
    biosamples= forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=granularity_choices,
        required=False
    )
    cohorts= forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=granularity_choices,
        required=False
    )
    genomicVariations= forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=granularity_choices,
        required=False
    )
    runs= forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=granularity_choices,
        required=False
    )
    