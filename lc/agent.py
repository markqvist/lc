# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

import re
import RNS
import json
from typing import List, Dict, Any, Optional, Iterator, Callable, TYPE_CHECKING

from lc.config import Config
from lc.rendering import TTYRenderer
from lc.toolkit import Context
from lc.quirks import get_quirk_registry

if TYPE_CHECKING: from lc.session import Session


class Agent:

    GATE_DESCRIPTIONS = { 0: "read-only operations",
                          1: "file write operations",
                          2: "command execution (read-only)",
                          3: "destructive/destructive execution" }
    
    def __init__(self, session: "Session", model_backend, toolkits: Dict[str, Any], gate_level: Optional[int] = None, can_prompt: bool = False,
                 disable_markdown=False, output_mode: str = "tty"):

        self.session     = session
        self.model       = model_backend
        self.toolkits    = toolkits
        self.gate_level  = gate_level
        self.can_prompt  = can_prompt
        self.output_mode = output_mode
        show_reasoning   = session.config.display.get("show_reasoning", True) and output_mode == "tty"
        stream_response  = session.config.display.get("stream_output", False) and output_mode == "tty"
        render_markdown  = session.config.display.get("render_markdown", False) and output_mode == "tty" and not disable_markdown
        self.renderer    = TTYRenderer(show_reasoning=show_reasoning, stream_response=stream_response, mode=output_mode, render_markdown=render_markdown)
        self.show_reasoning   = show_reasoning
        self.stream_response  = stream_response
        self.render_markdown  = render_markdown
        self.quirks           = get_quirk_registry()
        self.enabled_quirks   = model_backend.config.get("quirks", [])
    
    def run_turn(self, user_input: str, checkpoint_callback: Callable = None) -> str:
        if checkpoint_callback: checkpoint_callback()
        # Note: User message already added by session.execute()
        # Just ensure we have the latest tools and model response
        tools = self._get_all_tools()
        response = self._call_model(tools)

        usage = response.get("usage")
        if usage: self.session.record_turn_usage(usage)

        return self._process_response(response, checkpoint_callback=checkpoint_callback)
    
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
    
    def _got_chunk(self, type, delta):
        if   type == "reasoning": self.renderer.display_thinking(delta)
        elif type == "content"  : self.renderer.stream_chunk(delta)
        elif type == "tool_call": self.renderer.display_prepare_tool()
        elif type == "status":
            if delta == "request_sent": self.renderer.display_connected()

    def _call_model(self, tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        self.renderer.display_connecting()
        
        try:
            if self.stream_response:
                response = self.model.complete(messages=self.session.conversation, tools=tools if tools else None, chunk_callback=self._got_chunk)
                # Finalize streaming to flush markdown buffers
                self.renderer.finalize_stream()
            else:
                response = self.model.complete(messages=self.session.conversation, tools=tools if tools else None, chunk_callback=None)
            return response

        except Exception as e:
            # Ensure stream is finalized even on error
            if self.stream_response:
                self.renderer.finalize_stream()
            raise e
    
    def _process_response(self, response: Dict[str, Any], checkpoint_callback: Callable = None) -> str:
        for quirk in self.enabled_quirks:
            if not self.quirks.available(quirk): RNS.log(f"Enabled quirk \"{quirk}\" not available, cannot handle", RNS.LOG_ERROR)
            else:
                RNS.log(f"Handling quirk {quirk}", RNS.LOG_DEBUG)
                response = self.quirks.handle(quirk, response)

        message = response.get("message", {})
        tool_calls = message.get("tool_calls", [])

        if tool_calls:
            content = message.get("content")
            if not content: content = None
            
            assistant_msg = { "role": "assistant", "content": content, "tool_calls": tool_calls }
            self.session.conversation.append(assistant_msg)

            content = message.get("content", "")
            reasoning_content = message.get("reasoning_content", "")
            self.renderer.display_response(content, reasoning_content)

            multimodal_content = []
            for tool_call in tool_calls:
                if checkpoint_callback: checkpoint_callback()
                result, modality = self._execute_tool_call(tool_call)

                if modality == "image":
                    image_content = self._create_image_content(result, tool_call)
                    if image_content: multimodal_content.extend(image_content)
                    self.session.conversation.append({"role": "tool", "tool_call_id": tool_call.get("id"),
                                                      "name": tool_call.get("function", {}).get("name"), "content": "Image loaded successfully"})
                else:
                    self.session.conversation.append({"role": "tool", "tool_call_id": tool_call.get("id"),
                                                      "name": tool_call.get("function", {}).get("name"), "content": result})
            
            # Inject multimodal user message if we have image content
            if multimodal_content:
                self.session.conversation.append({ "role": "user",
                                                   "content": multimodal_content })
            
            final_response = self._call_model(self._get_all_tools())
            return self._process_response(final_response, checkpoint_callback=checkpoint_callback)
        
        # No tool calls - just content response
        content = message.get("content", "")
        reasoning_content = message.get("reasoning_content")
        self.renderer.display_response(content, reasoning_content)
        
        assistant_msg = { "role": "assistant", "content": content }
        if reasoning_content: assistant_msg["reasoning_content"] = reasoning_content
        self.session.conversation.append(assistant_msg)
        
        return content
    
    # Built-in toolkit prefixes that bypass skill gating
    BUILTIN_TOOLKIT_PREFIXES = {"Filesystem", "Shell", "Cryptography"}
    
    def _execute_tool_call(self, tool_call: Dict[str, Any]) -> tuple[str, str]:
        function = tool_call.get("function", {})
        tool_name = function.get("name", "")
        arguments_raw = function.get("arguments", "{}")
        
        # Handle both string and dict arguments (APIs vary)
        if isinstance(arguments_raw, dict): arguments = arguments_raw
        elif isinstance(arguments_raw, str):
            try: arguments = json.loads(arguments_raw)
            except json.JSONDecodeError: arguments = {}
        else: arguments = {}
        
        self.renderer.display_tool_call(tool_name, arguments)

        if tool_name == "skills.load_skill": 
            result = self._load_skill(arguments.get("name", ""))
            self.renderer.display_tool_result(result)
            return result, "text"
        
        if "." in tool_name: toolkit_name, method_name = tool_name.rsplit(".", 1)
        else: return f"Error: Invalid tool name '{tool_name}'", "text"
        
        if toolkit_name not in self.BUILTIN_TOOLKIT_PREFIXES and toolkit_name not in self.toolkits:
            if not self._is_skill_tool_allowed(toolkit_name):
                error_msg = f"Error: Skill '{toolkit_name}' documentation not loaded. Call skills.load_skill with name='{toolkit_name}' first."
                self.renderer.display_tool_result(error_msg)
                return error_msg, "text"

        toolkit = None
        if toolkit_name in self.toolkits: toolkit = self.toolkits[toolkit_name]
        elif hasattr(self.session, 'skill_registry'):
            skill = self.session.skill_registry.get_skill(toolkit_name)
            if skill and skill._toolkit: toolkit = skill._toolkit
        
        if toolkit is None: return f"Error: Unknown toolkit '{toolkit_name}'", "text"
        
        toolkit._lc_context = Context(session=self.session, config=self.session.config)
        
        modality = toolkit.get_modality(method_name)
        tool_gate = toolkit._gate_levels.get(method_name, toolkit.gate_level)
        if self.gate_level is not None and tool_gate >= self.gate_level:
            if not self._confirm_gate(tool_name, tool_gate, arguments):
                denied_msg = f"Tool execution denied by user at gate level {self.gate_level} (tool requires level {tool_gate})"
                self.renderer.display_tool_result(denied_msg)
                return denied_msg, "text"
        
        result = toolkit.dispatch(tool_name=method_name, arguments=arguments, gate_level=self.gate_level)
        self.renderer.display_tool_result(result, modality)
        
        return result, modality
    
    def _confirm_gate(self, tool_name: str, tool_gate: int, arguments: Dict[str, Any]) -> bool:
        if not self.can_prompt: return False
        
        args_display = []
        gate_desc = self.GATE_DESCRIPTIONS.get(tool_gate, f"level {tool_gate}")        
        for key, value in arguments.items():
            value_str = str(value)
            value_str = value_str.replace('\n', '\\n')
            args_display.append(f"  {key}: {value_str}")

        args_str = '\n'.join(args_display) if args_display else "  (no arguments)"

        print(f"\n⚠ Gate level {tool_gate} ({gate_desc})")
        print(f"Tool: {tool_name}")
        print(f"Arguments:\n{args_str}")

        try:
            response = input("Allow? [y/N] ").strip().lower()
            return response in ('y', 'yes')
        
        except (EOFError, KeyboardInterrupt):
            print()
            return False
    
    def _is_skill_tool_allowed(self, skill_name: str) -> bool:
        if skill_name in self.session.loaded_skills: return True

        if hasattr(self.session, 'skill_registry'):
            skill = self.session.skill_registry.get_skill(skill_name)
            if skill and skill.pinned: return True
        
        return False
    
    def _create_image_content(self, image_data: str, tool_call: Dict[str, Any]) -> list:
        function = tool_call.get("function", {})
        arguments_raw = function.get("arguments", "{}")
        if isinstance(arguments_raw, str):
            try: arguments = json.loads(arguments_raw)
            except: arguments = {}
        else: arguments = arguments_raw
        
        path = arguments.get("path", "image")
        filename = path.split("/")[-1] if "/" in path else path
        if not image_data.startswith("data:image/"): return [{"type": "text", "text": f"[Invalid image data for {filename}]"}]
        
        match = re.match(r"data:([^;]+);base64,(.+)", image_data)
        if not match: return [{"type": "text", "text": f"[Could not parse image data for {filename}]"}]
        mime_type, base64_data = match.groups()
        
        return [ {"type": "text", "text": f"Image: {filename}"},
                 {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_data}"}} ]

    def _load_skill(self, skill_name: str) -> str:
        if not hasattr(self.session, 'skill_registry'): return "Error: Skill registry not available"
        
        skill = self.session.skill_registry.get_skill(skill_name)
        if not skill: return f"Error: Skill '{skill_name}' not found"
        if skill_name not in self.session.loaded_skills: self.session.loaded_skills.append(skill_name)

        if skill.content: full_skill = skill.content
        else:             full_skill = "Error: Could not load skill content for \"{skill_name}\""

        full_skill += f"\n\n---\n\nIf the skill documentation references additional documentation or resources, you can find them in `{skill.path}`, and you may read them now if required."

        return full_skill


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
