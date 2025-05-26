from django import forms
import yaml

class BamForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(BamForm, self).__init__(*args, **kwargs)
        # assign a (computed, I assume) default value to the choice field
        self.fields['APIVersion'].widget.attrs['readonly'] = True
        self.fields['BeaconVersion'].widget.attrs['readonly'] = True
        with open("adminui/beacon/conf/conf.py") as f:
            lines = f.readlines()
        with open("adminui/beacon/conf/conf.py", "r") as f:
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
                elif 'api_version=' in str(line) or 'api_version =' in str(line):
                    linestring=str(line)
                    splitted_line=linestring.split("=")
                    placeholder=splitted_line[1].replace("'", '')
                    if isinstance(placeholder, str):
                        placeholder.strip()
                    if "#" in placeholder:
                        placeholder_def=placeholder.split('#')
                        placeholder=placeholder_def[0]
                        placeholder=placeholder.strip()
                    self.initial['APIVersion'] = placeholder
                elif 'org_id' in str(line):
                    linestring=str(line)
                    splitted_line=linestring.split("=")
                    placeholder=splitted_line[1].replace("'", '')
                    if isinstance(placeholder, str):
                        placeholder.strip()
                    if "#" in placeholder:
                        placeholder_def=placeholder.split('#')
                        placeholder=placeholder_def[0]
                        placeholder=placeholder.strip()
                    self.initial['OrgId'] = placeholder
                elif 'org_name' in str(line):
                    linestring=str(line)
                    splitted_line=linestring.split("=")
                    placeholder=splitted_line[1].replace("'", '')
                    if isinstance(placeholder, str):
                        placeholder.strip()
                    if "#" in placeholder:
                        placeholder_def=placeholder.split('#')
                        placeholder=placeholder_def[0]
                        placeholder=placeholder.strip()
                    self.initial['OrgName'] = placeholder
                elif 'org_description' in str(line):
                    linestring=str(line)
                    splitted_line=linestring.split("=")
                    placeholder=splitted_line[1].replace("'", '')
                    if isinstance(placeholder, str):
                        placeholder.strip()
                    if "#" in placeholder:
                        placeholder_def=placeholder.split('#')
                        placeholder=placeholder_def[0]
                        placeholder=placeholder.strip()
                    self.initial['OrgDescription'] = placeholder
                elif 'org_adress' in str(line):
                    linestring=str(line)
                    splitted_line=linestring.split("=")
                    placeholder=splitted_line[1].replace("'", '')
                    if isinstance(placeholder, str):
                        placeholder.strip()
                    if "#" in placeholder:
                        placeholder_def=placeholder.split('#')
                        placeholder=placeholder_def[0]
                        placeholder=placeholder.strip()
                    self.initial['OrgAddress'] = placeholder
                elif 'org_welcome_url' in str(line):
                    linestring=str(line)
                    splitted_line=linestring.split("=")
                    placeholder=splitted_line[1].replace("'", '')
                    if isinstance(placeholder, str):
                        placeholder.strip()
                    if "#" in placeholder:
                        placeholder_def=placeholder.split('#')
                        placeholder=placeholder_def[0]
                        placeholder=placeholder.strip()
                    self.initial['OrgWelcomeUrl'] = placeholder
                elif 'org_contact_url' in str(line):
                    linestring=str(line)
                    splitted_line=linestring.split("=")
                    placeholder=splitted_line[1].replace("'", '')
                    if isinstance(placeholder, str):
                        placeholder.strip()
                    if "#" in placeholder:
                        placeholder_def=placeholder.split('#')
                        placeholder=placeholder_def[0]
                        placeholder=placeholder.strip()
                    self.initial['OrgContactUrl'] = placeholder
                elif 'org_logo_url' in str(line):
                    linestring=str(line)
                    splitted_line=linestring.split("=")
                    placeholder=splitted_line[1].replace("'", '')
                    if isinstance(placeholder, str):
                        placeholder.strip()
                    if "#" in placeholder:
                        placeholder_def=placeholder.split('#')
                        placeholder=placeholder_def[0]
                        placeholder=placeholder.strip()
                    self.initial['OrgLogoUrl'] = placeholder
                elif str(line).startswith('version'):
                    with open("beacon/conf/api_version.yml") as api_version_file:
                        api_version_yaml = yaml.safe_load(api_version_file)
                    self.initial['BeaconVersion'] = api_version_yaml['api_version']
         
    BeaconName = forms.CharField(help_text='Beacon Name')
    BeaconId = forms.CharField(help_text='Beacon Id')
    environment_choices = [("TEST", "TEST"), ("DEV", "DEV"), ("PROD", "PROD")]
    Environment = forms.ChoiceField(choices=environment_choices, help_text="Environment")
    APIVersion = forms.CharField(help_text='API Version')
    BeaconVersion = forms.CharField(help_text='Beacon Version')
    OrgId = forms.CharField(help_text='Organization ID')
    OrgName = forms.CharField(help_text='Organization Name')
    OrgDescription = forms.CharField(help_text='Organization Description')
    OrgAddress = forms.CharField(help_text='Organization Address')
    OrgWelcomeUrl = forms.CharField(help_text='Organization Welcome Url')
    OrgContactUrl = forms.CharField(help_text='Organization Contact Url')
    OrgLogoUrl = forms.CharField(help_text='Organization Logo Url')