
import os
from typing import Union
import re
import yaml
from beacon.logs.logs import log_with_args_check_configuration, log_with_args
from beacon.conf.conf_override import config
from beacon.exceptions.exceptions import DatabaseIsDown
import asyncio
import time

#TODO: get_client() passing one variable with the database name.
@log_with_args(config.level)
def load_framework_module(self, script_name):
    """Choose what is the validator object class that will be loaded depending on the API version to return"""
    module='beacon.framework.validator.'+self.request_attributes.returned_apiVersion.replace(".","_")+'.'+script_name
    import importlib
    loaded_module = importlib.import_module(module, package=None)
    return loaded_module

@log_with_args(config.level)
def load_source_module(self, script_name):
    """Choose on the fly what is the database that is going to be used for the current request"""
    complete_module='beacon.connections.'+self.request_attributes.source+'.' + script_name
    import importlib
    module = importlib.import_module(complete_module, package=None)
    return module

@log_with_args_check_configuration(config.level)
async def check_database_connections(LOG=None, entry_type=None, pre_entry_type=None):
    """Choose on the fly what is the database that is going to be used for the current request"""
    # Load the configuration file for the models that are enabled
    with open("/beacon/conf/models/models_conf.yml", 'r') as pfile:
        models_confile= yaml.safe_load(pfile)
    pfile.close()
    # Check all the model folders that are found in the beacon/models path
    dirs = os.listdir("/beacon/models")
    # Load conf file for connection to check which are enabled
    with open('/beacon/conf/connections/connections_conf.yml') as infile:
        connections_conf=yaml.safe_load(infile)
    # Get array of enabled connections
    connections_enabled=[]
    for k, v in connections_conf.items():
        if v['connection_enabled']==True:
            connections_enabled.append(k)
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
                                    if conf_entry_type_param['connection']['name'] in connections_enabled:
                                        database_connections_to_check.append(conf_entry_type_param['connection']['name'])
                                # Do the same for the lookups inside the entry types
                                for conf_param, value_param in conf_entry_type_param.items():
                                    if conf_param == 'lookups':
                                        for lookup_id, lookup_value in value_param.items():
                                            if isinstance(lookup_value, dict):
                                                if pre_entry_type != None and entry_type != None:
                                                    if lookup_value['endpoint_name'] == pre_entry_type+'/{id}/'+entry_type:
                                                        if lookup_value['connection']['name'] not in database_connections_to_check:
                                                            if lookup_value['connection']['name'] in connections_enabled:
                                                                database_connections_to_check.append(lookup_value['connection']['name'])
                                                else:
                                                    if lookup_value['connection']['name'] in connections_enabled:
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
                                            if conf_entry_type_param['connection']['name'] in connections_enabled:
                                                database_connections_to_check.append(conf_entry_type_param['connection']['name'])
                                        # Do the same for the lookups inside the entry types
                                        for conf_param, value_param in conf_entry_type_param.items():
                                            if conf_param == 'lookups':
                                                for lookup_id, lookup_value in value_param.items():
                                                    if isinstance(lookup_value, dict):
                                                        if pre_entry_type != None and entry_type != None:
                                                            if lookup_value['endpoint_name'] == pre_entry_type+'/{id}/'+entry_type:
                                                                if lookup_value['connection']['name'] not in database_connections_to_check:
                                                                    if lookup_value['connection']['name'] in connections_enabled:
                                                                        database_connections_to_check.append(lookup_value['connection']['name'])
                                                        else:
                                                            if lookup_value['connection']['name'] in connections_enabled:
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

def load_class(self, script_name, className):
    """Method to get the classes for the validators that match the API version to return"""
    module='beacon.framework.validator.'+self.request_attributes.returned_apiVersion.replace(".","_")+'.'+script_name
    import importlib
    loaded_module = importlib.import_module(module, package=None)
    klass = getattr(loaded_module, className)
    return klass

# Module-level cache.
# Put these OUTSIDE load_types_of_results(), near the top of the module.

_RESULT_TYPES_CACHE = {}
_RESULT_TYPES_CONFIG_MTIME = None

