# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

"""Standalone tool loading for lc.

Loads individual tool classes from directories outside of the skill system.
This allows users to load custom tools without creating full skill packages.
"""

import importlib.util
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

from lc.toolkit import Toolkit


class ToolLoader:
    """Loads standalone tool classes from directories."""
    
    def __init__(self, tool_dirs: List[Path]):
        self.tool_dirs = tool_dirs
        self.toolkits: Dict[str, Toolkit] = {}
        self._load_tools()
    
    def _load_tools(self) -> None:
        """Discover and load all standalone tools."""
        for tool_dir in self.tool_dirs:
            if not tool_dir.exists():
                continue
            
            for item in tool_dir.iterdir():
                if item.is_file() and item.suffix == '.py':
                    self._load_tool_file(item)
                elif item.is_dir() and (item / '__init__.py').exists():
                    self._load_tool_package(item)
    
    def _load_tool_file(self, file_path: Path) -> None:
        """Load a standalone tool from a Python file."""
        module_name = f"lc.tool.{file_path.stem}"
        
        try:
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not load spec from {file_path}")
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            self._extract_toolkits(module, file_path.stem)
            
        except Exception as e:
            raise RuntimeError(f"Failed to load tool from {file_path}: {e}") from e
    
    def _load_tool_package(self, dir_path: Path) -> None:
        """Load a tool from a package directory."""
        init_file = dir_path / '__init__.py'
        module_name = f"lc.tool.{dir_path.name}"
        
        try:
            spec = importlib.util.spec_from_file_location(module_name, init_file)
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not load spec from {init_file}")
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            self._extract_toolkits(module, dir_path.name)
            
        except Exception as e:
            raise RuntimeError(f"Failed to load tool package from {dir_path}: {e}") from e
    
    def _extract_toolkits(self, module: Any, default_name: str) -> None:
        """Extract Toolkit subclasses from a module."""
        toolkit_classes = []
        
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                issubclass(attr, Toolkit) and 
                attr is not Toolkit and
                attr.__module__ == module.__name__):
                toolkit_classes.append(attr)
        
        for toolkit_class in toolkit_classes:
            try:
                toolkit = toolkit_class()
                # Use class name as the toolkit identifier
                self.toolkits[toolkit_class.__name__] = toolkit
            except Exception as e:
                raise RuntimeError(f"Failed to instantiate {toolkit_class.__name__}: {e}") from e
    
    def get_toolkits(self) -> Dict[str, Toolkit]:
        """Get all loaded toolkits."""
        return self.toolkits
