# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

import os
import RNS
from lc.vendor.configobj import ConfigObj
from lc.vendor.validate import Validator
from pathlib import Path
from typing import Dict, List, Any, Optional

class Config:
    def __init__(self, config_path: Path, data: Dict[str, Any]):
        self._path = config_path
        self._data = data
    
    @classmethod
    def load(cls, config_path: Path) -> "Config":
        config_file = config_path / "config"
        
        if not config_file.exists():
            config_path.mkdir(parents=True, exist_ok=True)
            config_file.write_text(DEFAULT_CONFIG.strip())
            (config_path / "sessions").mkdir(exist_ok=True)
            (config_path / "skills").mkdir(exist_ok=True)

        data = cls._parse_config(config_file)

        return cls(config_path, data)
    
    @classmethod
    def _parse_config(cls, config_file: Path) -> Dict[str, Any]:
        try:
            spec       = ConfigObj(CONFIG_SPEC.splitlines())
            data       = ConfigObj(os.path.expanduser(config_file), configspec=spec, write_empty_values=True)

            if not data.get("toolkits",  {}).get("builtin",     {}): data["toolkits"]["builtin"]   = []
            if not data.get("toolkits",  {}).get("custom",      {}): data["toolkits"]["custom"]    = []
            if not data.get("resolvers", {}).get("builtin",     {}): data["resolvers"]["builtin"]  = []
            if not data.get("resolvers", {}).get("custom",      {}): data["resolvers"]["custom"]   = []
            if not data.get("skills",    {}).get("directories", {}): data["skills"]["directories"] = []
            if not data.get("skills",    {}).get("pinned",      {}): data["skills"]["pinned"]      = []

            validation = data.validate(Validator())

            def is_invalid(data: dict) -> bool:
                for key, value in data.items():
                    if value is False: return True
                    if isinstance(value, dict):
                        if is_invalid(value): return True
                return False
            
            def failed_keys(data: dict) -> List[str]:
                errors = []
                def traverse(current_data, prefix=""):
                    for key, value in current_data.items():
                        full_key = f"{prefix}.{key}" if prefix else key
                        if value is False: errors.append(full_key)
                        elif isinstance(value, dict): traverse(value, full_key)
                
                traverse(data)
                return errors

            if not validation and is_invalid(validation):
                print("Config is invalid!")
                print(f"Failed keys: {failed_keys(validation)}")
                os._exit(255)

            return data

        except Exception as e:
            print("An exception occurred while loading and validating the configuration:")
            RNS.trace_exception(e)
            os._exit(255)
    
    @property
    def path(self) -> Path: return self._path
    
    @property
    def model(self) -> Dict[str, Any]: return self._data.get("model", {})

    @property
    def session(self) -> Dict[str, Any]: return self._data.get("session", {})

    @property
    def display(self) -> Dict[str, Any]: return self._data.get("display", {})
    
    @property
    def toolkits(self) -> Dict[str, List[str]]:
        tk = self._data.get("toolkits", {})
        return { "builtin": self._parse_list(tk.get("builtin", "filesystem, shell")),
                 "custom": self._parse_list(tk.get("custom", "")) }
    
    @property
    def resolvers(self) -> Dict[str, List[str]]:
        res = self._data.get("resolvers", {})
        return { "builtin": self._parse_list(res.get("builtin", "environment, filesystem, system")),
                 "custom": self._parse_list(res.get("custom", "")) }
    
    @property
    def skills(self) -> Dict[str, Any]:
        sk = self._data.get("skills", {})
        return { "directories": self._parse_list(sk.get("directories", "")),
                 "pinned": self._parse_list(sk.get("pinned", "")) }
    
    def _parse_list(self, value: Any) -> List[str]:
        if not value: return []
        if isinstance(value, list): return [v.strip() for v in value if v.strip()]
        if isinstance(value, str):  return [v.strip() for v in value.split(",") if v.strip()]
        return []
    
    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split(".")
        value = self._data
        for k in keys:
            if isinstance(value, dict) and k in value: value = value[k]
            else: return default
        
        return value

CONFIG_SPEC = """
[model]
backend = string
base_url = string
model = string
api_key = string
temperature = float
max_tokens = integer
context_limit = integer

[toolkits]
builtin = list
custom = list

[resolvers]
builtin = list
custom = list

[skills]
directories = list
pinned = list

[session]
persistence = boolean
max_history = integer

[display]
show_reasoning = boolean
stream_output = boolean
"""

DEFAULT_CONFIG = """[model]
backend = openai
base_url = http://localhost:1234/v1
model = local-model
api_key =
temperature = 0.7
max_tokens = 4096
context_limit = 128000

[toolkits]
builtin = filesystem, shell
custom =

[resolvers]
builtin = environment, filesystem, system
custom =

[skills]
directories =
pinned =

[session]
persistence = true
max_history = 100

[display]
show_reasoning = true
stream_output = true
"""