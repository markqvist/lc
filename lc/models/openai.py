"""OpenAI-compatible model backend for lc."""

import RNS
import json
from typing import List, Dict, Any, Optional

from lc.agent import ModelBackend


class OpenAIBackend(ModelBackend):
    """OpenAI API-compatible backend (works with local servers)."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_url = config.get("base_url", "http://localhost:1234/v1")
        self.model = config.get("model", "local-model")
        self.api_key = config.get("api_key", "")
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 4096)
        
        import requests
        self.session = requests.Session()
    
    def complete(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Send completion request."""
        
        return self._complete_requests(messages, tools)
        
    def _sanitize_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sanitize messages for llama.cpp compatibility.
        
        - Removes reasoning_content fields (causes prefill issues)
        - Ensures content is null (not empty string) for assistant tool calls
        - Removes name field from non-tool messages
        """
        sanitized = []
        for msg in messages:
            clean_msg = dict(msg)
            
            # Remove reasoning_content if present (llama.cpp prefill incompatibility)
            clean_msg.pop("reasoning_content", None)
            
            # Handle assistant messages with tool_calls
            if clean_msg.get("role") == "assistant":
                # If there are tool_calls, content should be null not empty string
                if clean_msg.get("tool_calls"):
                    if clean_msg.get("content") == "":
                        clean_msg["content"] = None
                # Remove name if present (not valid for assistant)
                clean_msg.pop("name", None)
            
            # Handle tool messages
            if clean_msg.get("role") == "tool":
                # Ensure tool_call_id is present
                if not clean_msg.get("tool_call_id"):
                    clean_msg["tool_call_id"] = "unknown"
            
            # Handle system/user messages - remove name if present
            if clean_msg.get("role") in ("system", "user"):
                clean_msg.pop("name", None)
            
            sanitized.append(clean_msg)
        
        return sanitized
    
    def _complete_requests(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """Complete using requests library."""
        import requests
        
        headers = {
            "Content-Type": "application/json",
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        # Sanitize messages for llama.cpp compatibility
        sanitized_messages = self._sanitize_messages(messages)
        
        payload = {
            "model": self.model,
            "messages": sanitized_messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        
        response = self.session.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        
        data = response.json()
        message = data["choices"][0]["message"]
        
        result = {
            "message": {
                "role": message["role"],
                "content": message.get("content", ""),
            }
        }
        
        # Extract reasoning content if present (Qwen3, etc.)
        if "reasoning_content" in message:
            result["message"]["reasoning_content"] = message["reasoning_content"]
        
        if "tool_calls" in message:
            result["message"]["tool_calls"] = message["tool_calls"]
        
        return result
