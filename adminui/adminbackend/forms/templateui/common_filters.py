from django import forms
import yaml
import logging
import os
import json

with open("/home/app/web/template-ui-config.json") as config_file:
    TEMPLATE_CONF = json.load(config_file)

class GroupForm(forms.Form):
    def __init__(self, *args, category=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["labels"].help_text = category
        supported_choices = []
        initial_choices = TEMPLATE_CONF["ui"]["commonFilters"]["filterLabels"][category]
        for initial_choice in initial_choices:
            supported_choices.append((initial_choice, initial_choice))
        self.fields['labels'].choices = supported_choices
        self.fields["labels"].initial = [
            value for value, label in supported_choices
        ]    
    labels=forms.MultipleChoiceField(
            choices=[], 
            widget=forms.CheckboxSelectMultiple,
            required=True
        )