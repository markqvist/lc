# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

"""Test skill toolkit."""

from lc.toolkit import Toolkit, tool


class TestSkillTools(Toolkit):
    """Test tools for skill system verification."""
    
    @tool(gate_level=0, modality="text")
    def echo(self, message: str) -> str:
        """
        Echo back the provided message.
        
        Args:
            message: The message to echo back
        
        Returns:
            The echoed message
        """
        return f"Echo: {message}"
    
    @tool(gate_level=0, modality="text")
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
