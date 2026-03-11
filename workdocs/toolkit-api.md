# Toolkit API

## Overview

Tools in `lc` are organized into Toolkits — Python classes that group related functionality. Each method decorated as a tool becomes available to the agent.

## Creating a Toolkit

```python
from lc.toolkit import Toolkit, tool
from typing import List
from pydantic import BaseModel

class WebTools(Toolkit):
    """Toolkit for web operations."""
    
    def __init__(self):
        super().__init__()
        self.gate_level = 1  # Minimum gate level for all tools in this toolkit
    
    @tool
    def fetch_url(self, url: str) -> str:
        """
        Fetch content from a URL.
        
        Args:
            url: The URL to fetch
        
        Returns:
            The content as string, or error message
        """
        try:
            # Implementation here
            return content
        except Exception as e:
            return f"Error fetching {url}: {e}"
    
    @tool(gate_level=2)  # Override toolkit default
    def download_file(self, url: str, destination: str) -> str:
        """Download a file from URL to destination path."""
        pass
```

## The @tool Decorator

The `@tool` decorator:
- Extracts the function signature for JSON Schema generation
- Registers the method as available to the agent
- Wraps execution with gating and error handling
- Makes session context available as `self.context` automatically

## Context Object

The `Context` object provides tools with access to:

```python
@tool
def example():
    # Get session context
    context = self.context

    # Session management
    session_id = context.session.id
    conversation = context.session.conversation
    
    # Configuration
    config = context.config
    model_backend = context.config.model.backend
    
    # Working state
    cwd = context.session.working_dir
    
    # Tool interaction
    result = context.call_tool("other_toolkit", "other_tool", args)
    
    # Skill access
    skill_doc = context.get_skill_doc("skill_name")
```

## Gating Levels

Specify gate level at toolkit or tool level:

```python
class FileTools(Toolkit):
    gate_level = 0  # Default for all tools
    
    @tool  # Inherits gate_level=0
    def read(self, path: str) -> str:
        pass
    
    @tool(gate_level=1)  # Override
    def write(self, path: str, content: str) -> str:
        pass
```

Gate levels:
- `0`: Read-only (safe)
- `1`: Write operations (potentially destructive)
- `2`: Execution (read-only commands)
- `3`: Execution with modification (rm, mv, etc.)

## Type Hints and Schema

Use Pydantic models for complex arguments:

```python
from pydantic import BaseModel, Field

class SearchQuery(BaseModel):
    terms: List[str] = Field(description="Search terms")
    max_results: int = Field(default=10, ge=1, le=100)
    include_deprecated: bool = Field(default=False)

class SearchTools(Toolkit):
    @tool
    def search(self, query: SearchQuery) -> str:
        # query.terms, query.max_results, etc.
        pass
```

## Return Values

Tools should return strings. The agent will receive this as the tool result:

- Success: Return the result content
- Error: Return f"Error: {description}"
- No result: Return "Completed successfully" or empty string

## Error Handling

Exceptions caught by the toolkit wrapper:
- Return formatted error message to agent
- Log to stderr (if verbose mode)
- Do not terminate session

Raise exceptions for truly fatal conditions only.

## Registering Toolkits

Toolkits are registered in configuration:

```ini
[toolkits]
builtin = filesystem, shell
custom = mypackage.MyTools, ./local_tools.py:LocalTools
```

Built-in toolkits are loaded from `lc/tools/`. Custom toolkits are loaded by import path.

## Best Practices

1. **Keep tools focused**: One clear operation per tool
2. **Document thoroughly**: Docstrings become tool descriptions
3. **Validate inputs**: Use Pydantic for complex args
4. **Return errors gracefully**: Never crash the session
5. **Use context for cross-cutting concerns**: Don't reimplement config/session access
6. **Idempotent where possible**: Same input → same output
7. **Respect gate levels**: Tag appropriately for user safety
