# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

import sys
import re
import time
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

    FRAME_INTERVAL = 0.025

    def __init__(self, stream=None, show_reasoning: bool = True, stream_response: bool = False, mode: str = "tty"):
        self.stream = stream or sys.stdout
        self.mode = mode
        self.show_reasoning = show_reasoning and (mode == "tty")
        self.stream_response = stream_response and (mode == "tty")
        self._buffer = ""
        self._in_reasoning = False
        self._reasoning_content = ""
        self._spinner_shown = False
        self._last_streamed = None
        self._last_frame = 0
        self._final = ""

    def _is_tty(self) -> bool:
        return self.mode == "tty"
    
    def write(self, text: str, end: str = "") -> None:
        self.stream.write(text + end)
        self.stream.flush()
    
    def write_line(self, text: str = "") -> None:
        self.write(text, end="\n")
    
    def start_reasoning(self) -> None:
        if self.show_reasoning and not self._in_reasoning:
            self._in_reasoning = True
            self.clear_thinking()
            self.write(f"{self.DIM}{self.ITALIC}", end="")
    
    def end_reasoning(self) -> None:
        if self.show_reasoning and self._in_reasoning:
            self._in_reasoning = False
            self.write(f"{self.RESET}\n", end="")
            if not self.stream_response: self.write("\n", end="")

    def _guard_reasoning(self):
        if self.show_reasoning and self._in_reasoning:
            self.end_reasoning()
            self.write("\n", end="")

        if self.show_reasoning == False and self._in_reasoning:
            self._in_reasoning = False
            self.write(f"{self.RESET}\r{self.CLEAR_LINE}", end="")

    def _guard_content(self):
        if self._last_streamed == "content":
            self.write("\n", end="\n")
            self._last_streamed = None

    def _guard_preparing(self):
        if self._last_streamed == "preparing":
            self.write(self.CLEAR_LINE, end="\r")
            self._last_streamed = None
    
    # Display reasoning content if enabled.
    # Called after receiving a complete response with reasoning_content.
    # For streaming, use stream_reasoning_chunk() instead.
    def display_reasoning_content(self, content: str) -> None:
        if self.show_reasoning and not self.stream_response and content:
            self.start_reasoning()
            self.write(f"{content.lstrip().rstrip()}", end="")
            self.end_reasoning()
            self._reasoning_content = content
    
    # Stream a chunk of reasoning content.
    # For future streaming implementation.
    # Called repeatedly as reasoning chunks arrive.
    def stream_reasoning_chunk(self, chunk: str) -> None:
        if self.show_reasoning:
            if not self._in_reasoning: self.start_reasoning()
            self.write(chunk, end="")
            self._last_streamed = "reasoning"

    # For MVP: just write directly
    # Future: accumulate, format on boundaries
    def stream_chunk(self, chunk: str) -> None:
        if self._spinner_shown: self.clear_thinking()
        self._guard_reasoning()
        self.write(chunk, end="")
        self._last_streamed = "content"

    def display_tool_call(self, tool_name: str, arguments: dict) -> None:
        if not self._is_tty(): return
        if not self.stream_response: self.clear_thinking()
        self._guard_preparing()
        self._guard_reasoning()
        self._guard_content()

        truncate_for = ["Filesystem.write", "Filesystem.edit"]
        self.write(f"{self.CYAN}▶ {tool_name}{self.RESET}", end="")
        if arguments:
            for key, value in arguments.items():
                display_value = str(value)
                if tool_name in truncate_for: display_value = self._compact_multiline(display_value)
                self.write(f" {self.DIM}{key}:{self.RESET} {display_value}", end="")

        self.write("")
    
    def display_tool_result(self, result: str, modality: str = "text") -> None:
        if not self._is_tty(): return
        self._guard_reasoning()
        self._guard_content()
        
        # Handle non-text modalities with placeholder
        if modality != "text":
            is_error = result.startswith("Error:") or result.startswith("[Invalid") or result.startswith("[Could not")
            if is_error: self.write(f"\n{self.RED}✗ Result:{self.RESET} {result}\n")
            else:        self.write(f"\n{self.GREEN}✓ Result:{self.RESET} ({modality} data)\n")
            return
        
        display = self._compact_multiline(result)
        self.write(f"\n{self.GREEN}✓ Result: {self.RESET} {display}{self.RESET}\n\n")

    def _compact_multiline(self, text, limit=384):
        display = text
        if len(display) > limit: display = f"{display[:limit-1]}…"
        lsep = f"{self.DIM}\\{self.RESET}"
        display = f"{lsep}".join(display.rstrip().splitlines())
        return display
    
    def display_error(self, message: str) -> None:
        if not self._is_tty(): return
        self._guard_reasoning()
        self.write(f"\n{self.RED}✗ Error: {message}{self.RESET}\n")

    def display_connecting(self) -> None:
        if not self._is_tty(): return
        self._guard_reasoning()
        self._spinner_shown = True
        self.write(f"\r{self.SYSTEM_ICON} {self.THINKING_ICON} Processing request...", end="")

    def display_connected(self) -> None:
        if not self._is_tty(): return
        self._guard_reasoning()
        self._spinner_shown = True
        self.write(f"\r{self.SYSTEM_ICON} {self.THINKING_ICON} Processing prompt...", end="")

    def display_prepare_tool(self) -> None:
        if not self._is_tty(): return
        self._guard_reasoning()
        self._guard_content()
        spinner = random.choice(SPINNER_FRAMES)
        self._spinner_shown = True
        if time.time() > self._last_frame + self.FRAME_INTERVAL:
            self._last_streamed = "preparing"
            self.write(f"\r{self.SYSTEM_ICON} {self.THINKING_ICON} Preparing tool... {spinner} ", end="")
            self._last_frame = time.time()

    def display_thinking(self, delta) -> None:
        if not self._is_tty(): return
        spinner = random.choice(SPINNER_FRAMES)
        self._spinner_shown = True
        if self.stream_response:
            if self.show_reasoning: self.stream_reasoning_chunk(delta)
            else:
                if time.time() > self._last_frame + self.FRAME_INTERVAL:
                    self.write(f"\r{self.SYSTEM_ICON} {self.THINKING_ICON} Thinking... {spinner} ", end="")
                    self._last_frame = time.time()
                    self._in_reasoning = True

        else:
            if time.time() > self._last_frame + self.FRAME_INTERVAL:
                if self.show_reasoning: self.write(f"\r{self.SYSTEM_ICON} {self.THINKING_ICON} Thinking... {spinner} ", end="")
                else:                   self.write(f"\r{self.SYSTEM_ICON} {self.THINKING_ICON} Thinking... {spinner} ", end="")
                self._last_frame = time.time()

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
            if content and not self.stream_response:
                self.clear_thinking()
                self.write(f"{content}", end="\n\n")

        # Pipe mode: Final, raw output only
        else:
            if content:
                self._final = self._stdout_sanitize(content).rstrip()
                self.write(self._final, end="\n")
    
    def format_markdown(self, text: str) -> str:
        # MVP: return as-is
        # Future: implement basic markdown to ANSI conversion
        return text

SPINNER_FRAMES = ['□□□□□□□□', '■□□□□□□□', '□■□□□□□□', '□□■□□□□□', '□□□■□□□□', '□□□□■□□□', '□□□□□■□□', '□□□□□□■□',
                  '□□□□□□□■', '□□□□■■□□', '□□□□□■■□', '■□■□□□□□', '□■□■□□□□', '□□■□■□□□', '□□□■□■□□', '□□□□■□■□',
                  '□□□□□■□■', '■□□■□□■□', '□■□□■□□■', '□□□□■■□■', '□■□■□□□□', '□■■□■□□□', '□□■□■■□□', '□□□■■□■□',
                  '□□□□■□■■', '■□■□■□■□', '□■□■□■□■', '■■■□■□□□', '□□■□■□■□', '□□□■□■□■', '□■■□■□□□', '□■□■□■□□',
                  '□□■□□■■□', '□□□■□■□■', '■□■■□■□□', '□■□□□□■□', '□□■■□■□■', '■□■□■□■□', '□■□■■□□■']