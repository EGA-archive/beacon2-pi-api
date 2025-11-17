from beacon.request.classes import RequestAttributes
import os
from typing import List, Optional, Union, Dict
import re
from beacon.logs.logs import LOG


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
        else:
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

def load_routes(app):
    dirs = os.listdir("/beacon/models")
    for folder in dirs:
        subdirs = os.listdir("/beacon/models/"+folder)
        if "routes" in subdirs:
            complete_module='beacon.models.'+folder+'.routes.routes'
            import importlib
            module = importlib.import_module(complete_module, package=None)
            app = module.extend_routes(app)
        else:
            for subfolder in subdirs:
                underdirs = os.listdir("/beacon/models/"+folder+'/'+subfolder)
                if "routes" in underdirs:
                    complete_module='beacon.models.'+folder+'.'+subfolder+'.routes.routes'
                    import importlib
                    module = importlib.import_module(complete_module, package=None)
                    app = module.extend_routes(app)
    return app

def get_conf(entry_type):
    dirs = os.listdir("/beacon/models")
    for folder in dirs:
        subdirs = os.listdir("/beacon/models/"+folder)
        if "conf" in subdirs:
            confiles = os.listdir("/beacon/models/"+folder+"/conf")
            for confile in confiles:
                if confile != '__pycache__':
                    complete_module='beacon.models.'+folder+'.conf.'+confile.replace('.py', '')
                    import importlib
                    module = importlib.import_module(complete_module, package=None)
                    if entry_type == module.endpoint_name:
                        return module
        else:
            for subfolder in subdirs:
                underdirs = os.listdir("/beacon/models/"+folder+"/"+subfolder)
                if "conf" in underdirs:
                    confiles = os.listdir("/beacon/models/"+folder+"/"+subfolder+"/conf")
                    for confile in confiles:
                        if confile != '__pycache__':
                            complete_module='beacon.models.'+folder+'.'+subfolder+'.conf.'+confile.replace('.py', '')
                            import importlib
                            module = importlib.import_module(complete_module, package=None)
                            if entry_type == module.endpoint_name:
                                return module
                        
def get_all_modules():
    list_of_modules=[]
    dirs = os.listdir("/beacon/models")
    for folder in dirs:
        subdirs = os.listdir("/beacon/models/"+folder)
        if "conf" in subdirs:
            confiles = os.listdir("/beacon/models/"+folder+"/conf")
            for confile in confiles:
                if confile != '__pycache__':
                    complete_module='beacon.models.'+folder+'.conf.'+confile.replace('.py', '')
                    import importlib
                    module = importlib.import_module(complete_module, package=None)
                    list_of_modules.append(module)
        else:
            for subfolder in subdirs:
                underdirs = os.listdir("/beacon/models/"+folder+"/"+subfolder)
                if "conf" in underdirs:
                    confiles = os.listdir("/beacon/models/"+folder+"/"+subfolder+"/conf")
                    for confile in confiles:
                        if confile != '__pycache__':
                            complete_module='beacon.models.'+folder+'.'+subfolder+'.conf.'+confile.replace('.py', '')
                            import importlib
                            module = importlib.import_module(complete_module, package=None)
                            list_of_modules.append(module)
    return list_of_modules
    

