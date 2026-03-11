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
        """Parse simple INI-style config file."""
        data = {}
        current_section = None
        
        content = config_file.read_text(encoding='utf-8')
        
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'): continue
            
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1]
                data[current_section] = {}
            
            elif '=' in line and current_section is not None:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Convert types
                if value.lower() == 'true':    value = True
                elif value.lower() == 'false': value = False
                elif value.isdigit():          value = int(value)
                elif value.replace('.', '', 1).isdigit() and value.count('.') == 1: value = float(value)
                
                data[current_section][key] = value
        
        return data
    
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