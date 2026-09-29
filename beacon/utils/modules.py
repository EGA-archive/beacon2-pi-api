
import os
from typing import Union
import re
import yaml
from beacon.logs.logs import log_with_args_check_configuration, log_with_args
from beacon.conf.conf_override import config
from beacon.exceptions.exceptions import DatabaseIsDown
import asyncio
import time
from functools import lru_cache
from pathlib import Path
import importlib

MODELS_CONFIG_PATH = Path("/beacon/conf/models/models_conf.yml")
CONNECTIONS_CONFIG_PATH = Path(
    "/beacon/conf/connections/connections_conf.yml"
)
MODELS_PATH = Path("/beacon/models")


# Increment this whenever configuration or model files change.
_CACHE_VERSION = 0


def clear_configuration_caches():
    """
    Clear all caches that depend on filesystem/configuration state.
    Call this after changing models_conf.yml, connections_conf.yml,
    adding/removing models, or adding/removing validator modules.
    """
    global _CACHE_VERSION
    _CACHE_VERSION += 1

    _load_models_config.cache_clear()
    _load_connections_config.cache_clear()
    _get_model_directories.cache_clear()
    _get_directory_entries.cache_clear()
    _load_entry_type_config.cache_clear()
    _discover_result_classes.cache_clear()
    _get_one_module_conf_cached.cache_clear()
    _get_modules_confiles_cached.cache_clear()
    _get_all_modules_connections_script_cached.cache_clear()
    _get_all_modules_datasets_cached.cache_clear()

@lru_cache(maxsize=1)
def _load_models_config():
    with MODELS_CONFIG_PATH.open("r") as pfile:
        return yaml.safe_load(pfile) or {}


@lru_cache(maxsize=1)
def _load_connections_config():
    with CONNECTIONS_CONFIG_PATH.open("r") as infile:
        return yaml.safe_load(infile) or {}


@lru_cache(maxsize=1)
def _get_model_directories():
    """
    Return a tuple because cached return values should not be mutated.
    """
    return tuple(
        entry.name
        for entry in MODELS_PATH.iterdir()
        if entry.is_dir()
    )


@lru_cache(maxsize=None)
def _get_directory_entries(path_string):
    """
    Cached equivalent of os.listdir(path).
    """
    path = Path(path_string)

    return tuple(
        entry.name
        for entry in path.iterdir()
    )


@lru_cache(maxsize=None)
def _load_entry_type_config(path_string):
    path = Path(path_string)

    with path.open("r") as pfile:
        return yaml.safe_load(pfile) or {}

@lru_cache(maxsize=None)
def _load_module(module_name):
    return importlib.import_module(module_name)


@lru_cache(maxsize=None)
def _load_class(module_name, class_name):
    module = _load_module(module_name)
    return getattr(module, class_name)

@log_with_args(config.level)
def load_framework_module(self, script_name):
    module_name = (
        "beacon.framework.validator."
        f"{self.request_attributes.returned_apiVersion.replace('.', '_')}."
        f"{script_name}"
    )
    return _load_module(module_name)


@log_with_args(config.level)
def load_source_module(self, script_name):
    module_name = (
        f"beacon.connections."
        f"{self.request_attributes.source}."
        f"{script_name}"
    )
    return _load_module(module_name)


def load_client(folder):
    module_name = f"beacon.connections.{folder}.client"
    return getattr(_load_module(module_name), "get_client")


def load_class(self, script_name, className):
    module_name = (
        "beacon.framework.validator."
        f"{self.request_attributes.returned_apiVersion.replace('.', '_')}."
        f"{script_name}"
    )
    return _load_class(module_name, className)

@lru_cache(maxsize=None)
def _discover_result_classes(response_type, underscored_version):
    models_config = _load_models_config()
    result_classes = []

    def add_validator_classes(
        model_parts,
        validator_base_path
    ):
        try:
            validator_dirs = _get_directory_entries(
                str(validator_base_path)
            )
        except FileNotFoundError:
            return

        for validator_folder in validator_dirs:
            validator_path = validator_base_path / validator_folder

            try:
                validator_files = _get_directory_entries(
                    str(validator_path)
                )
            except FileNotFoundError:
                continue

            for validator_file in validator_files:
                if not validator_file.endswith(".py"):
                    continue

                if underscored_version not in validator_file:
                    continue

                module_name = ".".join(
                    [
                        "beacon",
                        "models",
                        *model_parts,
                        "validator",
                        response_type,
                        validator_folder,
                        validator_file[:-3],
                    ]
                )

                class_name = validator_folder.capitalize()
                result_classes.append(
                    _load_class(module_name, class_name)
                )

    for folder in _get_model_directories():
        folder_path = MODELS_PATH / folder
        subdirs = _get_directory_entries(str(folder_path))

        if (
            folder in models_config
            and models_config[folder]["model_enabled"] is False
        ):
            continue

        # Model layout:
        #
        # /beacon/models/<folder>/validator/...
        #
        if "validator" in subdirs:
            add_validator_classes(
                [folder],
                folder_path / "validator" / response_type
            )

        # Nested model layout:
        #
        # /beacon/models/<folder>/<subfolder>/validator/...
        #
        for subfolder in subdirs:
            model_key = f"{folder}/{subfolder}"

            if (
                model_key in models_config
                and models_config[model_key]["model_enabled"] is False
            ):
                continue

            model_path = folder_path / subfolder
            underdirs = _get_directory_entries(str(model_path))

            if "validator" not in underdirs:
                continue

            add_validator_classes(
                [folder, subfolder],
                model_path / "validator" / response_type
            )

    return tuple(result_classes)


