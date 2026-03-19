# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

"""Command-line interface for lc."""

import RNS
import argparse
import json
import time
import sys
import os
from pathlib import Path
from typing import Optional
from importlib import resources as importlib_resources

from lc.session import Session
from lc.config import Config


def create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lc", description="Humanity's Last Command - natural language command execution", epilog='Example: lc "Find all PDFs and organize them by date"')
    
    parser.add_argument("command", nargs="?", help="Natural language command to execute (omit for interactive mode if -i specified)")
    parser.add_argument("-i", "--interactive", action="store_true", help="Enter interactive mode after executing command (if any)")
    parser.add_argument("-g", "--gate", type=int, metavar="LEVEL", help="Enable gating for operations at or above LEVEL (0-3)")
    parser.add_argument("-c", "--config", type=str, metavar="PATH", help="Path to configuration directory (default: ~/.lc or ~/.config/lc)")
    parser.add_argument("-r", "--resume", action="store_true", help="Resume previous session (implies -i)")
    parser.add_argument("-I", "--session-id", type=str, metavar="ID", help="Resume specific session by ID or name")
    parser.add_argument("-n", "--name", type=str, metavar="NAME", help="Name for new session (for easy reference later)")
    parser.add_argument("-m", "--model", type=str, metavar="NAME", help="Use named model configuration from config")
    parser.add_argument("-R", "--rebuild", action="store_true", help="Rebuild system prompt on resume (invalidates KV-cache, loads new skills, etc.)")
    parser.add_argument("-l", "--list-sessions", action="store_true", help="List available sessions and exit")
    parser.add_argument("-S", "--inspect-session", type=str, metavar="ID|PATH", help="Inspect session by ID/name or path to msgpack file")
    parser.add_argument("-f", "--follow", action="store_true", help="Follow session updates (stream mode, use with --inspect-session)")
    parser.add_argument("-M", "--no-markdown", action="store_true", help="Disable markdown rendering, even if enabled in config")
    parser.add_argument("--docs", action="store_true", help="Display essential documentation for lc")
    parser.add_argument("--readme", action="store_true", help="Display the readme")
    parser.add_argument("--guide", action="store_true", help="Display the guide")
    parser.add_argument("--examples", action="store_true", help="Display path to example skills and tools code")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--version", action="version", version=f"%(prog)s {Session.get_version()}")
    
    return parser

def resolve_config_path(specified: Optional[str]) -> Path:
    if specified:
        path = Path(specified).expanduser().resolve()
        if not path.exists(): path.mkdir(parents=True, exist_ok=True)
        return path
    
    # Check standard locations
    xdg_config = Path.home() / ".config" / "lc"
    dot_lc = Path.home() / ".lc"
    
    if dot_lc.exists(): return dot_lc
    elif xdg_config.exists(): return xdg_config
    else:
        dot_lc.mkdir(parents=True, exist_ok=True)
        return dot_lc

def list_sessions(config: Config) -> int:
    from lc.session import SessionManager    
    sessions = SessionManager.list_sessions(config)
    
    if not sessions:
        print("No sessions found.")
        return 0
    
    print(f"{'Name':<20} {'ID':<36} {'Msgs':<6} {'Tokens':<10} {'Updated':<16} {'Directory'}")
    print("-" * 120)

    for session in sessions:
        session_name = session.get("name", "") or ""
        name = session_name[:18]
        sid = session.get("session_id", "")[:36]
        msg_count = len([m for m in session.get("conversation", []) if m.get("role") in ("user", "assistant")])
        updated = session.get("updated_at", 0)

        # Token usage
        stats = session.get("stats", {})
        total_tokens = stats.get("total_tokens", stats.get("token_count", 0))
        tokens_str = f"{total_tokens:,}" if total_tokens else "-"

        try:    time_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(updated))
        except: time_str = "unknown"

        working_dir = session.get("working_dir", "")[:30]
        print(f"{name:<20} {sid:<36} {msg_count:<6} {tokens_str:<10} {time_str:<16} {working_dir}")

    return 0


