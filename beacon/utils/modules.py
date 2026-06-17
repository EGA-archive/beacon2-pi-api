from beacon.request.classes import RequestAttributes
import os
from typing import Union
import re
import yaml
from beacon.logs.logs import log_with_args_check_configuration, log_with_args
from beacon.conf.conf_override import config
from beacon.exceptions.exceptions import DatabaseIsDown
import asyncio

#TODO: get_client() passing one variable with the database name.

def load_framework_module(self, script_name):
    """Choose what is the validator object class that will be loaded depending on the API version to return"""
    module='beacon.framework.validator.'+RequestAttributes.returned_apiVersion.replace(".","_")+'.'+script_name
    import importlib
    loaded_module = importlib.import_module(module, package=None)
    return loaded_module

@log_with_args(config.level)
def load_source_module(self, script_name):
    """Choose on the fly what is the database that is going to be used for the current request"""
    complete_module='beacon.connections.'+RequestAttributes.source+'.' + script_name
    import importlib
    module = importlib.import_module(complete_module, package=None)
    return module

@log_with_args_check_configuration(config.level)
async def check_database_connections(LOG=None, entry_type=None, pre_entry_type=None):
    """Choose on the fly what is the database that is going to be used for the current request"""
    try:
        # Store the value for the entry type requested
        entry_type=RequestAttributes.entry_type
        # In case of a cross query, store the value for the entry type that will serve the requested id
        pre_entry_type=RequestAttributes.pre_entry_type
    except Exception:
        # In case there is an exception, load the variables to be added to the error response
        entry_type=None
        pre_entry_type=None
    # Load the configuration file for the models that are enabled
    with open("/beacon/conf/models/models_conf.yml", 'r') as pfile:
        models_confile= yaml.safe_load(pfile)
    pfile.close()
    # Check all the model folders that are found in the beacon/models path
    dirs = os.listdir("/beacon/models")
    # Initialize an array to keep what database connections are performed (and needed to have checks)
    database_connections_to_check=[]
    # Loop over the folders found in the mentioned path and save the ones that are active (enabled)
    for folder in dirs:
        subdirs = os.listdir("/beacon/models/"+folder)
        if folder in models_confile:
            if models_confile[folder]["model_enabled"] == False:
                continue
        # Go over the conf for the entry types of the models enabled
        if "conf" in subdirs:
            confiles = os.listdir("/beacon/models/"+folder+"/conf/entry_types/")
            for confile in confiles:
                # Check that the files are not pycache files
                if confile != '__pycache__':
                    with open("/beacon/models/"+folder+"/conf/entry_types/" + confile, 'r') as pfile:
                        entry_type_confile = yaml.safe_load(pfile)
                    pfile.close()
                    # Map over the different conf files attributes and look for the name of the connections
                    for entry_type_id, conf_entry_type_param in entry_type_confile.items():
                        if entry_type == None or conf_entry_type_param['endpoint_name'] == entry_type and pre_entry_type == None or conf_entry_type_param['endpoint_name'] == pre_entry_type:
                            if conf_entry_type_param['entry_type_enabled'] == True:
                                if conf_entry_type_param['connection']['name'] not in database_connections_to_check:
                                    database_connections_to_check.append(conf_entry_type_param['connection']['name'])
                                # Do the same for the lookups inside the entry types
                                for conf_param, value_param in conf_entry_type_param.items():
                                    if conf_param == 'lookups':
                                        for lookup_id, lookup_value in value_param.items():
                                            if isinstance(lookup_value, dict):
                                                if pre_entry_type != None and entry_type != None:
                                                    if lookup_value['endpoint_name'] == pre_entry_type+'/{id}/'+entry_type:
                                                        if lookup_value['connection']['name'] not in database_connections_to_check:
                                                            database_connections_to_check.append(lookup_value['connection']['name'])
                                                else:
                                                    database_connections_to_check.append(lookup_value['connection']['name'])
        # Loop over the subfolders found in the targeted path and save the ones that are active (enabled)
        else:
            for subfolder in subdirs:
                underdirs = os.listdir("/beacon/models/"+folder+"/"+subfolder)
                if folder+'/'+subfolder in models_confile:
                    if models_confile[folder+'/'+subfolder ]["model_enabled"] == False:
                        continue
                # Go over the conf for the entry types of the models enabled
                if "conf" in underdirs:
                    confiles = os.listdir("/beacon/models/"+folder+"/"+subfolder+"/conf/entry_types/")
                    for confile in confiles:
                        # Check that the files are not pycache files
                        if confile != '__pycache__':
                            with open("/beacon/models/"+folder+"/"+subfolder+"/conf/entry_types/" + confile, 'r') as pfile:
                                entry_type_confile = yaml.safe_load(pfile)
                            pfile.close()
                            # Map over the different conf files attributes and look for the name of the connections
                            for entry_type_id, conf_entry_type_param in entry_type_confile.items():
                                if entry_type == None or conf_entry_type_param['endpoint_name'] == entry_type and pre_entry_type == None or conf_entry_type_param['endpoint_name'] == pre_entry_type:
                                    if conf_entry_type_param['entry_type_enabled'] == True:
                                        if conf_entry_type_param['connection']['name'] not in database_connections_to_check:
                                            database_connections_to_check.append(conf_entry_type_param['connection']['name'])
                                        # Do the same for the lookups inside the entry types
                                        for conf_param, value_param in conf_entry_type_param.items():
                                            if conf_param == 'lookups':
                                                for lookup_id, lookup_value in value_param.items():
                                                    if isinstance(lookup_value, dict):
                                                        if pre_entry_type != None and entry_type != None:
                                                            if lookup_value['endpoint_name'] == pre_entry_type+'/{id}/'+entry_type:
                                                                if lookup_value['connection']['name'] not in database_connections_to_check:
                                                                    database_connections_to_check.append(lookup_value['connection']['name'])
                                                        else:
                                                            database_connections_to_check.append(lookup_value['connection']['name'])
    # Loop over the database connections collected
    for folder in database_connections_to_check:
        # Dynamically load all the modules to ping each of the databases
        complete_module='beacon.connections.'+folder+'.ping'
        import importlib
        module = importlib.import_module(complete_module, package=None)
        ping_from_module = getattr(module, 'ping_database')
        # And dynamically load all the modules to get the connections strings for each of the databases
        complete_client_module='beacon.connections.'+folder+'.client'
        import importlib
        module = importlib.import_module(complete_client_module, package=None)
        client_from_module = getattr(module, 'get_client')
        # Perform the ping of each of the connections with a timeout
        try:
            await asyncio.wait_for(ping_from_module(client_from_module()), timeout=config.pending_requests_timeout_in_seconds)
        # In case of timeout or ping not successful, raise an error of the database being down
        except Exception:
            LOG.error('{} database is down'.format(folder))
            raise DatabaseIsDown(folder)
        
