from django import forms
import yaml
import logging
import os
from beacon.conf.conf_override import config
from dotenv import load_dotenv, set_key

class ConnectionsForm(forms.Form):
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
    