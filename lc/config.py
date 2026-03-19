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
            print(f"Default configuration file created at {config_file}")
            print("Add model configuration to begin")
            os._exit(0)
        
        (config_path / "sessions").mkdir(exist_ok=True)
        (config_path / "templates").mkdir(exist_ok=True)
        (config_path / "skills").mkdir(exist_ok=True)

        RNS.logdest = RNS.LOG_FILE
        RNS.logfile = os.path.expanduser((config_path / "logfile"))

        sysprompt_path = (config_path / "templates" / "system.jinja")
        if not os.path.isfile(sysprompt_path):
            with open(sysprompt_path, "wb") as fh:
                fh.write(DEFAULT_SYSPROMPT.encode("UTF-8"))

        data = cls._parse_config(config_file)

        return cls(config_path, data)
    
    @classmethod
    def _parse_config(cls, config_file: Path) -> Dict[str, Any]:
        try:
            spec       = ConfigObj(CONFIG_SPEC.splitlines())
            model_spec = ConfigObj(MODEL_SPEC.splitlines())
            data       = ConfigObj(os.path.expanduser(config_file), configspec=spec, write_empty_values=True)

            if not "stdin"   in data: data["stdin"]   = {}
            if not "models"  in data: data["models"]  = {}
            if not "loading" in data: data["loading"] = {}
            if not "logging" in data: data["logging"] = {}
            if not "session" in data: data["session"] = {}
            if not "display" in data: data["display"] = {}

            if not data.get("toolkits",  {}).get("builtin",     {}): data["toolkits"]["builtin"]         = []
            if not data.get("toolkits",  {}).get("directories", {}): data["toolkits"]["directories"]     = []
            if not data.get("resolvers", {}).get("builtin",     {}): data["resolvers"]["builtin"]        = []
            if not data.get("resolvers", {}).get("directories", {}): data["resolvers"]["directories"]    = []
            if not data.get("skills",    {}).get("directories", {}): data["skills"]["directories"]       = []
            if not data.get("skills",    {}).get("pinned",      {}): data["skills"]["pinned"]            = []
            if not data.get("models",    {}).get("default",     {}): data["models"]["default"]           = "primary"
            if not data.get("logging",   {}).get("level",       {}): data["logging"]["level"]            = 4
            if not data.get("session",   {}).get("lock_timeout",{}): data["session"]["lock_timeout"]     = 10800
            
            if not data.get("loading",   {}).get("user_skills",   {}): data["loading"]["user_skills"]    = True
            if not data.get("loading",   {}).get("user_tools",    {}): data["loading"]["user_tools"]     = True
            if not data.get("loading",   {}).get("project_skills",{}): data["loading"]["project_skills"] = False
            if not data.get("loading",   {}).get("project_tools", {}): data["loading"]["project_tools"]  = False
            
            if not data.get("display",   {}).get("stream_output", {}): data["display"]["stream_output"]  = False

            if not data["stdin"].get("max_text_bytes", {}):   data["stdin"]["max_text_bytes"]   = 16384
            if not data["stdin"].get("max_binary_bytes", {}): data["stdin"]["max_binary_bytes"] = 512

            if isinstance(data["skills"]["directories"],    str): data["skills"]["directories"]    = [data["skills"]["directories"]]
            if isinstance(data["toolkits"]["directories"],  str): data["toolkits"]["directories"]  = [data["toolkits"]["directories"]]
            if isinstance(data["resolvers"]["directories"], str): data["resolvers"]["directories"] = [data["resolvers"]["directories"]]

            if isinstance(data["skills"]["pinned"],         str): data["skills"]["pinned"]         = [data["skills"]["pinned"]]
            if isinstance(data["toolkits"]["builtin"],      str): data["toolkits"]["builtin"]      = [data["toolkits"]["builtin"]]
            if isinstance(data["resolvers"]["builtin"],     str): data["resolvers"]["builtin"]     = [data["resolvers"]["builtin"]]

            validation = data.validate(Validator())

            RNS.loglevel = data["logging"]["level"]
            RNS.log(f"Configuration loaded from {config_file}", RNS.LOG_DEBUG)

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

            if not validation == True and is_invalid(validation):
                print("Configuration is invalid")
                print(f"The following entries have errors:")
                for k in failed_keys(validation): print(f" - {k}")
                os._exit(255)

            models_args = ["default"]
            configured_models = data.get("models", {})
            for model in [m for m in configured_models if not m in models_args]:
                model_data = ConfigObj(configured_models[model], configspec=model_spec, write_empty_values=True)
                if not model_data.get("sysprompt", {}): model_data["sysprompt"] = "system.jinja"
                if not model_data.get("vision",    {}): model_data["vision"]    = False
                model_validation = model_data.validate(Validator())
                if not model_validation == True and is_invalid(model_validation):
                    print(f"Model configuration for {model} is invalid")
                    print(f"The following entries have errors:")
                    for k in failed_keys(model_validation): print(f" - {k}")
                    os._exit(255)

                data["models"][model] = model_data

            return data

        except Exception as e:
            print("An exception occurred while loading and validating the configuration:")
            RNS.trace_exception(e)
            os._exit(255)
    
    @property
    def path(self) -> Path: return self._path
    
    @property
    def template_path(self) -> Path: return (self._path / "templates")
    
    @property
    def identity_path(self) -> Path: return (self._path / "agent_identity.rid")
    
    @property
    def model(self) -> Dict[str, Any]: return self.get_model_config()

    @property
    def session(self) -> Dict[str, Any]: return self._data.get("session", {})

    @property
    def display(self) -> Dict[str, Any]: return self._data.get("display", {})
    
    @property
    def toolkits(self) -> Dict[str, List[str]]:
        tk = self._data.get("toolkits", {})
        return { "builtin": self._parse_list(tk.get("builtin", "filesystem, shell")),
                 "directories": self._parse_list(tk.get("directories", "")) }
    
    @property
    def resolvers(self) -> Dict[str, List[str]]:
        res = self._data.get("resolvers", {})
        return { "builtin": self._parse_list(res.get("builtin", "environment, filesystem, system, tools, skills")),
                 "directories": self._parse_list(res.get("directories", "")) }
    
    @property
    def skills(self) -> Dict[str, Any]:
        sk = self._data.get("skills", {})
        return { "directories": self._parse_list(sk.get("directories", "")),
                 "pinned": self._parse_list(sk.get("pinned", "")) }
    
    @property
    def loading(self) -> Dict[str, bool]:
        ld = self._data.get("loading", {})
        return { "user_skills":    ld.get("user_skills", True),
                 "user_tools":     ld.get("user_tools", True),
                 "project_skills": ld.get("project_skills", False),
                 "project_tools":  ld.get("project_tools", False) }

    @property
    def stdin(self) -> Dict[str, int]:
        si = self._data.get("stdin", {})
        return { "max_text_bytes": si.get("max_text_bytes", 16384),
                 "max_binary_bytes": si.get("max_binary_bytes", 512) }

    def get_model_config(self, name: Optional[str] = None) -> Dict[str, Any]:
        model_section = self._data.get("models", {})
        
        # Get all nested model definitions (excluding top-level model keys)
        special_keys  = {"default"}
        nested_models = { k: v for k, v in model_section.items() 
                          if isinstance(v, dict) and k not in special_keys }
        
        if not nested_models: raise ValueError("No model configurations found in config file")
        
        primary_name = model_section.get("default")
        if not primary_name: primary_name = list(nested_models.keys())[0]
        
        target_name = name or primary_name
        if target_name not in nested_models:
            available = ", ".join(sorted(nested_models.keys()))
            raise ValueError(f"Model configuration '{target_name}' not found. Available: {available}")
        
        return nested_models[target_name]
    
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