def load_client(folder):
    """Method to get the modules of the connection strings for the databases dynamically"""
    complete_client_module='beacon.connections.'+folder+'.client'
    import importlib
    module = importlib.import_module(complete_client_module, package=None)
    client_from_module = getattr(module, 'get_client')

def load_class(script_name, className):
    """Method to get the classes for the validators that match the API version to return"""
    module='beacon.framework.validator.'+RequestAttributes.returned_apiVersion.replace(".","_")+'.'+script_name
    import importlib
    loaded_module = importlib.import_module(module, package=None)
    klass = getattr(loaded_module, className)
    return klass

def load_types_of_results(response_type):
    """Method to get the type of schema that are accepted (for validation) in case of a model and entry type match"""
    # Load the configuration file for the models that are enabled
    with open("/beacon/conf/models/models_conf.yml", 'r') as pfile:
        models_confile= yaml.safe_load(pfile)
    pfile.close()
    # Initialize the array to collect all the entry types objects to be accepted for validation
    list_of_results_classes_accepted=[]
    # Generate a search of the version getting rid of the characters that join the string to the version number in conf
    version_catch = re.search(r"(v\d+(\.\d+)*)", RequestAttributes.returned_schema[0]["schema"])
    # Keep the version number
    if version_catch:
        version = version_catch.group(1)
    
    # Replace dot for underscores of the version number as dots are not allowed for file names
    underscored_version = version.replace(".","_")
    dirs = os.listdir("/beacon/models")

    # Loop over the folders found in the mentioned path and save the ones that are active (enabled)
    for folder in dirs:
        subdirs = os.listdir("/beacon/models/"+folder)
        if folder in models_confile:
            if models_confile[folder]["model_enabled"] == False:
                continue
        # Go over the validator folders for the entry types of the models enabled
        if "validator" in subdirs:
            validatordirs = os.listdir("/beacon/models/"+folder+"/validator/"+response_type)
            for validatorfolder in validatordirs:
                validatorfiles = os.listdir("/beacon/models/"+folder+"/validator/"+response_type+"/"+validatorfolder)
                # In case a validator folder is found, load the modules dynamically
                for validatorfile in validatorfiles:
                    if underscored_version in validatorfile:
                        complete_module='beacon.models.'+folder+'.validator.'+response_type+'.'+validatorfolder+'.'+validatorfile
                        # Replace the python extension of the file in case there's any to avoid name not matching module
                        complete_module=complete_module.replace('.py', '')
                        import importlib
                        module = importlib.import_module(complete_module, package=None)
                        # Extract the module class matching the module name
                        klass = getattr(module, validatorfolder.capitalize())
                        list_of_results_classes_accepted.append(klass)
        # Loop over the subfolders found in the targeted path and save the ones that are active (enabled)
        for subfolder in subdirs:
            underdirs = os.listdir("/beacon/models/"+folder+"/"+subfolder)
            if  folder+'/'+subfolder in models_confile:
                if models_confile[folder+'/'+subfolder ]["model_enabled"] == False:
                    continue
            # Go over the validator for the entry types of the models enabled
            if "validator" in underdirs:
                try:
                    validatordirs = os.listdir("/beacon/models/"+folder+"/"+subfolder+"/validator/"+response_type)
                except Exception:
                    return None
                # In case a validator folder is found, load the modules dynamically
                for validatorfolder in validatordirs:
                    validatorfiles = os.listdir("/beacon/models/"+folder+"/"+subfolder+"/validator/"+response_type+"/"+validatorfolder)
                    for validatorfile in validatorfiles:
                        if underscored_version in validatorfile:
                            complete_module='beacon.models.'+folder+'.'+subfolder+'.validator.'+response_type+'.'+validatorfolder+'.'+validatorfile
                            # Replace the python extension of the file in case there's any to avoid name not matching module
                            complete_module=complete_module.replace('.py', '')
                            import importlib
                            module = importlib.import_module(complete_module, package=None)
                            # Extract the module class matching the module name
                            klass = getattr(module, validatorfolder.capitalize())
                            list_of_results_classes_accepted.append(klass)
    # Return a pydantinc Union type of response having all the possible entry types to be returned in response as validators of the response
    union_type = Union[tuple(list_of_results_classes_accepted)]
    return union_type

