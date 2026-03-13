# lc Architecture

## Overview

Humanity's Last Command (`lc`) is a terminal-based agentic command executor designed for local, self-sovereign infrastructure. It transforms natural language intent into sequences of file operations, shell commands, and reasoning steps.

## Design Principles

1. **Minimal Dependencies**: Every dependency must justify its existence
2. **Explicit State**: No hidden context; all state is inspectable and serializable
3. **Uniform Extensibility**: Tools, resolvers, and skills follow identical patterns
4. **KV-Cache Sanity**: System prompt is static per session; no cache invalidation = blazing local inference performance
5. **Graceful Degradation**: Features fail explicitly, not silently

## Execution Flow

```
User Input
    |
    v
Argument Parsing (cli.py)
    |
    v
Session Initialization (session.py)
    |-- Load/Create Session
    |-- Initialize Config
    |-- Load Toolkits
    |-- Load Resolvers
    |-- Load Skill Registry (signatures only)
    |
    v
Context Resolution (resolver dispatch)
    |-- Run active resolvers
    |-- Generate context variables
    |
    v
System Prompt Render (Jinja2)
    |-- Template + context variables
    |-- Static for session lifetime
    |
    v
Agent Loop (agent.py)
    |-- Send conversation + tools to model
    |-- Receive response
    |-- If tool calls: dispatch to toolkit.py
    |-- Stream output via rendering.py
    |-- Repeat until completion or error
    |
    v
Session Persistence (msgpack)
    |-- Save conversation state
    |-- Save tool execution context
```

## Component Responsibilities

### cli.py
Entry point. Parses arguments, handles `--interactive`, `--gate`, `--config` flags. Delegates to Session.

### session.py
Orchestrates execution flow. Manages:
- Configuration directory resolution (`~/.lc` → `~/.config/lc` → create)
- Session persistence (msgpack format)
- Toolkit and Resolver lifecycle
- Skill registry management

### agent.py
Core conversation loop. Handles:
- Model backend abstraction
- Tool call dispatch
- Response streaming
- Error handling and recovery

### toolkit.py
Base class for all tool collections. Responsible for:
- Tool schema extraction for argument mapping
- Tool dispatch with context injection
- Gating level enforcement

### resolver.py
Base class for context providers. Responsible for:
- Runtime information gathering
- Safe `None` returns for missing data
- Jinja2 template variable generation

### skills.py
Skill registry and loading. Manages:
- Skill discovery in filesystem
- Tool signature extraction via full import (fail-fast)
- Config-pinned skill overrides
- Skill gating enforcement (loaded vs. unloaded)

### toolloader.py
Standalone tool loading. Handles:
- Discovery of individual `.py` files and packages in tool directories
- Toolkit instantiation from user and project tool paths
- Integration with main toolkit registry (no skill wrapper required)

### rendering.py
Minimal, dependency-free ANSI output streaming. Handles:
- Token accumulation
- Basic ANSI formatting (italics for reasoning, basic progress feedback, etc.)
- Tool call display
- Progress indicators

## Data Flow

### Tool Call Flow
```
Model generates tool call
    |
    v
Agent receives JSON tool call
    |
    v
Toolkit.dispatch(call, context)
    |
    v
Gate check (if --gate enabled)
    |
    v
Execute tool callable
    |
    v
Return result to agent
    |
    v
Append to conversation as tool result
```

### Context Resolution Flow
```
Session initialization
    |
    v
Load active resolvers from config
    |
    v
For each resolver: resolve() → dict
    |
    v
Merge resolver outputs
    |
    v
Inject into Jinja2 template
    |
    v
Static system prompt generated
```

## Session Persistence Format

Stored as msgpack in `~/.lc/sessions/<session_id>.msgpack`:

```python
{
    "session_id": str,          # UUID
    "created_at": float,        # Unix timestamp
    "updated_at": float,        # Unix timestamp
    "config_path": str,         # Path to config directory used
    "working_dir": str,         # CWD at session start
    "conversation": list,       # List of message dicts
    "tool_context": dict,       # Serialized tool state
    "loaded_skills": list       # Names of fully loaded skills
}
```

## Gating Levels

| Level | Description | Tools |
|-------|-------------|-------|
| 0 | Read-only operations | Read |
| 1 | Write operations | Write, Edit |
| 2 | Execution | Exec (read-only) |
| 3 | Destructive execution | Exec (write/modify) |

Gating is checked before tool execution. If `--gate` is specified, interactive confirmation is required for any tool at or above the gate level.

## Configuration Hierarchy

1. Command-line flags (highest priority)
2. Session state (if resuming)
3. `~/.lc/config` or `~/.config/lc/config`
4. Built-in defaults (lowest priority)

## Loading Security Model

The `[loading]` configuration section controls what code executes:

```ini
[loading]
user_skills = true       # Load from ~/.lc/skills/
user_tools = false       # Load from ~/.lc/tools/
project_skills = false   # Load from ./.lc/skills/
project_tools = false    # Load from ./.lc/tools/
```

**Security defaults:**
- User skills: Enabled (backward compatibility)
- User tools, project skills/tools: Disabled (explicit opt-in required)
- All standalone tools bypass skill gating (trusted when enabled)
- Skill tools require `load_skill` unless pinned

## Error Handling Strategy

- **Configuration errors**: Exit with message, non-zero code
- **Model errors**: Retry with backoff, then fail session
- **Tool errors**: Return error message to model, let it decide
- **Context limit**: Current MVP: hard exit with "Context Exceeded"
- **Gate denial**: Skip tool, inform model

## Future Extension Points

- Context compaction/summarization (agent.py)
- Streaming tool output (toolkit.py)
- Full markdown rendering (rendering.py)
- Additional model backends (models/)
- Directory-scoped sessions (session.py)
- `--jail` filesystem restriction (toolkit.py, filesystem.py)
