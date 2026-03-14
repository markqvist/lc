# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

import RNS
import json
import time
from typing import List, Dict, Any, Optional

from lc.agent import ModelBackend


class OpenAIBackend(ModelBackend):
    CONNECT_TIMEOUT = 10
    READ_TIMEOUT    = 1800
    REQUEST_TRIES = 8
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_url = config.get("base_url", "http://localhost:1234/v1")
        self.model = config.get("model", "local-model")
        self.api_key = config.get("api_key", "")
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 32768)
        
        import requests
        self.session = requests.Session()
    
    def complete(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        return self._complete(messages, tools)
        
    def _sanitize_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        sanitized = []
        for msg in messages:
            clean_msg = dict(msg)
            
            # Remove reasoning_content if present (llama.cpp prefill incompatibility)
            clean_msg.pop("reasoning_content", None)
            
            # Handle assistant messages with tool_calls
            if clean_msg.get("role") == "assistant":
                # If there are tool_calls, content should be null not empty string
                if clean_msg.get("tool_calls"):
                    if clean_msg.get("content") == "": clean_msg["content"] = None
                
                # Remove name if present (not valid for assistant)
                clean_msg.pop("name", None)
            
            # Handle tool messages
            # Ensure tool_call_id is present
            if clean_msg.get("role") == "tool":
                if not clean_msg.get("tool_call_id"): clean_msg["tool_call_id"] = "unknown"
            
            # Handle system/user messages - remove name if present
            # Preserve multimodal content arrays (list-type content for images)
            # No transformation needed - pass through as-is
            if clean_msg.get("role") in ("system", "user"): clean_msg.pop("name", None)
            
            sanitized.append(clean_msg)
        
        return sanitized
    
    def _complete(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]]) -> Dict[str, Any]:
        import requests
        attempts_left = self.REQUEST_TRIES
        
        headers = { "Content-Type": "application/json",
                    "Connection": "close" }

        if self.api_key: headers["Authorization"] = f"Bearer {self.api_key}"

        sanitized_messages = self._sanitize_messages(messages)
        
        payload = { "model": self.model,
                    "messages": sanitized_messages,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        payload_json = json.dumps(payload, ensure_ascii=False)
        
        while attempts_left:
            attempts_left -= 1
            try:
                RNS.log("Sending inference request", RNS.LOG_DEBUG)
                response = self.session.post(f"{self.base_url}/chat/completions",
                                             headers=headers,
                                             data=payload_json,
                                             timeout=(self.CONNECT_TIMEOUT, self.READ_TIMEOUT))
                response.raise_for_status()
                data = response.json()
                message = data["choices"][0]["message"]

                RNS.log("Inference request succeeded", RNS.LOG_DEBUG)

                result = { "message": { "role": message["role"],
                                        "content": message.get("content", "") } }

                # Extract reasoning content if present
                if "reasoning_content" in message: result["message"]["reasoning_content"] = message["reasoning_content"]
                if "tool_calls" in message: result["message"]["tool_calls"] = message["tool_calls"]

                # Extract usage statistics if present
                usage = data.get("usage")
                if usage:
                    result["usage"] = {
                        "prompt_tokens": usage.get("prompt_tokens", 0),
                        "completion_tokens": usage.get("completion_tokens", 0),
                        "total_tokens": usage.get("total_tokens", 0)
                    }

                return result

            except Exception as e:
                RNS.log(f"Error during inference request: {e}", RNS.LOG_ERROR)
                RNS.trace_exception(e)
                if attempts_left:
                    backoff = self.REQUEST_TRIES-attempts_left+1
                    RNS.log(f"Retrying request in {RNS.prettytime(backoff)}", RNS.LOG_ERROR)
                    time.sleep(backoff)
        
        raise SystemError("Inference request failed")
