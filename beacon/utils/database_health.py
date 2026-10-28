
import os
import yaml

from functools import lru_cache

from beacon.conf.conf_override import config
from beacon.exceptions.exceptions import DatabaseIsDown


MODELS_CONF_PATH = "/beacon/conf/models/models_conf.yml"
CONNECTIONS_CONF_PATH = "/beacon/conf/connections/connections_conf.yml"
MODELS_PATH = "/beacon/models"


@lru_cache(maxsize=1)
def _load_configuration():
    """Load configuration files once and cache their contents."""
    with open(MODELS_CONF_PATH, "r") as f:
        models_config = yaml.safe_load(f) or {}

    with open(CONNECTIONS_CONF_PATH, "r") as f:
        connections_config = yaml.safe_load(f) or {}

    enabled_connections = {
        name
        for name, value in connections_config.items()
        if value.get("connection_enabled") is True
    }

    return models_config, enabled_connections


def _iter_entry_type_configs(models_config):
    """Yield entry-type configuration dictionaries from model folders."""
    for root, dirs, files in os.walk(MODELS_PATH):
        relative_model = os.path.relpath(root, MODELS_PATH)

        # Skip directories belonging to disabled models.
        model_key = relative_model.replace(os.sep, "/")
        if model_key in models_config:
            if models_config[model_key].get("model_enabled") is False:
                dirs[:] = []
                continue

        # Only inspect entry_types configuration directories.
        if os.path.basename(root) != "entry_types":
            continue

        for filename in files:
            if filename.endswith((".yml", ".yaml")):
                path = os.path.join(root, filename)
                with open(path, "r") as f:
                    yield yaml.safe_load(f) or {}


@lru_cache(maxsize=256)
def get_cached_connections(entry_type=None, pre_entry_type=None):
    """
    Discover enabled database connections for an entry type.
    Results are cached by entry_type and pre_entry_type.
    """
    models_config, enabled_connections = _load_configuration()
    connections = set()

    for entry_type_config in _iter_entry_type_configs(models_config):
        for entry_config in entry_type_config.values():
            endpoint = entry_config.get("endpoint_name")

            # Preserve the matching behavior of the original function.
            matches = (
                entry_type is None
                or (endpoint == entry_type and pre_entry_type is None)
                or endpoint == pre_entry_type
            )

            if not matches:
                continue

            if entry_config.get("entry_type_enabled") is not True:
                continue

            connection = entry_config.get("connection", {}).get("name")
            if connection in enabled_connections:
                connections.add(connection)

            # Discover applicable lookup connections.
            lookups = entry_config.get("lookups", {})
            if not isinstance(lookups, dict):
                continue

            for lookup in lookups.values():
                if not isinstance(lookup, dict):
                    continue

                lookup_connection = (
                    lookup.get("connection", {}).get("name")
                )
                if lookup_connection not in enabled_connections:
                    continue

                if pre_entry_type is not None and entry_type is not None:
                    expected_endpoint = (
                        f"{pre_entry_type}/{{id}}/{entry_type}"
                    )
                    if lookup.get("endpoint_name") != expected_endpoint:
                        continue

                connections.add(lookup_connection)

    return tuple(sorted(connections))


def clear_connection_cache():
    """Call after changing model or connection configuration."""
    get_cached_connections.cache_clear()
    _load_configuration.cache_clear()


async def check_selected_database_connections(
    LOG=None,
    connections=(),
):
    import asyncio
    import importlib


    async def ping_one(connection_name):

        try:
            ping_module = importlib.import_module(
                f"beacon.connections.{connection_name}.ping"
            )
            client_module = importlib.import_module(
                f"beacon.connections.{connection_name}.client"
            )

            ping_database = ping_module.ping_database
            get_client = client_module.get_client

            client = get_client()

            ping_task = asyncio.create_task(ping_database(client))

            await asyncio.wait_for(
                ping_task,
                timeout=config.pending_requests_timeout_in_seconds,
            )

        except Exception as exc:
            if LOG is not None:
                LOG.error("%s database is down", connection_name)
            raise DatabaseIsDown(connection_name) from exc

    await asyncio.gather(*(ping_one(name) for name in connections))