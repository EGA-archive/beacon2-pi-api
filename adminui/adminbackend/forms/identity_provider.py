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


class IDPForm(forms.Form):
    IdentityProvider = forms.CharField(help_text='Identity Provider')
    Issuer = forms.CharField(required=False,help_text='Issuer')
    ClientID = forms.CharField(required=False,help_text='Client ID')
    ClientSecret = forms.CharField(required=False,help_text='Client Secret')
    UserInfo = forms.CharField(required=False,help_text='User Info')
    Introspection = forms.CharField(required=False,help_text='Introspection')
    JWKSURL = forms.CharField(required=False,help_text='JWKS URL')
    