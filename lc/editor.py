# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

from __future__ import annotations

import os
import sys
import termios
import tty
import shutil
from enum import Enum, auto
from pathlib import Path
from typing import Optional, Callable


class KeyType(Enum):
    CHAR         = auto()
    ENTER        = auto()
    BACKSPACE    = auto()
    DELETE       = auto()
    UP           = auto()
    DOWN         = auto()
    LEFT         = auto()
    RIGHT        = auto()
    HOME         = auto()
    END          = auto()
    HOME_FULL    = auto()  # Ctrl+A - home of total input
    END_FULL     = auto()  # Ctrl+E - end of total input
    TAB          = auto()
    SUBMIT       = auto()  # Ctrl+D / Alt+Enter
    INTERRUPT    = auto()  # Ctrl+C
    CLEAR_BUFFER = auto()  # Ctrl+K - clear all input
    KILL_LINE_START = auto()  # Ctrl+U - kill to start of line
    KILL_WORD_PREV = auto()   # Ctrl+W - kill previous word
    YANK = auto()             # Ctrl+Y - yank from kill ring
    TRANSPOSE = auto()        # Ctrl+T - transpose characters
    REFRESH = auto()          # Ctrl+L - clear and redraw screen
    UNKNOWN      = auto()


class Key:
    __slots__ = ['type', 'char']
    def __init__(self, key_type: KeyType, char: str = ""):
        self.type = key_type
        self.char = char

    @classmethod
    def from_char(cls, c: str) -> Key: return cls(KeyType.CHAR, c)


