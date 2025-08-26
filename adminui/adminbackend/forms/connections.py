from django import forms
import yaml
import logging
import os
from beacon.conf.conf import uri

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

        # assign a (computed, I assume) default value to the choice field
        with open("adminui/beacon/connections/" + self.dire + "/conf.py") as f:
            lines = f.readlines()
        with open("adminui/beacon/connections/" + self.dire + "/conf.py", "r") as f:
            for line in lines:
                if 'database_host' in str(line):
                    placeholder = formatting_field(self, line)
                    self.initial['Host'] = placeholder
                elif 'host' in str(line):
                    placeholder = formatting_field(self, line)
                    self.initial['Host'] = placeholder
                elif 'database_port' in str(line):
                    placeholder = formatting_field(self, line)
                    self.initial['Port'] = placeholder
                elif 'database_user' in str(line):
                    placeholder = formatting_field(self, line)
                    self.initial['User'] = placeholder
                elif 'username' in str(line):
                    placeholder = formatting_field(self, line)
                    self.initial['User'] = placeholder
                elif 'database_password' in str(line):
                    placeholder = formatting_field(self, line)
                    self.initial['Password'] = placeholder
                elif 'password' in str(line):
                    placeholder = formatting_field(self, line)
                    self.initial['Password'] = placeholder
                elif 'database_user' in str(line):
                    placeholder = formatting_field(self, line)
                    self.initial['User'] = placeholder
                elif 'database_name' in str(line):
                    placeholder = formatting_field(self, line)
                    self.initial['Name'] = placeholder
                elif 'database_auth_source' in str(line):
                    placeholder = formatting_field(self, line)
                    self.initial['Auth'] = placeholder
                elif 'database_certificate' in str(line):
                    placeholder = formatting_field(self, line)
                    self.initial['Certificate'] = placeholder
                elif 'database_cafile' in str(line):
                    placeholder = formatting_field(self, line)
                    self.initial['CAFile'] = placeholder
                elif 'database_cluster' in str(line):
                    placeholder = formatting_field(self, line)
                    self.initial['Cluster'] = placeholder

    Host = forms.CharField(help_text='Host', required=False)
    Port = forms.IntegerField(help_text='Port', required=False)
    User = forms.CharField(help_text='User', required=False)
    Password = forms.CharField(help_text='Password')
    Name = forms.CharField(help_text='Database name', required=False)
    Auth = forms.CharField(help_text='Auth database name', required=False)
    Certificate = forms.CharField(help_text='Path to certificate', required=False)
    CAFile = forms.CharField(help_text='Path to CAFile', required=False)
    Cluster = forms.BooleanField(help_text='Cluster', required=False)

class ChooseConnection(forms.Form):
    dirs = os.listdir("adminui/beacon/connections")
    list_of_dirs=[]
    for dir in dirs:
        list_of_dirs.append((dir,dir))
    list_of_dirs.append(('API', 'API'))
    list_of_dirs.append(('UI', 'UI'))
    Connection = forms.ChoiceField(choices=list_of_dirs)

class LinkConnection(forms.Form):
    def __init__(self, *args, **kwargs):
        super(LinkConnection,self).__init__(*args,**kwargs)
        self.initial['Connection'] = uri
    Connection = forms.URLField()
    