def load_types_of_results(self, response_type):
    schema = self.request_attributes.returned_schema[0]["schema"]

    version_match = re.search(r"(v\d+(?:\.\d+)*)", schema)

    if not version_match:
        raise ValueError(
            "Could not determine schema version from returned_schema"
        )

    version = version_match.group(1)
    underscored_version = version.replace(".", "_")

    classes = _discover_result_classes(
        response_type,
        underscored_version
    )

    if not classes:
        raise ValueError(
            f"No result validator classes found for "
            f"response_type={response_type!r}, "
            f"version={version!r}"
        )

    return Union[classes]

def _iter_enabled_entry_type_configs():
    models_config = _load_models_config()

    for folder in _get_model_directories():
        folder_path = MODELS_PATH / folder
        subdirs = _get_directory_entries(str(folder_path))

        if (
            folder in models_config
            and models_config[folder]["model_enabled"] is False
        ):
            continue

        model_paths = []

        if "conf" in subdirs:
            model_paths.append((folder, folder_path))
        else:
            for subfolder in subdirs:
                model_key = f"{folder}/{subfolder}"

                if (
                    model_key in models_config
                    and models_config[model_key]["model_enabled"] is False
                ):
                    continue

                model_paths.append(
                    (
                        model_key,
                        folder_path / subfolder
                    )
                )

        for model_key, model_path in model_paths:
            entry_types_path = (
                model_path / "conf" / "entry_types"
            )

            try:
                config_files = _get_directory_entries(
                    str(entry_types_path)
                )
            except FileNotFoundError:
                continue

            for config_file in config_files:
                if config_file == "__pycache__":
                    continue

                if not config_file.endswith((".yml", ".yaml")):
                    continue

                config_path = entry_types_path / config_file
                yield _load_entry_type_config(str(config_path))

@lru_cache(maxsize=1)
def _load_routes_cached():
    routes_to_add = {}

    for entry_type_config in _iter_enabled_entry_type_configs():
        for _, entry_type_params in entry_type_config.items():
            if not entry_type_params.get("entry_type_enabled", False):
                continue

            endpoint = entry_type_params["endpoint_name"]
            response_type = entry_type_params["response_type"]

            routes_to_add[endpoint] = [response_type]
            routes_to_add[f"{endpoint}/{{id}}"] = [response_type]

            for lookup in entry_type_params.get("lookups", {}).values():
                if isinstance(lookup, dict):
                    routes_to_add[lookup["endpoint_name"]] = [
                        lookup["response_type"]
                    ]

    return routes_to_add


def load_routes():
    """
    Return a copy so callers cannot mutate the cached dictionary.
    """
    return dict(_load_routes_cached())

@lru_cache(maxsize=None)
def _get_one_module_conf_cached(entry_type):
    for entry_type_config in _iter_enabled_entry_type_configs():
        for _, entry_type_params in entry_type_config.items():
            if entry_type_params["endpoint_name"] == entry_type:
                return entry_type_config

    return None


def get_one_module_conf(entry_type):
    result = _get_one_module_conf_cached(entry_type)

    if result is None:
        return None

    return dict(result)

@lru_cache(maxsize=1)
def _get_modules_confiles_cached():
    return tuple(
        _iter_enabled_entry_type_configs()
    )


def get_modules_confiles():
    """
    Return a tuple of configuration dictionaries.
    """
    return _get_modules_confiles_cached()

@lru_cache(maxsize=None)
def _get_all_modules_connections_script_cached(script, connection):
    modules = []

    for folder in _get_model_directories():
        folder_path = MODELS_PATH / folder
        subdirs = _get_directory_entries(str(folder_path))

        # Direct model layout
        if "connections" in subdirs:
            connection_path = (
                folder_path / "connections" / connection
            )

            if connection_path.is_dir():
                module_name = (
                    f"beacon.models.{folder}."
                    f"connections.{connection}.{script}"
                )

                try:
                    modules.append(_load_module(module_name))
                except ModuleNotFoundError:
                    pass

            continue

        # Nested model layout
        for subfolder in subdirs:
            model_path = folder_path / subfolder
            underdirs = _get_directory_entries(str(model_path))

            if "connections" not in underdirs:
                continue

            connection_path = (
                model_path / "connections" / connection
            )

            if not connection_path.is_dir():
                continue

            module_name = (
                f"beacon.models.{folder}.{subfolder}."
                f"connections.{connection}.{script}"
            )

            try:
                modules.append(_load_module(module_name))
            except ModuleNotFoundError:
                pass

    return tuple(modules)


