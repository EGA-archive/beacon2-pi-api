from beacon.request.classes import RequestAttributes

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