def load_routes():
    """Method to add all the needed routes when initializing or restarting the API"""
    #TODO: add only the enabled lookups
    # Load the configuration file for the models that are enabled
    with open("/beacon/conf/models/models_conf.yml", 'r') as pfile:
        models_confile= yaml.safe_load(pfile)
    pfile.close()
    dirs = os.listdir("/beacon/models")
    routes_to_add={}
    # Loop over the folders found in the mentioned path and save the ones that are active (enabled)
    for folder in dirs:
        subdirs = os.listdir("/beacon/models/"+folder)
        if folder in models_confile:
            if models_confile[folder]["model_enabled"] == False:
                continue
        # Go over the conf for the entry types of the models enabled
        if "conf" in subdirs:
            confiles = os.listdir("/beacon/models/"+folder+"/conf/entry_types/")
            for confile in confiles:
                # Check that the files are not pycache files
                if confile != '__pycache__':
                    with open("/beacon/models/"+folder+"/conf/entry_types/" + confile, 'r') as pfile:
                        entry_type_confile = yaml.safe_load(pfile)
                    pfile.close()
                    # Get the routes names for each of the entry types
                    for entry_type_id, conf_entry_type_param in entry_type_confile.items():
                        if conf_entry_type_param['entry_type_enabled'] == True:
                            routes_to_add[conf_entry_type_param['endpoint_name']]=[conf_entry_type_param['response_type']]
                            routes_to_add[conf_entry_type_param['endpoint_name']+'/{id}']=[conf_entry_type_param['response_type']]
                            for conf_param, value_param in conf_entry_type_param.items():
                                # Get the routes names for each of the entry types lookups
                                if conf_param == 'lookups':
                                    for lookup_id, lookup_value in value_param.items():
                                        if isinstance(lookup_value, dict):
                                            routes_to_add[lookup_value['endpoint_name']]=[lookup_value['response_type']]
        else:
            # Loop over the subfolders found in the targeted path and save the ones that are active (enabled)
            for subfolder in subdirs:
                underdirs = os.listdir("/beacon/models/"+folder+"/"+subfolder)
                if folder+'/'+subfolder in models_confile:
                    if models_confile[folder+'/'+subfolder ]["model_enabled"] == False:
                        continue
                # Go over the conf for the entry types of the models enabled
                if "conf" in underdirs:
                    confiles = os.listdir("/beacon/models/"+folder+"/"+subfolder+"/conf/entry_types/")
                    for confile in confiles:
                        # Check that the files are not pycache files
                        if confile != '__pycache__':
                            with open("/beacon/models/"+folder+"/"+subfolder+"/conf/entry_types/" + confile, 'r') as pfile:
                                entry_type_confile = yaml.safe_load(pfile)
                            pfile.close()
                            # Get the routes names for each of the entry types
                            for entry_type_id, conf_entry_type_param in entry_type_confile.items():
                                if conf_entry_type_param['entry_type_enabled'] == True:
                                    routes_to_add[conf_entry_type_param['endpoint_name']]=[conf_entry_type_param['response_type']]
                                    routes_to_add[conf_entry_type_param['endpoint_name']+'/{id}']=[conf_entry_type_param['response_type']]
                                    for conf_param, value_param in conf_entry_type_param.items():
                                        # Get the routes names for each of the entry types lookups
                                        if conf_param == 'lookups':
                                            for lookup_id, lookup_value in value_param.items():
                                                if isinstance(lookup_value, dict):
                                                    routes_to_add[lookup_value['endpoint_name']]=[lookup_value['response_type']]
    return routes_to_add

