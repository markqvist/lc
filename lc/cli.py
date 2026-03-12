# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

"""Command-line interface for lc."""

import RNS
import argparse
import time
import sys
import os
from pathlib import Path
from typing import Optional

from lc.session import Session
from lc.config import Config


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(prog="lc", description="Humanity's Last Command - natural language command execution", epilog='Example: lc "Find all PDFs and organize them by date"')
    
    parser.add_argument("command", nargs="?", help="Natural language command to execute (omit for interactive mode if -i specified)")
    parser.add_argument("-i", "--interactive", action="store_true", help="Enter interactive mode after executing command (if any)")
    parser.add_argument("-g", "--gate", type=int, metavar="LEVEL", help="Enable gating for operations at or above LEVEL (0-3)")
    parser.add_argument("-c", "--config", type=str, metavar="PATH", help="Path to configuration directory (default: ~/.lc or ~/.config/lc)")
    parser.add_argument("-r", "--resume", action="store_true", help="Resume previous session (implies -i)")
    parser.add_argument("-I", "--session-id", type=str, metavar="ID", help="Resume specific session by ID or name")
    parser.add_argument("-n", "--name", type=str, metavar="NAME", help="Name for new session (for easy reference later)")
    parser.add_argument("-R", "--rebuild", action="store_true", help="Rebuild system prompt on resume (invalidates KV-cache, loads new skills, etc.)")
    parser.add_argument("-l", "--list-sessions", action="store_true", help="List available sessions and exit")
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
    """List available sessions and exit."""
    from lc.session import SessionManager
    
    sessions = SessionManager.list_sessions(config)
    
    if not sessions:
        print("No sessions found.")
        return 0
    
    print(f"{'Name':<20} {'ID':<36} {'Messages':<10} {'Updated':<20} {'Directory'}")
    print("-" * 120)
    
    for session in sessions:
        session_name = session.get("name", "") or ""
        name = session_name[:18]
        sid = session.get("session_id", "")[:36]
        msg_count = len([m for m in session.get("conversation", []) if m.get("role") in ("user", "assistant")])
        updated = session.get("updated_at", 0)

        try:    time_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(updated))
        except: time_str = "unknown"

        working_dir = session.get("working_dir", "")[:30]
        print(f"{name:<20} {sid:<36} {msg_count:<10} {time_str:<20} {working_dir}")
    
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

def main() -> int:
    parser      = create_argument_parser()
    args        = parser.parse_args()
    config_path = resolve_config_path(args.config)
    
    try:
        config = Config.load(config_path)
        
        # Handle session listing
        if args.list_sessions: return list_sessions(config)
        
        # Detect if we can prompt (TTY available)
        can_prompt = sys.stdin.isatty() and sys.stdout.isatty()
        
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
                                           session_name=args.name, rebuild_system_prompt=args.rebuild)

        if command:
            result = session.execute(command, gate_level=args.gate, can_prompt=can_prompt, stdin_context=stdin_context)
            
            if result.error:
                print(f"Error: {result.error}", file=sys.stderr)
                return 1
            
            if not args.interactive: return 0
        
        # Interactive mode
        if args.interactive or args.resume or not command: return session.run_interactive(gate_level=args.gate, can_prompt=can_prompt)
        
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