class InlineEditor:

    HISTORY_LIMIT = 1000

    def __init__(self, history_file: Optional[Path] = None):
        self.history_file = history_file
        self.history: list[str] = []
        self.history_index: int = 0
        self._saved_buffer: Optional[list[str]] = None
        self._saved_row: int = 0
        self._saved_col: int = 0

        self.buffer: list[str] = [""]
        self.cursor_row: int = 0
        self.cursor_col: int = 0
        self.prompt: str = ""
        self._prompt_width: int = 0

        self._visual_col: int = 0
        self._wrapped_view: list[tuple[int, int, str]] = []

        self._orig_termios: Optional[list] = None
        self._term_width: int = 80
        self._term_height: int = 24

        # Kill ring for cut/copy operations
        self._kill_ring: list[str] = []
        self._kill_index: int = -1

        if self.history_file: self._load_history()

    def read(self, prompt: str = "") -> str:
        if sys.platform == "win32" or not sys.stdin.isatty(): return input(prompt)
        return self._unix_read(prompt)

    def _unix_read(self, prompt: str) -> str:
        self.prompt = prompt
        self._prompt_width = len(prompt)
        self.buffer = [""]
        self.cursor_row = 0
        self.cursor_col = 0
        self._visual_col = self._prompt_width
        self.history_index = len(self.history)
        self._saved_buffer = None

        self._enable_raw_mode()
        try:
            self._render()
            while True:
                key = self._read_key()

                if key.type == KeyType.SUBMIT:
                    result = "\n".join(self.buffer)
                    self._add_to_history(result)
                    # Move cursor to end of displayed input before returning control
                    # First ensure wrapped view is current
                    self._wrapped_view = self._compute_wrapped_view()
                    last_row = len(self.buffer) - 1
                    last_col = len(self.buffer[last_row])
                    end_vis_row, end_vis_col = self._logical_to_visual(last_row, last_col)
                    # Calculate movement from current cursor position to end
                    current_vis_row = getattr(self, '_last_render_row', 0)
                    row_delta = end_vis_row - current_vis_row
                    if row_delta > 0:   sys.stdout.write(f"\x1b[{row_delta}B")  # Move down
                    elif row_delta < 0: sys.stdout.write(f"\x1b[{-row_delta}A") # Move up
                    sys.stdout.write(f"\r\x1b[{end_vis_col}C")
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    return result

                elif key.type == KeyType.INTERRUPT:
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    return ""

                elif key.type == KeyType.UNKNOWN: continue

                self._dispatch(key)
                self._render()

        finally: self._disable_raw_mode()

    def _enable_raw_mode(self):
        fd = sys.stdin.fileno()
        self._orig_termios = termios.tcgetattr(fd)
        tty.setraw(fd, termios.TCSANOW)

    def _disable_raw_mode(self):
        if self._orig_termios:
            fd = sys.stdin.fileno()
            termios.tcsetattr(fd, termios.TCSADRAIN, self._orig_termios)
            self._orig_termios = None

    def _update_terminal_size(self):
        try:
            size = shutil.get_terminal_size()
            self._term_width = size.columns
            self._term_height = size.lines
        
        # Keep defaults as fallback
        except Exception: pass

    def _wrap_line_at_words(self, line: str, avail_width: int) -> list[tuple[int, str]]:
        # Word-wrap a line at available width.
        if not line: return [(0, "")]

        segments = []
        start = 0
        line_len = len(line)

        while start < line_len:
            # Calculate end position for this segment
            end = start + avail_width

            if end >= line_len:
                # Remaining text fits, use it all
                segments.append((start, line[start:]))
                break

            # Look for last space in the segment [start:end]
            # We want to find a space such that everything after it goes to next line
            search_pos = end - 1  # Last character that could fit
            break_pos = -1        # Position of space where we should break (exclusive)

            while search_pos >= start:
                if line[search_pos] == ' ':
                    break_pos = search_pos
                    break
                search_pos -= 1

            if break_pos == -1:
                # No space found - word is longer than line width
                # Force-break at avail_width
                segments.append((start, line[start:end]))
                start = end
            
            else:
                # Found a space - wrap before it (don't include trailing spaces)
                segments.append((start, line[start:break_pos]))
                # Skip any spaces for the next segment
                start = break_pos + 1
                while start < line_len and line[start] == ' ': start += 1

        return segments

    def _compute_wrapped_view(self) -> list[tuple[int, int, str]]:
        # Computes wrapped view of buffer for current terminal width.
        view = []
        for log_row, line in enumerate(self.buffer):
            if log_row == 0:
                # First line: prompt reduces available width
                avail_width = self._term_width - self._prompt_width
                if avail_width < 1: avail_width = 1
            
            # Continuation lines: indent by prompt_width, so reduce available width
            else: avail_width = self._term_width - self._prompt_width

            # Word-wrap this line, tracking character positions
            wrapped_segments = self._wrap_line_at_words(line, avail_width)
            for start_col, text in wrapped_segments: view.append((log_row, start_col, text))

        return view

    def _logical_to_visual(self, log_row: int, log_col: int) -> tuple[int, int]:
        # Maps logical coordinates to visual (screen) coordinates.
        view = self._wrapped_view
        vis_row = 0

        # Find which visual row contains this logical position
        for vrow, (v_log_row, start_col, text) in enumerate(view):
            if v_log_row == log_row:
                if log_col >= start_col and log_col <= start_col + len(text):
                    vis_row = vrow
                    vis_col = log_col - start_col
                    # All visual lines are indented by prompt_width for alignment
                    vis_col += self._prompt_width
                    return (vis_row, vis_col)

        # Fallback: end of view
        if view:
            last = view[-1]
            vis_row = len(view) - 1
            vis_col = self._prompt_width + len(last[2])
            return (vis_row, vis_col)
        
        return (0, self._prompt_width)

    def _visual_to_logical(self, vis_row: int, vis_col: int) -> tuple[int, int]:
        # Maps visual (screen) coordinates to logical coordinates.
        if not self._wrapped_view: return (0, 0)

        if vis_row < 0:                        vis_row = 0
        if vis_row >= len(self._wrapped_view): vis_row = len(self._wrapped_view) - 1

        log_row, start_col, text = self._wrapped_view[vis_row]

        # All visual lines are indented by prompt_width
        vis_col -= self._prompt_width
        if vis_col < 0: vis_col = 0
        log_col = start_col + vis_col

        # Clamp to line length
        if log_row < len(self.buffer): log_col = min(log_col, len(self.buffer[log_row]))

        return (log_row, log_col)

    def _read_key(self) -> Key:
        c = sys.stdin.read(1)
        if not c: return Key(KeyType.UNKNOWN)
        if ord(c) == 4: return Key(KeyType.SUBMIT)                         # Ctrl+D (EOF)
        if ord(c) == 3: return Key(KeyType.INTERRUPT)                      # Ctrl+C
        if c in ('\r', '\n'): return Key(KeyType.ENTER)                    # Enter (Ctrl+M or Ctrl+J)
        if c == '\t': return Key(KeyType.TAB)                              # Tab
        if c in ('\x08', '\x7f'): return Key(KeyType.BACKSPACE)            # Backspace (Ctrl+H or DEL character)
        if c == '\x1b': return self._read_escape_sequence()                # Escape sequences (arrow keys, etc.)
        if ord(c) == 10 and self._orig_termios: return Key(KeyType.SUBMIT) # Ctrl+Enter (Ctrl+J when already in raw mode is \x0a)
        if ord(c) == 1: return Key(KeyType.HOME_FULL)                      # Ctrl+A
        if ord(c) == 5: return Key(KeyType.END_FULL)                       # Ctrl+E
        if ord(c) == 11: return Key(KeyType.CLEAR_BUFFER)                  # Ctrl+K
        if ord(c) == 21: return Key(KeyType.KILL_LINE_START)               # Ctrl+U
        if ord(c) == 23: return Key(KeyType.KILL_WORD_PREV)                # Ctrl+W
        if ord(c) == 25: return Key(KeyType.YANK)                          # Ctrl+Y
        if ord(c) == 20: return Key(KeyType.TRANSPOSE)                     # Ctrl+T
        if ord(c) == 12: return Key(KeyType.REFRESH)                       # Ctrl+L
        return Key.from_char(c) # Regular characters

    def _read_escape_sequence(self) -> Key:
        c1 = sys.stdin.read(1)
        
        # Alt+Enter (escape followed by \r or \n)
        if c1 in ('\r', '\n'): return Key(KeyType.SUBMIT)
        
        if c1 == '[':
            c2 = sys.stdin.read(1)
            if c2 == 'A': return Key(KeyType.UP)
            elif c2 == 'B': return Key(KeyType.DOWN)
            elif c2 == 'C': return Key(KeyType.RIGHT)
            elif c2 == 'D': return Key(KeyType.LEFT)
            elif c2 == 'H': return Key(KeyType.HOME)
            elif c2 == 'F': return Key(KeyType.END)

            elif c2 == '3':
                if sys.stdin.read(1) == '~': return Key(KeyType.DELETE)
                return Key(KeyType.UNKNOWN)

            elif c2.isdigit():
                c3 = sys.stdin.read(1)
                if c3 == '~':
                    if c2 == '1': return Key(KeyType.HOME)
                    elif c2 == '4': return Key(KeyType.END)
                    elif c2 == '3': return Key(KeyType.DELETE)
                return Key(KeyType.UNKNOWN)

        elif c1 == 'O':
            c2 = sys.stdin.read(1)
            if not c2: return Key(KeyType.UNKNOWN)
            if c2 == 'H': return Key(KeyType.HOME)
            elif c2 == 'F': return Key(KeyType.END)

        return Key(KeyType.UNKNOWN)

    def _dispatch(self, key: Key):
        handlers: dict[KeyType, Callable[[], None]] = { KeyType.CHAR: lambda: self._insert_char(key.char),
                                                        KeyType.ENTER: self._split_line,
                                                        KeyType.BACKSPACE: self._backspace,
                                                        KeyType.DELETE: self._delete,
                                                        KeyType.LEFT: self._cursor_left,
                                                        KeyType.RIGHT: self._cursor_right,
                                                        KeyType.UP: self._cursor_up,
                                                        KeyType.DOWN: self._cursor_down,
                                                        KeyType.HOME: self._cursor_home,
                                                        KeyType.END: self._cursor_end,
                                                        KeyType.HOME_FULL: self._cursor_home_total,
                                                        KeyType.END_FULL: self._cursor_end_total,
                                                        KeyType.CLEAR_BUFFER: self._clear_input,
                                                        KeyType.KILL_LINE_START: self._kill_line_start,
                                                        KeyType.KILL_WORD_PREV: self._kill_word_prev,
                                                        KeyType.YANK: self._yank,
                                                        KeyType.TRANSPOSE: self._transpose_chars,
                                                        KeyType.REFRESH: self._refresh_screen,
                                                        KeyType.TAB: lambda: self._insert_char("    ") }
        handler = handlers.get(key.type)
        if handler: handler()

    def _render(self):
        # Update terminal size and compute wrapped view
        self._update_terminal_size()
        self._wrapped_view = self._compute_wrapped_view()

        # Move cursor to first line (where we left it after last render)
        last_row = getattr(self, '_last_render_row', 0)
        if last_row > 0: sys.stdout.write(f"\x1b[{last_row}A")

        # Move to start of line
        sys.stdout.write("\r")

        # Track which logical rows we've seen to identify first segment of each
        seen_logical_rows = set()

        # Draw each visual line from wrapped view
        for i, (log_row, start_col, text) in enumerate(self._wrapped_view):
            if i > 0: sys.stdout.write("\r\n")

            # Clear to end of line before drawing
            sys.stdout.write("\x1b[K")

            # Only show prompt on the first visual segment of logical line 0
            is_first_segment_of_line = log_row not in seen_logical_rows
            seen_logical_rows.add(log_row)

            if log_row == 0 and is_first_segment_of_line: sys.stdout.write(self.prompt)
            else:                                         sys.stdout.write(" " * self._prompt_width)
            
            sys.stdout.write(text)

        # Clear any remaining lines from previous render
        sys.stdout.write("\x1b[J")

        # Calculate visual position of cursor
        vis_row, vis_col = self._logical_to_visual(self.cursor_row, self.cursor_col)

        # Position cursor: move up from last line to target row
        lines_up = len(self._wrapped_view) - vis_row - 1
        if lines_up > 0: sys.stdout.write(f"\x1b[{lines_up}A")

        # Move to correct column
        sys.stdout.write(f"\r\x1b[{vis_col}C")
        sys.stdout.flush()

        # Remember where we left the cursor for next render
        self._last_render_row = vis_row

    #######################
    # Buffer manipulation #
    #######################

    def _insert_char(self, char: str):
        # Insert a character at cursor position
        line = self.buffer[self.cursor_row]
        self.buffer[self.cursor_row] = line[:self.cursor_col] + char + line[self.cursor_col:]
        self.cursor_col += 1
        # Recompute wrapped view and update visual column tracking
        self._wrapped_view = self._compute_wrapped_view()
        _, self._visual_col = self._logical_to_visual(self.cursor_row, self.cursor_col)

    def _split_line(self):
        # Split current line at cursor position
        line = self.buffer[self.cursor_row]
        new_line = line[self.cursor_col:]
        self.buffer[self.cursor_row] = line[:self.cursor_col]
        self.cursor_row += 1
        self.cursor_col = 0
        self.buffer.insert(self.cursor_row, new_line)
        
        # Recompute wrapped view and update visual column tracking
        self._wrapped_view = self._compute_wrapped_view()
        _, self._visual_col = self._logical_to_visual(self.cursor_row, self.cursor_col)

    def _backspace(self):
        # Delete character before cursor, or join with previous line
        if self.cursor_col > 0:
            line = self.buffer[self.cursor_row]
            self.buffer[self.cursor_row] = line[:self.cursor_col - 1] + line[self.cursor_col:]
            self.cursor_col -= 1
        
        # Join with previous line
        elif self.cursor_row > 0:
            prev_line = self.buffer[self.cursor_row - 1]
            curr_line = self.buffer[self.cursor_row]
            self.cursor_col = len(prev_line)
            self.buffer[self.cursor_row - 1] = prev_line + curr_line
            del self.buffer[self.cursor_row]
            self.cursor_row -= 1
        
        # Recompute wrapped view and update visual column tracking
        self._wrapped_view = self._compute_wrapped_view()
        _, self._visual_col = self._logical_to_visual(self.cursor_row, self.cursor_col)

    def _delete(self):
        # Delete character at cursor position, or join with next line
        line = self.buffer[self.cursor_row]
        if self.cursor_col < len(line): self.buffer[self.cursor_row] = line[:self.cursor_col] + line[self.cursor_col + 1:]
        
        # Join with next line
        elif self.cursor_row < len(self.buffer) - 1:
            next_line = self.buffer[self.cursor_row + 1]
            self.buffer[self.cursor_row] = line + next_line
            del self.buffer[self.cursor_row + 1]
        
        # Recompute wrapped view and update visual column tracking
        self._wrapped_view = self._compute_wrapped_view()
        _, self._visual_col = self._logical_to_visual(self.cursor_row, self.cursor_col)

    ###################
    # Cursor movement #
    ###################

    def _cursor_left(self):
        if self.cursor_col > 0: self.cursor_col -= 1
        elif self.cursor_row > 0:
            self.cursor_row -= 1
            self.cursor_col = len(self.buffer[self.cursor_row])
        # Update visual column tracking for up/down movement
        # Ensure wrapped view is current
        if not self._wrapped_view: self._wrapped_view = self._compute_wrapped_view()
        _, self._visual_col = self._logical_to_visual(self.cursor_row, self.cursor_col)

    def _cursor_right(self):
        line = self.buffer[self.cursor_row]
        if self.cursor_col < len(line): self.cursor_col += 1
        elif self.cursor_row < len(self.buffer) - 1:
            self.cursor_row += 1
            self.cursor_col = 0
        # Update visual column tracking for up/down movement
        # Ensure wrapped view is current
        if not self._wrapped_view: self._wrapped_view = self._compute_wrapped_view()
        _, self._visual_col = self._logical_to_visual(self.cursor_row, self.cursor_col)

    def _cursor_up(self):
        # Ensure wrapped view is computed
        if not self._wrapped_view:
            self._update_terminal_size()
            self._wrapped_view = self._compute_wrapped_view()

        # Get current visual row
        vis_row, _ = self._logical_to_visual(self.cursor_row, self.cursor_col)
        if vis_row > 0:
            # Move up one visual line, preserving desired visual column
            new_vis_row = vis_row - 1
            # Clamp visual column to what's available on the target line
            if new_vis_row < len(self._wrapped_view):
                _, _, text = self._wrapped_view[new_vis_row]
                target_vis_col = self._visual_col
                # Text spans from prompt_width to prompt_width + len(text)
                min_col = self._prompt_width
                max_col = self._prompt_width + len(text)
                if target_vis_col < min_col: target_vis_col = min_col
                if target_vis_col > max_col: target_vis_col = max_col
                # Convert back to logical
                self.cursor_row, self.cursor_col = self._visual_to_logical(new_vis_row, target_vis_col)
            
            else: self.cursor_row, self.cursor_col = self._visual_to_logical(new_vis_row, self._visual_col)
        
        elif self.cursor_row == 0 and self.cursor_col == 0: self._history_prev()
        elif self.cursor_row == 0 and self.cursor_col > 0: self.cursor_col = 0

    def _cursor_down(self):
        # Ensure wrapped view is computed
        if not self._wrapped_view:
            self._update_terminal_size()
            self._wrapped_view = self._compute_wrapped_view()
        
        # Get current visual row
        vis_row, _ = self._logical_to_visual(self.cursor_row, self.cursor_col)
        if vis_row < len(self._wrapped_view) - 1:
            # Move down one visual line, preserving desired visual column
            new_vis_row = vis_row + 1
            # Clamp visual column to what's available on the target line
            if new_vis_row < len(self._wrapped_view):
                _, _, text = self._wrapped_view[new_vis_row]
                target_vis_col = self._visual_col
                # Text spans from prompt_width to prompt_width + len(text)
                min_col = self._prompt_width
                max_col = self._prompt_width + len(text)
                if target_vis_col < min_col: target_vis_col = min_col
                if target_vis_col > max_col: target_vis_col = max_col
                # Convert back to logical
                self.cursor_row, self.cursor_col = self._visual_to_logical(new_vis_row, target_vis_col)
            else: self.cursor_row, self.cursor_col = self._visual_to_logical(new_vis_row, self._visual_col)
        
        elif self.cursor_row == len(self.buffer) - 1 and self.cursor_col >= len(self.buffer[self.cursor_row]): self._history_next()
        elif self.cursor_row == len(self.buffer) - 1 and self.cursor_col < len(self.buffer[self.cursor_row]): self._cursor_end()

    def _cursor_home(self):
        self.cursor_col = 0
        # Update visual column tracking for up/down movement
        # Ensure wrapped view is current
        if not self._wrapped_view: self._wrapped_view = self._compute_wrapped_view()
        _, self._visual_col = self._logical_to_visual(self.cursor_row, self.cursor_col)

    def _cursor_end(self):
        self.cursor_col = len(self.buffer[self.cursor_row])
        # Update visual column tracking for up/down movement
        # Ensure wrapped view is current
        if not self._wrapped_view: self._wrapped_view = self._compute_wrapped_view()
        _, self._visual_col = self._logical_to_visual(self.cursor_row, self.cursor_col)

    def _cursor_home_total(self):
        self.cursor_row = 0
        self.cursor_col = 0
        # Update wrapped view and visual column tracking
        self._wrapped_view = self._compute_wrapped_view()
        _, self._visual_col = self._logical_to_visual(0, 0)

    def _cursor_end_total(self):
        if not self.buffer:
            return
        self.cursor_row = len(self.buffer) - 1
        self.cursor_col = len(self.buffer[-1])
        # Update wrapped view and visual column tracking
        self._wrapped_view = self._compute_wrapped_view()
        _, self._visual_col = self._logical_to_visual(self.cursor_row, self.cursor_col)

    def _clear_input(self):
        self.buffer = [""]
        self.cursor_row = 0
        self.cursor_col = 0
        # Update wrapped view and visual column tracking
        self._wrapped_view = self._compute_wrapped_view()
        _, self._visual_col = self._logical_to_visual(0, 0)

    ########################
    # Kill ring operations #
    ########################

    def _kill_line_start(self):
        """Kill text from cursor to start of current line."""
        killed = self.buffer[self.cursor_row][:self.cursor_col]
        self.buffer[self.cursor_row] = self.buffer[self.cursor_row][self.cursor_col:]
        self.cursor_col = 0
        if killed:  # Only add non-empty kills to ring
            self._kill_ring.append(killed)
            self._kill_index = len(self._kill_ring) - 1  # Fix: use 0-based index
        self._wrapped_view = self._compute_wrapped_view()
        _, self._visual_col = self._logical_to_visual(self.cursor_row, self.cursor_col)

    def _kill_word_prev(self):
        """Kill text from cursor back to previous word boundary."""
        line = self.buffer[self.cursor_row]
        if self.cursor_col == 0:
            return

        # Find word boundary before cursor
        i = self.cursor_col - 1
        while i >= 0 and not line[i].isalnum():
            i -= 1
        while i >= 0 and line[i].isalnum():
            i -= 1

        killed = line[i+1:self.cursor_col]
        self.buffer[self.cursor_row] = line[:i+1] + line[self.cursor_col:]
        self.cursor_col = i + 1
        if killed:  # Only add non-empty kills to ring
            self._kill_ring.append(killed)
            self._kill_index = len(self._kill_ring) - 1  # Fix: use 0-based index
        self._wrapped_view = self._compute_wrapped_view()
        _, self._visual_col = self._logical_to_visual(self.cursor_row, self.cursor_col)

    def _yank(self):
        """Yank text from kill ring at cursor position."""
        # Validate kill index is within bounds
        if 0 <= self._kill_index < len(self._kill_ring):
            killed_text = self._kill_ring[self._kill_index]
            for c in killed_text:
                self._insert_char(c)

    def _transpose_chars(self):
        """Transpose character before cursor with character at cursor."""
        line = self.buffer[self.cursor_row]
        if self.cursor_col > 0 and self.cursor_col < len(line):
            # Swap characters at cursor_col-1 and cursor_col
            self.buffer[self.cursor_row] = line[:self.cursor_col-1] + line[self.cursor_col] + line[self.cursor_col-1] + line[self.cursor_col+1:]
            self.cursor_col += 1
            self._wrapped_view = self._compute_wrapped_view()
            _, self._visual_col = self._logical_to_visual(self.cursor_row, self.cursor_col)

    def _refresh_screen(self):
        """Clear screen and re-render editor content."""
        sys.stdout.write("\x1b[H\x1b[2J")  # Clear screen and move cursor to origin
        self._render()

    ######################
    # History management #
    ######################

    def _save_current_buffer(self):
        self._saved_buffer = self.buffer.copy()
        self._saved_row = self.cursor_row
        self._saved_col = self.cursor_col

    def _restore_saved_buffer(self):
        if self._saved_buffer is not None:
            self.buffer = self._saved_buffer
            self.cursor_row = self._saved_row
            self.cursor_col = self._saved_col
            self._saved_buffer = None
            # Recompute wrapped view for restored buffer
            self._update_terminal_size()
            self._wrapped_view = self._compute_wrapped_view()
            # Update visual column tracking for up/down movement
            _, self._visual_col = self._logical_to_visual(self.cursor_row, self.cursor_col)

    def _load_history_entry(self, entry: str):
        if '\n' in entry: self.buffer = entry.split('\n')
        else: self.buffer = [entry]
        self.cursor_row = len(self.buffer) - 1
        self.cursor_col = len(self.buffer[-1])
        # Recompute wrapped view for loaded entry
        self._update_terminal_size()
        self._wrapped_view = self._compute_wrapped_view()
        # Update visual column tracking for up/down movement
        _, self._visual_col = self._logical_to_visual(self.cursor_row, self.cursor_col)

    def _history_prev(self):
        if self.history_index == len(self.history): self._save_current_buffer()
        if self.history_index > 0:
            self.history_index -= 1
            self._load_history_entry(self.history[self.history_index])

    def _history_next(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self._load_history_entry(self.history[self.history_index])
        elif self.history_index == len(self.history) - 1:
            # At end of history, restore saved buffer
            self.history_index = len(self.history)
            self._restore_saved_buffer()

    def _add_to_history(self, entry: str):
        if not entry.strip(): return

        # Don't add duplicates of the most recent entry
        if self.history and self.history[-1] == entry: return

        self.history.append(entry)
        if len(self.history) > self.HISTORY_LIMIT: self.history = self.history[-self.HISTORY_LIMIT:]

        self._save_history()

    def _load_history(self):
        if not self.history_file or not self.history_file.exists(): return

        try:
            text = self.history_file.read_text(encoding='utf-8')
            # Split by null byte to handle multiline entries
            self.history = [entry for entry in text.split('\x00') if entry]
        
        except Exception: self.history = []

    def _save_history(self):
        if not self.history_file: return

        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            # Join with null byte to preserve multiline entries
            text = '\x00'.join(self.history)
            self.history_file.write_text(text, encoding='utf-8')

        # History persistence is best-effort
        except Exception: pass


def main():
    editor = InlineEditor(history_file=None)

    print("Inline Editor Test")
    print("==================")
    print("Type your text below.")
    print("- Arrow keys: move cursor")
    print("- Enter: insert new line")
    print("- Backspace/Delete: remove characters")
    print("- Ctrl+A: move to beginning of total input")
    print("- Ctrl+E: move to end of total input")
    print("- Ctrl+K: clear all current input")
    print("- Ctrl+U: kill to start of line")
    print("- Ctrl+W: kill previous word")
    print("- Ctrl+Y: yank from kill ring")
    print("- Ctrl+T: transpose characters")
    print("- Ctrl+L: clear and redraw screen")
    print("- Ctrl+D: submit and display result")
    print("- Ctrl+C: cancel\n")
    
    try:
        result = editor.read("edit> ")
        print("\n" + "=" * 40)
        print("RECEIVED TEXT:")
        print("=" * 40)
        print(result)
        print("=" * 40)
        print(f"Total length: {len(result)} characters")
        print(f"Total lines: {result.count(chr(10)) + 1 if result else 0}")
        
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        sys.exit(1)

if __name__ == "__main__": main()