def _model_is_enabled(models_confile, folder, subfolder=None):
    """Methot tho get the models enabled dynamically"""
    if folder in models_confile and models_confile[folder]["model_enabled"] == False:
        return False
    if subfolder is not None:
        model_key = folder + '/' + subfolder
        if model_key in models_confile and models_confile[model_key]["model_enabled"] == False:
            return False
    return True

def get_all_modules_mongo_connections_script(script):
    """Method to get all the submodules of mongo connections per model loaded dynamically"""
    list_of_modules=[]
    # Load the configuration file for the models that are enabled
    with open("/beacon/conf/models/models_conf.yml", 'r') as pfile:
        models_confile= yaml.safe_load(pfile)
    pfile.close()
    dirs = os.listdir("/beacon/models")
    # Loop over the folders found in the mentioned path and save the ones that are active (enabled)
    for folder in dirs:
        subdirs = os.listdir("/beacon/models/"+folder)
        # Get the models that are specifically enabled
        if not _model_is_enabled(models_confile, folder):
            continue
        # Go over the connections for the entry types of the models enabled
        if "connections" in subdirs:
            connections = os.listdir("/beacon/models/"+folder+"/connections")
            for dir in connections:
                if dir == 'mongo':
                    # Get the modules names in an array
                    complete_module='beacon.models.'+folder+'.connections.mongo.'+script
                    import importlib
                    module = importlib.import_module(complete_module, package=None)
                    list_of_modules.append(module)
        else:
            # Loop over the subfolders found in the mentioned path and save the ones that are active (enabled)
            for subfolder in subdirs:
                underdirs = os.listdir("/beacon/models/"+folder+"/"+subfolder)
                # Get the models that are specifically enabled
                if not _model_is_enabled(models_confile, folder, subfolder):
                    continue
                # Go over the connections for the entry types of the models enabled
                if "connections" in underdirs:
                    connections = os.listdir("/beacon/models/"+folder+"/"+subfolder+"/connections")
                    for dir in connections:
                        if dir == 'mongo':
                            # Get the modules names in an array
                            complete_module='beacon.models.'+folder+'.'+subfolder+'.connections.mongo.'+script
                            import importlib
                            module = importlib.import_module(complete_module, package=None)
                            list_of_modules.append(module)
    return list_of_modules

def get_all_modules_datasets():
    """Method to get the datasets collections for each of the models to be returned"""
    list_of_modules=[]
    # Load the configuration file for the models that are enabled
    with open("/beacon/conf/models/models_conf.yml", 'r') as pfile:
        models_confile= yaml.safe_load(pfile)
    pfile.close()
    dirs = os.listdir("/beacon/models")
    # Loop over the folders found in the mentioned path and save the ones that are active (enabled)
    for folder in dirs:
        subdirs = os.listdir("/beacon/models/"+folder)
        # Get the models that are specifically enabled
        if not _model_is_enabled(models_confile, folder):
            continue
        # Go over the collections of the models enabled in the connections folder
        if "connections" in subdirs:
            try:
                # Get the names of the collections validators to be validated and accepted
                complete_module='beacon.models.'+folder+'.connections.mongo.collections'
                import importlib
                module = importlib.import_module(complete_module, package=None)
                list_of_modules.append(module)
            except Exception:
                pass
        # Loop over the subfolders found in the mentioned path and save the ones that are active (enabled)
        for subfolder in subdirs:
            underdirs = os.listdir("/beacon/models/"+folder+"/"+subfolder)
            # Get the models that are specifically enabled
            if not _model_is_enabled(models_confile, folder, subfolder):
                continue
            # Go over the collections of the models enabled in the connections folder
            if "connections" in underdirs:
                try:
                    # Get the names of the collections validators to be validated and accepted
                    complete_module='beacon.models.'+folder+'.'+subfolder+'.connections.mongo.collections'
                    import importlib
                    module = importlib.import_module(complete_module, package=None)
                    list_of_modules.append(module)
                except Exception:
                    pass
    return list_of_modules
                            