def _resolve_session_file(config: Config, session_ref: str) -> Optional[Path]:
    """Resolve session reference to file path."""
    from lc.session import SessionManager
    
    # Case 1: Direct file path
    path = Path(session_ref).expanduser().resolve()
    if path.exists() and path.is_file():
        return path
    
    # Case 2: UUID
    uuid_path = config.path / "sessions" / f"{session_ref}.msgpack"
    if uuid_path.exists():
        return uuid_path
    
    # Case 3: Name resolution
    named_file = SessionManager.find_session_by_name(config, session_ref)
    if named_file:
        return named_file
    
    return None


def follow_session(config: Config, session_ref: str, verbose: bool = True) -> int:
    """Stream session updates as they occur."""
    from RNS.vendor import umsgpack
    import signal
    
    # Track state between polls
    last_mtime = 0
    last_msg_count = 0
    header_printed = False
    running = True
    waiting_for_session = True
    session_file = None
    
    def handle_interrupt(sig, frame):
        nonlocal running
        running = False
    
    # Restore default signal handler for clean exit
    old_handler = signal.signal(signal.SIGINT, handle_interrupt)
    
    try:
        while running:
            # Try to resolve session file (may not exist yet)
            if session_file is None or not session_file.exists():
                session_file = _resolve_session_file(config, session_ref)
                if session_file is None:
                    if waiting_for_session:
                        print(f"Waiting for session '{session_ref}' to appear...", end="\r")
                        sys.stdout.flush()
                        time.sleep(0.5)
                        continue
                    else:
                        print(f"\n*[Session file deleted, waiting...]*")
                        waiting_for_session = True
                        time.sleep(0.5)
                        continue

                else: waiting_for_session = False
            
            # Session found, proceed with normal logic
            if waiting_for_session and session_file.exists():
                waiting_for_session = False
                print(f"{' ' * 60}", end="\r")  # Clear waiting message
            
            try:
                current_mtime = session_file.stat().st_mtime
                if current_mtime > last_mtime:
                    with open(session_file, "rb") as f:
                        data = umsgpack.unpack(f)
                    
                    conversation = data.get("conversation", [])
                    current_msg_count = len(conversation)
                    
                    # Print header and all existing messages on first run
                    if not header_printed:
                        session_name = data.get("name")
                        session_id = data.get("session_id", "unknown")
                        display_title = session_name or session_id[:8] + "..."
                        
                        print(f"# Session: {display_title}")
                        print()
                        print("## Conversation Transcript")
                        print()
                        
                        # Render all existing messages
                        for i, msg in enumerate(conversation):
                            msg_num = i + 1
                            role = msg.get("role", "unknown")
                            content = msg.get("content")
                            tool_calls = msg.get("tool_calls", [])
                            tool_call_id = msg.get("tool_call_id")
                            name = msg.get("name")
                            reasoning_content = msg.get("reasoning_content")
                            
                            if role == "assistant" and tool_calls:
                                print(f"### Message {msg_num}: Assistant [Tool Call{'s' if len(tool_calls) > 1 else ''}]")
                                print()
                                if content:
                                    print(f"*Assistant commentary:* {content.lstrip().rstrip()}")
                                    print()
                                for tc in tool_calls:
                                    fn = tc.get("function", {})
                                    tc_name = fn.get("name", "unknown")
                                    tc_args = fn.get("arguments", {})
                                    tc_id = tc.get("id", "unknown")
                                    print(f"**{tc_name}** `{tc_id}`")
                                    if tc_args:
                                        if isinstance(tc_args, dict):
                                            for key, val in tc_args.items():
                                                print(f"- `{key}`: `{val}`")
                                        else:
                                            print(f"- Arguments: `{tc_args}`")
                                    print()
                            elif role == "assistant":
                                text = content or ""
                                print(f"### Message {msg_num}: Assistant")
                                print()
                                if reasoning_content:
                                    print(f"*Reasoning:*")
                                    print("```")
                                    print(reasoning_content.lstrip().rstrip())
                                    print("```")
                                    print()
                                print(text)
                                print()
                            elif role == "tool":
                                text = content or ""
                                print(f"### Message {msg_num}: Tool Result")
                                print()
                                print(f"**Tool:** `{name or 'unknown'}`  ")
                                print(f"**Call ID:** `{tool_call_id or 'unknown'}`")
                                print()
                                print("````")
                                print(text.lstrip().rstrip())
                                print("````")
                                print()
                            elif role == "user":
                                text = content or ""
                                print(f"### Message {msg_num}: User")
                                print()
                                for line in text.splitlines():
                                    print(f"> {line}")
                                print()
                        
                        sys.stdout.flush()
                        header_printed = True
                        last_msg_count = current_msg_count
                    
                    # Render new messages
                    elif current_msg_count > last_msg_count:
                        new_messages = conversation[last_msg_count:]
                        # Render new messages directly
                        for i, msg in enumerate(new_messages):
                            msg_num = last_msg_count + i + 1
                            role = msg.get("role", "unknown")
                            content = msg.get("content")
                            tool_calls = msg.get("tool_calls", [])
                            tool_call_id = msg.get("tool_call_id")
                            name = msg.get("name")
                            reasoning_content = msg.get("reasoning_content")
                            
                            if role == "assistant" and tool_calls:
                                print(f"### Message {msg_num}: Assistant [Tool Call{'s' if len(tool_calls) > 1 else ''}]")
                                print()
                                if content: print(f"**Assistant commentary:** {content.lstrip().rstrip()}\n")
                                
                                for tc in tool_calls:
                                    fn = tc.get("function", {})
                                    tc_name = fn.get("name", "unknown")
                                    tc_args = fn.get("arguments", {})
                                    tc_id = tc.get("id", "unknown")
                                    print(f"**{tc_name}** `{tc_id}`")
                                    if tc_args:
                                        if isinstance(tc_args, dict):
                                            for key, val in tc_args.items():
                                                print(f"- `{key}`: `{val}`")
                                        else:
                                            print(f"- Arguments: `{tc_args}`")
                                    print()

                            elif role == "assistant":
                                text = content or ""
                                print(f"### Message {msg_num}: Assistant")
                                print()
                                if reasoning_content:
                                    print("*Reasoning:*")
                                    print("```")
                                    print(reasoning_content.lstrip().rstrip())
                                    print("```")
                                    print()
                                print(text)
                                print()
                            elif role == "tool":
                                text = content or ""
                                print(f"### Message {msg_num}: Tool Result")
                                print()
                                print(f"**Tool:** `{name or 'unknown'}`  ")
                                print(f"**Call ID:** `{tool_call_id or 'unknown'}`")
                                print()
                                print("````")
                                print(text.lstrip().rstrip())
                                print("````")
                                print()
                            elif role == "user":
                                text = content or ""
                                print(f"### Message {msg_num}: User")
                                print()
                                for line in text.splitlines():
                                    print(f"> {line}")
                                print()
                        
                        sys.stdout.flush()
                        last_msg_count = current_msg_count
                    
                    # Handle session reset (messages deleted)
                    elif current_msg_count < last_msg_count:
                        print(f"\n*[Session reset: {last_msg_count} -> {current_msg_count} messages]*")
                        print()
                        last_msg_count = current_msg_count
                    
                    last_mtime = current_mtime
                    
            except FileNotFoundError:
                # Session file deleted, reset and wait for it to reappear
                if not waiting_for_session:
                    print(f"\n*[Session file deleted, waiting...]*")
                    waiting_for_session = True
                    session_file = None
                    last_mtime = 0
                    
            except Exception as e:
                # Log error but keep polling
                print(f"\n*[Error reading session: {e}]*", file=sys.stderr)
            
            if running:
                time.sleep(0.5)
                
    except BrokenPipeError:
        # Viewer closed, exit cleanly
        pass
    finally:
        signal.signal(signal.SIGINT, old_handler)
    
    return 0


