# Skill Format

## Overview

Skills bundle domain knowledge (procedures) with optional tooling. They follow the pattern:

```
skills/
└── skill-name/
    ├── SKILL.md          # Required: Procedures and guidelines
    ├── __init__.py       # Optional: Toolkit subclass
    └── tools.py          # Optional: Additional Python modules
```

## SKILL.md Format

Frontmatter + Markdown body:

```markdown
---
name: Database Operations
version: 1.0.0
description: Guidelines for safe database interactions
triggers:
  - "database"
  - "sql"
  - "query"
pinned: false
---

# Database Operations

## Overview

This skill provides procedures for interacting with SQL databases safely.

## Procedures

### 1. Always Backup First

Before any destructive operation:

```bash
# Create backup
cp database.db "database.backup.$(date +%s).db"
```

### 2. Test Queries on Copies

Never run untested queries on production data.

### 3. Transaction Safety

Wrap modifications in transactions:

```sql
BEGIN TRANSACTION;
-- operations
COMMIT;
```

## Common Pitfalls

- Forgetting WHERE clauses
- Not handling NULL values
- Ignoring index performance

## Tool Reference

Available tools when this skill is loaded:

- `db_query(sql: str)`: Execute read-only query
- `db_execute(sql: str)`: Execute modification (gated)
- `db_backup(destination: str)`: Create backup

```

## Frontmatter Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | str | Human-readable skill name |
| `version` | str | Semver version |
| `description` | str | Brief description |
| `triggers` | list | Keywords that suggest this skill |
| `pinned` | bool | Load fully at session start |

## Loading Behavior

### Phase 1: Registry Scan

At session start, `lc` scans all skill directories and:
- Parses SKILL.md frontmatter metadata
- Imports and instantiates toolkit from `__init__.py` (if present)
- Extracts tool signatures for KV-cache population

**Design note:** Full toolkit instantiation happens at discovery time (not lazy) to ensure fail-fast error detection and schema consistency.

### Phase 2: Lazy Documentation Loading

When the agent calls `skills.load_skill`:
- Full SKILL.md content is returned as tool result
- Skill is marked as "loaded" in session state
- No KV-cache invalidation (state change via conversation)

### Phase 3: Pinned Skills

Skills can be pinned two ways:
- **SKILL.md frontmatter:** `pinned: true`
- **Configuration:** Add to `skills.pinned` list in config

Pinned skills bypass the documentation loading requirement — their tools execute immediately without `load_skill`.

## Tool Integration

Skills can include Python tools by providing a Toolkit subclass:

```python
# skills/database/__init__.py
from lc.toolkit import Toolkit, tool, Context

class DatabaseTools(Toolkit):
    """Database interaction tools."""
    
    gate_level = 1
    
    @tool
    def db_query(self, sql: str, context: Context) -> str:
        """Execute a read-only SQL query."""
        # Implementation
        pass
    
    @tool(gate_level=2)
    def db_execute(self, sql: str, context: Context) -> str:
        """Execute a SQL statement that modifies data."""
        # Implementation
        pass
```

## Skill Discovery

Skills are discovered from (in order):

1. **Built-in:** `lc/skills/` (always loaded)
2. **User:** `~/.lc/skills/` (configurable via `loading.user_skills`, default: true)
3. **Project:** `./.lc/skills/` (configurable via `loading.project_skills`, default: false)
4. **Custom:** Paths from `skills.directories` config (always checked if specified)

### Security Configuration

The `[loading]` section controls skill loading:

```ini
[loading]
user_skills = true       # Enable ~/.lc/skills/ (default)
project_skills = false   # Enable ./.lc/skills/ (opt-in)
```

Project-level skills are disabled by default for security — enabling allows repositories to provide custom skills when you work in their directories.

## The load_skill Tool

Agents can request skill loading:

```python
@tool
def load_skill(self, name: str, context: Context) -> str:
    """
    Load a skill by name.
    
    Args:
        name: Skill identifier (directory name)
    
    Returns:
        Skill description and available tools
    """
```

This is always available, regardless of loaded skills.

## Best Practices

1. **SKILL.md is documentation**: Write it for the agent, not just humans
2. **Include examples**: Show expected tool usage patterns
3. **Document failure modes**: What can go wrong, how to recover
4. **Keep tools focused**: One job per tool
5. **Use triggers wisely**: Too broad = false positives
6. **Version your skills**: Breaking changes need new versions

## Skill Template

```markdown
---
name: 
version: 1.0.0
description: 
triggers: []
pinned: false
---

# 

## Overview

## Procedures

### 1. 

## Common Pitfalls

## Tool Reference
```

## Advanced: Conditional Tools

Tools can be conditionally available based on environment:

```python
class ConditionalTools(Toolkit):
    @property
    def available_tools(self):
        tools = [self.always_available]
        if shutil.which("docker"):
            tools.append(self.docker_command)
        return tools
```
