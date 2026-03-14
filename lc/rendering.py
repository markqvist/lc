# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

import sys
import re
import random
from typing import Optional

class TTYRenderer:

    # ANSI codes
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"

    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"

    CLEAR_LINE = "\x1b[2K"
    MOVE_UP = "\033[A"

    THINKING_ICON = "⧖"
    DONE_THINKING_ICON = "⧗"
    SYSTEM_ICON = "⚙"

    def __init__(self, stream=None, show_reasoning: bool = True, mode: str = "tty"):
        self.stream = stream or sys.stdout
        self.mode = mode
        self.show_reasoning = show_reasoning and (mode == "tty")
        self._buffer = ""
        self._in_reasoning = False
        self._reasoning_content = ""
        self._spinner_shown = False

    def _is_tty(self) -> bool:
        return self.mode == "tty"
    
    def write(self, text: str, end: str = "") -> None:
        self.stream.write(text + end)
        self.stream.flush()
    
    def write_line(self, text: str = "") -> None:
        self.write(text, end="\n")
    
    # For MVP: just write directly
    # Future: accumulate, format on boundaries
    def stream_token(self, token: str) -> None:
        self.write(token, end="")
    
    def start_reasoning(self) -> None:
        if self.show_reasoning and not self._in_reasoning:
            self._in_reasoning = True
            self.clear_thinking()
            self.write(f"{self.DIM}{self.ITALIC}", end="")
    
    def end_reasoning(self) -> None:
        if self.show_reasoning and self._in_reasoning:
            self._in_reasoning = False
            self.write(f"{self.RESET}\n", end="")
    
    # Display reasoning content if enabled.
    # Called after receiving a complete response with reasoning_content.
    # For streaming, use stream_reasoning_chunk() instead.
    def display_reasoning_content(self, content: str) -> None:
        if self.show_reasoning and content:
            self.start_reasoning()
            self.write(content.rstrip(), end="")
            self.end_reasoning()
            self._reasoning_content = content
    
    # Stream a chunk of reasoning content.
    # For future streaming implementation.
    # Called repeatedly as reasoning chunks arrive.
    def stream_reasoning_chunk(self, chunk: str) -> None:
        if self.show_reasoning:
            if not self._in_reasoning: self.start_reasoning()
            self.write(chunk, end="")
    
    def display_tool_call(self, tool_name: str, arguments: dict) -> None:
        if not self._is_tty(): return
        self.write(f"\n{self.CYAN}▶ {tool_name}{self.RESET}", end="")
        if arguments:
            for key, value in arguments.items():
                display_value = str(value)
                # This is getting scary pretty fast. No more argument truncation.
                # if len(display_value) > 33: display_value = display_value[:32] + "…"
                self.write(f" {self.DIM}{key}:{self.RESET} {display_value}", end="")

        self.write("")
    
    def display_tool_result(self, result: str, modality: str = "text") -> None:
        if not self._is_tty(): return
        
        # Handle non-text modalities with placeholder
        if modality != "text":
            # Check if result indicates an error
            if result.startswith("Error:") or result.startswith("[Invalid") or result.startswith("[Could not"):
                self.write(f"\n{self.RED}✗ Result:{self.RESET} {result}\n")
            else:
                self.write(f"\n{self.GREEN}✓ Result:{self.RESET} ({modality} data)\n")
            return
        
        lsep = f"{self.DIM}\\{self.RESET}"
        display = f"{lsep}".join(result.rstrip().splitlines())
        limit = 384
        if len(display) > limit:
            display = f"{display[:limit-1]}"
            found_non_printable = 0; pos = 0;
            for char in reversed(display[-5:]):
                pos += 1
                if not char.isprintable() and char != '\n': found_non_printable = pos

            if found_non_printable: display = display[:-pos]
            display = f"{display}…"

        self.write(f"\n{self.GREEN}✓ Result: {self.RESET} {display}{self.RESET}\n")
    
    def display_error(self, message: str) -> None:
        if not self._is_tty(): return
        self.write(f"\n{self.RED}✗ Error: {message}{self.RESET}\n")

    def display_thinking(self) -> None:
        if not self._is_tty(): return
        spinner = random.choice(SPINNER_FRAMES)
        self._spinner_shown = True
        if self.show_reasoning: self.write(f"\r{self.SYSTEM_ICON} {self.THINKING_ICON} Thinking... {spinner}", end="")
        else:                   self.write(f"\r{self.SYSTEM_ICON} {self.THINKING_ICON} Thinking... {spinner}", end="")

    def clear_thinking(self) -> None:
        if not self._is_tty():
            self._spinner_shown = False
            return
        if self._spinner_shown:
            self.write(self.CLEAR_LINE, end="\r")
            self._spinner_shown = False

    ANSI_PATTERN = re.compile(r'\x1b\[[0-9;]*m')
    def _stdout_sanitize(self, text: str) -> str:
        strip_ansi = False
        if strip_ansi: return self.ANSI_PATTERN.sub('', text)
        else:          return text

    def display_response(self, content: str, reasoning_content: Optional[str] = None) -> None:
        if self._is_tty():
            if reasoning_content and self.show_reasoning: self.display_reasoning_content(reasoning_content)
            if content: self.write(f"\n{content}", end="\n")
        else:
            # Pipe mode: Final, raw output only
            if content: self.write(self._stdout_sanitize(content).rstrip(), end="\n")
    
    def format_markdown(self, text: str) -> str:
        # MVP: return as-is
        # Future: implement basic markdown to ANSI conversion
        return text

SPINNER_FRAMES = ['□□□□□□□□', '■□□□□□□□', '□■□□□□□□', '□□■□□□□□', '□□□■□□□□', '□□□□■□□□', '□□□□□■□□', '□□□□□□■□',
                  '□□□□□□□■', '□□□□■■□□', '□□□□□■■□', '■□■□□□□□', '□■□■□□□□', '□□■□■□□□', '□□□■□■□□', '□□□□■□■□',
                  '□□□□□■□■', '■□□■□□■□', '□■□□■□□■', '□□□□■■□■', '□■□■□□□□', '□■■□■□□□', '□□■□■■□□', '□□□■■□■□',
                  '□□□□■□■■', '■□■□■□■□', '□■□■□■□■', '■■■□■□□□', '□□■□■□■□', '□□□■□■□■', '□■■□■□□□', '□■□■□■□□',
                  '□□■□□■■□', '□□□■□■□■', '■□■■□■□□', '□■□□□□■□', '□□■■□■□■', '■□■□■□■□', '□■□■■□□■']