def inspect_session(config: Config, session_ref: str, output_mode: str = "tty", verbose: bool = True) -> int:
    from lc.session import SessionManager
    from RNS.vendor import umsgpack
    from pathlib import Path
    
    session_file = None
    
    # Case 1: Direct file path
    path = Path(session_ref).expanduser().resolve()
    if path.exists() and path.is_file():
        session_file = path
    
    # Case 2: UUID or name resolution
    if not session_file:
        # Try UUID first
        uuid_path = config.path / "sessions" / f"{session_ref}.msgpack"
        if uuid_path.exists(): session_file = uuid_path
        else:
            # Try as name
            named_file = SessionManager.find_session_by_name(config, session_ref)
            if named_file: session_file = named_file
    
    if not session_file or not session_file.exists():
        print(f"Error: Session not found: {session_ref}", file=sys.stderr)
        return 1
    
    # Load the session data
    try:
        with open(session_file, "rb") as f: data = umsgpack.unpack(f)
    
    except Exception as e:
        print(f"Error: Failed to load session file: {e}", file=sys.stderr)
        return 1
    
    # Format as markdown
    lines = []
    is_pipe = output_mode == "pipe"
    
    def add(line: str = ""): lines.append(line)
    
    # Header
    session_name = data.get("name")
    session_id = data.get("session_id", "unknown")
    display_title = session_name or session_id[:8] + "..."
    
    add(f"# Session: {display_title}")
    add()
    
    # Metadata section
    add("## Metadata")
    add()
    add("| Field | Value |")
    add("|-------|-------|")
    add(f"| Session ID | `{session_id}` |")
    add(f"| Name | {session_name or '*unnamed*'} |")
    
    created_at = data.get("created_at", 0)
    updated_at = data.get("updated_at", 0)
    try:
        created_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(created_at))
        updated_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(updated_at))
    except:
        created_str = str(created_at)
        updated_str = str(updated_at)
    
    add(f"| Created | {created_str} |")
    add(f"| Updated | {updated_str} |")
    add(f"| Working Directory | `{data.get('working_dir', 'unknown')}` |")
    add(f"| Config Path | `{data.get('config_path', 'unknown')}` |")
    add(f"| Format Version | {data.get('version', 'unknown')} |")
    add()
    
    # Statistics section
    stats = data.get("stats", {})
    conversation = data.get("conversation", [])
    
    # Count message types
    user_msgs = len([m for m in conversation if m.get("role") == "user"])
    assistant_msgs = len([m for m in conversation if m.get("role") == "assistant"])
    tool_msgs = len([m for m in conversation if m.get("role") == "tool"])
    system_msgs = len([m for m in conversation if m.get("role") == "system"])
    
    add("## Statistics")
    add()
    add(f"- **Turns**: {stats.get('turn_count', 0)}")
    add(f"- **Messages**: {len(conversation)} ({user_msgs} user, {assistant_msgs} assistant, {tool_msgs} tool, {system_msgs} system)")
    add(f"- **Tool Calls**: {stats.get('tool_call_count', 0)}")

    # Token usage (new format with detailed breakdown)
    input_tokens = stats.get('input_tokens', 0)
    output_tokens = stats.get('output_tokens', 0)
    total_tokens = stats.get('total_tokens', stats.get('token_count', 0))

    if input_tokens or output_tokens:
        add(f"- **Tokens**: {total_tokens:,} ({input_tokens:,} input, {output_tokens:,} output)")
    elif total_tokens:
        add(f"- **Tokens**: {total_tokens:,} (legacy count)")
    else:
        add(f"- **Tokens**: -")

    add()
    
    # Loaded skills
    loaded_skills = data.get("loaded_skills", [])
    if loaded_skills:
        add("## Loaded Skills")
        add()
        for skill in loaded_skills: add(f"- `{skill}`")
        add()
    
    # Tool context
    tool_context = data.get("tool_context", {})
    if tool_context and verbose:
        add("## Tool Context")
        add()
        add("```json")
        add(json.dumps(tool_context, indent=2))
        add("```")
        add()
    
    # Configuration snapshot
    config_snapshot = data.get("config_snapshot", {})
    if config_snapshot and verbose:
        add("## Configuration Snapshot")
        add()
        add("```json")
        add(json.dumps(config_snapshot, indent=2))
        add("```")
        add()
    elif not config_snapshot:
        add("## Configuration Snapshot")
        add()
        add("*Not captured in this session*")
        add()
    
    # Context analysis for per-message token lookup
    context_analysis = data.get("context_analysis", [])
    message_token_map = {}
    for turn in context_analysis:
        for mt in turn.get("message_tokens", []):
            idx = mt.get("index")
            if idx is not None and idx not in message_token_map:
                message_token_map[idx] = (mt.get("estimated_tokens", 0), mt.get("is_estimated", True))

    # Conversation transcript
    add("## Conversation Transcript")
    add()

    for i, msg in enumerate(conversation):
        role = msg.get("role", "unknown")
        content = msg.get("content")
        tool_calls = msg.get("tool_calls", [])
        tool_call_id = msg.get("tool_call_id")
        name = msg.get("name")
        reasoning_content = msg.get("reasoning_content")
        
        # Skip empty messages in pipe mode for brevity
        if is_pipe and not content and not tool_calls and role not in ("tool", "system"):
            continue
        
        msg_num = i + 1
        
        if role == "system":
            token_count, is_est = message_token_map.get(i, (None, True))
            token_str = f" ~{token_count} tokens" if token_count else ""
            add(f"### Message {msg_num}: System{token_str}")
            add()
            if content:
                content_len = len(content)
                if verbose or is_pipe:
                    add("````")
                    add(content)
                    add("````")
                else:
                    add(f"*[System prompt: {content_len} characters]*")
            add()
        
        elif role == "user":
            token_count, is_est = message_token_map.get(i, (None, True))
            token_str = f" ~{token_count} tokens" if token_count else ""
            # Handle multimodal content
            if isinstance(content, list):
                add(f"### Message {msg_num}: User [Multimodal]{token_str}")
                add()
                for item in content:
                    if item.get("type") == "text":
                        text = item.get("text", "")
                        add(f"> {text}")
                    elif item.get("type") == "image_url":
                        url = item.get("image_url", {}).get("url", "")
                        if url.startswith("data:"): add(f"> *[Image data URI: {len(url)} chars]*")
                        else: add(f"> *[Image: {url}]*")
                add()
            else:
                text = content or ""
                # Truncate long content in TTY mode
                if not is_pipe and not verbose and len(text) > 500:
                    text = text[:497] + "..."
                add(f"### Message {msg_num}: User{token_str}")
                add()
                for line in text.splitlines(): add(f"> {line}")
                add()
        
        elif role == "assistant":
            token_count, is_est = message_token_map.get(i, (None, True))
            token_str = f" ~{token_count} tokens" if token_count else ""
            if tool_calls:
                add(f"### Message {msg_num}: Assistant [Tool Call{'s' if len(tool_calls) > 1 else ''}]{token_str}")
                add()
                # Show content if present (sometimes assistant adds commentary)
                if content:
                    add(f"*Assistant commentary:* {content.lstrip().rstrip()}")
                    add()

                for tc in tool_calls:
                    fn = tc.get("function", {})
                    tc_name = fn.get("name", "unknown")
                    tc_args = fn.get("arguments", {})
                    tc_id = tc.get("id", "unknown")
                    
                    add(f"**{tc_name}** `{tc_id}`")
                    if tc_args:
                        if isinstance(tc_args, dict):
                            for key, val in tc_args.items():
                                val_str = str(val)
                                if not is_pipe and len(val_str) > 200:
                                    val_str = val_str[:197] + "..."
                                add(f"- `{key}`: `{val_str}`")
                        
                        else: add(f"- Arguments: `{tc_args}`")
                    add()
                
            else:
                text = content or ""
                # Truncate long content in TTY mode
                if not is_pipe and not verbose and len(text) > 800:
                    text = text[:797] + "..."

                add(f"### Message {msg_num}: Assistant{token_str}")
                add()
                if reasoning_content:
                    add("*Reasoning:*")
                    add("```")
                    add(reasoning_content.lstrip().rstrip())
                    add("```")
                    add()
                add(text)
                add()
        
        elif role == "tool":
            token_count, is_est = message_token_map.get(i, (None, True))
            token_str = f" ~{token_count} tokens" if token_count else ""
            text = content or ""
            # Truncate long content in TTY mode
            if not is_pipe and not verbose and len(text) > 600:
                text = text[:597] + "..."

            add(f"### Message {msg_num}: Tool Result{token_str}")
            add()
            add(f"**Tool:** `{name or 'unknown'}`  ")
            add(f"**Call ID:** `{tool_call_id or 'unknown'}`")
            add()
            # add("/// details | Tool Output")
            add("````")
            add(text)
            add("````")
            # add("///")
            add()
        
        else:
            add(f"### Message {msg_num}: {role}")
            add()
            add(f"```json")
            add(json.dumps(msg, indent=2))
            add("```")
            add()
    
    output = "\n".join(lines)
    print(output)
    
    return 0


