# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

"""Core agent loop for lc."""

import RNS
import json
from typing import List, Dict, Any, Optional, Iterator, TYPE_CHECKING

from lc.config import Config
from lc.rendering import Renderer
from lc.toolkit import Context

if TYPE_CHECKING: from lc.session import Session


class Agent:
    """Core agent orchestrating model interaction and tool execution."""
    
    def __init__(self, session: "Session", model_backend, toolkits: Dict[str, Any], gate_level: Optional[int] = None):
        self.session    = session
        self.model      = model_backend
        self.toolkits   = toolkits
        self.gate_level = gate_level
        self.renderer   = Renderer(show_reasoning=session.config.display.get("show_reasoning", True))
    
    def run_turn(self, user_input: str) -> str:
        # Note: User message already added by session.execute()
        # Just ensure we have the latest tools and model response
        tools = self._get_all_tools()
        response = self._call_model(tools)
        
        return self._process_response(response)
    
    def _get_all_tools(self) -> List[Dict[str, Any]]:
        tools = []
        
        # Built-in toolkits
        for toolkit_name, toolkit in self.toolkits.items():
            for tool_spec in toolkit.tools.values():
                tools.append({"type": "function",
                              "function": { "name": tool_spec["name"],
                                            "description": tool_spec["description"],
                                            "parameters": tool_spec["parameters"] } })
        
        # Skill toolkits (namespaced)
        if hasattr(self.session, 'skill_registry'):
            for skill_name, toolkit in self.session.skill_registry.get_all_toolkits().items():
                for tool_key, tool_spec in toolkit.tools.items():
                    # Namespace skill tools: SkillName.tool_name
                    short_name = tool_key.split('.')[-1]
                    namespaced_name = f"{skill_name}.{short_name}"
                    tools.append({"type": "function",
                                  "function": { "name": namespaced_name,
                                                "description": tool_spec["description"],
                                                "parameters": tool_spec["parameters"] } })
        
        # Add load_skill tool
        tools.append({"type": "function",
                      "function": { "name": "skills.load_skill",
                                    "description": "Load a skill by name to access its documentation and tools. Required before using skill-specific tools.",
                                    "parameters": { "type": "object",
                                                    "properties": { "name": { "type": "string", "description": "Name of the skill to load" } },
                                                    "required": ["name"] } } })

        return tools
    
    def _call_model(self, tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        self.renderer.display_thinking()
        
        try:
            response = self.model.complete(messages=self.session.conversation, tools=tools if tools else None)
            self.renderer.clear_thinking()
            return response

        except Exception as e:
            self.renderer.clear_thinking()
            raise e
    
    def _process_response(self, response: Dict[str, Any]) -> str:
        message = response.get("message", {})
        tool_calls = message.get("tool_calls", [])
        
        if tool_calls:
            # Add assistant message with tool calls
            # Use null content when there are tool calls (not empty string)
            content = message.get("content")
            if not content: content = None
            
            assistant_msg = { "role": "assistant", "content": content, "tool_calls": tool_calls }
            self.session.conversation.append(assistant_msg)
            
            for tool_call in tool_calls:
                result = self._execute_tool_call(tool_call)
                self.session.conversation.append({"role": "tool", "tool_call_id": tool_call.get("id"),
                                                  "name": tool_call.get("function", {}).get("name"), "content": result})
            
            final_response = self._call_model(self._get_all_tools())
            return self._process_response(final_response)
        
        # No tool calls - just content response
        content = message.get("content", "")
        reasoning_content = message.get("reasoning_content")
        self.renderer.display_response(content, reasoning_content)
        
        # Add to conversation
        assistant_msg = { "role": "assistant", "content": content }
        
        if reasoning_content: assistant_msg["reasoning_content"] = reasoning_content
        self.session.conversation.append(assistant_msg)
        
        return content
    
    # Built-in toolkit prefixes that bypass skill gating
    BUILTIN_TOOLKIT_PREFIXES = {"FileSystemTools", "ShellTools"}
    
    def _execute_tool_call(self, tool_call: Dict[str, Any]) -> str:
        function = tool_call.get("function", {})
        tool_name = function.get("name", "")
        arguments_raw = function.get("arguments", "{}")
        
        # Handle both string and dict arguments (APIs vary)
        if isinstance(arguments_raw, dict): arguments = arguments_raw
        elif isinstance(arguments_raw, str):
            try: arguments = json.loads(arguments_raw)
            except json.JSONDecodeError: arguments = {}
        else: arguments = {}
        
        # Display tool call
        self.renderer.display_tool_call(tool_name, arguments)
        
        # Handle load_skill specially
        if tool_name == "skills.load_skill": 
            result = self._load_skill(arguments.get("name", ""))
            self.renderer.display_tool_result(result)
            return result
        
        # Find toolkit
        if "." in tool_name: toolkit_name, method_name = tool_name.rsplit(".", 1)
        else: return f"Error: Invalid tool name '{tool_name}'"
        
        # Check skill gating for non-built-in tools
        if toolkit_name not in self.BUILTIN_TOOLKIT_PREFIXES:
            if not self._is_skill_tool_allowed(toolkit_name):
                error_msg = f"Error: Skill '{toolkit_name}' documentation not loaded. Call skills.load_skill with name='{toolkit_name}' first."
                self.renderer.display_tool_result(error_msg)
                return error_msg
        
        # Get toolkit from built-ins or skill registry
        toolkit = None
        if toolkit_name in self.toolkits:
            toolkit = self.toolkits[toolkit_name]
        elif hasattr(self.session, 'skill_registry'):
            skill = self.session.skill_registry.get_skill(toolkit_name)
            if skill and skill._toolkit:
                toolkit = skill._toolkit
        
        if toolkit is None:
            return f"Error: Unknown toolkit '{toolkit_name}'"
        
        toolkit._lc_context = Context(session=self.session, config=self.session.config)
        
        # Dispatch & Render
        result = toolkit.dispatch(tool_name=method_name, arguments=arguments, gate_level=self.gate_level)
        self.renderer.display_tool_result(result)
        
        return result
    
    def _is_skill_tool_allowed(self, skill_name: str) -> bool:
        """Check if a skill tool is allowed to execute (loaded or pinned)."""
        # Check if explicitly loaded
        if skill_name in self.session.loaded_skills:
            return True
        
        # Check if skill is pinned (always allowed)
        if hasattr(self.session, 'skill_registry'):
            skill = self.session.skill_registry.get_skill(skill_name)
            if skill and skill.pinned:
                return True
        
        return False
    
    def _load_skill(self, skill_name: str) -> str:
        """Load skill documentation and mark skill as loaded."""
        if not hasattr(self.session, 'skill_registry'):
            return "Error: Skill registry not available"
        
        skill = self.session.skill_registry.get_skill(skill_name)
        if not skill:
            return f"Error: Skill '{skill_name}' not found"
        
        # Mark as loaded (idempotent)
        if skill_name not in self.session.loaded_skills:
            self.session.loaded_skills.append(skill_name)
        
        # Build response with skill documentation and available tools
        lines = [f"# {skill.name}", ""]
        
        if skill.description:
            lines.append(f"**Description:** {skill.description}")
            lines.append("")
        
        if skill.version:
            lines.append(f"**Version:** {skill.version}")
            lines.append("")
        
        # List available tools
        if skill.tools:
            lines.append("## Available Tools")
            lines.append("")
            for tool_name, tool_spec in skill.tools.items():
                short_name = tool_name.split('.')[-1]
                desc = tool_spec.get("description", "").split('\n')[0] if tool_spec.get("description") else ""
                lines.append(f"- `{short_name}`: {desc}")
            lines.append("")
        
        # Add documentation content
        if skill.content:
            lines.append("## Documentation")
            lines.append("")
            lines.append(skill.content)
        
        return "\n".join(lines)


class ModelBackend:
    """Abstract base for model backends."""
    
    def complete(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Send completion request to model.
        
        Args:
            messages: Conversation history
            tools: Available tools (if any)
        
        Returns:
            Response dict with 'message' key
        """
        raise NotImplementedError
    
    def complete_stream(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Iterator[str]:
        """Stream completion tokens (future implementation)."""
        raise NotImplementedError
