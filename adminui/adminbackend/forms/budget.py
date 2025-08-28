from django import forms
import yaml
import logging
import os

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


class BudgetForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(BudgetForm, self).__init__(*args, **kwargs)
        # assign a (computed, I assume) default value to the choice field
        with open("/home/app/web/beacon/conf/conf.py") as f:
            lines = f.readlines()
        with open("/home/app/web/beacon/conf/conf.py", "r") as f:
            for line in lines:
                if 'query_budget_per_user' in str(line):
                    placeholder = formatting_field(self, line)
                    if placeholder == 'False':
                        self.initial['BudgetUser'] = None
                    else:
                        self.initial['BudgetUser'] = True
                elif 'query_budget_per_ip' in str(line):
                    placeholder = formatting_field(self, line)
                    if placeholder == 'False':
                        self.initial['BudgetIP'] = None
                    else:
                        self.initial['BudgetIP'] = True
                elif 'query_budget_amount' in str(line):
                    placeholder = formatting_field(self, line)
                    self.initial['BudgetAmount'] = placeholder
                elif 'query_budget_time_in_seconds' in str(line) or 'api_version =' in str(line):
                    placeholder = formatting_field(self, line)
                    self.initial['BudgetTime'] = placeholder
                elif 'query_budget_database' in str(line):
                    placeholder = formatting_field(self, line)
                    self.initial['BudgetDB'] = placeholder
                elif 'query_budget_db_name' in str(line):
                    placeholder = formatting_field(self, line)
                    self.initial['BudgetDBName'] = placeholder
                elif 'query_budget_table' in str(line):
                    placeholder = formatting_field(self, line)
                    self.initial['BudgetTable'] = placeholder
         
    BudgetUser = forms.BooleanField(required=False,help_text='Limit Queries per User Account')
    BudgetIP = forms.BooleanField(required=False,help_text='Limit Queries per IP address')
    BudgetAmount = forms.IntegerField(help_text="Max. number of queries")
    BudgetTime = forms.IntegerField(help_text='Time for reset')
    dirs = os.listdir("/home/app/web/beacon/connections")
    list_databases=[]
    for dir in dirs:
        list_databases.append((dir, dir))
    BudgetDB = forms.ChoiceField(choices=list_databases,help_text='Database Engine')
    BudgetDBName = forms.CharField(help_text='Database Name where budget is stored inside Database Engine')
    BudgetTable = forms.CharField(help_text='Table Name where budget is stored inside Database Name')
    