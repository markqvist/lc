"""Shell execution toolkit for lc."""

import subprocess
import shlex
from pathlib import Path
from typing import Optional

from lc.toolkit import Toolkit, tool

class ShellTools(Toolkit):
    """Toolkit for shell command execution."""
    
    gate_level = 2  # Execution required
    
    # Dangerous commands that require higher gating
    # We should probably expand this
    DANGEROUS_COMMANDS = [ 'rm', 'dd', 'mkfs', 'fdisk', 'format',
                           '> ', '>>', '|' ] # Redirections can modify
    
    @tool(gate_level=2)
    def exec(self, command: str, timeout: int = 60) -> str:
        """
        Execute a shell command and return output.
        
        Args:
            command: Shell command to execute
            timeout: Maximum execution time in seconds (default: 60)
        
        Returns:
            Command output (stdout + stderr) or error message
        """

        try:
            # Check for dangerous commands
            is_dangerous = any(dangerous in command.lower() for dangerous in self.DANGEROUS_COMMANDS)
            
            tool_gate = 3 if is_dangerous else 2
            
            # Run command
            result = subprocess.run(command, shell=True, capture_output=True,
                                    text=True, timeout=timeout)
            
            output = result.stdout
            if result.stderr:          output += f"\n[stderr]: {result.stderr}"
            if result.returncode != 0: output += f"\n[exit code: {result.returncode}]"
            
            return output
            
        except subprocess.TimeoutExpired: return f"Error: Command timed out after {timeout} seconds"
        except Exception as e:            return f"Error executing command: {e}"
