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

def get_entry_types(entry_type):
    with open("adminui/beacon/conf/" + entry_type+".py") as f:
        lines = f.readlines()
    lookups=[]
    active_entry_type=None
    with open("adminui/beacon/conf/"+ entry_type+".py", "r") as f:
        for line in lines:
            if 'endpoint_name' in str(line):
                placeholder = formatting_field(line)
                if placeholder != '':
                    active_entry_type=entry_type
                    active_endpoint_name=placeholder
            elif 'analysis_lookup' in str(line):
                if 'True' in str(line):
                    lookups.append('analysis')
            elif 'biosample_lookup' in str(line):
                if 'True' in str(line):
                    lookups.append('biosample')
            elif 'cohort_lookup' in str(line):
                if 'True' in str(line):
                    lookups.append('cohort')
            elif 'dataset_lookup' in str(line):
                if 'True' in str(line):
                    lookups.append('dataset')
            elif 'genomicVariant_lookup' in str(line):
                if 'True' in str(line):
                    lookups.append('genomicVariant')
            elif 'individual_lookup' in str(line):
                if 'True' in str(line):
                    lookups.append('individual')
            elif 'run_lookup' in str(line):
                if 'True' in str(line):
                    lookups.append('run')
            elif 'singleEntryUrl' in str(line):
                if 'True' in str(line):
                    lookups.append(entry_type)
    return active_entry_type, active_endpoint_name, lookups

