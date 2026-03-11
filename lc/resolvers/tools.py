# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

"""Tools resolver for lc."""

from typing import Dict, Any, Optional, List

from lc.resolver import Resolver, Context


class ToolsResolver(Resolver):
    """Provides tool information for system prompt templates."""
    
    def resolve(self, context: Context) -> Optional[Dict[str, Any]]:
        """Generate tool context variables from built-in and skill toolkits."""
        # Get toolkits from session
        toolkits = context.session._load_toolkits()
        
        # Get skill toolkits from registry
        skill_toolkits = {}
        if hasattr(context.session, 'skill_registry'):
            skill_toolkits = context.session.skill_registry.get_all_toolkits()
        
        all_tools: Dict[str, Dict[str, Any]] = {}
        
        # Collect from built-in toolkits
        for name, toolkit in toolkits.items():
            all_tools.update(toolkit.tools)
        
        # Collect from skill toolkits (namespaced)
        for skill_name, toolkit in skill_toolkits.items():
            for tool_key, tool_spec in toolkit.tools.items():
                # Namespace skill tools: SkillName.tool_name
                namespaced_key = f"{skill_name}.{tool_key.split('.')[-1]}"
                all_tools[namespaced_key] = tool_spec
        
        return {
            "tools": {
                "names": list(all_tools.keys()),
                "summary_list": self._format_summary(all_tools),
                "by_toolkit": self._group_by_toolkit(all_tools),
                "full_schema": list(all_tools.values()),
                "count": len(all_tools),
            }
        }
    
    def _format_summary(self, tools: Dict[str, Dict[str, Any]]) -> str:
        """Format tools as readable summary with name, args, and description."""
        lines = []
        for name in sorted(tools.keys()):
            tool = tools[name]
            description = tool.get("description", "").strip()
            params = tool.get("parameters", {}).get("properties", {})
            
            # Extract parameter names
            param_names = list(params.keys())
            param_str = f"({', '.join(param_names)})" if param_names else "()"
            
            # Get first sentence or first line of description
            short_desc = description.split('\n')[0] if description else ""
            if '.' in short_desc:
                short_desc = short_desc[:short_desc.find('.') + 1]
            
            lines.append(f"• {name}{param_str} — {short_desc}")
        
        return '\n'.join(lines) if lines else "No tools available"
    
    def _group_by_toolkit(self, tools: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Group tools by their toolkit/skill name."""
        grouped: Dict[str, Dict[str, Any]] = {}
        
        for full_name, tool_spec in tools.items():
            # Extract toolkit name (everything before last dot)
            if '.' in full_name:
                toolkit_name = full_name.rsplit('.', 1)[0]
            else:
                toolkit_name = "builtin"
            
            if toolkit_name not in grouped:
                grouped[toolkit_name] = {
                    "tools": [],
                    "count": 0
                }
            
            grouped[toolkit_name]["tools"].append({
                "name": full_name,
                "description": tool_spec.get("description", "").split('\n')[0] if tool_spec.get("description") else "",
                "parameters": list(tool_spec.get("parameters", {}).get("properties", {}).keys())
            })
            grouped[toolkit_name]["count"] += 1
        
        return grouped