_MODELS_CONF_PATH = "/beacon/conf/models/models_conf.yml"
_MODELS_BASE_PATH = "/beacon/models"


def load_types_of_results(self, response_type):
    """
    Load the result validator types for the requested response type/version.

    The discovered Union type is cached so that filesystem scanning,
    YAML parsing and dynamic imports do not happen on every request.

    The cache is automatically invalidated when models_conf.yml changes.
    """

    import importlib
    import sys
    import time

    global _RESULT_TYPES_CONFIG_MTIME

    total_start = time.perf_counter()

    # ---------------------------------------------------------
    # Get schema version
    # ---------------------------------------------------------
    start = time.perf_counter()

    version_catch = re.search(
        r"(v\d+(\.\d+)*)",
        self.request_attributes.returned_schema[0]["schema"]
    )

    if not version_catch:
        raise ValueError(
            "Could not determine schema version from returned_schema"
        )

    version = version_catch.group(1)
    underscored_version = version.replace(".", "_")

    print(
        f"[TIMING] version processing: "
        f"{(time.perf_counter() - start) * 1000:.2f} ms",
        flush=True,
    )

    # ---------------------------------------------------------
    # Check models_conf.yml modification time
    # ---------------------------------------------------------
    start = time.perf_counter()

    config_mtime = os.stat(
        _MODELS_CONF_PATH
    ).st_mtime_ns

    print(
        f"[TIMING] config mtime check: "
        f"{(time.perf_counter() - start) * 1000:.2f} ms",
        flush=True,
    )

    # ---------------------------------------------------------
    # Invalidate entire cache if configuration changed
    # ---------------------------------------------------------
    if _RESULT_TYPES_CONFIG_MTIME != config_mtime:

        if _RESULT_TYPES_CONFIG_MTIME is not None:
            print(
                "[TIMING] models_conf.yml changed - "
                "clearing result types cache",
                flush=True,
            )

        _RESULT_TYPES_CACHE.clear()

        _RESULT_TYPES_CONFIG_MTIME = config_mtime

    # ---------------------------------------------------------
    # Cache lookup
    # ---------------------------------------------------------
    cache_key = (
        response_type,
        underscored_version,
    )

    if cache_key in _RESULT_TYPES_CACHE:

        print(
            f"[TIMING] load_types_of_results CACHE HIT: "
            f"{cache_key}",
            flush=True,
        )

        print(
            f"[TIMING] load_types_of_results TOTAL: "
            f"{(time.perf_counter() - total_start) * 1000:.2f} ms",
            flush=True,
        )

        return _RESULT_TYPES_CACHE[cache_key]

    print(
        f"[TIMING] load_types_of_results CACHE MISS: "
        f"{cache_key}",
        flush=True,
    )

    # ---------------------------------------------------------
    # Load configuration
    # ---------------------------------------------------------
    start = time.perf_counter()

    with open(
        _MODELS_CONF_PATH,
        "r"
    ) as pfile:
        models_confile = yaml.safe_load(pfile)

    print(
        f"[TIMING] load_types YAML: "
        f"{(time.perf_counter() - start) * 1000:.2f} ms",
        flush=True,
    )

    # ---------------------------------------------------------
    # Initialize
    # ---------------------------------------------------------
    list_of_results_classes_accepted = []

    import_count = 0
    cached_import_count = 0

    # ---------------------------------------------------------
    # Helper for imports
    # ---------------------------------------------------------
    def timed_import(module_name):

        nonlocal import_count
        nonlocal cached_import_count

        already_cached = module_name in sys.modules

        print(
            f"[TIMING] IMPORT START: {module_name} "
            f"(cached={already_cached})",
            flush=True,
        )

        start_import = time.perf_counter()

        module = importlib.import_module(
            module_name,
            package=None
        )

        elapsed_import = (
            time.perf_counter() - start_import
        )

        import_count += 1

        if already_cached:
            cached_import_count += 1

        print(
            f"[TIMING] IMPORT END: {module_name} "
            f"{elapsed_import * 1000:.2f} ms "
            f"(cached={already_cached})",
            flush=True,
        )

        return module

    # ---------------------------------------------------------
    # Get model directories
    # ---------------------------------------------------------
    start = time.perf_counter()

    dirs = os.listdir(
        _MODELS_BASE_PATH
    )

    print(
        f"[TIMING] initial os.listdir: "
        f"{(time.perf_counter() - start) * 1000:.2f} ms",
        flush=True,
    )

    # ---------------------------------------------------------
    # Search models
    # ---------------------------------------------------------
    filesystem_start = time.perf_counter()

    for folder in dirs:

        start = time.perf_counter()

        subdirs = os.listdir(
            _MODELS_BASE_PATH + "/" + folder
        )

        elapsed = time.perf_counter() - start

        if elapsed > 0.5 / 1000:
            print(
                f"[TIMING] os.listdir folder={folder}: "
                f"{elapsed * 1000:.2f} ms",
                flush=True,
            )

        # -----------------------------------------------------
        # Check if top-level model is enabled
        # -----------------------------------------------------
        if folder in models_confile:

            if models_confile[
                folder
            ]["model_enabled"] is False:
                continue

        # =====================================================
        # Direct validator directory
        # =====================================================
        if "validator" in subdirs:

            validator_base_path = (
                _MODELS_BASE_PATH
                + "/"
                + folder
                + "/validator/"
                + response_type
            )

            start = time.perf_counter()

            validatordirs = os.listdir(
                validator_base_path
            )

            print(
                f"[TIMING] os.listdir validators "
                f"{validator_base_path}: "
                f"{(time.perf_counter() - start) * 1000:.2f} ms",
                flush=True,
            )

            for validatorfolder in validatordirs:

                validator_path = (
                    validator_base_path
                    + "/"
                    + validatorfolder
                )

                start = time.perf_counter()

                validatorfiles = os.listdir(
                    validator_path
                )

                elapsed = time.perf_counter() - start

                if elapsed > 0.5 / 1000:
                    print(
                        f"[TIMING] os.listdir validator "
                        f"{validatorfolder}: "
                        f"{elapsed * 1000:.2f} ms",
                        flush=True,
                    )

                for validatorfile in validatorfiles:

                    if underscored_version not in validatorfile:
                        continue

                    complete_module = (
                        "beacon.models."
                        + folder
                        + ".validator."
                        + response_type
                        + "."
                        + validatorfolder
                        + "."
                        + validatorfile
                    )

                    complete_module = complete_module.replace(
                        ".py",
                        ""
                    )

                    module = timed_import(
                        complete_module
                    )

                    start = time.perf_counter()

                    klass = getattr(
                        module,
                        validatorfolder.capitalize()
                    )

                    print(
                        f"[TIMING] getattr "
                        f"{complete_module}: "
                        f"{(time.perf_counter() - start) * 1000:.2f} ms",
                        flush=True,
                    )

                    list_of_results_classes_accepted.append(
                        klass
                    )

        # =====================================================
        # Nested model directories
        # =====================================================
        for subfolder in subdirs:

            model_path = (
                _MODELS_BASE_PATH
                + "/"
                + folder
                + "/"
                + subfolder
            )

            start = time.perf_counter()

            underdirs = os.listdir(
                model_path
            )

            elapsed = time.perf_counter() - start

            if elapsed > 0.5 / 1000:
                print(
                    f"[TIMING] os.listdir model "
                    f"{folder}/{subfolder}: "
                    f"{elapsed * 1000:.2f} ms",
                    flush=True,
                )

            model_config_key = (
                folder + "/" + subfolder
            )

            if model_config_key in models_confile:

                if models_confile[
                    model_config_key
                ]["model_enabled"] is False:
                    continue

            if "validator" not in underdirs:
                continue

            validator_base_path = (
                _MODELS_BASE_PATH
                + "/"
                + folder
                + "/"
                + subfolder
                + "/validator/"
                + response_type
            )

            try:

                start = time.perf_counter()

                validatordirs = os.listdir(
                    validator_base_path
                )

                print(
                    f"[TIMING] os.listdir nested validators "
                    f"{folder}/{subfolder}: "
                    f"{(time.perf_counter() - start) * 1000:.2f} ms",
                    flush=True,
                )

            except Exception:
                return None

            for validatorfolder in validatordirs:

                validator_path = (
                    validator_base_path
                    + "/"
                    + validatorfolder
                )

                start = time.perf_counter()

                validatorfiles = os.listdir(
                    validator_path
                )

                elapsed = time.perf_counter() - start

                if elapsed > 0.5 / 1000:
                    print(
                        f"[TIMING] os.listdir nested validator "
                        f"{validatorfolder}: "
                        f"{elapsed * 1000:.2f} ms",
                        flush=True,
                    )

                for validatorfile in validatorfiles:

                    if underscored_version not in validatorfile:
                        continue

                    complete_module = (
                        "beacon.models."
                        + folder
                        + "."
                        + subfolder
                        + ".validator."
                        + response_type
                        + "."
                        + validatorfolder
                        + "."
                        + validatorfile
                    )

                    complete_module = complete_module.replace(
                        ".py",
                        ""
                    )

                    module = timed_import(
                        complete_module
                    )

                    start = time.perf_counter()

                    klass = getattr(
                        module,
                        validatorfolder.capitalize()
                    )

                    print(
                        f"[TIMING] getattr "
                        f"{complete_module}: "
                        f"{(time.perf_counter() - start) * 1000:.2f} ms",
                        flush=True,
                    )

                    list_of_results_classes_accepted.append(
                        klass
                    )

    # ---------------------------------------------------------
    # Filesystem + imports timing
    # ---------------------------------------------------------
    print(
        f"[TIMING] filesystem + imports: "
        f"{(time.perf_counter() - filesystem_start) * 1000:.2f} ms "
        f"({import_count} imports, "
        f"{cached_import_count} already cached)",
        flush=True,
    )

    # ---------------------------------------------------------
    # Show discovered classes
    # ---------------------------------------------------------
    print(
        f"[TIMING] result classes found: "
        f"{len(list_of_results_classes_accepted)}",
        flush=True,
    )

    for klass in list_of_results_classes_accepted:

        print(
            f"[TIMING] result class: "
            f"{klass.__module__}.{klass.__name__}",
            flush=True,
        )

    # ---------------------------------------------------------
    # Build Union
    # ---------------------------------------------------------
    start = time.perf_counter()

    union_type = Union[
        tuple(list_of_results_classes_accepted)
    ]

    print(
        f"[TIMING] Union construction: "
        f"{(time.perf_counter() - start) * 1000:.2f} ms",
        flush=True,
    )

    # ---------------------------------------------------------
    # Store in cache
    # ---------------------------------------------------------
    _RESULT_TYPES_CACHE[cache_key] = union_type

    print(
        f"[TIMING] load_types_of_results cached: "
        f"{cache_key}",
        flush=True,
    )

    # ---------------------------------------------------------
    # Total
    # ---------------------------------------------------------
    print(
        f"[TIMING] load_types_of_results TOTAL: "
        f"{(time.perf_counter() - total_start) * 1000:.2f} ms",
        flush=True,
    )

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

def get_all_modules_connections_script(script, connection):
    """Method to get all the submodules of connections per model loaded dynamically"""
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
                if dir == connection:
                    # Get the modules names in an array
                    complete_module='beacon.models.'+folder+'.connections.'+connection+'.'+script
                    import importlib
                    try:
                        module = importlib.import_module(complete_module, package=None)
                        list_of_modules.append(module)
                    except Exception as e:
                        continue
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
                        if dir == connection:
                            # Get the modules names in an array
                            complete_module='beacon.models.'+folder+'.'+subfolder+'.connections.'+connection+'.'+script
                            import importlib
                            module = importlib.import_module(complete_module, package=None)
                            list_of_modules.append(module)
    return list_of_modules

def get_all_modules_datasets(connection):
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
                complete_module='beacon.models.'+folder+'.connections.'+connection+'.collections'
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
                    complete_module='beacon.models.'+folder+'.'+subfolder+'.connections.'+connection+'.collections'
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
    