def read_stdin(config: Config) -> Optional[tuple[str, bool]]:
    """
    Read stdin if available and determine if content is binary.
    
    Returns:
        Tuple of (content, is_binary) or None if no stdin data
    """
    import select
    
    # Check if stdin has data without blocking
    if not select.select([sys.stdin], [], [], 0)[0]: return None
    
    # Read all available data
    data = sys.stdin.buffer.read()
    
    if not data: return None
    
    # Try to detect if binary
    is_binary = False
    
    # Check for null bytes - strong indicator of binary
    if b'\x00' in data: is_binary = True
    else:
        try: text = data.decode('utf-8')
        except UnicodeDecodeError:
            # Not valid UTF-8, treat as binary
            is_binary = True
            text = None
        
        if not is_binary:
            # Count non-printable characters
            non_printable = sum(1 for c in text if ord(c) < 32 and c not in '\n\r\t')
            if len(text) > 0 and non_printable / len(text) > 0.1: is_binary = True # >10% control chars
    
    stdin_config = config.stdin
    
    if is_binary:
        # For binary, include hex representation
        max_bytes = stdin_config.get("max_binary_bytes", 512)
        truncated = len(data) > max_bytes
        display_data = data[:max_bytes]
        
        # Format as hex dump
        hex_lines = []
        for i in range(0, len(display_data), 16):
            chunk = display_data[i:i+16]
            hex_part = ' '.join(f'{b:02x}' for b in chunk)
            ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
            hex_lines.append(f"  {i:04x}: {hex_part:<48} {ascii_part}")
        
        result = f"[Binary data received ({len(data)} bytes total){', truncated' if truncated else ''}]\n"
        result += "[Note: This appears to be binary data which may have been unintentionally piped.\n"
        result += "If you intended to pipe text, check the source program's output encoding.]\n\n"
        result += "Hex dump of first " + str(len(display_data)) + " bytes:\n"
        result += '\n'.join(hex_lines)
        
        if truncated: result += f"\n\n... [{len(data) - max_bytes} more bytes]"
        return (result, True)

    else:
        # Text data
        text = data.decode('utf-8')
        max_bytes = stdin_config.get("max_text_bytes", 16384)
        
        # Handle truncation
        if len(data) > max_bytes:
            # Find a safe truncation point (don't cut in middle of multi-byte char)
            truncated_text = text[:max_bytes]
            # Try to end on a line boundary if possible
            last_newline = truncated_text.rfind('\n')
            if last_newline > max_bytes * 0.8:  # Only if we don't lose too much
                truncated_text = truncated_text[:last_newline]
            
            remaining = len(data) - len(truncated_text.encode('utf-8'))
            text = truncated_text + f"\n\n[... {remaining} more bytes truncated]"
        
        return (text, False)

