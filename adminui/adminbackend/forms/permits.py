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
    DatasetID= forms.CharField(help_text='DatasetId')
    granularity_choices = [
        ('boolean', 'Boolean'),
        ('count', 'Count'),
        ('record', 'Record'),
    ]
    granularity= forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=granularity_choices,
        help_text='Granularity'
    )
    security_level_choices = [
        ('public', 'Public'),
        ('registered', 'Registered'),
        ('controlled', 'Controlled'),
    ]
    SecurityLevel= forms.ChoiceField(
        choices=security_level_choices, 
        widget=forms.RadioSelect,
        help_text='Security Level'
    )
    individualgranularity= forms.ChoiceField(
        choices=granularity_choices,
        required=False,
        help_text='Individual'
    )
    datasetgranularity= forms.ChoiceField(
        choices=granularity_choices,
        required=False,
        help_text='Dataset'
    )
    analysisgranularity= forms.ChoiceField(
        choices=granularity_choices,
        required=False,
        help_text='Analysis'
    )
    biosamplegranularity= forms.ChoiceField(
        choices=granularity_choices,
        required=False,
        help_text='Biosample'
    )
    cohortgranularity= forms.ChoiceField(
        choices=granularity_choices,
        required=False,
        help_text='Cohort'
    )
    genomicVariationgranularity = forms.ChoiceField(
        choices=granularity_choices,
        required=False,
        help_text='Genomic Variant'
    )
    rungranularity= forms.ChoiceField(
        choices=granularity_choices,
        required=False,
        help_text='Run'
    )

class UserPermitsForm(forms.Form):
    User= forms.CharField(help_text='User')
    granularity_choices = [
        ('boolean', 'Boolean'),
        ('count', 'Count'),
        ('record', 'Record'),
    ]
    granularity= forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=granularity_choices,
        help_text='Granularity'
    )
    userindividualgranularity= forms.ChoiceField(
        choices=granularity_choices,
        required=False,
        help_text='Individual'
    )
    userdatasetgranularity= forms.ChoiceField(
        choices=granularity_choices,
        required=False,
        help_text='Dataset'
    )
    useranalysisgranularity= forms.ChoiceField(
        choices=granularity_choices,
        required=False,
        help_text='Analysis'
    )
    userbiosamplegranularity= forms.ChoiceField(
        choices=granularity_choices,
        required=False,
        help_text='Biosample'
    )
    usercohortgranularity= forms.ChoiceField(
        choices=granularity_choices,
        required=False,
        help_text='Cohort'
    )
    usergenomicVariationgranularity = forms.ChoiceField(
        choices=granularity_choices,
        required=False,
        help_text='GenomicVariant'
    )
    userrungranularity= forms.ChoiceField(
        choices=granularity_choices,
        required=False,
        help_text='Run'
    )