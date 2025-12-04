from beacon.request.classes import RequestAttributes
import os
from typing import List, Optional, Union, Dict
import re
from beacon.logs.logs import LOG
import yaml

def load_framework_module(self, script_name):
    module='beacon.framework.validator.'+RequestAttributes.returned_apiVersion.replace(".","_")+'.'+script_name
    import importlib
    loaded_module = importlib.import_module(module, package=None)
    return loaded_module

def load_source_module(self, script_name):
    complete_module='beacon.connections.'+RequestAttributes.source+'.' + script_name
    import importlib
    module = importlib.import_module(complete_module, package=None)
    return module

def load_class(script_name, className):
    module='beacon.framework.validator.'+RequestAttributes.returned_apiVersion.replace(".","_")+'.'+script_name
    import importlib
    loaded_module = importlib.import_module(module, package=None)
    klass = getattr(loaded_module, className)
    return klass

def load_types_of_results(response_type):
    list_of_results_classes_accepted=[]
    version_catch = re.search(r"(v\d+(\.\d+)*)", RequestAttributes.returned_schema[0]["schema"])
    if version_catch:
        version = version_catch.group(1)
    
    underscored_version = version.replace(".","_")
    dirs = os.listdir("/beacon/models")
    for folder in dirs:
        subdirs = os.listdir("/beacon/models/"+folder)
        if "validator" in subdirs:
            validatordirs = os.listdir("/beacon/models/"+folder+"/validator/"+response_type)
            for validatorfolder in validatordirs:
                validatorfiles = os.listdir("/beacon/models/"+folder+"/validator/"+response_type+"/"+validatorfolder)
                for validatorfile in validatorfiles:
                    if underscored_version in validatorfile:
                        complete_module='beacon.models.'+folder+'.validator.'+response_type+'.'+validatorfolder+'.'+validatorfile
                        complete_module=complete_module.replace('.py', '')
                        import importlib
                        module = importlib.import_module(complete_module, package=None)
                        klass = getattr(module, validatorfolder.capitalize())
                        list_of_results_classes_accepted.append(klass)
        for subfolder in subdirs:
            underdirs = os.listdir("/beacon/models/"+folder+"/"+subfolder)
            if "validator" in underdirs:
                try:
                    validatordirs = os.listdir("/beacon/models/"+folder+"/"+subfolder+"/validator/"+response_type)
                except Exception:
                    return None
                for validatorfolder in validatordirs:
                    validatorfiles = os.listdir("/beacon/models/"+folder+"/"+subfolder+"/validator/"+response_type+"/"+validatorfolder)
                    for validatorfile in validatorfiles:
                        if underscored_version in validatorfile:
                            complete_module='beacon.models.'+folder+'.'+subfolder+'.validator.'+response_type+'.'+validatorfolder+'.'+validatorfile
                            complete_module=complete_module.replace('.py', '')
                            import importlib
                            module = importlib.import_module(complete_module, package=None)
                            klass = getattr(module, validatorfolder.capitalize())
                            list_of_results_classes_accepted.append(klass)
    union_type = Union[tuple(list_of_results_classes_accepted)]
    return union_type

def load_routes():
    dirs = os.listdir("/beacon/models")
    routes_to_add={}
    for folder in dirs:
        subdirs = os.listdir("/beacon/models/"+folder)
        if "conf" in subdirs:
            confiles = os.listdir("/beacon/models/"+folder+"/conf/entry_types/")
            for confile in confiles:
                if confile != '__pycache__':
                    with open("/beacon/models/"+folder+"/conf/entry_types/" + confile, 'r') as pfile:
                        entry_type_confile = yaml.safe_load(pfile)
                    pfile.close()
                    for entry_type_id, conf_entry_type_param in entry_type_confile.items():
                        routes_to_add[conf_entry_type_param['endpoint_name']]=[conf_entry_type_param['response_type']]
                        routes_to_add[conf_entry_type_param['endpoint_name']+'/{id}']=[conf_entry_type_param['response_type']]
                        for conf_param, value_param in conf_entry_type_param.items():
                            if conf_param == 'lookups':
                                for lookup_id, lookup_value in value_param.items():
                                    if isinstance(lookup_value, dict):
                                        routes_to_add[lookup_value['endpoint_name']]=[lookup_value['response_type']]
        else:
            for subfolder in subdirs:
                underdirs = os.listdir("/beacon/models/"+folder+"/"+subfolder)
                if "conf" in underdirs:
                    confiles = os.listdir("/beacon/models/"+folder+"/"+subfolder+"/conf/entry_types/")
                    for confile in confiles:
                        if confile != '__pycache__':
                            with open("/beacon/models/"+folder+"/"+subfolder+"/conf/entry_types/" + confile, 'r') as pfile:
                                entry_type_confile = yaml.safe_load(pfile)
                            pfile.close()
                            for entry_type_id, conf_entry_type_param in entry_type_confile.items():
                                routes_to_add[conf_entry_type_param['endpoint_name']]=[conf_entry_type_param['response_type']]
                                routes_to_add[conf_entry_type_param['endpoint_name']+'/{id}']=[conf_entry_type_param['response_type']]
                                for conf_param, value_param in conf_entry_type_param.items():
                                    if conf_param == 'lookups':
                                        for lookup_id, lookup_value in value_param.items():
                                            if isinstance(lookup_value, dict):
                                                routes_to_add[lookup_value['endpoint_name']]=[lookup_value['response_type']]
    return routes_to_add

