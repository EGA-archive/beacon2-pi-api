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

def formatting_field(line):
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

def get_entry_types():
    with open("adminui/beacon/conf/analysis.py") as f:
        lines = f.readlines()
    entry_types=[]
    analysis_lookups=[]
    biosample_lookups=[]
    cohort_lookups=[]
    dataset_lookups=[]
    genomicVariation_lookups=[]
    individual_lookups=[]
    run_lookups=[]
    with open("adminui/beacon/conf/analysis.py", "r") as f:
        for line in lines:
            if 'endpoint_name' in str(line):
                placeholder = formatting_field(line)
                if placeholder != '':
                    entry_types.append('analysis')
            elif 'biosample_lookup' in str(line):
                if 'True' in str(line):
                    analysis_lookups.append('biosample')
            elif 'cohort_lookup' in str(line):
                if 'True' in str(line):
                    analysis_lookups.append('cohort')
            elif 'dataset_lookup' in str(line):
                if 'True' in str(line):
                    analysis_lookups.append('dataset')
            elif 'genomicVariant_lookup' in str(line):
                if 'True' in str(line):
                    analysis_lookups.append('genomicVariant')
            elif 'individual_lookup' in str(line):
                if 'True' in str(line):
                    analysis_lookups.append('individual')
            elif 'run_lookup' in str(line):
                if 'True' in str(line):
                    analysis_lookups.append('run')
    with open("adminui/beacon/conf/biosample.py") as f:
        lines = f.readlines()
    with open("adminui/beacon/conf/biosample.py", "r") as f:
        for line in lines:
            if 'endpoint_name' in str(line):
                placeholder = formatting_field(line)
                if placeholder != '':
                    entry_types.append('biosample')
            elif 'analysis_lookup' in str(line):
                if 'True' in str(line):
                    biosample_lookups.append('analysis')
            elif 'cohort_lookup' in str(line):
                if 'True' in str(line):
                    biosample_lookups.append('cohort')
            elif 'dataset_lookup' in str(line):
                if 'True' in str(line):
                    biosample_lookups.append('dataset')
            elif 'genomicVariant_lookup' in str(line):
                if 'True' in str(line):
                    biosample_lookups.append('genomicVariant')
            elif 'individual_lookup' in str(line):
                if 'True' in str(line):
                    biosample_lookups.append('individual')
            elif 'run_lookup' in str(line):
                if 'True' in str(line):
                    biosample_lookups.append('run')
    with open("adminui/beacon/conf/cohort.py") as f:
        lines = f.readlines()
    with open("adminui/beacon/conf/cohort.py", "r") as f:
        for line in lines:
            if 'endpoint_name' in str(line):
                placeholder = formatting_field(line)
                if placeholder != '':
                    entry_types.append('cohort')
            elif 'analysis_lookup' in str(line):
                if 'True' in str(line):
                    cohort_lookups.append('analysis')
            elif 'biosample_lookup' in str(line):
                if 'True' in str(line):
                    cohort_lookups.append('biosample')
            elif 'dataset_lookup' in str(line):
                if 'True' in str(line):
                    cohort_lookups.append('dataset')
            elif 'genomicVariant_lookup' in str(line):
                if 'True' in str(line):
                    cohort_lookups.append('genomicVariant')
            elif 'individual_lookup' in str(line):
                if 'True' in str(line):
                    cohort_lookups.append('individual')
            elif 'run_lookup' in str(line):
                if 'True' in str(line):
                    cohort_lookups.append('run')
    with open("adminui/beacon/conf/dataset.py") as f:
        lines = f.readlines()
    with open("adminui/beacon/conf/dataset.py", "r") as f:
        for line in lines:
            if 'endpoint_name' in str(line):
                placeholder = formatting_field(line)
                if placeholder != '':
                    entry_types.append('dataset')
            elif 'analysis_lookup' in str(line):
                if 'True' in str(line):
                    dataset_lookups.append('analysis')
            elif 'cohort_lookup' in str(line):
                if 'True' in str(line):
                    dataset_lookups.append('cohort')
            elif 'biosample_lookup' in str(line):
                if 'True' in str(line):
                    dataset_lookups.append('biosample')
            elif 'genomicVariant_lookup' in str(line):
                if 'True' in str(line):
                    dataset_lookups.append('genomicVariant')
            elif 'individual_lookup' in str(line):
                if 'True' in str(line):
                    dataset_lookups.append('individual')
            elif 'run_lookup' in str(line):
                if 'True' in str(line):
                    dataset_lookups.append('run')
    with open("adminui/beacon/conf/genomicVariant.py") as f:
        lines = f.readlines()
    with open("adminui/beacon/conf/genomicVariant.py", "r") as f:
        for line in lines:
            if 'endpoint_name' in str(line):
                placeholder = formatting_field(line)
                if placeholder != '':
                    entry_types.append('genomicVariant')
            elif 'analysis_lookup' in str(line):
                if 'True' in str(line):
                    genomicVariation_lookups.append('analysis')
            elif 'cohort_lookup' in str(line):
                if 'True' in str(line):
                    genomicVariation_lookups.append('cohort')
            elif 'dataset_lookup' in str(line):
                if 'True' in str(line):
                    genomicVariation_lookups.append('dataset')
            elif 'biosample_lookup' in str(line):
                if 'True' in str(line):
                    genomicVariation_lookups.append('biosample')
            elif 'individual_lookup' in str(line):
                if 'True' in str(line):
                    genomicVariation_lookups.append('individual')
            elif 'run_lookup' in str(line):
                if 'True' in str(line):
                    genomicVariation_lookups.append('run')
    with open("adminui/beacon/conf/individual.py") as f:
        lines = f.readlines()
    with open("adminui/beacon/conf/individual.py", "r") as f:
        for line in lines:
            if 'endpoint_name' in str(line):
                placeholder = formatting_field(line)
                if placeholder != '':
                    entry_types.append('individual')
            elif 'analysis_lookup' in str(line):
                if 'True' in str(line):
                    individual_lookups.append('analysis')
            elif 'cohort_lookup' in str(line):
                if 'True' in str(line):
                    individual_lookups.append('cohort')
            elif 'dataset_lookup' in str(line):
                if 'True' in str(line):
                    individual_lookups.append('dataset')
            elif 'genomicVariant_lookup' in str(line):
                if 'True' in str(line):
                    individual_lookups.append('genomicVariant')
            elif 'biosample_lookup' in str(line):
                if 'True' in str(line):
                    individual_lookups.append('biosample')
            elif 'run_lookup' in str(line):
                if 'True' in str(line):
                    individual_lookups.append('run')
    with open("adminui/beacon/conf/run.py") as f:
        lines = f.readlines()
    with open("adminui/beacon/conf/run.py", "r") as f:
        for line in lines:
            if 'endpoint_name' in str(line):
                placeholder = formatting_field(line)
                if placeholder != '':
                    entry_types.append('run')
            elif 'analysis_lookup' in str(line):
                if 'True' in str(line):
                    run_lookups.append('analysis')
            elif 'cohort_lookup' in str(line):
                if 'True' in str(line):
                    run_lookups.append('cohort')
            elif 'dataset_lookup' in str(line):
                if 'True' in str(line):
                    run_lookups.append('dataset')
            elif 'genomicVariant_lookup' in str(line):
                if 'True' in str(line):
                    run_lookups.append('genomicVariant')
            elif 'individual_lookup' in str(line):
                if 'True' in str(line):
                    run_lookups.append('individual')
            elif 'biosample_lookup' in str(line):
                if 'True' in str(line):
                    run_lookups.append('biosample')
    return entry_types, analysis_lookups, biosample_lookups, cohort_lookups, dataset_lookups, genomicVariation_lookups, individual_lookups, run_lookups


class EntryTypesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(EntryTypesForm, self).__init__(*args, **kwargs)
        # assign a (computed, I assume) default value to the choice field
        with open("adminui/beacon/conf/analysis.py") as f:
            lines = f.readlines()
        entry_types=[]
        with open("adminui/beacon/conf/analysis.py", "r") as f:
            for line in lines:
                if 'endpoint_name' in str(line):
                    placeholder = formatting_field(line)
                    self.initial['AnalysisEndpointName'] = placeholder
                    if placeholder != '':
                        entry_types.append('analysis')
        with open("adminui/beacon/conf/biosample.py") as f:
            lines = f.readlines()
        with open("adminui/beacon/conf/biosample.py", "r") as f:
            for line in lines:
                if 'endpoint_name' in str(line):
                    placeholder = formatting_field(line)
                    self.initial['BiosampleEndpointName'] = placeholder
                    if placeholder != '':
                        entry_types.append('biosample')
        with open("adminui/beacon/conf/cohort.py") as f:
            lines = f.readlines()
        with open("adminui/beacon/conf/cohort.py", "r") as f:
            for line in lines:
                if 'endpoint_name' in str(line):
                    placeholder = formatting_field(line)
                    self.initial['CohortEndpointName'] = placeholder
                    if placeholder != '':
                        entry_types.append('cohort')
        with open("adminui/beacon/conf/dataset.py") as f:
            lines = f.readlines()
        with open("adminui/beacon/conf/dataset.py", "r") as f:
            for line in lines:
                if 'endpoint_name' in str(line):
                    placeholder = formatting_field(line)
                    self.initial['DatasetEndpointName'] = placeholder
                    if placeholder != '':
                        entry_types.append('dataset')
        with open("adminui/beacon/conf/genomicVariant.py") as f:
            lines = f.readlines()
        with open("adminui/beacon/conf/genomicVariant.py", "r") as f:
            for line in lines:
                if 'endpoint_name' in str(line):
                    placeholder = formatting_field(line)
                    self.initial['GenomicVariantEndpointName'] = placeholder
                    if placeholder != '':
                        entry_types.append('genomicVariant')
        with open("adminui/beacon/conf/individual.py") as f:
            lines = f.readlines()
        with open("adminui/beacon/conf/individual.py", "r") as f:
            for line in lines:
                if 'endpoint_name' in str(line):
                    placeholder = formatting_field(line)
                    self.initial['IndividualEndpointName'] = placeholder
                    if placeholder != '':
                        entry_types.append('individual')
        with open("adminui/beacon/conf/run.py") as f:
            lines = f.readlines()
        with open("adminui/beacon/conf/run.py", "r") as f:
            for line in lines:
                if 'endpoint_name' in str(line):
                    placeholder = formatting_field(line)
                    self.initial['RunEndpointName'] = placeholder
                    if placeholder != '':
                        entry_types.append('run')
        self.initial['EntryTypes'] = entry_types
        self.entry_types=entry_types
    entry_type_choices = [("analysis", "analysis"), ("biosample", "biosample"), ("cohort", "cohort"), ("dataset", "dataset"), ("genomicVariant", "genomicVariant"), ("individual", "individual"), ("run", "run")]
    EntryTypes = forms.MultipleChoiceField(
        choices=entry_type_choices, 
        widget=forms.CheckboxSelectMultiple
    )
    AnalysisEndpointName = forms.CharField(help_text='Endpoint Name')
    BiosampleEndpointName = forms.CharField(help_text='Endpoint Name')
    CohortEndpointName = forms.CharField(help_text='Endpoint Name')
    DatasetEndpointName = forms.CharField(help_text='Endpoint Name')
    GenomicVariantEndpointName = forms.CharField(help_text='Endpoint Name')
    IndividualEndpointName = forms.CharField(help_text='Endpoint Name')
    RunEndpointName = forms.CharField(help_text='Endpoint Name')
    entry_types, analysis_lookups, biosample_lookups, cohort_lookups, dataset_lookups, genomicVariation_lookups, individual_lookups, run_lookups=get_entry_types()
    analysis_choices=[]
    for entry_type in entry_types:
        if entry_type != 'analysis':
            analysis_choices.append(('analysis/{id}/'+entry_type, 'analysis/{id}/'+entry_type))
    Analysis = forms.MultipleChoiceField(
        choices=analysis_choices, 
        widget=forms.CheckboxSelectMultiple
    )

    