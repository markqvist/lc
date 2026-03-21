# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

# Quirks handling system for lc.
#
# Quirks are model-specific workarounds for edge cases in model behavior.
# They are lightweight modules that can be enabled per model.

import importlib
from pathlib import Path
from typing import Dict, Any, Optional, List
from lc.config import Config

import RNS

class QuirkRegistry:

    def __init__(self):
        self.quirks: Dict[str, Any] = {}
        self._load_quirks()

    def _load_quirks(self):
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

    def available(self, quirk_id: str) -> bool: return quirk_id in self.quirks
    def handle(self, quirk_id: str, response: Dict[str, Any]) -> Dict[str, Any]:
        if not quirk_id in self.quirks: return response
        else: return self.quirks[quirk_id].handle(response)


_registry: Optional[QuirkRegistry] = None
def get_quirk_registry() -> QuirkRegistry:
    global _registry
    if _registry is None: _registry = QuirkRegistry()
    return _registry