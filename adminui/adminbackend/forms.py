from django import forms

class BamForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(BamForm, self).__init__(*args, **kwargs)
        # assign a (computed, I assume) default value to the choice field
        with open("adminui/beacon/conf/conf.py") as f:
            lines = f.readlines()
        with open("adminui/beacon/conf/conf.py", "r") as f:
            new_lines =''
            for line in lines:
                if 'beacon_name' in str(line):
                    linestring=str(line)
                    splitted_line=linestring.split("=")
                    placeholder=splitted_line[1].replace("'", '')
                    if isinstance(placeholder, str):
                        placeholder.strip()
                    if "#" in placeholder:
                        placeholder_def=placeholder.split('#')
                        placeholder=placeholder_def[0]
                        placeholder=placeholder.strip()
                    self.initial['BeaconName'] = placeholder
                elif 'beacon_id' in str(line):
                    linestring=str(line)
                    splitted_line=linestring.split("=")
                    placeholder=splitted_line[1].replace("'", '')
                    if isinstance(placeholder, str):
                        placeholder.strip()
                    if "#" in placeholder:
                        placeholder_def=placeholder.split('#')
                        placeholder=placeholder_def[0]
                        placeholder=placeholder.strip()
                    self.initial['BeaconId'] = placeholder
                elif 'environment' in str(line):
                    linestring=str(line)
                    splitted_line=linestring.split("=")
                    placeholder=splitted_line[1].replace("'", '')
                    if isinstance(placeholder, str):
                        placeholder.strip()
                    if "#" in placeholder:
                        placeholder_def=placeholder.split('#')
                        placeholder=placeholder_def[0]
                        placeholder=placeholder.strip()
                    self.initial['Environment'] = placeholder
         
    BeaconName = forms.CharField(help_text='Beacon Name')
    BeaconId = forms.CharField(help_text='Beacon Id')
    environment_choices = [("TEST", "TEST"), ("DEV", "DEV"), ("PROD", "PROD")]
    Environment = forms.ChoiceField(choices=environment_choices, help_text="Environment")