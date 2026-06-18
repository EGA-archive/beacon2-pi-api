import sys
import unittest
from enum import Enum
import builtins
import importlib as importlib_module
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import mock_open

# Provide a lightweight fallback implementation of strenum
# when the dependency is not installed in the environment.
if "strenum" not in sys.modules:
    strenum_stub = SimpleNamespace()

    # Minimal StrEnum implementation for tests.
    class StrEnum(str, Enum):
        pass

    strenum_stub.StrEnum = StrEnum
    sys.modules["strenum"] = strenum_stub

# Provide a stub YAML module if PyYAML is unavailable.
if "yaml" not in sys.modules:
    yaml_stub = SimpleNamespace()

    # Return predictable configuration data for tests.
    def safe_load(_stream):
        stream_name = getattr(_stream, "name", "")

        # Mock API version configuration file.
        if "api_version.yml" in stream_name:
            return {"api_version": "v2.2.0"}

        # Mock model configuration file.
        return {
            "ga4gh/beacon_v2_default_model": {"model_enabled": True},
            "EUCAIM": {"model_enabled": False},
        }

    yaml_stub.safe_load = safe_load

    # dump is not required in these tests.
    yaml_stub.dump = lambda *args, **kwargs: None
    sys.modules["yaml"] = yaml_stub

# Stub humps package to avoid importing the real dependency.
if "humps" not in sys.modules:
    humps_stub = SimpleNamespace()

    # Keep camelize behavior as a no-op for tests.
    humps_main_stub = SimpleNamespace(camelize=lambda value: value)

    humps_stub.main = humps_main_stub
    sys.modules["humps"] = humps_stub
    sys.modules["humps.main"] = humps_main_stub

# Module under test.
import beacon.utils.modules as module_utils


class TestModuleLoaders(unittest.TestCase):
    def setUp(self):
        # Sample model configuration used by multiple tests.
        self.models_conf = (
            "ga4gh/beacon_v2_default_model:\n"
            "  model_enabled: True\n"
            "EUCAIM:\n"
            "  model_enabled: False\n"
        )

    def _listdir(self, path):
        # Mock filesystem layout expected by module loaders.
        mapping = {
            "/beacon/models": ["ga4gh", "EUCAIM"],
            "/beacon/models/ga4gh": ["connections"],
            "/beacon/models/EUCAIM": ["connections"],
            "/beacon/models/ga4gh/connections": ["mongo"],
            "/beacon/models/EUCAIM/connections": ["mongo"],
        }
        return mapping.get(path, [])

    def _assert_loader_skips_disabled_model(self, script_name):
        # Save original functions so they can be restored later.
        orig_listdir = module_utils.os.listdir
        orig_open = builtins.open
        orig_import_module = importlib_module.import_module
        imported_names = []

        # Track imports performed by the loader.
        def fake_import_module(name, package=None):
            imported_names.append(name)
            return SimpleNamespace(name=name)

        # Mock configuration file reads.
        def fake_open(*args, **kwargs):
            handle = mock_open(read_data=self.models_conf)()
            handle.name = args[0] if args else ""
            return handle

        try:
            # Patch dependencies with test doubles.
            module_utils.os.listdir = self._listdir
            builtins.open = fake_open
            importlib_module.import_module = fake_import_module

            modules = module_utils.get_all_modules_mongo_connections_script(script_name)

            # Only enabled models should be imported.
            self.assertEqual(len(modules), 1)
            self.assertEqual(
                imported_names[0],
                f"beacon.models.ga4gh.connections.mongo.{script_name}",
            )

            # Disabled models must not be imported.
            self.assertNotIn(
                f"beacon.models.EUCAIM.connections.mongo.{script_name}",
                imported_names,
            )
        finally:
            # Restore original functions.
            module_utils.os.listdir = orig_listdir
            builtins.open = orig_open
            importlib_module.import_module = orig_import_module

    def test_get_all_modules_mongo_connections_script_skips_disabled_models(
        self,
    ):
        # Verify collection scripts ignore disabled models.
        self._assert_loader_skips_disabled_model("collections")

    def test_get_all_modules_mongo_connections_script_skips_disabled_models_for_non_collections(
        self,
    ):
        # Verify non-collection scripts ignore disabled models.
        self._assert_loader_skips_disabled_model("non_collections")

    def test_get_all_modules_datasets_skips_disabled_models(
        self,
    ):
        orig_listdir = module_utils.os.listdir
        orig_open = builtins.open
        orig_import_module = importlib_module.import_module
        imported_names = []

        # Capture imported module names.
        def fake_import_module(name, package=None):
            imported_names.append(name)
            return SimpleNamespace(name=name)

        # Return mocked model configuration.
        def fake_open(*args, **kwargs):
            handle = mock_open(read_data=self.models_conf)()
            handle.name = args[0] if args else ""
            return handle

        try:
            module_utils.os.listdir = self._listdir
            builtins.open = fake_open
            importlib_module.import_module = fake_import_module

            modules = module_utils.get_all_modules_datasets()

            # Expect only one enabled dataset module.
            self.assertEqual(len(modules), 1)
            self.assertEqual(
                imported_names[0],
                "beacon.models.ga4gh.connections.mongo.collections",
            )

            # Disabled dataset module should be skipped.
            self.assertNotIn(
                "beacon.models.EUCAIM.connections.mongo.collections",
                imported_names,
            )
        finally:
            # Clean up monkey patches.
            module_utils.os.listdir = orig_listdir
            builtins.open = orig_open
            importlib_module.import_module = orig_import_module

    def test_collection_validator_import_does_not_require_eucaim(self):
        # Ensure validator imports work without EUCAIM installed.
        module_name = "beacon.framework.validator.v2_0_0.collection"
        original_import = builtins.__import__

        # Force a fresh import.
        sys.modules.pop(module_name, None)

        def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
            # Simulate missing EUCAIM modules.
            if name.startswith("beacon.models.EUCAIM"):
                raise ModuleNotFoundError(name)

            return original_import(name, globals, locals, fromlist, level)

        try:
            builtins.__import__ = fake_import

            module = importlib_module.import_module(module_name)

            # Validator factory functions should still exist.
            self.assertTrue(hasattr(module, "make_Collections"))
            self.assertTrue(hasattr(module, "make_CollectionResponse"))
        finally:
            builtins.__import__ = original_import

    def test_get_variants_of_dataset_uses_dataset_dataset_string(self):
        # Verify dataset identifier is sourced from dataset.dataset.
        source = (
            Path(__file__).resolve().parents[1]
            / "models"
            / "ga4gh"
            / "beacon_v2_default_model"
            / "connections"
            / "mongo"
            / "non_collections.py"
        )

        source_text = source.read_text().replace(" ", "")

        self.assertIn(
            'queryid["datasetid"]=dataset.dataset',
            source_text.lower(),
        )

    def test_request_setup_uses_configured_database_name(self):
        # Verify configured database name is used in requests setup.
        source = Path(__file__).resolve().parents[1] / "utils" / "requests.py"

        source_text = source.read_text().replace(" ", "").lower()

        self.assertIn(
            'connection=client[mongo_conf.database_name][param_value["table"]]',
            source_text,
        )
