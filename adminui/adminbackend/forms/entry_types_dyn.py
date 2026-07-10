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
    def __init__(self, *args, model=None, entry_type=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        self.entry_type = entry_type
        filename = (
            f"/home/app/web/beacon/models/"
            f"{model}/conf/entry_types/{entry_type}.yml"
        )
        with open(filename) as f:
            entry_type_yaml = yaml.safe_load(f)
        config = entry_type_yaml[entry_type]
        initial_choices=[]
        self.initial['entry_type_name']=entry_type
        self.fields['entry_type_name'].widget.attrs['readonly'] = True
        self.initial['entry_typeEndpointName']=config['endpoint_name']
        self.initial['entry_typeNonFiltered']=config['allow_queries_without_filters']
        self.initial['entry_type_id'] = config['allow_id_query']
        placeholder = config['max_granularity']
        self.initial['entry_type_granularity'] = placeholder
        placeholder = config['connection']['name']
        self.initial['entry_type_engine'] = placeholder
        placeholder = config['connection']['database']
        self.initial['entry_type_dbname'] = placeholder
        placeholder = config['connection']['table']
        self.initial['entry_type_tablename'] = placeholder
        placeholder = config['connection']['functions']['function_name_assigned']
        self.initial['entry_type_function'] = placeholder
        placeholder = config['connection']['functions']['id_query_function_name_assigned']
        self.initial['entry_type_id_function'] = placeholder
        placeholder = config['info']['name']
        self.initial['entry_type_info_name'] = placeholder
        placeholder = config['info']['ontology_id']
        self.initial['entry_type_info_ontology_id'] = placeholder
        placeholder = config['info']['ontology_name']
        self.initial['entry_type_info_ontology_name'] = placeholder
        placeholder = config['info']['description']
        self.initial['entry_type_info_description'] = placeholder
        placeholder = config['schema']['specification']
        self.initial['entry_type_schema_specification'] = placeholder
        placeholder = config['schema']['default_schema_id']
        self.initial['entry_type_schema_id'] = placeholder
        placeholder = config['schema']['default_schema_name']
        self.initial['entry_type_schema_name'] = placeholder
        placeholder = config['schema']['default_schema_version']
        self.initial['entry_type_schema_version'] = placeholder
        placeholder = config['schema']['supported_schemas']
        self.initial['entry_type_supported_schemas'] = placeholder
        placeholder = config['schema']['reference_to_default_schema_definition']
        self.initial['entry_type_schema_reference'] = placeholder
        placeholder = config['response_type']
        self.initial['entry_type_response_type'] = placeholder
        placeholder = config['open_api_definition']
        self.initial['entry_type_open_api_definition'] = placeholder
    def clean(self):
        cleaned_data = super(EntryTypeForm, self).clean()
        cleaned_entry_type = cleaned_data.get(self.entry_type)
        cleaned_endpoint_name = cleaned_data.get("entry_typeEndpointName")
        if cleaned_endpoint_name == '' and cleaned_entry_type != None:
            self.add_error('entry_typeEndpointName', 'If {} is checked, {} endpoint name can not be empty'.format(self.entry_type, self.entry_type))
    database_choices=[(name, name) for name in os.listdir("/home/app/web/beacon/connections")]
    granularity_choices = [
    ('boolean', 'Boolean'),
    ('count', 'Count'),
    ('record', 'Record'),
    ]
    entry_type_name=forms.CharField(required=False,help_text='Name of the entry type')
    entry_typeEndpointName = forms.CharField(required=False,help_text='Endpoint Name')
    entry_type = forms.BooleanField(required=False, help_text='/entry_type')
    entry_type_id = forms.BooleanField(required=False, help_text='/'+'entry_type')
    entry_typeNonFiltered = forms.BooleanField(required=False, help_text='entry_type Non-Filtered Queries')
    entry_type_granularity= forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=granularity_choices, 
    )
    entry_type_response_type=forms.CharField(required=False,help_text='Response type')
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
    entry_type_open_api_definition=forms.CharField(required=False,help_text='Open API definition')

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

class LookupsForm(forms.Form):
    def __init__(self, *args, model=None, entry_type=None, lookup=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        self.entry_type = entry_type
        self.lookup = lookup
        filename = (
            f"/home/app/web/beacon/models/"
            f"{model}/conf/entry_types/{entry_type}.yml"
        )
        with open(filename) as f:
            entry_type_yaml = yaml.safe_load(f)
        for k, v in entry_type_yaml[entry_type]['lookups'].items():
            if k == self.lookup:
                self.initial['lookup_name']=k
                self.initial['lookup_response_type']=v['response_type']
                self.initial['lookup_endpoint_name']=v['endpoint_name']
                self.initial['lookup']=v['endpoint_enabled']
                self.initial['lookup_engine']=v['connection']['name']
                self.initial['lookup_dbname']=v['connection']['database']
                self.initial['lookup_tablename']=v['connection']['table']
                self.initial['lookup_function']=v['connection']['functions']['function_name_assigned']
    def clean(self):
        cleaned_data = super(LookupsForm, self).clean()
        cleaned_lookup = cleaned_data.get(self.lookup)
        cleaned_lookup_endpoint_name = cleaned_data.get("entry_typeEndpointName")
        if cleaned_lookup_endpoint_name == '' and cleaned_lookup != None:
            self.add_error('lookup_endpoint_name', 'If {} is checked, {} endpoint name can not be empty'.format(self.lookup, self.lookup))
    database_choices=[(name, name) for name in os.listdir("/home/app/web/beacon/connections")]
    lookup_name = forms.CharField(required=False,help_text='Name of the lookup')
    lookup_endpoint_name = forms.CharField(required=False,help_text='Endpoint Name of the lookup')
    lookup_response_type = forms.CharField(required=False,help_text='Lookup Response type')
    lookup = forms.BooleanField(required=False, help_text='/entry_type')
    lookup_engine = forms.ChoiceField(choices=database_choices, help_text="Lookup Database Engine")
    lookup_dbname= forms.CharField(required=False, help_text='Lookup Database Name')
    lookup_tablename= forms.CharField(required=False, help_text='Lookup Table/Collection Name')
    lookup_function= forms.CharField(required=False, help_text='Lookup Function Name Assigned')