def generate_endpoints(choices, first_endpoint_name,second_endpoint_name,second_entry_type, lookups):
    for entry_type in lookups:
        if first_endpoint_name == second_endpoint_name and entry_type == second_entry_type:
            choices.append((first_endpoint_name+'/{id}', first_endpoint_name+'/{id}'))
        elif entry_type == second_entry_type:
                choices.append((first_endpoint_name+'/{id}/'+second_endpoint_name, first_endpoint_name+'/{id}/'+second_endpoint_name))
    return choices

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
    analysis_entry_type, analysis_endpoint_name, analysis_lookups =get_entry_types('analysis')
    biosample_entry_type, biosample_endpoint_name, biosample_lookups =get_entry_types('biosample')
    cohort_entry_type, cohort_endpoint_name, cohort_lookups =get_entry_types('cohort')
    dataset_entry_type, dataset_endpoint_name, dataset_lookups =get_entry_types('dataset')
    genomicVariant_entry_type, genomicVariant_endpoint_name, genomicVariant_lookups =get_entry_types('genomicVariant')
    individual_entry_type, individual_endpoint_name, individual_lookups =get_entry_types('individual')
    run_entry_type, run_endpoint_name, run_lookups =get_entry_types('run')
    analysis_choices=[]
    analysis_choices=generate_endpoints(analysis_choices, analysis_endpoint_name, biosample_endpoint_name, biosample_entry_type, analysis_lookups)
    analysis_choices=generate_endpoints(analysis_choices, analysis_endpoint_name, cohort_endpoint_name, cohort_entry_type, analysis_lookups)
    analysis_choices=generate_endpoints(analysis_choices, analysis_endpoint_name, dataset_endpoint_name, dataset_entry_type, analysis_lookups)
    analysis_choices=generate_endpoints(analysis_choices, analysis_endpoint_name, genomicVariant_endpoint_name, genomicVariant_entry_type, analysis_lookups)
    analysis_choices=generate_endpoints(analysis_choices, analysis_endpoint_name, individual_endpoint_name, individual_entry_type, analysis_lookups)
    analysis_choices=generate_endpoints(analysis_choices, analysis_endpoint_name, run_endpoint_name, run_entry_type, analysis_lookups)
    analysis_choices=generate_endpoints(analysis_choices, analysis_endpoint_name, analysis_endpoint_name, analysis_entry_type, analysis_lookups)
    Analysis = forms.MultipleChoiceField(
        choices=analysis_choices, 
        widget=forms.CheckboxSelectMultiple
    )
    biosample_choices=[]
    biosample_choices=generate_endpoints(biosample_choices, biosample_endpoint_name, analysis_endpoint_name, analysis_entry_type, biosample_lookups)
    biosample_choices=generate_endpoints(biosample_choices, biosample_endpoint_name, cohort_endpoint_name, cohort_entry_type, biosample_lookups)
    biosample_choices=generate_endpoints(biosample_choices, biosample_endpoint_name, dataset_endpoint_name, dataset_entry_type, biosample_lookups)
    biosample_choices=generate_endpoints(biosample_choices, biosample_endpoint_name, genomicVariant_endpoint_name, genomicVariant_entry_type, biosample_lookups)
    biosample_choices=generate_endpoints(biosample_choices, biosample_endpoint_name, individual_endpoint_name, individual_entry_type, biosample_lookups)
    biosample_choices=generate_endpoints(biosample_choices, biosample_endpoint_name, run_endpoint_name, run_entry_type, biosample_lookups)
    biosample_choices=generate_endpoints(biosample_choices, biosample_endpoint_name, biosample_endpoint_name, biosample_entry_type, biosample_lookups)
    Biosample = forms.MultipleChoiceField(
        choices=biosample_choices, 
        widget=forms.CheckboxSelectMultiple
    )
    cohort_choices=[]
    cohort_choices=generate_endpoints(cohort_choices, cohort_endpoint_name, analysis_endpoint_name, analysis_entry_type, cohort_lookups)
    cohort_choices=generate_endpoints(cohort_choices, cohort_endpoint_name, biosample_endpoint_name, biosample_entry_type, cohort_lookups)
    cohort_choices=generate_endpoints(cohort_choices, cohort_endpoint_name, dataset_endpoint_name, dataset_entry_type, cohort_lookups)
    cohort_choices=generate_endpoints(cohort_choices, cohort_endpoint_name, genomicVariant_endpoint_name, genomicVariant_entry_type, cohort_lookups)
    cohort_choices=generate_endpoints(cohort_choices, cohort_endpoint_name, individual_endpoint_name, individual_entry_type, cohort_lookups)
    cohort_choices=generate_endpoints(cohort_choices, cohort_endpoint_name, run_endpoint_name, run_entry_type, cohort_lookups)
    cohort_choices=generate_endpoints(cohort_choices, cohort_endpoint_name, cohort_endpoint_name, cohort_entry_type, cohort_lookups)
    Cohort = forms.MultipleChoiceField(
        choices=cohort_choices, 
        widget=forms.CheckboxSelectMultiple
    )
    dataset_choices=[]
    dataset_choices=generate_endpoints(dataset_choices, dataset_endpoint_name, analysis_endpoint_name, analysis_entry_type, dataset_lookups)
    dataset_choices=generate_endpoints(dataset_choices, dataset_endpoint_name, biosample_endpoint_name, biosample_entry_type, dataset_lookups)
    dataset_choices=generate_endpoints(dataset_choices, dataset_endpoint_name, cohort_endpoint_name, cohort_entry_type, dataset_lookups)
    dataset_choices=generate_endpoints(dataset_choices, dataset_endpoint_name, genomicVariant_endpoint_name, genomicVariant_entry_type, dataset_lookups)
    dataset_choices=generate_endpoints(dataset_choices, dataset_endpoint_name, individual_endpoint_name, individual_entry_type, dataset_lookups)
    dataset_choices=generate_endpoints(dataset_choices, dataset_endpoint_name, run_endpoint_name, run_entry_type, dataset_lookups)
    dataset_choices=generate_endpoints(dataset_choices, dataset_endpoint_name, dataset_endpoint_name, dataset_entry_type, dataset_lookups)
    Dataset = forms.MultipleChoiceField(
        choices=dataset_choices, 
        widget=forms.CheckboxSelectMultiple
    )
    genomicVariant_choices=[]
    genomicVariant_choices=generate_endpoints(genomicVariant_choices, genomicVariant_endpoint_name, analysis_endpoint_name, analysis_entry_type, genomicVariant_lookups)
    genomicVariant_choices=generate_endpoints(genomicVariant_choices, genomicVariant_endpoint_name, biosample_endpoint_name, biosample_entry_type, genomicVariant_lookups)
    genomicVariant_choices=generate_endpoints(genomicVariant_choices, genomicVariant_endpoint_name, cohort_endpoint_name, cohort_entry_type, genomicVariant_lookups)
    genomicVariant_choices=generate_endpoints(genomicVariant_choices, genomicVariant_endpoint_name, dataset_endpoint_name, dataset_entry_type, genomicVariant_lookups)
    genomicVariant_choices=generate_endpoints(genomicVariant_choices, genomicVariant_endpoint_name, individual_endpoint_name, individual_entry_type, genomicVariant_lookups)
    genomicVariant_choices=generate_endpoints(genomicVariant_choices, genomicVariant_endpoint_name, run_endpoint_name, run_entry_type, genomicVariant_lookups)
    genomicVariant_choices=generate_endpoints(genomicVariant_choices, genomicVariant_endpoint_name, genomicVariant_endpoint_name, genomicVariant_entry_type, genomicVariant_lookups)
    GenomicVariant = forms.MultipleChoiceField(
        choices=genomicVariant_choices, 
        widget=forms.CheckboxSelectMultiple
    )
    individual_choices=[]
    individual_choices=generate_endpoints(individual_choices, individual_endpoint_name, analysis_endpoint_name, analysis_entry_type, individual_lookups)
    individual_choices=generate_endpoints(individual_choices, individual_endpoint_name, biosample_endpoint_name, biosample_entry_type, individual_lookups)
    individual_choices=generate_endpoints(individual_choices, individual_endpoint_name, cohort_endpoint_name, cohort_entry_type, individual_lookups)
    individual_choices=generate_endpoints(individual_choices, individual_endpoint_name, dataset_endpoint_name, dataset_entry_type, individual_lookups)
    individual_choices=generate_endpoints(individual_choices, individual_endpoint_name, genomicVariant_endpoint_name, genomicVariant_entry_type, individual_lookups)
    individual_choices=generate_endpoints(individual_choices, individual_endpoint_name, run_endpoint_name, run_entry_type, individual_lookups)
    individual_choices=generate_endpoints(individual_choices, individual_endpoint_name, individual_endpoint_name, individual_entry_type, individual_lookups)
    Individual = forms.MultipleChoiceField(
        choices=individual_choices, 
        widget=forms.CheckboxSelectMultiple
    )
    run_choices=[]
    run_choices=generate_endpoints(run_choices, run_endpoint_name, analysis_endpoint_name, analysis_entry_type, run_lookups)
    run_choices=generate_endpoints(run_choices, run_endpoint_name, biosample_endpoint_name, biosample_entry_type, run_lookups)
    run_choices=generate_endpoints(run_choices, run_endpoint_name, cohort_endpoint_name, cohort_entry_type, run_lookups)
    run_choices=generate_endpoints(run_choices, run_endpoint_name, dataset_endpoint_name, dataset_entry_type, run_lookups)
    run_choices=generate_endpoints(run_choices, run_endpoint_name, genomicVariant_endpoint_name, genomicVariant_entry_type, run_lookups)
    run_choices=generate_endpoints(run_choices, run_endpoint_name, individual_endpoint_name, individual_entry_type, run_lookups)
    run_choices=generate_endpoints(run_choices, run_endpoint_name, run_endpoint_name, run_entry_type, run_lookups)
    Run = forms.MultipleChoiceField(
        choices=run_choices, 
        widget=forms.CheckboxSelectMultiple
    )