from django import forms
import yaml
import logging
import os

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
    with open("/home/app/web/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/"+entry_type+".yml") as f:
        lines = yaml.safe_load(f)
    lookups=[]
    active_entry_type=None
    active_endpoint_name=None
    placeholder = lines[entry_type]['endpoint_name']
    if placeholder != '':
        active_entry_type=entry_type
        active_endpoint_name=placeholder
    for k, v in lines[entry_type]['lookups'].items():
        if v['endpoint_enabled']==True:
            lookups.append(k)
    if lines[entry_type]['entry_type_enabled']==True:
        lookups.append(entry_type)
    return active_entry_type, active_endpoint_name, lookups

def generate_endpoints(choices, first_endpoint_name,second_endpoint_name,second_entry_type, lookups):
    for entry_type in lookups:
        if first_endpoint_name == second_endpoint_name and entry_type == second_entry_type:
            choices.append((first_endpoint_name+'/{id}', first_endpoint_name+'/{id}'))
        elif entry_type == second_entry_type:
                choices.append((first_endpoint_name+'/{id}/'+second_endpoint_name, first_endpoint_name+'/{id}/'+second_endpoint_name))
    return choices

def initialize_lookup_endpoints(entry_type,initial_choices):
    with open("/home/app/web/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/"+entry_type+".yml") as f:
        lines = yaml.safe_load(f)
    for k, v in lines[entry_type]['lookups'].items():
        if v['endpoint_enabled']==True:
            initial_choices.append(v['endpoint_name'])
    return initial_choices

class EntryTypesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(EntryTypesForm, self).__init__(*args, **kwargs)
        # assign a (computed, I assume) default value to the choice field
        with open("/home/app/web/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/analysis.yml") as f:
            lines = yaml.safe_load(f)
        entry_types=[]
        endpoint_names=[]
        analysis_initial_choices=[]
        analysis_endpoint_name = lines['analysis']['endpoint_name']
        self.initial['analysisEndpointName'] = analysis_endpoint_name
        if analysis_endpoint_name != '':
            entry_types.append('analysis')
            endpoint_names.append(analysis_endpoint_name)
            self.initial['analysis'] = True
        else:
            self.initial['analysis'] = None
        placeholder = lines['analysis']['allow_queries_without_filters']
        if placeholder == False:
            self.initial['analysisNonFiltered'] = None
        else:
            self.initial['analysisNonFiltered'] = True
        placeholder = lines['analysis']['allow_id_query']
        if placeholder == True:
            analysis_initial_choices.append(self.initial['analysisEndpointName']+"/{id}")
        placeholder = lines['analysis']['max_granularity']
        self.initial['analysis_granularity'] = placeholder
        placeholder = lines['analysis']['connection']['name']
        self.initial['analysis_engine'] = placeholder
        placeholder = lines['analysis']['connection']['database']
        self.initial['analysis_dbname'] = placeholder
        placeholder = lines['analysis']['connection']['table']
        self.initial['analysis_tablename'] = placeholder
        placeholder = lines['analysis']['connection']['functions']['function_name_assigned']
        self.initial['analysis_function'] = placeholder
        placeholder = lines['analysis']['connection']['functions']['id_query_function_name_assigned']
        self.initial['analysis_id_function'] = placeholder
        placeholder = lines['analysis']['info']['name']
        self.initial['analysis_info_name'] = placeholder
        placeholder = lines['analysis']['info']['ontology_id']
        self.initial['analysis_info_ontology_id'] = placeholder
        placeholder = lines['analysis']['info']['ontology_name']
        self.initial['analysis_info_ontology_name'] = placeholder
        placeholder = lines['analysis']['info']['description']
        self.initial['analysis_info_description'] = placeholder
        placeholder = lines['analysis']['schema']['specification']
        self.initial['analysis_schema_specification'] = placeholder
        placeholder = lines['analysis']['schema']['default_schema_id']
        self.initial['analysis_schema_id'] = placeholder
        placeholder = lines['analysis']['schema']['default_schema_name']
        self.initial['analysis_schema_name'] = placeholder
        placeholder = lines['analysis']['schema']['default_schema_version']
        self.initial['analysis_schema_version'] = placeholder
        placeholder = lines['analysis']['schema']['supported_schemas']
        self.initial['analysis_supported_schemas'] = placeholder
        placeholder = lines['analysis']['schema']['reference_to_default_schema_definition']
        self.initial['analysis_schema_reference'] = placeholder
        with open("/home/app/web/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/biosample.yml") as f:
            lines = yaml.safe_load(f)
        biosample_initial_choices=[]
        biosample_endpoint_name = lines['biosample']['endpoint_name']
        self.initial['biosampleEndpointName'] = biosample_endpoint_name
        if biosample_endpoint_name != '':
            entry_types.append('biosample')
            endpoint_names.append(biosample_endpoint_name)
            self.initial['biosample'] = True
        else:
            self.initial['biosample'] = None
        placeholder = lines['biosample']['allow_queries_without_filters']
        if placeholder == False:
            self.initial['biosampleNonFiltered'] = None
        else:
            self.initial['biosampleNonFiltered'] = True
        placeholder = lines['biosample']['allow_id_query']
        if placeholder == True:
            biosample_initial_choices.append(self.initial['biosampleEndpointName']+"/{id}")
        placeholder = lines['biosample']['max_granularity']
        self.initial['biosample_granularity'] = placeholder
        placeholder = lines['biosample']['connection']['name']
        self.initial['biosample_engine'] = placeholder
        placeholder = lines['biosample']['connection']['database']
        self.initial['biosample_dbname'] = placeholder
        placeholder = lines['biosample']['connection']['table']
        self.initial['biosample_tablename'] = placeholder
        placeholder = lines['biosample']['connection']['functions']['function_name_assigned']
        self.initial['biosample_function'] = placeholder
        placeholder = lines['biosample']['connection']['functions']['id_query_function_name_assigned']
        self.initial['biosample_id_function'] = placeholder
        placeholder = lines['biosample']['connection']['database']
        self.initial['biosample_dbname'] = placeholder
        placeholder = lines['biosample']['connection']['table']
        self.initial['biosample_tablename'] = placeholder
        placeholder = lines['biosample']['connection']['functions']['function_name_assigned']
        self.initial['biosample_function'] = placeholder
        placeholder = lines['biosample']['connection']['functions']['id_query_function_name_assigned']
        self.initial['biosample_id_function'] = placeholder
        placeholder = lines['biosample']['info']['name']
        self.initial['biosample_info_name'] = placeholder
        placeholder = lines['biosample']['info']['ontology_id']
        self.initial['biosample_info_ontology_id'] = placeholder
        placeholder = lines['biosample']['info']['ontology_name']
        self.initial['biosample_info_ontology_name'] = placeholder
        placeholder = lines['biosample']['info']['description']
        self.initial['biosample_info_description'] = placeholder
        placeholder = lines['biosample']['schema']['specification']
        self.initial['biosample_schema_specification'] = placeholder
        placeholder = lines['biosample']['schema']['default_schema_id']
        self.initial['biosample_schema_id'] = placeholder
        placeholder = lines['biosample']['schema']['default_schema_name']
        self.initial['biosample_schema_name'] = placeholder
        placeholder = lines['biosample']['schema']['default_schema_version']
        self.initial['biosample_schema_version'] = placeholder
        placeholder = lines['biosample']['schema']['supported_schemas']
        self.initial['biosample_supported_schemas'] = placeholder
        placeholder = lines['biosample']['schema']['reference_to_default_schema_definition']
        self.initial['biosample_schema_reference'] = placeholder
        with open("/home/app/web/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/cohort.yml") as f:
            lines = yaml.safe_load(f)
        cohort_initial_choices=[]
        cohort_endpoint_name = lines['cohort']['endpoint_name']
        self.initial['cohortEndpointName'] = cohort_endpoint_name
        if cohort_endpoint_name != '':
            entry_types.append('cohort')
            endpoint_names.append(cohort_endpoint_name)
            self.initial['cohort'] = True
        else:
            self.initial['cohort'] = None
        placeholder = lines['cohort']['allow_queries_without_filters']
        if placeholder == False:
            self.initial['cohortNonFiltered'] = None
        else:
            self.initial['cohortNonFiltered'] = True
        placeholder = lines['cohort']['allow_id_query']
        if placeholder == True:
            cohort_initial_choices.append(self.initial['cohortEndpointName']+"/{id}")
        placeholder = lines['cohort']['max_granularity']
        self.initial['cohort_granularity'] = placeholder
        placeholder = lines['cohort']['connection']['name']
        self.initial['cohort_engine'] = placeholder
        placeholder = lines['cohort']['connection']['database']
        self.initial['cohort_dbname'] = placeholder
        placeholder = lines['cohort']['connection']['table']
        self.initial['cohort_tablename'] = placeholder
        placeholder = lines['cohort']['connection']['functions']['function_name_assigned']
        self.initial['cohort_function'] = placeholder
        placeholder = lines['cohort']['connection']['functions']['id_query_function_name_assigned']
        self.initial['cohort_id_function'] = placeholder
        placeholder = lines['cohort']['connection']['database']
        self.initial['cohort_dbname'] = placeholder
        placeholder = lines['cohort']['connection']['table']
        self.initial['cohort_tablename'] = placeholder
        placeholder = lines['cohort']['connection']['functions']['function_name_assigned']
        self.initial['cohort_function'] = placeholder
        placeholder = lines['cohort']['connection']['functions']['id_query_function_name_assigned']
        self.initial['cohort_id_function'] = placeholder
        placeholder = lines['cohort']['info']['name']
        self.initial['cohort_info_name'] = placeholder
        placeholder = lines['cohort']['info']['ontology_id']
        self.initial['cohort_info_ontology_id'] = placeholder
        placeholder = lines['cohort']['info']['ontology_name']
        self.initial['cohort_info_ontology_name'] = placeholder
        placeholder = lines['cohort']['info']['description']
        self.initial['cohort_info_description'] = placeholder
        placeholder = lines['cohort']['schema']['specification']
        self.initial['cohort_schema_specification'] = placeholder
        placeholder = lines['cohort']['schema']['default_schema_id']
        self.initial['cohort_schema_id'] = placeholder
        placeholder = lines['cohort']['schema']['default_schema_name']
        self.initial['cohort_schema_name'] = placeholder
        placeholder = lines['cohort']['schema']['default_schema_version']
        self.initial['cohort_schema_version'] = placeholder
        placeholder = lines['cohort']['schema']['supported_schemas']
        self.initial['cohort_supported_schemas'] = placeholder
        placeholder = lines['cohort']['schema']['reference_to_default_schema_definition']
        self.initial['cohort_schema_reference'] = placeholder
        with open("/home/app/web/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/dataset.yml") as f:
            lines = yaml.safe_load(f)
        dataset_initial_choices=[]
        dataset_endpoint_name = lines['dataset']['endpoint_name']
        self.initial['datasetEndpointName'] = dataset_endpoint_name
        if dataset_endpoint_name != '':
            entry_types.append('dataset')
            endpoint_names.append(dataset_endpoint_name)
            self.initial['dataset'] = True
        else:
            self.initial['dataset'] = None
        placeholder = lines['dataset']['allow_queries_without_filters']
        if placeholder == False:
            self.initial['datasetNonFiltered'] = None
        else:
            self.initial['datasetNonFiltered'] = True
        placeholder = lines['dataset']['allow_id_query']
        if placeholder == True:
            dataset_initial_choices.append(self.initial['datasetEndpointName']+"/{id}")
        placeholder = lines['dataset']['max_granularity']
        self.initial['dataset_granularity'] = placeholder
        placeholder = lines['dataset']['connection']['name']
        self.initial['dataset_engine'] = placeholder
        placeholder = lines['dataset']['connection']['database']
        self.initial['dataset_dbname'] = placeholder
        placeholder = lines['dataset']['connection']['table']
        self.initial['dataset_tablename'] = placeholder
        placeholder = lines['dataset']['connection']['functions']['function_name_assigned']
        self.initial['dataset_function'] = placeholder
        placeholder = lines['dataset']['connection']['functions']['id_query_function_name_assigned']
        self.initial['dataset_id_function'] = placeholder
        placeholder = lines['dataset']['connection']['database']
        self.initial['dataset_dbname'] = placeholder
        placeholder = lines['dataset']['connection']['table']
        self.initial['dataset_tablename'] = placeholder
        placeholder = lines['dataset']['connection']['functions']['function_name_assigned']
        self.initial['dataset_function'] = placeholder
        placeholder = lines['dataset']['connection']['functions']['id_query_function_name_assigned']
        self.initial['dataset_id_function'] = placeholder
        placeholder = lines['dataset']['info']['name']
        self.initial['dataset_info_name'] = placeholder
        placeholder = lines['dataset']['info']['ontology_id']
        self.initial['dataset_info_ontology_id'] = placeholder
        placeholder = lines['dataset']['info']['ontology_name']
        self.initial['dataset_info_ontology_name'] = placeholder
        placeholder = lines['dataset']['info']['description']
        self.initial['dataset_info_description'] = placeholder
        placeholder = lines['dataset']['schema']['specification']
        self.initial['dataset_schema_specification'] = placeholder
        placeholder = lines['dataset']['schema']['default_schema_id']
        self.initial['dataset_schema_id'] = placeholder
        placeholder = lines['dataset']['schema']['default_schema_name']
        self.initial['dataset_schema_name'] = placeholder
        placeholder = lines['dataset']['schema']['default_schema_version']
        self.initial['dataset_schema_version'] = placeholder
        placeholder = lines['dataset']['schema']['supported_schemas']
        self.initial['dataset_supported_schemas'] = placeholder
        placeholder = lines['dataset']['schema']['reference_to_default_schema_definition']
        self.initial['dataset_schema_reference'] = placeholder
        with open("/home/app/web/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/genomicVariant.yml") as f:
            lines = yaml.safe_load(f)
        genomicVariant_initial_choices=[]
        genomicVariant_endpoint_name = lines['genomicVariant']['endpoint_name']
        self.initial['genomicVariationEndpointName'] = genomicVariant_endpoint_name
        if genomicVariant_endpoint_name != '':
            entry_types.append('genomicVariation')
            endpoint_names.append(genomicVariant_endpoint_name)
            self.initial['genomicVariation'] = True
        else:
            self.initial['genomicVariation'] = None
        placeholder = lines['genomicVariant']['allow_queries_without_filters']
        if placeholder == False:
            self.initial['genomicVariationNonFiltered'] = None
        else:
            self.initial['genomicVariationNonFiltered'] = True
        placeholder = lines['genomicVariant']['allow_id_query']
        if placeholder == True:
            genomicVariant_initial_choices.append(self.initial['genomicVariationEndpointName']+"/{id}")
        placeholder = lines['genomicVariant']['max_granularity']
        self.initial['genomicVariant_granularity'] = placeholder
        placeholder = lines['genomicVariant']['connection']['name']
        self.initial['genomicVariant_engine'] = placeholder
        placeholder = lines['genomicVariant']['connection']['database']
        self.initial['genomicVariant_dbname'] = placeholder
        placeholder = lines['genomicVariant']['connection']['table']
        self.initial['genomicVariant_tablename'] = placeholder
        placeholder = lines['genomicVariant']['connection']['functions']['function_name_assigned']
        self.initial['genomicVariant_function'] = placeholder
        placeholder = lines['genomicVariant']['connection']['functions']['id_query_function_name_assigned']
        self.initial['genomicVariant_id_function'] = placeholder
        placeholder = lines['genomicVariant']['connection']['database']
        self.initial['genomicVariant_dbname'] = placeholder
        placeholder = lines['genomicVariant']['connection']['table']
        self.initial['genomicVariant_tablename'] = placeholder
        placeholder = lines['genomicVariant']['connection']['functions']['function_name_assigned']
        self.initial['genomicVariant_function'] = placeholder
        placeholder = lines['genomicVariant']['connection']['functions']['id_query_function_name_assigned']
        self.initial['genomicVariant_id_function'] = placeholder
        placeholder = lines['genomicVariant']['info']['name']
        self.initial['genomicVariant_info_name'] = placeholder
        placeholder = lines['genomicVariant']['info']['ontology_id']
        self.initial['genomicVariant_info_ontology_id'] = placeholder
        placeholder = lines['genomicVariant']['info']['ontology_name']
        self.initial['genomicVariant_info_ontology_name'] = placeholder
        placeholder = lines['genomicVariant']['info']['description']
        self.initial['genomicVariant_info_description'] = placeholder
        placeholder = lines['genomicVariant']['schema']['specification']
        self.initial['genomicVariant_schema_specification'] = placeholder
        placeholder = lines['genomicVariant']['schema']['default_schema_id']
        self.initial['genomicVariant_schema_id'] = placeholder
        placeholder = lines['genomicVariant']['schema']['default_schema_name']
        self.initial['genomicVariant_schema_name'] = placeholder
        placeholder = lines['genomicVariant']['schema']['default_schema_version']
        self.initial['genomicVariant_schema_version'] = placeholder
        placeholder = lines['genomicVariant']['schema']['supported_schemas']
        self.initial['genomicVariant_supported_schemas'] = placeholder
        placeholder = lines['genomicVariant']['schema']['reference_to_default_schema_definition']
        self.initial['genomicVariant_schema_reference'] = placeholder
        with open("/home/app/web/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/individual.yml") as f:
            lines = yaml.safe_load(f)
        individual_initial_choices=[]
        individual_endpoint_name = lines['individual']['endpoint_name']
        self.initial['individualEndpointName'] = individual_endpoint_name
        if individual_endpoint_name != '':
            entry_types.append('individual')
            endpoint_names.append(individual_endpoint_name)
            self.initial['individual'] = True
        else:
            self.initial['individual'] = None
        placeholder = lines['individual']['allow_queries_without_filters']
        if placeholder == False:
            self.initial['individualNonFiltered'] = None
        else:
            self.initial['individualNonFiltered'] = True
        placeholder = lines['individual']['allow_id_query']
        if placeholder == True:
            individual_initial_choices.append(self.initial['individualEndpointName']+"/{id}")
        placeholder = lines['individual']['max_granularity']
        self.initial['individual_granularity'] = placeholder
        placeholder = lines['individual']['connection']['name']
        self.initial['individual_engine'] = placeholder
        placeholder = lines['individual']['connection']['database']
        self.initial['individual_dbname'] = placeholder
        placeholder = lines['individual']['connection']['table']
        self.initial['individual_tablename'] = placeholder
        placeholder = lines['individual']['connection']['functions']['function_name_assigned']
        self.initial['individual_function'] = placeholder
        placeholder = lines['individual']['connection']['functions']['id_query_function_name_assigned']
        self.initial['individual_id_function'] = placeholder
        placeholder = lines['individual']['connection']['database']
        self.initial['individual_dbname'] = placeholder
        placeholder = lines['individual']['connection']['table']
        self.initial['individual_tablename'] = placeholder
        placeholder = lines['individual']['connection']['functions']['function_name_assigned']
        self.initial['individual_function'] = placeholder
        placeholder = lines['individual']['connection']['functions']['id_query_function_name_assigned']
        self.initial['individual_id_function'] = placeholder
        placeholder = lines['individual']['info']['name']
        self.initial['individual_info_name'] = placeholder
        placeholder = lines['individual']['info']['ontology_id']
        self.initial['individual_info_ontology_id'] = placeholder
        placeholder = lines['individual']['info']['ontology_name']
        self.initial['individual_info_ontology_name'] = placeholder
        placeholder = lines['individual']['info']['description']
        self.initial['individual_info_description'] = placeholder
        placeholder = lines['individual']['schema']['specification']
        self.initial['individual_schema_specification'] = placeholder
        placeholder = lines['individual']['schema']['default_schema_id']
        self.initial['individual_schema_id'] = placeholder
        placeholder = lines['individual']['schema']['default_schema_name']
        self.initial['individual_schema_name'] = placeholder
        placeholder = lines['individual']['schema']['default_schema_version']
        self.initial['individual_schema_version'] = placeholder
        placeholder = lines['individual']['schema']['supported_schemas']
        self.initial['individual_supported_schemas'] = placeholder
        placeholder = lines['individual']['schema']['reference_to_default_schema_definition']
        self.initial['individual_schema_reference'] = placeholder
        with open("/home/app/web/beacon/models/ga4gh/beacon_v2_default_model/conf/entry_types/run.yml") as f:
            lines = yaml.safe_load(f)
        run_initial_choices=[]
        run_endpoint_name = lines['run']['endpoint_name']
        self.initial['runEndpointName'] = run_endpoint_name
        if run_endpoint_name != '':
            entry_types.append('run')
            endpoint_names.append(run_endpoint_name)
            self.initial['run'] = True
        else:
            self.initial['run'] = None
        placeholder = lines['run']['allow_queries_without_filters']
        if placeholder == False:
            self.initial['runNonFiltered'] = None
        else:
            self.initial['runNonFiltered'] = True
        placeholder = lines['run']['allow_id_query']
        if placeholder == True:
            run_initial_choices.append(self.initial['runEndpointName']+"/{id}")
        placeholder = lines['run']['max_granularity']
        self.initial['run_granularity'] = placeholder
        placeholder = lines['run']['connection']['name']
        self.initial['run_engine'] = placeholder
        placeholder = lines['run']['connection']['database']
        self.initial['run_dbname'] = placeholder
        placeholder = lines['run']['connection']['table']
        self.initial['run_tablename'] = placeholder
        placeholder = lines['run']['connection']['functions']['function_name_assigned']
        self.initial['run_function'] = placeholder
        placeholder = lines['run']['connection']['functions']['id_query_function_name_assigned']
        self.initial['run_id_function'] = placeholder
        placeholder = lines['run']['connection']['database']
        self.initial['run_dbname'] = placeholder
        placeholder = lines['run']['connection']['table']
        self.initial['run_tablename'] = placeholder
        placeholder = lines['run']['connection']['functions']['function_name_assigned']
        self.initial['run_function'] = placeholder
        placeholder = lines['run']['connection']['functions']['id_query_function_name_assigned']
        self.initial['run_id_function'] = placeholder
        placeholder = lines['run']['info']['name']
        self.initial['run_info_name'] = placeholder
        placeholder = lines['run']['info']['ontology_id']
        self.initial['run_info_ontology_id'] = placeholder
        placeholder = lines['run']['info']['ontology_name']
        self.initial['run_info_ontology_name'] = placeholder
        placeholder = lines['run']['info']['description']
        self.initial['run_info_description'] = placeholder
        placeholder = lines['run']['schema']['specification']
        self.initial['run_schema_specification'] = placeholder
        placeholder = lines['run']['schema']['default_schema_id']
        self.initial['run_schema_id'] = placeholder
        placeholder = lines['run']['schema']['default_schema_name']
        self.initial['run_schema_name'] = placeholder
        placeholder = lines['run']['schema']['default_schema_version']
        self.initial['run_schema_version'] = placeholder
        placeholder = lines['run']['schema']['supported_schemas']
        self.initial['run_supported_schemas'] = placeholder
        placeholder = lines['run']['schema']['reference_to_default_schema_definition']
        self.initial['run_schema_reference'] = placeholder
        analysis_initial_choices=initialize_lookup_endpoints('analysis', analysis_initial_choices)
        self.initial['AnalysisEndpoints'] = analysis_initial_choices
        biosample_initial_choices=initialize_lookup_endpoints('biosample', biosample_initial_choices)
        self.initial['BiosampleEndpoints'] = biosample_initial_choices
        cohort_initial_choices=initialize_lookup_endpoints('cohort', cohort_initial_choices)
        self.initial['CohortEndpoints'] = cohort_initial_choices
        dataset_initial_choices=initialize_lookup_endpoints('dataset', dataset_initial_choices)
        self.initial['DatasetEndpoints'] = dataset_initial_choices
        genomicVariant_initial_choices=initialize_lookup_endpoints('genomicVariant', genomicVariant_initial_choices)
        self.initial['GenomicVariantEndpoints'] = genomicVariant_initial_choices
        individual_initial_choices=initialize_lookup_endpoints('individual', individual_initial_choices)
        self.initial['IndividualEndpoints'] = individual_initial_choices
        run_initial_choices=initialize_lookup_endpoints('run', run_initial_choices)
        self.initial['RunEndpoints'] = run_initial_choices

    def clean(self):
        cleaned_data = super(EntryTypesForm, self).clean()
        analysis = cleaned_data.get("Analysis")
        analysis_endpoint_name = cleaned_data.get("AnalysisEndpointName")
        if analysis_endpoint_name == '' and analysis != None:
            self.add_error('AnalysisEndpointName', 'If analysis is checked, analysis endpoint name can not be empty')
        biosample = cleaned_data.get("Biosample")
        biosample_endpoint_name = cleaned_data.get("BiosampleEndpointName")
        if biosample_endpoint_name == '' and biosample != None:
            self.add_error('BiosampleEndpointName', 'If biosample is checked, analysis endpoint name can not be empty')
        cohort = cleaned_data.get("Cohort")
        cohort_endpoint_name = cleaned_data.get("CohortEndpointName")
        if cohort_endpoint_name == '' and cohort != None:
            self.add_error('CohortEndpointName', 'If cohort is checked, analysis endpoint name can not be empty')
        dataset = cleaned_data.get("Dataset")
        dataset_endpoint_name = cleaned_data.get("DatasetEndpointName")
        if dataset_endpoint_name == '' and dataset != None:
            self.add_error('DatasetEndpointName', 'If dataset is checked, analysis endpoint name can not be empty')
        genomicVariant = cleaned_data.get("GenomicVariant")
        genomicVariant_endpoint_name = cleaned_data.get("GenomicVariantEndpointName")
        if genomicVariant_endpoint_name == '' and genomicVariant != None:
            self.add_error('GenomicVariantEndpointName', 'If genomicVariant is checked, analysis endpoint name can not be empty')
        individual = cleaned_data.get("Individual")
        individual_endpoint_name = cleaned_data.get("IndividualEndpointName")
        if individual_endpoint_name == '' and individual != None:
            self.add_error('IndividualEndpointName', 'If individual is checked, analysis endpoint name can not be empty')
        run = cleaned_data.get("Run")
        run_endpoint_name = cleaned_data.get("RunEndpointName")
        if run_endpoint_name == '' and run != None:
            self.add_error('RunEndpointName', 'If run is checked, analysis endpoint name can not be empty')
    
    entry_type_choices = [("analysis", "analysis"), ("biosample", "biosample"), ("cohort", "cohort"), ("dataset", "dataset"), ("genomicVariant", "genomicVariant"), ("individual", "individual"), ("run", "run")]
    granularity_choices = [
    ('boolean', 'Boolean'),
    ('count', 'Count'),
    ('record', 'Record'),
    ]
    database_choices=[(name, name) for name in os.listdir("/home/app/web/beacon/connections")]
    analysis_entry_type, analysis_endpoint_name, analysis_lookups =get_entry_types('analysis')
    biosample_entry_type, biosample_endpoint_name, biosample_lookups =get_entry_types('biosample')
    cohort_entry_type, cohort_endpoint_name, cohort_lookups =get_entry_types('cohort')
    dataset_entry_type, dataset_endpoint_name, dataset_lookups =get_entry_types('dataset')
    genomicVariant_entry_type, genomicVariant_endpoint_name, genomicVariant_lookups =get_entry_types('genomicVariant')
    individual_entry_type, individual_endpoint_name, individual_lookups =get_entry_types('individual')
    run_entry_type, run_endpoint_name, run_lookups =get_entry_types('run')
    analysis = forms.BooleanField(required=False, help_text='/'+analysis_endpoint_name)
    analysisEndpointName = forms.CharField(required=False,help_text='Endpoint Name')
    analysisNonFiltered = forms.BooleanField(required=False, help_text='Analysis Non-Filtered Queries')
    analysis_choices=[]
    analysis_choices=generate_endpoints(analysis_choices, analysis_endpoint_name, biosample_endpoint_name, biosample_entry_type, analysis_lookups)
    analysis_choices=generate_endpoints(analysis_choices, analysis_endpoint_name, cohort_endpoint_name, cohort_entry_type, analysis_lookups)
    analysis_choices=generate_endpoints(analysis_choices, analysis_endpoint_name, dataset_endpoint_name, dataset_entry_type, analysis_lookups)
    analysis_choices=generate_endpoints(analysis_choices, analysis_endpoint_name, genomicVariant_endpoint_name, genomicVariant_entry_type, analysis_lookups)
    analysis_choices=generate_endpoints(analysis_choices, analysis_endpoint_name, individual_endpoint_name, individual_entry_type, analysis_lookups)
    analysis_choices=generate_endpoints(analysis_choices, analysis_endpoint_name, run_endpoint_name, run_entry_type, analysis_lookups)
    analysis_choices=generate_endpoints(analysis_choices, analysis_endpoint_name, analysis_endpoint_name, analysis_entry_type, analysis_lookups)
    analysisEndpoints = forms.MultipleChoiceField(
        choices=analysis_choices, 
        widget=forms.CheckboxSelectMultiple
    )
    analysis_granularity= forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=granularity_choices, 
    )
    analysis_engine= forms.ChoiceField(choices=database_choices, help_text="Database Engine")
    analysis_dbname= forms.CharField(required=False, help_text='Database Name')
    analysis_tablename= forms.CharField(required=False, help_text='Table/Collection Name')
    analysis_function= forms.CharField(required=False, help_text='Function Name Assigned')
    analysis_id_function= forms.CharField(required=False, help_text='Id Function Name Assigned')
    analysis_info_name= forms.CharField(required=False, help_text='Info Name')
    analysis_info_ontology_id= forms.CharField(required=False, help_text='Info Ontology ID')
    analysis_info_ontology_name= forms.CharField(required=False, help_text='Info Ontology Name')
    analysis_info_description= forms.CharField(required=False, help_text='Info Description')
    analysis_schema_specification= forms.CharField(required=False, help_text='Schema specification')
    analysis_schema_id= forms.CharField(required=False, help_text='Default Schema ID')
    analysis_schema_name= forms.CharField(required=False, help_text='Default Schema Name')
    analysis_schema_version= forms.CharField(required=False, help_text='Schema Version')
    analysis_supported_schemas= forms.CharField(required=False, help_text='Supported Schemas')
    analysis_schema_reference= forms.CharField(required=False, help_text='Schema reference')
    biosample = forms.BooleanField(required=False, help_text='/'+biosample_endpoint_name)
    biosampleEndpointName = forms.CharField(required=False,help_text='Endpoint Name')
    biosampleNonFiltered = forms.BooleanField(required=False, help_text='Biosample Non-Filtered Queries')
    biosample_choices=[]
    biosample_choices=generate_endpoints(biosample_choices, biosample_endpoint_name, analysis_endpoint_name, analysis_entry_type, biosample_lookups)
    biosample_choices=generate_endpoints(biosample_choices, biosample_endpoint_name, cohort_endpoint_name, cohort_entry_type, biosample_lookups)
    biosample_choices=generate_endpoints(biosample_choices, biosample_endpoint_name, dataset_endpoint_name, dataset_entry_type, biosample_lookups)
    biosample_choices=generate_endpoints(biosample_choices, biosample_endpoint_name, genomicVariant_endpoint_name, genomicVariant_entry_type, biosample_lookups)
    biosample_choices=generate_endpoints(biosample_choices, biosample_endpoint_name, individual_endpoint_name, individual_entry_type, biosample_lookups)
    biosample_choices=generate_endpoints(biosample_choices, biosample_endpoint_name, run_endpoint_name, run_entry_type, biosample_lookups)
    biosample_choices=generate_endpoints(biosample_choices, biosample_endpoint_name, biosample_endpoint_name, biosample_entry_type, biosample_lookups)
    biosampleEndpoints = forms.MultipleChoiceField(
        choices=biosample_choices, 
        widget=forms.CheckboxSelectMultiple
    )
    biosample_granularity= forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=granularity_choices, 
    )
    biosample_engine= forms.ChoiceField(choices=database_choices, help_text="Database Engine")
    biosample_dbname= forms.CharField(required=False, help_text='Database Name')
    biosample_tablename= forms.CharField(required=False, help_text='Table/Collection Name')
    biosample_function= forms.CharField(required=False, help_text='Function Name Assigned')
    biosample_id_function= forms.CharField(required=False, help_text='Id Function Name Assigned')
    biosample_info_name= forms.CharField(required=False, help_text='Info Name')
    biosample_info_ontology_id= forms.CharField(required=False, help_text='Info Ontology ID')
    biosample_info_ontology_name= forms.CharField(required=False, help_text='Info Ontology Name')
    biosample_info_description= forms.CharField(required=False, help_text='Info Description')
    biosample_schema_specification= forms.CharField(required=False, help_text='Schema specification')
    biosample_schema_id= forms.CharField(required=False, help_text='Default Schema ID')
    biosample_schema_name= forms.CharField(required=False, help_text='Default Schema Name')
    biosample_schema_version= forms.CharField(required=False, help_text='Schema Version')
    biosample_supported_schemas= forms.CharField(required=False, help_text='Supported Schemas')
    biosample_schema_reference= forms.CharField(required=False, help_text='Schema reference')
    cohort = forms.BooleanField(required=False, help_text='/'+cohort_endpoint_name)
    cohortEndpointName = forms.CharField(required=False,help_text='Endpoint Name')
    cohortNonFiltered = forms.BooleanField(required=False, help_text='Cohort Non-Filtered Queries')
    cohort_choices=[]
    cohort_choices=generate_endpoints(cohort_choices, cohort_endpoint_name, analysis_endpoint_name, analysis_entry_type, cohort_lookups)
    cohort_choices=generate_endpoints(cohort_choices, cohort_endpoint_name, biosample_endpoint_name, biosample_entry_type, cohort_lookups)
    cohort_choices=generate_endpoints(cohort_choices, cohort_endpoint_name, dataset_endpoint_name, dataset_entry_type, cohort_lookups)
    cohort_choices=generate_endpoints(cohort_choices, cohort_endpoint_name, genomicVariant_endpoint_name, genomicVariant_entry_type, cohort_lookups)
    cohort_choices=generate_endpoints(cohort_choices, cohort_endpoint_name, individual_endpoint_name, individual_entry_type, cohort_lookups)
    cohort_choices=generate_endpoints(cohort_choices, cohort_endpoint_name, run_endpoint_name, run_entry_type, cohort_lookups)
    cohort_choices=generate_endpoints(cohort_choices, cohort_endpoint_name, cohort_endpoint_name, cohort_entry_type, cohort_lookups)
    cohortEndpoints = forms.MultipleChoiceField(
        choices=cohort_choices, 
        widget=forms.CheckboxSelectMultiple
    )
    cohort_granularity= forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=granularity_choices, 
    )
    cohort_engine= forms.ChoiceField(choices=database_choices, help_text="Database Engine")
    cohort_dbname= forms.CharField(required=False, help_text='Database Name')
    cohort_tablename= forms.CharField(required=False, help_text='Table/Collection Name')
    cohort_function= forms.CharField(required=False, help_text='Function Name Assigned')
    cohort_id_function= forms.CharField(required=False, help_text='Id Function Name Assigned')
    cohort_info_name= forms.CharField(required=False, help_text='Info Name')
    cohort_info_ontology_id= forms.CharField(required=False, help_text='Info Ontology ID')
    cohort_info_ontology_name= forms.CharField(required=False, help_text='Info Ontology Name')
    cohort_info_description= forms.CharField(required=False, help_text='Info Description')
    cohort_schema_specification= forms.CharField(required=False, help_text='Schema specification')
    cohort_schema_id= forms.CharField(required=False, help_text='Default Schema ID')
    cohort_schema_name= forms.CharField(required=False, help_text='Default Schema Name')
    cohort_schema_version= forms.CharField(required=False, help_text='Schema Version')
    cohort_supported_schemas= forms.CharField(required=False, help_text='Supported Schemas')
    cohort_schema_reference= forms.CharField(required=False, help_text='Schema reference')
    dataset = forms.BooleanField(required=False, help_text='/'+dataset_endpoint_name)
    datasetEndpointName = forms.CharField(required=False,help_text='Endpoint Name')
    datasetNonFiltered = forms.BooleanField(required=False, help_text='Dataset Non-Filtered Queries')
    dataset_choices=[]
    dataset_choices=generate_endpoints(dataset_choices, dataset_endpoint_name, analysis_endpoint_name, analysis_entry_type, dataset_lookups)
    dataset_choices=generate_endpoints(dataset_choices, dataset_endpoint_name, biosample_endpoint_name, biosample_entry_type, dataset_lookups)
    dataset_choices=generate_endpoints(dataset_choices, dataset_endpoint_name, cohort_endpoint_name, cohort_entry_type, dataset_lookups)
    dataset_choices=generate_endpoints(dataset_choices, dataset_endpoint_name, genomicVariant_endpoint_name, genomicVariant_entry_type, dataset_lookups)
    dataset_choices=generate_endpoints(dataset_choices, dataset_endpoint_name, individual_endpoint_name, individual_entry_type, dataset_lookups)
    dataset_choices=generate_endpoints(dataset_choices, dataset_endpoint_name, run_endpoint_name, run_entry_type, dataset_lookups)
    dataset_choices=generate_endpoints(dataset_choices, dataset_endpoint_name, dataset_endpoint_name, dataset_entry_type, dataset_lookups)
    datasetEndpoints = forms.MultipleChoiceField(
        choices=dataset_choices, 
        widget=forms.CheckboxSelectMultiple
    )
    dataset_granularity= forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=granularity_choices, 
    )
    dataset_engine= forms.ChoiceField(choices=database_choices, help_text="Database Engine")
    dataset_dbname= forms.CharField(required=False, help_text='Database Name')
    dataset_tablename= forms.CharField(required=False, help_text='Table/Collection Name')
    dataset_function= forms.CharField(required=False, help_text='Function Name Assigned')
    dataset_id_function= forms.CharField(required=False, help_text='Id Function Name Assigned')
    dataset_info_name= forms.CharField(required=False, help_text='Info Name')
    dataset_info_ontology_id= forms.CharField(required=False, help_text='Info Ontology ID')
    dataset_info_ontology_name= forms.CharField(required=False, help_text='Info Ontology Name')
    dataset_info_description= forms.CharField(required=False, help_text='Info Description')
    dataset_schema_specification= forms.CharField(required=False, help_text='Schema specification')
    dataset_schema_id= forms.CharField(required=False, help_text='Default Schema ID')
    dataset_schema_name= forms.CharField(required=False, help_text='Default Schema Name')
    dataset_schema_version= forms.CharField(required=False, help_text='Schema Version')
    dataset_supported_schemas= forms.CharField(required=False, help_text='Supported Schemas')
    dataset_schema_reference= forms.CharField(required=False, help_text='Schema reference')
    genomicVariant = forms.BooleanField(required=False, help_text='/'+genomicVariant_endpoint_name)
    genomicVariantEndpointName = forms.CharField(required=False,help_text='Endpoint Name')
    genomicVariantNonFiltered = forms.BooleanField(required=False, help_text='Genomic Variant Non-Filtered Queries')
    genomicVariant_choices=[]
    genomicVariant_choices=generate_endpoints(genomicVariant_choices, genomicVariant_endpoint_name, analysis_endpoint_name, analysis_entry_type, genomicVariant_lookups)
    genomicVariant_choices=generate_endpoints(genomicVariant_choices, genomicVariant_endpoint_name, biosample_endpoint_name, biosample_entry_type, genomicVariant_lookups)
    genomicVariant_choices=generate_endpoints(genomicVariant_choices, genomicVariant_endpoint_name, cohort_endpoint_name, cohort_entry_type, genomicVariant_lookups)
    genomicVariant_choices=generate_endpoints(genomicVariant_choices, genomicVariant_endpoint_name, dataset_endpoint_name, dataset_entry_type, genomicVariant_lookups)
    genomicVariant_choices=generate_endpoints(genomicVariant_choices, genomicVariant_endpoint_name, individual_endpoint_name, individual_entry_type, genomicVariant_lookups)
    genomicVariant_choices=generate_endpoints(genomicVariant_choices, genomicVariant_endpoint_name, run_endpoint_name, run_entry_type, genomicVariant_lookups)
    genomicVariant_choices=generate_endpoints(genomicVariant_choices, genomicVariant_endpoint_name, genomicVariant_endpoint_name, genomicVariant_entry_type, genomicVariant_lookups)
    genomicVariantEndpoints = forms.MultipleChoiceField(
        choices=genomicVariant_choices, 
        widget=forms.CheckboxSelectMultiple
    )
    genomicVariant_granularity= forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=granularity_choices, 
    )
    genomicVariant_engine= forms.ChoiceField(choices=database_choices, help_text="Database Engine")
    genomicVariant_dbname= forms.CharField(required=False, help_text='Database Name')
    genomicVariant_tablename= forms.CharField(required=False, help_text='Table/Collection Name')
    genomicVariant_function= forms.CharField(required=False, help_text='Function Name Assigned')
    genomicVariant_id_function= forms.CharField(required=False, help_text='Id Function Name Assigned')
    genomicVariant_info_name= forms.CharField(required=False, help_text='Info Name')
    genomicVariant_info_ontology_id= forms.CharField(required=False, help_text='Info Ontology ID')
    genomicVariant_info_ontology_name= forms.CharField(required=False, help_text='Info Ontology Name')
    genomicVariant_info_description= forms.CharField(required=False, help_text='Info Description')
    genomicVariant_schema_specification= forms.CharField(required=False, help_text='Schema specification')
    genomicVariant_schema_id= forms.CharField(required=False, help_text='Default Schema ID')
    genomicVariant_schema_name= forms.CharField(required=False, help_text='Default Schema Name')
    genomicVariant_schema_version= forms.CharField(required=False, help_text='Schema Version')
    genomicVariant_supported_schemas= forms.CharField(required=False, help_text='Supported Schemas')
    genomicVariant_schema_reference= forms.CharField(required=False, help_text='Schema reference')
    individual = forms.BooleanField(required=False, help_text='/'+individual_endpoint_name)
    individualEndpointName = forms.CharField(required=False,help_text='Endpoint Name')
    individualNonFiltered = forms.BooleanField(required=False, help_text='Individual Non-Filtered Queries')
    individual_choices=[]
    individual_choices=generate_endpoints(individual_choices, individual_endpoint_name, analysis_endpoint_name, analysis_entry_type, individual_lookups)
    individual_choices=generate_endpoints(individual_choices, individual_endpoint_name, biosample_endpoint_name, biosample_entry_type, individual_lookups)
    individual_choices=generate_endpoints(individual_choices, individual_endpoint_name, cohort_endpoint_name, cohort_entry_type, individual_lookups)
    individual_choices=generate_endpoints(individual_choices, individual_endpoint_name, dataset_endpoint_name, dataset_entry_type, individual_lookups)
    individual_choices=generate_endpoints(individual_choices, individual_endpoint_name, genomicVariant_endpoint_name, genomicVariant_entry_type, individual_lookups)
    individual_choices=generate_endpoints(individual_choices, individual_endpoint_name, run_endpoint_name, run_entry_type, individual_lookups)
    individual_choices=generate_endpoints(individual_choices, individual_endpoint_name, individual_endpoint_name, individual_entry_type, individual_lookups)
    individualEndpoints = forms.MultipleChoiceField(
        choices=individual_choices, 
        widget=forms.CheckboxSelectMultiple
    )
    individual_granularity= forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=granularity_choices, 
    )
    individual_engine= forms.ChoiceField(choices=database_choices, help_text="Database Engine")
    individual_dbname= forms.CharField(required=False, help_text='Database Name')
    individual_tablename= forms.CharField(required=False, help_text='Table/Collection Name')
    individual_function= forms.CharField(required=False, help_text='Function Name Assigned')
    individual_id_function= forms.CharField(required=False, help_text='Id Function Name Assigned')
    individual_info_name= forms.CharField(required=False, help_text='Info Name')
    individual_info_ontology_id= forms.CharField(required=False, help_text='Info Ontology ID')
    individual_info_ontology_name= forms.CharField(required=False, help_text='Info Ontology Name')
    individual_info_description= forms.CharField(required=False, help_text='Info Description')
    individual_schema_specification= forms.CharField(required=False, help_text='Schema specification')
    individual_schema_id= forms.CharField(required=False, help_text='Default Schema ID')
    individual_schema_name= forms.CharField(required=False, help_text='Default Schema Name')
    individual_schema_version= forms.CharField(required=False, help_text='Schema Version')
    individual_supported_schemas= forms.CharField(required=False, help_text='Supported Schemas')
    individual_schema_reference= forms.CharField(required=False, help_text='Schema reference')
    run = forms.BooleanField(required=False, help_text='/'+run_endpoint_name)
    runEndpointName = forms.CharField(required=False,help_text='Endpoint Name')
    runNonFiltered = forms.BooleanField(required=False, help_text='Run Non-Filtered Queries')
    run_choices=[]
    run_choices=generate_endpoints(run_choices, run_endpoint_name, analysis_endpoint_name, analysis_entry_type, run_lookups)
    run_choices=generate_endpoints(run_choices, run_endpoint_name, biosample_endpoint_name, biosample_entry_type, run_lookups)
    run_choices=generate_endpoints(run_choices, run_endpoint_name, cohort_endpoint_name, cohort_entry_type, run_lookups)
    run_choices=generate_endpoints(run_choices, run_endpoint_name, dataset_endpoint_name, dataset_entry_type, run_lookups)
    run_choices=generate_endpoints(run_choices, run_endpoint_name, genomicVariant_endpoint_name, genomicVariant_entry_type, run_lookups)
    run_choices=generate_endpoints(run_choices, run_endpoint_name, individual_endpoint_name, individual_entry_type, run_lookups)
    run_choices=generate_endpoints(run_choices, run_endpoint_name, run_endpoint_name, run_entry_type, run_lookups)
    runEndpoints = forms.MultipleChoiceField(
        choices=run_choices, 
        widget=forms.CheckboxSelectMultiple
    )
    run_granularity= forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=granularity_choices, 
    )
    run_engine= forms.ChoiceField(choices=database_choices, help_text="Database Engine")
    run_dbname= forms.CharField(required=False, help_text='Database Name')
    run_tablename= forms.CharField(required=False, help_text='Table/Collection Name')
    run_function= forms.CharField(required=False, help_text='Function Name Assigned')
    run_id_function= forms.CharField(required=False, help_text='Id Function Name Assigned')
    run_info_name= forms.CharField(required=False, help_text='Info Name')
    run_info_ontology_id= forms.CharField(required=False, help_text='Info Ontology ID')
    run_info_ontology_name= forms.CharField(required=False, help_text='Info Ontology Name')
    run_info_description= forms.CharField(required=False, help_text='Info Description')
    run_schema_specification= forms.CharField(required=False, help_text='Schema specification')
    run_schema_id= forms.CharField(required=False, help_text='Default Schema ID')
    run_schema_name= forms.CharField(required=False, help_text='Default Schema Name')
    run_schema_version= forms.CharField(required=False, help_text='Schema Version')
    run_supported_schemas= forms.CharField(required=False, help_text='Supported Schemas')
    run_schema_reference= forms.CharField(required=False, help_text='Schema reference')