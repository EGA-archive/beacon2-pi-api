from django import forms
import yaml
import os

def get_all_entry_types():
    entry_types=[]
    with open("/home/app/web/beacon/conf/models/models_conf.yml", 'r') as pfile:
        models_confile= yaml.safe_load(pfile)
    dirs = os.listdir("/home/app/web/beacon/models")
    for folder in dirs:
        subdirs = os.listdir("/home/app/web/beacon/models/"+folder)
        if folder in models_confile:
            if models_confile[folder]["model_enabled"] == False:
                continue
        # Go over the conf for the entry types of the models enabled
        if "conf" in subdirs:
            path = (
                "/home/app/web/beacon/models/"
                f"{folder}/conf/entry_types"
            )
            for filename in os.listdir(path):

                if filename.endswith(".yml"):
                    entry_type = filename[:-4]
                    entry_types.append((entry_type,entry_type))
        else:
            for subfolder in subdirs:
                if subfolder not in ['validator', 'conf', 'connections']:
                    underdirs = os.listdir("/home/app/web/beacon/models/"+folder+"/"+subfolder)
                    if folder+'/'+subfolder in models_confile:
                        if models_confile[folder+'/'+subfolder ]["model_enabled"] == False:
                            continue
                    # Go over the conf for the entry types of the models enabled
                    if "conf" in underdirs:
                        path = (
                            "/home/app/web/beacon/models/"
                            f"{folder}/{subfolder}/conf/entry_types"
                        )
                        for filename in os.listdir(path):

                            if filename.endswith(".yml"):
                                entry_type = filename[:-4]
                                entry_types.append((entry_type,entry_type))

    return entry_types

class FilteringTermsForm(forms.Form):
    FilteringTermID = forms.CharField(required=False)
    FilteringTermsList = forms.FileField(required=False)
    ScanDB = forms.CharField(required=False)
    SearchAscendant = forms.CharField(required=False)

class AddFilteringTerm(forms.Form):
    Synonym_FilteringTermID = forms.CharField(required=True, help_text="Id")
    type_choices = [("Ontology", "Ontology"), ("Alphanumeric", "Alphanumeric")]
    FilteringTermType = forms.ChoiceField(choices=type_choices, help_text="Type", required=True)
    FilteringTermLabel = forms.CharField(required=False, help_text="Label")
    Synonym = forms.CharField(help_text='Synonym', required=False)
    Scope = forms.MultipleChoiceField(
        choices=get_all_entry_types(), 
        widget=forms.CheckboxSelectMultiple,
        required=True,
        help_text="Scope"
    )