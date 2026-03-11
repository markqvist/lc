"""Mock model backend for testing lc."""

import json
from typing import List, Dict, Any, Optional

from lc.agent import ModelBackend


class MockBackend(ModelBackend):
    """Mock backend for testing without a live model."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.response_count = 0
    
    def complete(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Return a mock response."""
        self.response_count += 1
        
        # Get the last user message
        last_message = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_message = msg.get("content", "")
                break
        
        if not last_message:
            last_message = "No user message found"
        
        # Check if we should simulate a tool call
        if tools and "list" in last_message.lower() or "ls" in last_message.lower():
            # Simulate a tool call for list_dir
            return {
                "message": {
                    "role": "assistant",
                    "content": "I'll list the directory for you.",
                    "tool_calls": [
                        {
                            "id": f"call_{self.response_count}",
                            "type": "function",
                            "function": {
                                "name": "FileSystemTools.list_dir",
                                "arguments": json.dumps({"path": "."}),
                            }
                        }
                    ]
                }
            }
        
        # Simple echo response
        return {
            "message": {
                "role": "assistant",
                "content": f"[MOCK] Received: {last_message}\n\nI would normally process this and use tools if needed.",
            }
        }
