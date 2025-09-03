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


class RoundingCountsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(RoundingCountsForm, self).__init__(*args, **kwargs)
        # assign a (computed, I assume) default value to the choice field
        with open("/home/app/web/beacon/conf/conf.py") as f:
            lines = f.readlines()
        with open("/home/app/web/beacon/conf/conf.py", "r") as f:
            for line in lines:
                if 'round_to_tens' in str(line):
                    placeholder = formatting_field(self, line)
                    if placeholder == 'True':
                        self.initial['Activate'] = True
                        self.initial['Rounding'] = 'tenths'
                        self.initial['Type'] = 'rounded'
                elif 'round_to_hundreds' in str(line):
                    placeholder = formatting_field(self, line)
                    if placeholder == 'True':
                        self.initial['Activate'] = True
                        self.initial['Rounding'] = 'hundredths'
                        self.initial['Type'] = 'rounded'
                elif 'imprecise_count' in str(line):
                    placeholder = formatting_field(self, line)
                    self.initial['Imprecise'] = placeholder
                    if placeholder != '0':
                        self.initial['Activate'] = True
                        self.initial['Type'] = 'imprecise'
    Activate = forms.BooleanField(help_text='activate')
    precision_choices = [('imprecise', 'imprecise'), ('rounded', 'rounded')]
    Type = forms.ChoiceField(choices=precision_choices, help_text="Precision of the counts")
    type_choices = [('tenths', 'tenths'), ('hundredths','hundredths')]
    Rounding = forms.ChoiceField(choices=type_choices, help_text='Rounded to tenths or hundredths', required=False)
    Imprecise = forms.IntegerField(help_text='Threshold lowest value', required=False)
    