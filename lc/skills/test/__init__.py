# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

"""Test skill toolkit."""

from lc.toolkit import Toolkit, tool


class TestSkillTools(Toolkit):
    """Test tools for skill system verification."""
    
    gate_level = 0
    
    @tool
    def echo(self, message: str) -> str:
        """
        Echo back the provided message.
        
        Args:
            message: The message to echo back
        
        Returns:
            The echoed message
        """
        return f"Echo: {message}"
    
    @tool
    def add(self, a: int, b: int) -> str:
        """
        Add two numbers together.
        
        Args:
            a: First number
            b: Second number
        
        Returns:
            Sum as string
        """
        return str(a + b)
