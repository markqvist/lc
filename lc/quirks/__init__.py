# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

# Quirks handling system for lc.
#
# Quirks are model-specific workarounds for edge cases in model behavior.
# They are lightweight modules that can be enabled per model.

import sys
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, Any, Optional, List
from lc.config import Config

import RNS

class QuirkRegistry:

    def __init__(self, config):
        self.config = config
        self.quirks: Dict[str, Any] = {}
        self._load_builtin_quirks()
        self._load_user_quirks()

    def _load_builtin_quirks(self):
        quirks_dir = Path(__file__).parent
        for quirk_file in quirks_dir.glob("*.py"):
            if quirk_file.name == "__init__.py": continue
            quirk_name = quirk_file.stem

            try:
                module = importlib.import_module(f"lc.quirks.{quirk_name}")
                if hasattr(module, "quirk_id"):
                    quirk_id = module.quirk_id
                    self.quirks[quirk_id] = module
                    RNS.log(f"Loaded quirk: {quirk_id}", RNS.LOG_DEBUG)
                
                else: RNS.log(f"Quirk module {quirk_name} missing quirk_id attribute", RNS.LOG_ERROR)
            
            except Exception as e: RNS.log(f"Could not load quirk {quirk_name}: {e}", RNS.LOG_ERROR)

    def _load_user_quirks(self):
        if not self.config.loading["user_quirks"]:
            RNS.log("User quirk loading disabled, skipping", RNS.LOG_DEBUG)
            return

        quirks_dir = self.config.quirks_path
        if not quirks_dir.exists():
            RNS.log(f"User quirks directory does not exist: {quirks_dir}", RNS.LOG_DEBUG)
            return

        RNS.log(f"Loading user quirks from {quirks_dir}", RNS.LOG_DEBUG)

        for quirk_file in quirks_dir.glob("*.py"):
            if quirk_file.name == "__init__.py": continue

            quirk_name = quirk_file.stem
            module_name = f"lc.user_quirks.{quirk_name}"

            try:
                spec = importlib.util.spec_from_file_location(module_name, quirk_file)
                if spec is None or spec.loader is None:
                    RNS.log(f"Could not create module spec for {quirk_name}", RNS.LOG_ERROR)
                    continue

                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)

                if not hasattr(module, "quirk_id"):
                    RNS.log(f"Quirk module {quirk_name} missing quirk_id attribute", RNS.LOG_ERROR)
                    continue

                quirk_id = module.quirk_id
                self.quirks[quirk_id] = module
                RNS.log(f"Loaded user quirk: {quirk_id}", RNS.LOG_DEBUG)

            except Exception as e:
                RNS.log(f"Could not load user quirk {quirk_name}: {e}", RNS.LOG_ERROR)

    def available(self, quirk_id: str) -> bool: return quirk_id in self.quirks
    def handle(self, quirk_id: str, response: Dict[str, Any]) -> Dict[str, Any]:
        if not quirk_id in self.quirks: return response
        else: return self.quirks[quirk_id].handle(response)


_registry: Optional[QuirkRegistry] = None
def get_quirk_registry(config) -> QuirkRegistry:
    global _registry
    if _registry is None: _registry = QuirkRegistry(config)
    return _registry