def data_path(filename: str) -> Path:
    pkg = __package__ if __package__ else 'lc'
    return importlib_resources.files(pkg).joinpath('data', filename)

def main() -> int:
    parser      = create_argument_parser()
    args        = parser.parse_args()
    config_path = resolve_config_path(args.config)

    try:
        if args.docs:
            args.readme = True
            args.guide = True
            args.examples = True

        if args.readme:
            with open(data_path("README.md"), "rb") as fh: print(fh.read().decode("utf-8"))
        if args.guide:
            with open(data_path("GUIDE.md"), "rb") as fh: print(fh.read().decode("utf-8"))
        
        if args.examples:
            examples_path = data_path("examples")
            print(f"Example code for skills and toolkits can be found at:\n{examples_path}")

        if args.readme or args.guide or args.examples: return 0

    except Exception as e:
        print("Error while loading documentation")
        RNS.trace_exception(e)
        return 255
    
    try:
        config = Config.load(config_path)
        
        # Handle session listing
        if args.list_sessions: return list_sessions(config)
        
        # Handle session inspection
        if args.inspect_session:
            # Handle follow mode (streaming)
            if args.follow:
                return follow_session(config, args.inspect_session, verbose=args.verbose)
            
            # Detect TTY state for output formatting
            stdout_is_tty = sys.stdout.isatty()
            output_mode = "tty" if stdout_is_tty else "pipe"
            return inspect_session(config, args.inspect_session, output_mode=output_mode, verbose=args.verbose)
        
        # Detect TTY states for input prompting and output formatting
        stdin_is_tty = sys.stdin.isatty()
        stdout_is_tty = sys.stdout.isatty()
        can_prompt = stdin_is_tty and stdout_is_tty
        output_mode = "tty" if stdout_is_tty else "pipe"
        
        # Read stdin if available
        stdin_data = read_stdin(config)
        
        # Determine command and stdin context
        command = args.command
        stdin_context = None
        
        if stdin_data:
            stdin_content, is_binary = stdin_data
            
            # Case 1: stdin IS the command
            if not command: command = stdin_content
            
            # Case 2: stdin is additional context
            else: stdin_context = stdin_content
        
        if not command and not args.interactive and not args.resume:
            parser.print_help()
            return 1
        
        session = Session.create_or_resume(config=config, resume=args.resume or bool(args.session_id), session_id=args.session_id,
                                           session_name=args.name, rebuild_system_prompt=args.rebuild, disable_markdown=args.no_markdown,
                                           model_override=args.model)

        if command:
            result = session.execute(command, gate_level=args.gate, can_prompt=can_prompt, output_mode=output_mode, stdin_context=stdin_context)
            
            if result.error:
                print(f"Error: {result.error}", file=sys.stderr)
                return 1
            
            if not args.interactive:
                if config.display["stream_output"] == True: print("")
                return 0
        
        # Interactive mode
        if args.interactive or args.resume or not command:
            if command: print("\n")
            return session.run_interactive(gate_level=args.gate, can_prompt=can_prompt, output_mode=output_mode)
        
        return 0
        
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 130
    except Exception as e:
        if args.verbose:
            import traceback
            traceback.print_exc()
        else:
            print(f"Error: {e}", file=sys.stderr)
            RNS.trace_exception(e)
        return 1

if __name__ == "__main__": sys.exit(main())
