# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

import re
import shutil
from typing import Optional, TextIO

from lc.vendor import wcwidth
def display_width(text: str) -> int:
    # wcswidth returns -1 for non-printable strings,
    # fallback to len in this case
    w = wcwidth.wcswidth(text)
    return w if w is not None and w >= 0 else len(text)

class MarkdownFormatter:
    # ANSI escape sequences
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    STRIKETHROUGH = "\033[9m"
    
    # Subtle colors for code blocks
    CODE_FG = "\033[38;5;250m"      # Light gray for code text
    CODE_BG = "\033[48;5;238m"      # Dark gray background (inline only)
    
    # Box drawing elements
    BLOCK_TOP = "╭"
    BLOCK_MID = "│"
    BLOCK_BOT = "╰"
    RULE_CHAR = "─"
    
    # Indent for code block content
    BLOCK_INDENT = "  "
    
    # Regex patterns for markdown elements
    HEADER_RE = re.compile(r'^(#{1,6})\s+(.+)$')
    CODE_FENCE_RE = re.compile(r'^(\s*)```(.*)$')
    HORIZONTAL_RULE_RE = re.compile(r'^(\s*)(---+|===+|\*\*\*+|___+)\s*$')
    UNORDERED_LIST_RE = re.compile(r'^(\s*)([-*+])\s+(.+)$')
    
    # Inline patterns (processed in order of specificity)
    INLINE_CODE_RE = re.compile(r'`([^`]+)`')
    BOLD_RE = re.compile(r'\*\*(.+?)\*\*|__(.+?)__')
    ITALIC_RE = re.compile(r'\*(.+?)\*|_(.+?)_')
    STRIKE_RE = re.compile(r'~~(.+?)~~')
    
    # ANSI escape sequence pattern (for stripping when calculating width)
    ANSI_ESCAPE_RE = re.compile(r'\x1b\[[0-9;]*m')
    
    def __init__(self): pass
    
    def strip_ansi(self, text: str) -> str: return self.ANSI_ESCAPE_RE.sub('', text)
    
    def visible_width(self, text: str) -> int: return display_width(self.strip_ansi(text))
    
    def format_line(self, line: str, mode: str = "normal", indent: str = "") -> str:
        if mode == "codeblock": return self._format_codeblock_line(line, indent)
        
        # Check for horizontal rule first
        if self.HORIZONTAL_RULE_RE.match(line): return self._format_horizontal_rule()
        
        # Check for header
        header_match = self.HEADER_RE.match(line)
        if header_match: return self._format_header(header_match)
        
        # Check for unordered list
        list_match = self.UNORDERED_LIST_RE.match(line)
        if list_match: return self._format_list_item(list_match)
        
        # Apply inline formatting
        line = self._format_inline(line)
        
        return line
    
    def _format_inline(self, text: str) -> str:
        # Order matters: code first (no nesting), then bold, then italic
        text = self.INLINE_CODE_RE.sub(self._inline_code_sub, text)
        text = self.BOLD_RE.sub(self._bold_sub, text)
        text = self.ITALIC_RE.sub(self._italic_sub, text)
        text = self.STRIKE_RE.sub(self._strike_sub, text)
        return text
    
    def _inline_code_sub(self, match: re.Match) -> str:
        content = match.group(1)
        return f"{self.CODE_BG}{self.CODE_FG}{content}{self.RESET}"
    
    def _bold_sub(self, match: re.Match) -> str:
        content = match.group(1) or match.group(2)
        return f"{self.BOLD}{content}{self.RESET}"
    
    def _italic_sub(self, match: re.Match) -> str:
        content = match.group(1) or match.group(2)
        return f"{self.ITALIC}{content}{self.RESET}"
    
    def _strike_sub(self, match: re.Match) -> str:
        content = match.group(1)
        return f"{self.STRIKETHROUGH}{content}{self.RESET}"
    
    def _format_header(self, match: re.Match) -> str:
        hashes = match.group(1)
        content = match.group(2)
        level = len(hashes)
        
        if level == 1:   return f"{self.BOLD}{self.UNDERLINE}{content}{self.RESET}"
        elif level == 2: return f"{self.BOLD}{content}{self.RESET}"
        else:            return f"{self.BOLD}{self.DIM}{content}{self.RESET}"
    
    def _format_list_item(self, match: re.Match) -> str:
        indent = match.group(1)
        bullet = match.group(2)
        content = match.group(3)
        
        content = self._format_inline(content)        
        return f"{indent}{self.DIM}•{self.RESET} {content}"
    
    def _format_horizontal_rule(self) -> str:
        full_width = self._get_terminal_width()
        margin = 10; padding = " " * (margin//2)
        rule = self.RULE_CHAR * (full_width-margin)
        return f"{self.DIM}{padding}{rule}{self.RESET}"
    
    def _format_codeblock_line(self, line: str, fence_indent: str, simple: bool = True) -> str:
        if simple: return f"{self.DIM}{self.CODE_FG}{line}{self.RESET}"
        else:
            # Remove the fence indent from the line content if present
            if line.startswith(fence_indent): content = line[len(fence_indent):]
            else:                             content = line
            
            # Apply code styling: dim + left margin indicator
            return f"{self.BLOCK_INDENT}{self.DIM}{self.BLOCK_MID}{self.RESET} {self.DIM}{self.CODE_FG}{content}{self.RESET}"
    
    def _get_terminal_width(self) -> int:
        try:
            size = shutil.get_terminal_size()
            return max(size.columns, 4)
        
        except Exception: return 80  # Default fallback
    
    def format_codeblock_start(self, simple: bool = True) -> str:
        if simple:
            border = self.RULE_CHAR * self._get_terminal_width()
            return f"{self.DIM}{border}{self.RESET}"
        else:
            # Fixed width for the border
            border = self.RULE_CHAR * 58
            return f"{self.BLOCK_INDENT}{self.DIM}{self.BLOCK_TOP}{border}{self.RESET}"
        
    def format_codeblock_end(self, simple: bool = True) -> str:
        if simple:
            border = self.RULE_CHAR * self._get_terminal_width()
            return f"{self.DIM}{border}{self.RESET}"
        else:
            border = self.RULE_CHAR * 58
            return f"{self.BLOCK_INDENT}{self.DIM}{self.BLOCK_BOT}{border}{self.RESET}"
    
    def detect_code_fence(self, line: str) -> tuple[bool, str]:
        match = self.CODE_FENCE_RE.match(line)
        if match: return True, match.group(1)
        return False, ""
    
    def format_block(self, text: str) -> str:
        lines = text.split('\n')
        result_lines = []
        in_code_block = False
        code_indent = ""
        
        for line in lines:
            is_fence, fence_indent = self.detect_code_fence(line)
            
            if is_fence:
                if not in_code_block:
                    # Starting code block
                    in_code_block = True
                    code_indent = fence_indent
                    result_lines.append(self.format_codeblock_start())
                else:
                    # Ending code block
                    result_lines.append(self.format_codeblock_end())
                    in_code_block = False
                    code_indent = ""
            else:
                formatted = self.format_line(line, mode="codeblock" if in_code_block else "normal", indent=code_indent)
                result_lines.append(formatted)
        
        # Handle unclosed code block
        if in_code_block: result_lines.append(self.format_codeblock_end())
        
        return '\n'.join(result_lines)


class StreamingMarkdownRenderer:
    CLEAR_LINE = "\x1b[2K"          # Erase entire line
    CURSOR_UP = "\x1b[{}A"          # CUU - Cursor Up N lines
    CLEAR_TO_END = "\x1b[J"         # ED0 - Erase from cursor to end of screen
    
    def __init__(self, formatter: MarkdownFormatter, stream: TextIO):
        self.formatter = formatter
        self.stream = stream
        self.line_buffer = ""
        self.in_code_block = False
        self.code_fence_indent = ""
        
        self._term_width = self._get_terminal_width()
        self._provisional_width = 0       # Display columns of provisional output
        self._provisional_active = False  # Whether provisional output is on screen
    
    def _get_terminal_width(self) -> int:
        try:
            size = shutil.get_terminal_size()
            return max(size.columns, 4)
        
        except Exception: return 80  # Default fallback
    
    def _update_term_width(self) -> None:
        self._term_width = self._get_terminal_width()
    
    def ingest(self, chunk: str) -> None:
        while chunk:
            if '\n' in chunk:
                # Split at first newline
                pre, _, post = chunk.partition('\n')
                self.line_buffer += pre
                self._flush_line()
                chunk = post

            else:
                # No newline - buffer and output provisionally
                self.line_buffer += chunk
                if chunk:
                    self._write_provisional(chunk)
                break
    
    def _write_provisional(self, text: str) -> None:
        # Update terminal width before significant operations
        if not self._provisional_active: self._update_term_width()
        
        self.stream.write(text)
        self.stream.flush()
        
        # Track display width (excluding any ANSI that might be in text)
        self._provisional_width += display_width(text)
        self._provisional_active = True
    
    def _flush_line(self) -> None:
        line = self.line_buffer
        self.line_buffer = ""
        
        # Check for code fence
        is_fence, fence_indent = self.formatter.detect_code_fence(line)
        
        if is_fence:
            if not self.in_code_block:
                # Starting code block
                self.in_code_block = True
                self.code_fence_indent = fence_indent
                self._clear_provisional()
                self._write_formatted(self.formatter.format_codeblock_start())
            else:
                # Ending code block
                self._clear_provisional()
                self._write_formatted(self.formatter.format_codeblock_end())
                self.in_code_block = False
                self.code_fence_indent = ""
        else:
            # Regular line - clear provisional and rewrite formatted
            self._clear_provisional()
            
            formatted = self.formatter.format_line(line, mode="codeblock" if self.in_code_block else "normal", indent=self.code_fence_indent)
            self._write_formatted(formatted)
        
        # Always emit newline after formatted line
        self.stream.write('\n')
        self.stream.flush()
    
    def _clear_provisional(self) -> None:
        if not self._provisional_active: return
        
        # Calculate how many terminal lines the provisional output occupies
        # We subtract 1 from width because a line that exactly fills term_width
        # columns will have wrapped to the next line
        if self._provisional_width == 0: lines_up = 0
        else:
            # Integer division: (width - 1) // term_width gives 0 for single line
            lines_up = (self._provisional_width - 1) // self._term_width
        
        # Move cursor up to the start of provisional output
        if lines_up > 0: self.stream.write(self.CURSOR_UP.format(lines_up))
        
        # Carriage return to start of line, then clear to end
        self.stream.write('\r' + self.CLEAR_TO_END)
        self.stream.flush()
        
        # Reset tracking
        self._provisional_width = 0
        self._provisional_active = False
    
    def _write_formatted(self, text: str) -> None:
        self.stream.write(text)
        self.stream.flush()
    
    def finalize(self) -> None:
        # Flush remaining content as final line
        if self.line_buffer: self._flush_line()
        
        # Close any unclosed code block
        if self.in_code_block:
            self._write_formatted(self.formatter.format_codeblock_end())
            self.stream.write('\n')
            self.stream.flush()
            self.in_code_block = False
    
    def reset(self) -> None:
        self.line_buffer = ""
        self.in_code_block = False
        self.code_fence_indent = ""
        self._provisional_width = 0
        self._provisional_active = False
