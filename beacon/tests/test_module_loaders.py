import sys
import unittest
from enum import Enum
import builtins
import importlib as importlib_module
from types import SimpleNamespace
from unittest.mock import mock_open

if "strenum" not in sys.modules:
    strenum_stub = SimpleNamespace()

    class StrEnum(str, Enum):
        pass

    strenum_stub.StrEnum = StrEnum
    sys.modules["strenum"] = strenum_stub

if "yaml" not in sys.modules:
    yaml_stub = SimpleNamespace()

    def safe_load(_stream):
        stream_name = getattr(_stream, "name", "")
        if "api_version.yml" in stream_name:
            return {"api_version": "v2.2.0"}
        return {
            "ga4gh/beacon_v2_default_model": {"model_enabled": True},
            "EUCAIM": {"model_enabled": False},
        }

    yaml_stub.safe_load = safe_load
    yaml_stub.dump = lambda *args, **kwargs: None
    sys.modules["yaml"] = yaml_stub

import beacon.utils.modules as module_utils


class TestModuleLoaders(unittest.TestCase):
    def setUp(self):
        self.models_conf = (
            "ga4gh/beacon_v2_default_model:\n"
            "  model_enabled: True\n"
            "EUCAIM:\n"
            "  model_enabled: False\n"
        )

    def _listdir(self, path):
        mapping = {
            "/beacon/models": ["ga4gh", "EUCAIM"],
            "/beacon/models/ga4gh": ["connections"],
            "/beacon/models/EUCAIM": ["connections"],
            "/beacon/models/ga4gh/connections": ["mongo"],
            "/beacon/models/EUCAIM/connections": ["mongo"],
        }
        return mapping.get(path, [])

    def _assert_loader_skips_disabled_model(self, script_name):
        orig_listdir = module_utils.os.listdir
        orig_open = builtins.open
        orig_import_module = importlib_module.import_module
        imported_names = []

        def fake_import_module(name, package=None):
            imported_names.append(name)
            return SimpleNamespace(name=name)

        def fake_open(*args, **kwargs):
            handle = mock_open(read_data=self.models_conf)()
            handle.name = args[0] if args else ""
            return handle

        try:
            module_utils.os.listdir = self._listdir
            builtins.open = fake_open
            importlib_module.import_module = fake_import_module

            modules = module_utils.get_all_modules_mongo_connections_script(script_name)

            self.assertEqual(len(modules), 1)
            self.assertEqual(
                imported_names[0],
                f"beacon.models.ga4gh.connections.mongo.{script_name}",
            )
            self.assertNotIn(
                f"beacon.models.EUCAIM.connections.mongo.{script_name}",
                imported_names,
            )
        finally:
            module_utils.os.listdir = orig_listdir
            builtins.open = orig_open
            importlib_module.import_module = orig_import_module

    def test_get_all_modules_mongo_connections_script_skips_disabled_models(
        self,
    ):
        self._assert_loader_skips_disabled_model("collections")

    def test_get_all_modules_mongo_connections_script_skips_disabled_models_for_non_collections(
        self,
    ):
        self._assert_loader_skips_disabled_model("non_collections")

    def test_get_all_modules_datasets_skips_disabled_models(
        self,
    ):
        orig_listdir = module_utils.os.listdir
        orig_open = builtins.open
        orig_import_module = importlib_module.import_module
        imported_names = []

        def fake_import_module(name, package=None):
            imported_names.append(name)
            return SimpleNamespace(name=name)

        def fake_open(*args, **kwargs):
            handle = mock_open(read_data=self.models_conf)()
            handle.name = args[0] if args else ""
            return handle

        try:
            module_utils.os.listdir = self._listdir
            builtins.open = fake_open
            importlib_module.import_module = fake_import_module

            modules = module_utils.get_all_modules_datasets()

            self.assertEqual(len(modules), 1)
            self.assertEqual(
                imported_names[0],
                "beacon.models.ga4gh.connections.mongo.collections",
            )
            self.assertNotIn("beacon.models.EUCAIM.connections.mongo.collections", imported_names)
        finally:
            module_utils.os.listdir = orig_listdir
            builtins.open = orig_open
            importlib_module.import_module = orig_import_module

    def test_collection_validator_import_does_not_require_eucaim(self):
        module_name = "beacon.framework.validator.v2_0_0.collection"
        original_import = builtins.__import__
        sys.modules.pop(module_name, None)

        def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name.startswith("beacon.models.EUCAIM"):
                raise ModuleNotFoundError(name)
            return original_import(name, globals, locals, fromlist, level)

        try:
            builtins.__import__ = fake_import
            module = importlib_module.import_module(module_name)
            self.assertTrue(hasattr(module, "make_Collections"))
            self.assertTrue(hasattr(module, "make_CollectionResponse"))
        finally:
            builtins.__import__ = original_import