def get_all_modules_mongo_connections_script(script):
    list_of_modules=[]
    dirs = os.listdir("/beacon/models")
    for folder in dirs:
        subdirs = os.listdir("/beacon/models/"+folder)
        if "connections" in subdirs:
            connections = os.listdir("/beacon/models/"+folder+"/connections")
            for dir in connections:
                if dir == 'mongo':
                    complete_module='beacon.models.'+folder+'.connections.mongo.'+script
                    import importlib
                    module = importlib.import_module(complete_module, package=None)
                    list_of_modules.append(module)
        else:
            for subfolder in subdirs:
                underdirs = os.listdir("/beacon/models/"+folder+"/"+subfolder)
                if "connections" in underdirs:
                    connections = os.listdir("/beacon/models/"+folder+"/"+subfolder+"/connections")
                    for dir in connections:
                        if dir == 'mongo':
                            complete_module='beacon.models.'+folder+'.'+subfolder+'.connections.mongo.'+script
                            import importlib
                            module = importlib.import_module(complete_module, package=None)
                            list_of_modules.append(module)
    return list_of_modules

def get_all_modules_datasets():
    list_of_modules=[]
    dirs = os.listdir("/beacon/models")
    for folder in dirs:
        subdirs = os.listdir("/beacon/models/"+folder)
        if "connections" in subdirs:
            try:
                complete_module='beacon.models.'+folder+'.connections.mongo.collections'
                import importlib
                module = importlib.import_module(complete_module, package=None)
                list_of_modules.append(module)
            except Exception:
                pass
        for subfolder in subdirs:
            underdirs = os.listdir("/beacon/models/"+folder+"/"+subfolder)
            if "connections" in underdirs:
                try:
                    complete_module='beacon.models.'+folder+'.'+subfolder+'.connections.mongo.collections'
                    import importlib
                    module = importlib.import_module(complete_module, package=None)
                    list_of_modules.append(module)
                except Exception:
                    pass
    return list_of_modules
                            
def get_one_module_conf(entry_type):
    dirs = os.listdir("/beacon/models")
    for folder in dirs:
        subdirs = os.listdir("/beacon/models/"+folder)
        if "conf" in subdirs:
            confiles = os.listdir("/beacon/models/"+folder+"/conf/entry_types/")
            for confile in confiles:
                if confile != '__pycache__':
                    with open("/beacon/models/"+folder+"/conf/entry_types/" + confile, 'r') as pfile:
                        entry_type_confile = yaml.safe_load(pfile)
                    pfile.close()
                for entry_type_id, entry_type_params in entry_type_confile.items():
                    if entry_type_params["endpoint_name"] == entry_type:
                        return entry_type_confile
        else:
            for subfolder in subdirs:
                underdirs = os.listdir("/beacon/models/"+folder+"/"+subfolder)
                if "conf" in underdirs:
                    confiles = os.listdir("/beacon/models/"+folder+"/"+subfolder+"/conf/entry_types/")
                    for confile in confiles:
                        if confile != '__pycache__':
                            with open("/beacon/models/"+folder+"/"+subfolder+"/conf/entry_types/" + confile, 'r') as pfile:
                                entry_type_confile = yaml.safe_load(pfile)
                            pfile.close()
                        for entry_type_id, entry_type_params in entry_type_confile.items():
                            if entry_type_params["endpoint_name"] == entry_type:
                                return entry_type_confile

def get_modules_confiles():
    dirs = os.listdir("/beacon/models")
    list_of_confiles=[]
    for folder in dirs:
        subdirs = os.listdir("/beacon/models/"+folder)
        if "conf" in subdirs:
            confiles = os.listdir("/beacon/models/"+folder+"/conf/entry_types/")
            for confile in confiles:
                if confile != '__pycache__':
                    with open("/beacon/models/"+folder+"/conf/entry_types/" + confile, 'r') as pfile:
                        entry_type_confile = yaml.safe_load(pfile)
                    pfile.close()
                list_of_confiles.append(entry_type_confile)
        else:
            for subfolder in subdirs:
                underdirs = os.listdir("/beacon/models/"+folder+"/"+subfolder)
                if "conf" in underdirs:
                    confiles = os.listdir("/beacon/models/"+folder+"/"+subfolder+"/conf/entry_types/")
                    for confile in confiles:
                        if confile != '__pycache__':
                            with open("/beacon/models/"+folder+"/"+subfolder+"/conf/entry_types/" + confile, 'r') as pfile:
                                entry_type_confile = yaml.safe_load(pfile)
                            pfile.close()
                            list_of_confiles.append(entry_type_confile)
    return list_of_confiles
    