def get_all_modules_connections_script(script, connection):
    return list(
        _get_all_modules_connections_script_cached(
            script,
            connection
        )
    )

@lru_cache(maxsize=None)
def _get_all_modules_datasets_cached(connection):
    modules = []

    for folder in _get_model_directories():
        folder_path = MODELS_PATH / folder
        subdirs = _get_directory_entries(str(folder_path))

        if "connections" in subdirs:
            module_name = (
                f"beacon.models.{folder}."
                f"connections.{connection}.collections"
            )

            try:
                modules.append(_load_module(module_name))
            except ModuleNotFoundError:
                pass

        for subfolder in subdirs:
            model_path = folder_path / subfolder
            underdirs = _get_directory_entries(str(model_path))

            if "connections" not in underdirs:
                continue

            module_name = (
                f"beacon.models.{folder}.{subfolder}."
                f"connections.{connection}.collections"
            )

            try:
                modules.append(_load_module(module_name))
            except ModuleNotFoundError:
                pass

    return tuple(modules)


def get_all_modules_datasets(connection):
    return list(
        _get_all_modules_datasets_cached(connection)
    )

@lru_cache(maxsize=None)
def _get_all_modules_datasets_cached(connection):
    modules = []

    for folder in _get_model_directories():
        folder_path = MODELS_PATH / folder
        subdirs = _get_directory_entries(str(folder_path))

        if "connections" in subdirs:
            module_name = (
                f"beacon.models.{folder}."
                f"connections.{connection}.collections"
            )

            try:
                modules.append(_load_module(module_name))
            except ModuleNotFoundError:
                pass

        for subfolder in subdirs:
            model_path = folder_path / subfolder
            underdirs = _get_directory_entries(str(model_path))

            if "connections" not in underdirs:
                continue

            module_name = (
                f"beacon.models.{folder}.{subfolder}."
                f"connections.{connection}.collections"
            )

            try:
                modules.append(_load_module(module_name))
            except ModuleNotFoundError:
                pass

    return tuple(modules)


def get_all_modules_datasets(connection):
    return list(
        _get_all_modules_datasets_cached(connection)
    )

@lru_cache(maxsize=None)
def _get_database_connections_to_check(
    entry_type=None,
    pre_entry_type=None
):
    connections_config = _load_connections_config()

    connections_enabled = {
        name
        for name, value in connections_config.items()
        if value.get("connection_enabled") is True
    }

    connections_to_check = set()

    for entry_type_config in _iter_enabled_entry_type_configs():
        for _, params in entry_type_config.items():
            endpoint = params.get("endpoint_name")

            matches = (
                entry_type is None
                or endpoint == entry_type
                or pre_entry_type is None
                or endpoint == pre_entry_type
            )

            if not matches:
                continue

            if not params.get("entry_type_enabled", False):
                continue

            connection_name = params["connection"]["name"]

            if connection_name in connections_enabled:
                connections_to_check.add(connection_name)

            for lookup in params.get("lookups", {}).values():
                if not isinstance(lookup, dict):
                    continue

                lookup_endpoint = lookup.get("endpoint_name")

                if (
                    entry_type is not None
                    and pre_entry_type is not None
                    and lookup_endpoint
                    == f"{pre_entry_type}/{{id}}/{entry_type}"
                ):
                    lookup_connection = lookup["connection"]["name"]

                    if lookup_connection in connections_enabled:
                        connections_to_check.add(lookup_connection)

    return tuple(sorted(connections_to_check))

@log_with_args_check_configuration(config.level)
async def check_database_connections(
    LOG=None,
    entry_type=None,
    pre_entry_type=None
):
    connections = _get_database_connections_to_check(
        entry_type,
        pre_entry_type
    )

    for folder in connections:
        ping_module = _load_module(
            f"beacon.connections.{folder}.ping"
        )
        client_module = _load_module(
            f"beacon.connections.{folder}.client"
        )

        ping_database = getattr(
            ping_module,
            "ping_database"
        )
        get_client = getattr(
            client_module,
            "get_client"
        )

        try:
            await asyncio.wait_for(
                ping_database(get_client()),
                timeout=config.pending_requests_timeout_in_seconds
            )
        except Exception:
            LOG.error(f"{folder} database is down")
            raise DatabaseIsDown(folder)