# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

"""Toolkit base class and tool dispatch for lc."""

import inspect
import json
from abc import ABC
from typing import Dict, List, Any, Callable, Optional, get_type_hints
from functools import wraps

from pydantic import BaseModel, create_model


class Context:
    """Execution context passed to tools."""
    
    def __init__(self, session=None, config=None):
        self.session = session
        self.config = config
    
    def call_tool(self, toolkit: str, tool: str, arguments: Dict[str, Any]) -> str:
        """Call another tool programmatically."""
        # TODO: Implement cross-toolkit calls
        return ""
    
    def get_skill_doc(self, skill_name: str) -> Optional[str]:
        """Get documentation for a skill."""
        # TODO: Implement skill documentation access
        return None


def tool(func: Optional[Callable] = None, *, gate_level: Optional[int] = None):
    """Decorator to mark a method as a tool."""
    def decorator(f):
        f._is_tool = True
        f._gate_level = gate_level
        return f
    
    if func is not None: return decorator(func)
    return decorator


class Toolkit(ABC):
    """Base class for tool collections."""
    
    gate_level: int = 0
    
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._schemas: Dict[str, Dict[str, Any]] = {}
        self._gate_levels: Dict[str, int] = {}
        self._lc_context = None
        self._discover_tools()

    @property
    def context(self): return self._lc_context
    
    def _discover_tools(self) -> None:
        """Discover and register all tools in this toolkit."""
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if hasattr(method, '_is_tool'): self._register_tool(name, method)
    
    def _register_tool(self, name: str, method: Callable) -> None:
        """Register a tool and generate its schema."""
        self._tools[name] = method
        self._schemas[name] = self._generate_schema(method)
        
        # Determine gate level
        tool_gate = getattr(method, '_gate_level', None)
        if tool_gate is not None: self._gate_levels[name] = tool_gate
        else:                     self._gate_levels[name] = self.gate_level
    
    def _generate_schema(self, method: Callable) -> Dict[str, Any]:
        """Generate JSON schema for tool parameters."""
        sig = inspect.signature(method)
        type_hints = get_type_hints(method)
        
        properties = {}
        required = []
        
        for name, param in sig.parameters.items():
            # Skip 'self'
            if name in ('self'): continue
            
            param_schema = {}
            
            # Get type hint
            if name in type_hints:
                param_type = type_hints[name]
                param_schema.update(self._type_to_schema(param_type))
            
            # Check if required
            if param.default is inspect.Parameter.empty: required.append(name)
            else:                                        param_schema['default'] = param.default
            
            # Get docstring info
            if method.__doc__:
                # Simple param extraction from docstring
                # TODO: Better parsing
                pass
            
            properties[name] = param_schema
        
        schema = {"type": "object", "properties": properties}
        if required: schema["required"] = required
        
        return schema
    
    def _type_to_schema(self, param_type: type) -> Dict[str, Any]:
        """Convert Python type to JSON schema type."""
        type_map = {
            str: {"type": "string"},
            int: {"type": "integer"},
            float: {"type": "number"},
            bool: {"type": "boolean"},
            list: {"type": "array"},
            dict: {"type": "object"},
        }
        
        # Handle Pydantic models
        if isinstance(param_type, type) and issubclass(param_type, BaseModel): return param_type.model_json_schema()
        
        # Handle List[X] and Optional[X]
        origin = getattr(param_type, '__origin__', None)
        if origin is not None:
            if origin is list:
                args = getattr(param_type, '__args__', ())
                item_type = args[0] if args else Any
                return {"type": "array", "items": self._type_to_schema(item_type)}

            elif origin is Optional:
                args = getattr(param_type, '__args__', ())
                if args: return self._type_to_schema(args[0])
        
        return type_map.get(param_type, {"type": "string"})
    
    @property
    def tools(self) -> Dict[str, Dict[str, Any]]:
        """Get all tool schemas for this toolkit."""
        return {
            f"{self.__class__.__name__}.{name}": {
                "name": f"{self.__class__.__name__}.{name}",
                "description": self._tools[name].__doc__ or "",
                "parameters": schema,
                "gate_level": self._gate_levels[name],
            }
            for name, schema in self._schemas.items()
        }
    
    def dispatch(self, tool_name: str, arguments: Dict[str, Any], gate_level: Optional[int] = None) -> str:
        """Dispatch a tool call."""
        # Strip toolkit prefix if present
        if '.' in tool_name: _, tool_name = tool_name.rsplit('.', 1)
        
        if tool_name not in self._tools: return f"Error: Unknown tool '{tool_name}'"
        
        method = self._tools[tool_name]
        
        try:
            result = method(**arguments)
            return str(result) if result is not None else ""
        
        except Exception as e: return f"Error: {e}"
