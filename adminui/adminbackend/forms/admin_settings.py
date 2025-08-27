from django import forms
import yaml
import logging
from django.contrib.auth.models import Group

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


class AdminForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(AdminForm, self).__init__(*args, **kwargs)
        # assign a (computed, I assume) default value to the choice field
        self.fields['Email'].widget.attrs['readonly'] = True
         
    Email = forms.EmailField()
    groups = Group.objects.all()
    groups_choices=[(group.name,group.name) for group in groups]
    Groups = forms.ChoiceField(choices=groups_choices)