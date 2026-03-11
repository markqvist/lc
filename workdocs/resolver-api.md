# Resolver API

## Overview

Resolvers generate context variables for the system prompt template. They run once at session initialization to populate Jinja2 variables for use in templates.

## Creating a Resolver

```python
from lc.resolver import Resolver, Context
from typing import Optional, Dict, Any

class GitResolver(Resolver):
    """Provides git repository information."""
    
    def resolve(self, context: Context) -> Optional[Dict[str, Any]]:
        """
        Generate git-related context variables.
        
        Returns:
            Dict of variables to inject into template, or None to skip
        """
        import subprocess
        
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=context.session.working_dir
            )
            
            if result.returncode != 0:
                return None  # Not a git repository
            
            dirty_files = [line.strip() for line in result.stdout.split("\n") if line.strip()]
            
            return {
                "git_status": {
                    "is_repo": True,
                    "dirty": len(dirty_files) > 0,
                    "dirty_count": len(dirty_files),
                    "files": dirty_files[:10]  # Limit context usage
                }
            }
            
        except Exception:
            return None
```

## The Resolver Contract

Resolvers must:
1. Inherit from `Resolver` base class
2. Implement `resolve(context) -> Optional[Dict]`
3. Return `None` for unavailable/unapplicable data
4. Return flat or nested dicts of JSON-serializable values

## Context Parameter

The `context` parameter provides:

```python
def resolve(self, context: Context) -> Optional[Dict[str, Any]]:
    # Session information
    session_id = context.session.id
    created_at = context.session.created_at
    
    # Configuration access
    max_depth = context.config.resolvers.directory_tree_max_depth
    
    # Working directory (session start, not current process CWD)
    base_path = context.session.working_dir
    
    # Call other resolvers (avoid circular dependencies)
    other_data = context.get_resolver_output("other_resolver")
```

## Template Integration

Resolver outputs are flattened and injected into Jinja2:

```python
# Resolver returns
{
    "environment": {
        "cwd": "/home/user/project",
        "user": "user"
    }
}

# Template access
{{ environment.cwd }}
{{ environment.user }}
```

Handle missing values in templates:

```jinja
{% if environment is defined %}
Current directory: {{ environment.cwd }}
{% endif %}

{# Or with default #}
Directory: {{ environment.cwd | default("unknown") }}
```

## Built-in Resolvers

### EnvironmentResolver
```python
{
    "environment": {
        "cwd": str,           # Working directory at session start
        "user": str,          # Current user
        "hostname": str,      # Machine hostname
        "shell": str,         # User's shell
        "date": str,          # ISO format date
        "time": str           # ISO format time
    }
}
```

### FilesystemResolver
```python
{
    "filesystem": {
        "tree": str,          # ASCII tree of current directory
        "file_count": int,    # Number of files
        "dir_count": int,     # Number of directories
        "recent_files": list  # Recently modified files
    }
}
```

### SystemResolver
```python
{
    "system": {
        "platform": str,      # OS platform
        "python_version": str,
        "lc_version": str
    }
}
```

## Custom Resolvers

Register in configuration:

```ini
[resolvers]
builtin = environment, filesystem, system
custom = mypackage.MyResolver, ./custom_res.py:CustomResolver
```

## Best Practices

1. **Return None generously**: Better to omit than include stale/meaningless data
2. **Limit output size**: Large trees, file lists burn context window
3. **Cache expensive operations**: Use context.cache for repeated lookups
4. **Fail silently**: Never crash session initialization
5. **Document output schema**: Users need to know what variables are available
6. **Keep it static**: Remember: resolvers run ONCE at session start

## Performance Considerations

Resolvers block session initialization. Keep them fast:
- Avoid network calls
- Limit subprocess invocations
- Cache filesystem walks
- Cap list sizes before returning

## Testing Resolvers

```python
from lc.resolver import Context
from lc.session import Session

# Create mock context
session = Session.create()
context = Context(session=session, config={})

# Test resolver
resolver = GitResolver()
result = resolver.resolve(context)

assert result is None or "git_status" in result
```
