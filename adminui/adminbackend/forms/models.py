from django import forms
import yaml
import logging
import os

class ModelsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ModelsForm, self).__init__(*args, **kwargs)
        # assign a (computed, I assume) default value to the choice field
        with open("/home/app/web/beacon/conf/models/models_conf.yml") as f:
            models_conf = yaml.safe_load(f)
        for k, v in models_conf.items():
            self.fields[k] = forms.BooleanField(
                required=False,
                help_text=str(k),
            )
            self.initial[k]=bool(v["model_enabled"])