MODEL_SPEC = """
backend = string
base_url = string
model = string
api_key = string
sysprompt = string
vision = boolean
temperature = float
max_tokens = integer
context_limit = integer
context_shift_factor = float
"""

CONFIG_SPEC = """
[models]
default = string

[toolkits]
builtin = list
directories = list

[resolvers]
builtin = list
directories = list

[skills]
pinned = list
directories = list

[loading]
user_skills = boolean
user_tools = boolean
project_skills = boolean
project_tools = boolean

[session]
persistence = boolean
lock_timeout = integer

[display]
show_reasoning = boolean
stream_output = boolean

[stdin]
max_text_bytes = integer
max_binary_bytes = integer

[logging]
level = integer
"""

DEFAULT_CONFIG = """
[models]
  default = primary

  [[primary]]
    backend = openai
    base_url = http://localhost:1234/v1
    model = local-model
    api_key =
    sysprompt = system.jinja
    vision = yes
    temperature = 0.7
    max_tokens = 32768
    context_limit = 200000
    context_shift_factor = 0.35

# Add more model configurations as needed:
# [[fast-model]]
#   backend = openai
#   base_url = http://localhost:1234/v1
#   model = glm4-flash
#   temperature = 0.3
#   max_tokens = 8192

[toolkits]
  # You can selectively enable built-in tools
  builtin = filesystem, shell, cryptography

  # And add additional, custom tool loading
  # directories in addition to the defaults.
  directories =

[resolvers]
  # You can selectively enable built-in resolvers
  builtin = environment, filesystem, system

  # And add additional, custom resolver loading
  # directories in addition to the defaults.
  directories =

[skills]
  # Pinned skills are fully loaded on session
  # initialization, and injected into the
  # system prompt. Also doesn't require pre-
  # execution skill load (already available).
  pinned =

  # You can add additional skill loading
  # directories in addition to the defaults.
  directories =

[loading]
  # You can control skill and tool loading
  # behaviour defaults.
  user_skills = true
  user_tools = true

  # Project tools and skills look for a
  # local .lc folder in the current working
  # directory, and load from here if available
  # and enabled.
  project_skills = false
  project_tools = false

[session]
  persistence = true
  lock_timeout = 10800

[display]
  show_reasoning = true
  stream_output = true

[stdin]
  # Truncation limits for piped data.
  max_text_bytes = 16384
  max_binary_bytes = 512

[logging]
  level = 4
"""

DEFAULT_SYSPROMPT = """I am `lc`, Humanity's Last Command: An excellent terminal assistant.
I augment the user's capabilities by reading files, executing commands, writing code and answering questions. I don't waste time on niceties, greetings, emojies and similar, but optimize the information density, semantic latitude and code quality in my outputs, while operating the available tools and the shell environment itself like a silicon wizard.

# Current context:

- User: {{ environment.user }}
- Session started: {{ environment.date }} {{ environment.time }}
- Working directory: {{ environment.cwd }}
- Directory contains: {{ filesystem.file_count }} files, {{ filesystem.dir_count }} directories
- Recent files: {{ filesystem.recent_files | join(", ") }}

## Tree of current working directory

{{ filesystem.tree }}

# Available skills ({{ skills.count }} total)

{{ skills.summary }}

# Available tools ({{ tools.count }} total)

{{ tools.summary_list }}

# Instructions

Use the available tools and skills to help the user accomplish their tasks. When using tools:
- Always check file contents before making modifications
- Confirm destructive operations with the user when appropriate
- For unpinned skill tools, call `skills.load_skill` first to get documentation
"""