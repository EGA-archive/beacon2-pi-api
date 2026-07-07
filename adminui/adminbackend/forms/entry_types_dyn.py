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

class EntryTypeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(EntryTypeForm, self).__init__(*args, **kwargs)
        with open("/home/app/web/beacon/conf/models/models_conf.yml") as f:
            models_conf = yaml.safe_load(f)
        for k, v in models_conf.items():
            if v['model_enabled'] == True:
                dirs = os.listdir("/home/app/web/beacon/models"+k+"/conf/entry_types")
                for filename in dirs:
                    initial_choices=[]
                    with open("/home/app/web/beacon/models/"+k+"/conf/entry_types/"+filename) as f:
                        entry_type_lines = yaml.safe_load(f)
                    self.initial['entry_type_name']=filename
                    self.initial['entry_typeEndpointName']=entry_type_lines[filename]['endpoint_name']
                    self.initial['entry_typeNonFiltered']=entry_type_lines[filename]['allow_queries_without_filters']
                    self.initial['entry_type_id'] = entry_type_lines[filename]['allow_id_query']
                    placeholder = entry_type_lines[filename]['max_granularity']
                    self.initial['entry_type_granularity'] = placeholder
                    placeholder = entry_type_lines[filename]['connection']['name']
                    self.initial['entry_type_engine'] = placeholder
                    placeholder = entry_type_lines[filename]['connection']['database']
                    self.initial['entry_type_dbname'] = placeholder
                    placeholder = entry_type_lines[filename]['connection']['table']
                    self.initial['entry_type_tablename'] = placeholder
                    placeholder = entry_type_lines[filename]['connection']['functions']['function_name_assigned']
                    self.initial['entry_type_function'] = placeholder
                    placeholder = entry_type_lines[filename]['connection']['functions']['id_query_function_name_assigned']
                    self.initial['entry_type_id_function'] = placeholder
                    placeholder = entry_type_lines[filename]['info']['name']
                    self.initial['entry_type_info_name'] = placeholder
                    placeholder = entry_type_lines[filename]['info']['ontology_id']
                    self.initial['entry_type_info_ontology_id'] = placeholder
                    placeholder = entry_type_lines[filename]['info']['ontology_name']
                    self.initial['entry_type_info_ontology_name'] = placeholder
                    placeholder = entry_type_lines[filename]['info']['description']
                    self.initial['entry_type_info_description'] = placeholder
                    placeholder = entry_type_lines[filename]['schema']['specification']
                    self.initial['entry_type_schema_specification'] = placeholder
                    placeholder = entry_type_lines[filename]['schema']['default_schema_id']
                    self.initial['entry_type_schema_id'] = placeholder
                    placeholder = entry_type_lines[filename]['schema']['default_schema_name']
                    self.initial['entry_type_schema_name'] = placeholder
                    placeholder = entry_type_lines[filename]['schema']['default_schema_version']
                    self.initial['entry_type_schema_version'] = placeholder
                    placeholder = entry_type_lines[filename]['schema']['supported_schemas']
                    self.initial['entry_type_supported_schemas'] = placeholder
                    placeholder = entry_type_lines[filename]['schema']['reference_to_default_schema_definition']
                    self.initial['entry_type_schema_reference'] = placeholder
    def clean(self):
        cleaned_data = super(EntryTypeForm, self).clean()
        with open("/home/app/web/beacon/conf/models/models_conf.yml") as f:
            models_conf = yaml.safe_load(f)
        for k, v in models_conf.items():
            if v['model_enabled'] == True:
                dirs = os.listdir("/home/app/web/beacon/models"+k+"/conf/entry_types")
                for filename in dirs:
                    if self.entry_type_name == filename:
                        cleaned_entry_type = cleaned_data.get(filename)
                        cleaned_endpoint_name = cleaned_data.get("entry_typeEndpointName")
                        if cleaned_endpoint_name == '' and cleaned_entry_type != None:
                            self.add_error('entry_typeEndpointName', 'If {} is checked, {} endpoint name can not be empty'.format(filename, filename))
    database_choices=[(name, name) for name in os.listdir("/home/app/web/beacon/connections")]
    granularity_choices = [
    ('boolean', 'Boolean'),
    ('count', 'Count'),
    ('record', 'Record'),
    ]
    entry_type_name=forms.CharField(required=False,help_text='Name of the entry type')
    entry_typeEndpointName = forms.CharField(required=False,help_text='Endpoint Name')
    entry_type = forms.BooleanField(required=False, help_text='/'+entry_typeEndpointName+'/{id}')
    entry_type_id = forms.BooleanField(required=False, help_text='/'+'entry_type')
    entry_typeNonFiltered = forms.BooleanField(required=False, help_text='entry_type Non-Filtered Queries')
    entry_type_granularity= forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=granularity_choices, 
    )
    entry_type_engine= forms.ChoiceField(choices=database_choices, help_text="Database Engine")
    entry_type_dbname= forms.CharField(required=False, help_text='Database Name')
    entry_type_tablename= forms.CharField(required=False, help_text='Table/Collection Name')
    entry_type_function= forms.CharField(required=False, help_text='Function Name Assigned')
    entry_type_id_function= forms.CharField(required=False, help_text='Id Function Name Assigned')
    entry_type_info_name= forms.CharField(required=False, help_text='Info Name')
    entry_type_info_ontology_id= forms.CharField(required=False, help_text='Info Ontology ID')
    entry_type_info_ontology_name= forms.CharField(required=False, help_text='Info Ontology Name')
    entry_type_info_description= forms.CharField(required=False, help_text='Info Description')
    entry_type_schema_specification= forms.CharField(required=False, help_text='Schema specification')
    entry_type_schema_id= forms.CharField(required=False, help_text='Default Schema ID')
    entry_type_schema_name= forms.CharField(required=False, help_text='Default Schema Name')
    entry_type_schema_version= forms.CharField(required=False, help_text='Schema Version')
    entry_type_supported_schemas= forms.CharField(required=False, help_text='Supported Schemas')
    entry_type_schema_reference= forms.CharField(required=False, help_text='Schema reference')
    entry_type_choices = []
    with open("/home/app/web/beacon/conf/models/models_conf.yml") as f:
        models_conf = yaml.safe_load(f)
    for k, v in models_conf.items():
        if v['model_enabled'] == True:
            dirs = os.listdir("/home/app/web/beacon/models/"+k+"/conf/entry_types")
            for filename in dirs:
                with open("/home/app/web/beacon/models/"+k+"/conf/entry_types/"+filename+".yml") as entrytypeyaml:
                    yamlfile = yaml.safe_load(entrytypeyaml)
                entry_type_choices.append((filename, filename))

    entry_typeEndpoints = forms.MultipleChoiceField(
        choices=entry_type_choices, 
        widget=forms.CheckboxSelectMultiple
    )


class ModelsForm(forms.Form):
    with open("/home/app/web/beacon/conf/models/models_conf.yml") as f:
        models_conf = yaml.safe_load(f)
    models_choices=[]
    for k, v in models_conf.items():
        if v['model_enabled'] == True:
            models_choices.append(k)
    models_tabs=forms.ChoiceField(
        choices=models_choices, 
        widget=forms.RadioSelect
    )