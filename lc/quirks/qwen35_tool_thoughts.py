# Qwen 3.5 Tool Thoughts Quirk
# 
# Handles the edge case where Qwen3.5 models output tool calls inside thinking blocks.
# This quirk extracts tool calls from reasoning_content and restructures them
# into the expected format before they reach lc's tool handling logic.
# 
# - Qwen3.5 models may output XML-formatted tool calls inside reasoning blocks
# - These tool calls appear in the reasoning_content field instead of tool_calls
# - The quirk parses XML tool calls in reasoning and converts them to JSON
# - Then injects them into the message's tool_calls field

quirk_id = "qwen3.5_tool_thoughts"

import re
import json
import uuid
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field

import RNS

@dataclass
class ToolCall:
    id: str
    name: str
    arguments: str

TOOL_CALL_PATTERN = re.compile(r'<tool_call>\s*<function\s*=\s*["\']?([^"\'>\s]+)["\']?\s*>\s*'
                               r'(.*?)\s*</function>\s*</tool_call>', re.DOTALL)

PARAMETER_PATTERN = re.compile(r'<parameter\s*=\s*["\']?([^"\'>\s]+)["\']?\s*>\s*'
                               r'(.*?)\s*</parameter>', re.DOTALL)

def parse_xml_tool_call(xml_text: str) -> Optional[ToolCall]:
    function_match = TOOL_CALL_PATTERN.search(xml_text)
    if not function_match: return None

    function_name = function_match.group(1)

    parameters = {}
    param_matches = PARAMETER_PATTERN.findall(xml_text)
    for param_name, param_value in param_matches:
        param_value = param_value.strip()
        if (param_value.startswith('"') and param_value.endswith('"')) or \
           (param_value.startswith("'") and param_value.endswith("'")):
            param_value = param_value[1:-1]

        parameters[param_name] = param_value

    try: arguments = json.dumps(parameters)
    except (TypeError, ValueError) as e:
        RNS.log(f"Failed to convert parameters to JSON: {e}", RNS.LOG_ERROR)
        RNS.trace_exception(e)
        return None

    call_id = _generate_call_id()
    return ToolCall(id=call_id, name=function_name, arguments=arguments)

def extract_tool_calls_from_reasoning(reasoning_content: str) -> List[ToolCall]:
    tool_calls = []

    # Find all function blocks
    for match in TOOL_CALL_PATTERN.finditer(reasoning_content):
        xml_block = match.group(0)
        tool_call = parse_xml_tool_call(xml_block)
        if tool_call:
            tool_calls.append(tool_call)

    return tool_calls

def _generate_call_id() -> str: return f"call_{uuid.uuid4().hex[:8]}"

def fix_tool_calls(message: Dict[str, Any]) -> Dict[str, Any]:
    if not message.get("reasoning_content"): return message

    reasoning_content = message["reasoning_content"]
    tool_calls = extract_tool_calls_from_reasoning(reasoning_content)

    if not tool_calls: return message

    tool_calls_list = []
    for tool_call in tool_calls:
        tool_calls_list.append( {"id": tool_call.id,
                                 "type": "function",
                                 "function": { "name": tool_call.name,
                                               "arguments": tool_call.arguments } } )

    if "tool_calls" not in message: message["tool_calls"] = []
    message["tool_calls"].extend(tool_calls_list)

    # TODO: Remove tool call from reasoning content?

    return message

def handle(response: Dict[str, Any]) -> Dict[str, Any]:
    if "message" in response and "reasoning_content" in response["message"]: fix_tool_calls(response["message"])
    return response