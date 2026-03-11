# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

"""Command-line interface for lc."""

import argparse
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
    parser.add_argument("--gate", type=int, metavar="LEVEL", help="Enable gating for operations at or above LEVEL (0-3)")
    parser.add_argument("-c", "--config", type=str, metavar="PATH", help="Path to configuration directory (default: ~/.lc or ~/.config/lc)")
    parser.add_argument("--resume", action="store_true", help="Resume previous session (implies -i)")
    parser.add_argument("--session-id", type=str, metavar="ID", help="Resume specific session by ID or name")
    parser.add_argument("--name", type=str, metavar="NAME", help="Name for the session (for easy reference later)")
    parser.add_argument("--rebuild", action="store_true", help="Rebuild system prompt on resume (invalidates KV-cache, loads new skills)")
    parser.add_argument("--list-sessions", action="store_true", help="List available sessions and exit")
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
        name = session.get("name", "")[:18]
        sid = session.get("session_id", "")[:36]
        msg_count = len([m for m in session.get("conversation", []) if m.get("role") in ("user", "assistant")])
        updated = session.get("updated_at", 0)
        
        # Format timestamp
        import time
        try:
            time_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(updated))
        except:
            time_str = "unknown"
        
        working_dir = session.get("working_dir", "")[:30]
        
        print(f"{name:<20} {sid:<36} {msg_count:<10} {time_str:<20} {working_dir}")
    
    return 0

def main() -> int:
    parser = create_argument_parser()
    args = parser.parse_args()
    
    config_path = resolve_config_path(args.config)
    
    try:
        config = Config.load(config_path)
        
        # Handle session listing
        if args.list_sessions:
            return list_sessions(config)
        
        if not args.command and not args.interactive and not args.resume:
            parser.print_help()
            return 1
        
        # Detect if we can prompt (TTY available)
        can_prompt = sys.stdin.isatty() and sys.stdout.isatty()
        
        session = Session.create_or_resume(
            config=config, 
            resume=args.resume or bool(args.session_id), 
            session_id=args.session_id,
            session_name=args.name,
            rebuild_system_prompt=args.rebuild
        )

        if args.command:
            result = session.execute(args.command, gate_level=args.gate, can_prompt=can_prompt)
            
            if result.error:
                print(f"Error: {result.error}", file=sys.stderr)
                return 1
            
            if not args.interactive: return 0
        
        # Interactive mode
        if args.interactive or args.resume or not args.command:
            return session.run_interactive(gate_level=args.gate, can_prompt=can_prompt)
        
        return 0
        
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 130
    except Exception as e:
        if args.verbose:
            import traceback
            traceback.print_exc()
        else: print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__": sys.exit(main())
