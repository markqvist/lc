# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

"""Test standalone tool for verifying the tool loading system."""

from lc.toolkit import Toolkit, tool


class TestTool(Toolkit):
    """A test standalone tool."""
    
    gate_level = 0
    
    @tool
    def greet(self, name: str = "world") -> str:
        """
        Return a greeting message.
        
        Args:
            name: Name to greet (default: world)
        
        Returns:
            Greeting message
        """
        return f"Hello, {name}! This is a standalone tool."
    
    @tool
    def multiply(self, x: float, y: float) -> str:
        """
        Multiply two numbers.
        
        Args:
            x: First number
            y: Second number
        
        Returns:
            Product as string
        """
        return str(x * y)
