# Standalone Tools

## Overview

While skills bundle documentation with tools, sometimes you just want a tool. No ceremony. No SKILL.md. Just a Python file that does something useful.

Standalone tools live outside the skill system. They're loaded directly from tool directories and immediately available — no `load_skill` required.

## When to Use Standalone Tools

**Use standalone tools when:**
- You have a simple utility that doesn't need documentation
- You're prototyping before promoting to a full skill
- You want project-specific tools without skill overhead
- You just don't feel like writing YAML frontmatter today

**Use skills when:**
- The tool needs usage guidelines or safety procedures
- Complex multi-step workflows need explanation
- You want lazy-loading semantics with gating
- Documentation is part of the value

## Tool Directory Structure

Tools can be single files or packages:

```
~/.lc/tools/              # User tools (configurable)
./.lc/tools/              # Project tools (configurable)

single_tool.py            # Single file tool
my_toolkit/               # Package tool
├── __init__.py
└── utils.py
```

## Creating a Standalone Tool

Same as creating a skill toolkit, minus the skill wrapper:

```python
# ~/.lc/tools/network_utils.py
from lc.toolkit import Toolkit, tool
import subprocess

class NetworkTools(Toolkit):
    """Network diagnostic utilities."""
    
    gate_level = 0
    
    @tool
    def ping(self, host: str, count: int = 4) -> str:
        """Ping a host and return results."""
        try:
            result = subprocess.run(
                ["ping", "-c", str(count), host],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
        except Exception as e:
            return f"Error: {e}"
    
    @tool(gate_level=1)
    def traceroute(self, host: str) -> str:
        """Trace route to host."""
        # Implementation...
        pass
```

That's it. Drop it in the tools directory, enable in config, and it's available as `NetworkTools.ping`.

## Configuration

Enable tool loading in your config:

```ini
[loading]
user_tools = true        # Load from ~/.lc/tools/
project_tools = true     # Load from ./.lc/tools/
```

**Security note:** Both are disabled by default. Unlike skills, standalone tools are "trusted when enabled" — they bypass the skill documentation gating and are immediately executable.

## Tool Discovery Rules

- **Files:** Any `.py` file is imported and searched for Toolkit subclasses
- **Packages:** Any directory with `__init__.py` is treated as a package
- **Naming:** The toolkit class name becomes the tool prefix (e.g., `NetworkTools.ping`)
- **Multiple classes:** A single file/package can define multiple Toolkit subclasses

## Comparison: Skills vs. Standalone Tools

| Feature | Skills | Standalone Tools |
|---------|--------|------------------|
| Documentation | SKILL.md required | None |
| Loading | `load_skill` required (unless pinned) | Immediate when enabled |
| Gating | Skill-level + tool-level | Tool-level only |
| Discovery | Built-in, user, project, custom | User, project (configurable) |
| Use case | Complex, documented workflows | Simple utilities, prototypes |
| KV-cache impact | All skill tools present | All tools present |

## Best Practices

1. **Start standalone, promote to skill:** Prototype as standalone tool, add SKILL.md when complexity demands documentation
2. **Use descriptive class names:** The class name becomes the user's interface
3. **Gate appropriately:** Standalone tools still respect gate levels
4. **Document in code:** Since there's no SKILL.md, docstrings matter more
5. **Consider project tools:** Enable `project_tools` for repository-specific utilities that shouldn't be global

## Migration: Tool → Skill

To promote a standalone tool to a skill:

1. Create `~/.lc/skills/your_skill/` directory
2. Move tool file to `__init__.py`
3. Add `SKILL.md` with frontmatter and documentation
4. Remove from tools directory (or keep both)
5. Add to `skills.pinned` if immediate execution still desired

The toolkit code doesn't change — only the packaging around it.
