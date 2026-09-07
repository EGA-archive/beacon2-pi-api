from django import forms
import yaml
import logging
import os
from beacon.conf.conf_override import config
from dotenv import load_dotenv, set_key

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

class ConnectionsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.dire = kwargs.pop('dire')
        super(ConnectionsForm,self).__init__(*args,**kwargs)

        load_dotenv("/home/app/web/beacon/connections/" + self.dire + "/conf.env", override=True)
        self.initial['Host'] = os.getenv('database_host')
        self.initial['Port'] = os.getenv('database_port')
        self.initial['User'] = os.getenv('database_user')
        self.initial['Password'] = os.getenv('database_password')
        self.initial['Name'] = os.getenv('database_name')
        self.initial['Auth'] = os.getenv('database_auth_source')
        self.initial['Certificate'] = os.getenv('database_certificate')
        self.initial['CAFile'] = os.getenv('database_cafile')
        self.initial['Cluster'] = os.getenv('database_cluster')

    Host = forms.CharField(help_text='Host', required=False)
    Port = forms.IntegerField(help_text='Port', required=False)
    User = forms.CharField(help_text='User', required=False)
    Password = forms.CharField(help_text='Password')
    Name = forms.CharField(help_text='Database name', required=False)
    Auth = forms.CharField(help_text='Auth database name', required=False)
    Certificate = forms.CharField(help_text='Path to certificate', required=False)
    CAFile = forms.CharField(help_text='Path to CAFile', required=False)
    Cluster = forms.BooleanField(help_text='Cluster', required=False)

class APIConnection(forms.Form):
    def __init__(self, *args, **kwargs):
        super(APIConnection,self).__init__(*args,**kwargs)
        self.initial['Connection'] = config.complete_url
    Connection = forms.URLField()

class UIConnection(forms.Form):
    def __init__(self, *args, **kwargs):
        super(UIConnection,self).__init__(*args,**kwargs)
        self.initial['Connection'] = config.welcome_url
    Connection = forms.URLField()
    