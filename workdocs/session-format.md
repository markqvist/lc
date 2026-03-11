# Session Format

## Overview

Sessions are persisted as msgpack files for efficiency and atomicity. This document specifies the exact format for interoperability and debugging.

## File Location

```
~/.lc/sessions/
├── active          # Symlink to current active session (or session ID)
├── <uuid>.msgpack  # Individual session files
└── archive/        # Old sessions
```

## Top-Level Structure

```python
{
    # Metadata
    "version": 1,                    # Session format version
    "session_id": "uuid-string",     # Unique identifier
    "created_at": 1234567890.0,      # Unix timestamp (float)
    "updated_at": 1234567890.0,      # Unix timestamp (float)
    
    # Configuration
    "config_path": "/home/user/.lc", # Config directory used
    "config_snapshot": {...},        # Copy of config at session start
    
    # Execution State
    "working_dir": "/home/user",     # CWD at session start
    "gate_level": 0,                 # Gating level in effect
    
    # Conversation
    "conversation": [
        {"role": "system", "content": "..."},
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."},
        {"role": "assistant", "tool_calls": [...]},
        {"role": "tool", "tool_call_id": "...", "content": "..."}
    ],
    
    # Tool State
    "tool_context": {
        "executed_commands": [],     # History for context
        "created_files": [],         # For cleanup/tracking
        "custom_state": {}           # Toolkit-specific data
    },
    
    # Skill State
    "skill_registry": {
        "all_skills": [...],         # All discovered skills (metadata)
        "loaded_skills": [...],      # Fully loaded skill names
        "pinned_skills": [...]       # Skills loaded at start
    },
    
    # Resolver Output (cached)
    "resolver_cache": {
        "environment": {...},
        "filesystem": {...}
    },
    
    # Statistics
    "stats": {
        "turn_count": 5,
        "token_count": 15000,
        "tool_call_count": 3
    }
}
```

## Conversation Message Formats

### System Message
```python
{
    "role": "system",
    "content": "Rendered system prompt..."
}
```

### User Message
```python
{
    "role": "user",
    "content": "User input text"
}
```

### Assistant Text Response
```python
{
    "role": "assistant",
    "content": "Response text..."
}
```

### Assistant Tool Calls
```python
{
    "role": "assistant",
    "tool_calls": [
        {
            "id": "call_abc123",
            "type": "function",
            "function": {
                "name": "filesystem.read",
                "arguments": '{"path": "/etc/hosts"}'
            }
        }
    ]
}
```

### Tool Result
```python
{
    "role": "tool",
    "tool_call_id": "call_abc123",
    "name": "filesystem.read",       # Optional: for debugging
    "content": "127.0.0.1 localhost..."
}
```

## Versioning

The `version` field enables format migration:

- Version 1: Initial format (this spec)
- Future versions: Migrate on load, save as latest

## Atomic Writes

Sessions are written atomically:

1. Write to `<uuid>.msgpack.tmp`
2. fsync to disk
3. Rename to `<uuid>.msgpack`

This prevents corruption on crash.

## Session Inspection

Use the `lc-session` utility (TBD) to inspect sessions:

```bash
# List all sessions
lc-session list

# View session details
lc-session show <uuid>

# Export to JSON for debugging
lc-session export <uuid> > session.json

# Resume specific session
lc --resume <uuid>
```

## Session Lifecycle

1. **Creation**: `lc "command"` creates new session
2. **Active**: Session file updated after each turn
3. **Completion**: Session archived if completed successfully
4. **Resume**: `lc --interactive --resume` continues session

## Configuration Snapshot

The `config_snapshot` preserves settings that affect behavior:

```python
{
    "model": {
        "backend": "openai",
        "model": "gpt-4",
        "temperature": 0.7
    },
    "toolkits": ["filesystem", "shell"],
    "resolvers": ["environment", "filesystem"],
    "skills": ["database"]  # Pinned skills
}
```

This enables reproducibility: same session, same settings, same behavior.

## Compression

Session files are not compressed by default. For large sessions, consider:

```bash
# Manual compression
gzip ~/.lc/sessions/<uuid>.msgpack

# Auto-compression threshold (future)
compress_threshold_bytes = 1048576  # 1MB
```

## Privacy Considerations

Sessions may contain sensitive data:
- File contents read by tools
- Command outputs
- User queries

Treat everything in `~/.lc/` as sensitive data.

## Migration Strategy

When format version changes:

1. Detect old version on load
2. Migrate in-memory representation
3. Mark for rewrite on next save
4. Keep backup of original

```python
def migrate_v1_to_v2(session_data: dict) -> dict:
    """Migrate version 1 session to version 2."""
    session_data["version"] = 2
    # Migration logic here
    return session_data
```
