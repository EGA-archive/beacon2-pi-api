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

class FilteringTermsForm(forms.Form):
    FilteringTermID = forms.CharField(required=False)
    FilteringTermsList = forms.FileField(required=False)

class AddFilteringTerm(forms.Form):
    Synonym_FilteringTermID = forms.CharField(required=True, help_text="Id")
    type_choices = [("Ontology", "Ontology"), ("Alphanumeric", "Alphanumeric")]
    FilteringTermType = forms.ChoiceField(choices=type_choices, help_text="Type", required=True)
    FilteringTermLabel = forms.CharField(required=True, help_text="Label")
    Synonym = forms.CharField(help_text='Synonym', required=False)