def get_one_module_conf(entry_type):
    """Method to get the configuration of the desired entry types"""
    # TODO: Cache the module conf loading to only execute it once.
    dirs = os.listdir("/beacon/models")
    # Loop over the folders found in the models and get the entry types configuration
    for folder in dirs:
        subdirs = os.listdir("/beacon/models/"+folder)
        # Go over the entry types files in the conf folder
        if "conf" in subdirs:
            confiles = os.listdir("/beacon/models/"+folder+"/conf/entry_types/")
            for confile in confiles:
                # Skip the files that are of pycache type
                if confile != '__pycache__':
                    with open("/beacon/models/"+folder+"/conf/entry_types/" + confile, 'r') as pfile:
                        entry_type_confile = yaml.safe_load(pfile)
                    pfile.close()
                # Get the configuration file for the entry type that matches the one requested
                for entry_type_id, entry_type_params in entry_type_confile.items():
                    if entry_type_params["endpoint_name"] == entry_type:
                        return entry_type_confile
        else:
            # Loop over the subfolders found in the models and get the entry types configuration
            for subfolder in subdirs:
                underdirs = os.listdir("/beacon/models/"+folder+"/"+subfolder)
                # Go over the entry types files in the conf folder
                if "conf" in underdirs:
                    confiles = os.listdir("/beacon/models/"+folder+"/"+subfolder+"/conf/entry_types/")
                    for confile in confiles:
                        # Skip the files that are of pycache type
                        if confile != '__pycache__':
                            with open("/beacon/models/"+folder+"/"+subfolder+"/conf/entry_types/" + confile, 'r') as pfile:
                                entry_type_confile = yaml.safe_load(pfile)
                            pfile.close()
                        # Get the configuration file for the entry type that matches the one requested
                        for entry_type_id, entry_type_params in entry_type_confile.items():
                            if entry_type_params["endpoint_name"] == entry_type:
                                return entry_type_confile

def get_modules_confiles():
    """Method to get all the entry types configuration files"""
    # Load the configuration file for the models that are enabled
    with open("/beacon/conf/models/models_conf.yml", 'r') as pfile:
        models_confile= yaml.safe_load(pfile)
    pfile.close()
    dirs = os.listdir("/beacon/models")
    list_of_confiles=[]
    # Loop over the folders found in the models and get the entry types configuration
    for folder in dirs:
        subdirs = os.listdir("/beacon/models/"+folder)
        # Go over the entry types files in the conf folder
        if "conf" in subdirs:
            confiles = os.listdir("/beacon/models/"+folder+"/conf/entry_types/")
            if folder in models_confile:
                if models_confile[folder]["model_enabled"] == False:
                    continue
            for confile in confiles:
                # Skip the files that are of pycache type
                if confile != '__pycache__':
                    with open("/beacon/models/"+folder+"/conf/entry_types/" + confile, 'r') as pfile:
                        entry_type_confile = yaml.safe_load(pfile)
                    pfile.close()
                list_of_confiles.append(entry_type_confile)
        else:
            # Loop over the subfolders found in the models and get the entry types configuration
            for subfolder in subdirs:
                underdirs = os.listdir("/beacon/models/"+folder+"/"+subfolder)
                if folder+'/'+subfolder in models_confile:
                    if models_confile[folder+'/'+subfolder ]["model_enabled"] == False:
                        continue
                # Go over the entry types files in the conf folder
                if "conf" in underdirs:
                    confiles = os.listdir("/beacon/models/"+folder+"/"+subfolder+"/conf/entry_types/")
                    for confile in confiles:
                        # Skip the files that are of pycache type
                        if confile != '__pycache__':
                            with open("/beacon/models/"+folder+"/"+subfolder+"/conf/entry_types/" + confile, 'r') as pfile:
                                entry_type_confile = yaml.safe_load(pfile)
                            pfile.close()
                            list_of_confiles.append(entry_type_confile)
    return list_of_confiles
    
