# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

import re
import shutil
from typing import Optional, TextIO, List, Tuple

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
    
    # Table box drawing
    TABLE_H = "─"
    TABLE_V = "│"
    TABLE_TL = "┌"
    TABLE_TR = "┐"
    TABLE_BL = "└"
    TABLE_BR = "┘"
    TABLE_ML = "├"
    TABLE_MR = "┤"
    TABLE_TM = "┬"
    TABLE_BM = "┴"
    TABLE_MM = "┼"
    
    # Indent for code block content
    BLOCK_INDENT = "  "
    
    # Regex patterns for markdown elements
    HEADER_RE = re.compile(r'^(#{1,6})\s+(.+)$')
    CODE_FENCE_RE = re.compile(r'^(\s*)```(.*)$')
    HORIZONTAL_RULE_RE = re.compile(r'^(\s*)(---+|===+|\*\*\*+|___+)\s*$')
    UNORDERED_LIST_RE = re.compile(r'^(\s*)([-*+])\s+(.+)$')
    
    # Table patterns
    TABLE_ROW_RE = re.compile(r'^\s*\|?(.+?)\|?\s*$')
    TABLE_SEP_RE = re.compile(r'^\s*\|?(?:\s*:?-+:?\s*\|)+\s*$')
    
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
    
    # Table methods
    
    def is_table_row(self, line: str) -> bool:
        """Check if line looks like a table row (contains pipes)."""
        if '|' not in line: return False
        match = self.TABLE_ROW_RE.match(line)
        if match is None: return False
        # Either has internal pipes OR has outer pipes (single column)
        content = match.group(1)
        return '|' in content or line.strip().startswith('|')
    
    def is_table_separator(self, line: str) -> bool:
        """Check if line is a table separator row (---, :---, :---:)."""
        if '|' not in line: return False
        match = self.TABLE_SEP_RE.match(line)
        return match is not None
    
    def parse_table_row(self, line: str) -> List[str]:
        """Parse a table row into cells. Handles outer pipes optionally."""
        # Extract content between optional outer pipes
        line = line.strip()
        if line.startswith('|'): line = line[1:]
        if line.endswith('|'): line = line[:-1]
        
        # Split by pipe, handle escaped pipes
        cells = []
        current = ""
        escaped = False
        for char in line:
            if escaped:
                current += char
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '|':
                cells.append(current.strip())
                current = ""
            else:
                current += char
        cells.append(current.strip())
        return cells
    
    def parse_table_alignments(self, line: str) -> List[str]:
        """Parse separator row to extract column alignments."""
        cells = self.parse_table_row(line)
        alignments = []
        for cell in cells:
            cell = cell.strip()
            if cell.startswith(':') and cell.endswith(':'): alignments.append('center')
            elif cell.endswith(':'): alignments.append('right')
            else: alignments.append('left')
        return alignments
    
    def _truncate_cell(self, text: str, width: int) -> str:
        """Truncate text to fit within width, accounting for ANSI codes."""
        if self.visible_width(text) <= width: return text
        
        # Need to truncate - find byte position without breaking ANSI
        stripped = self.strip_ansi(text)
        if len(stripped) <= width - 1: return text  # Shouldn't happen but safety check
        
        # Truncate stripped text and add ellipsis
        truncated = stripped[:width - 1] + "…"
        return truncated
    
    def _pad_cell(self, text: str, width: int, align: str) -> str:
        """Pad or truncate cell content to exact width."""
        text = self._truncate_cell(text, width)
        text_width = self.visible_width(text)
        padding = width - text_width
        
        if align == 'right': return " " * padding + text
        elif align == 'center':
            left = padding // 2
            right = padding - left
            return " " * left + text + " " * right
        else:  # left
            return text + " " * padding
    
    def format_table(self, rows: List[str]) -> List[str]:
        """
        Format a complete table. rows includes header and separator.
        Returns list of formatted lines.
        """
        if len(rows) < 2: return rows  # Not enough for a table
        
        # Parse header and separator
        header_cells = self.parse_table_row(rows[0])
        alignments = self.parse_table_alignments(rows[1])
        
        # Ensure alignment count matches header cells
        while len(alignments) < len(header_cells): alignments.append('left')
        alignments = alignments[:len(header_cells)]
        
        # Parse data rows
        data_rows = []
        for i in range(2, len(rows)):
            cells = self.parse_table_row(rows[i])
            # Ensure cell count matches header
            while len(cells) < len(header_cells): cells.append("")
            cells = cells[:len(header_cells)]
            data_rows.append(cells)
        
        # Calculate column widths based on content
        num_cols = len(header_cells)
        col_widths = [0] * num_cols
        
        all_rows = [header_cells] + data_rows
        for row in all_rows:
            for i, cell in enumerate(row):
                # Format cell content for width calculation (apply inline formatting)
                formatted = self._format_inline(cell)
                width = self.visible_width(formatted)
                col_widths[i] = max(col_widths[i], width)
        
        # Apply minimum width and calculate total
        min_col_width = 3
        col_widths = [max(w, min_col_width) for w in col_widths]
        
        # Check terminal width constraint
        term_width = self._get_terminal_width()
        # Total = sum of columns + 3 chars per column (space + 2 borders) + 1 for final border
        total_inner = sum(col_widths)
        total_width = total_inner + (num_cols * 3) + 1
        
        if total_width > term_width:
            # Need to truncate - reduce widest columns proportionally
            excess = total_width - term_width
            # Sort columns by width descending
            indexed_widths = [(i, w) for i, w in enumerate(col_widths)]
            indexed_widths.sort(key=lambda x: -x[1])
            
            for i, w in indexed_widths:
                if excess <= 0: break
                reduction = min(excess, w - min_col_width)
                col_widths[i] -= reduction
                excess -= reduction
        
        # Build formatted table
        result = []
        
        # Top border
        border = self.TABLE_TL
        for i, w in enumerate(col_widths):
            border += self.TABLE_H * (w + 2)
            if i < len(col_widths) - 1: border += self.TABLE_TM
            else: border += self.TABLE_TR
        result.append(f"{self.DIM}{border}{self.RESET}")
        
        # Header row
        header_line = self.TABLE_V
        for i, cell in enumerate(header_cells):
            formatted = self._format_inline(cell)
            padded = self._pad_cell(formatted, col_widths[i], 'left')
            header_line += f" {padded} {self.DIM}{self.TABLE_V}{self.RESET}"
        result.append(header_line)
        
        # Separator row
        sep_line = self.DIM + self.TABLE_ML
        for i, w in enumerate(col_widths):
            # w is the content width, we have 2 padding spaces (1 on each side)
            # so total cell width is w + 2
            cell_width = w + 2
            if alignments[i] == 'center':
                # :<cell_width-2 dashes>:
                sep_line += f":{self.TABLE_H * (cell_width - 2)}:"
            elif alignments[i] == 'right':
                # <cell_width-1 dashes>:
                sep_line += f"{self.TABLE_H * (cell_width - 1)}:"
            else:  # left
                # <cell_width dashes>
                sep_line += self.TABLE_H * cell_width
            
            if i < len(col_widths) - 1:
                sep_line += self.TABLE_MM
            else:
                sep_line += self.TABLE_MR + self.RESET
        result.append(sep_line)
        
        # Data rows
        for row in data_rows:
            row_line = self.TABLE_V
            for i, cell in enumerate(row):
                formatted = self._format_inline(cell)
                padded = self._pad_cell(formatted, col_widths[i], alignments[i])
                row_line += f" {padded} {self.DIM}{self.TABLE_V}{self.RESET}"
            result.append(row_line)
        
        # Bottom border
        border = self.DIM + self.TABLE_BL
        for i, w in enumerate(col_widths):
            border += self.TABLE_H * (w + 2)
            if i < len(col_widths) - 1: border += self.TABLE_BM
            else: border += self.TABLE_BR
        border += self.RESET
        result.append(border)
        
        return result
    
    def format_block(self, text: str) -> str:
        lines = text.split('\n')
        result_lines = []
        in_code_block = False
        code_indent = ""
        table_buffer = []
        in_table = False
        
        def flush_table_buffer():
            """Flush the table buffer, either as formatted table or plain lines."""
            nonlocal result_lines, table_buffer, in_table
            if not table_buffer:
                in_table = False
                return
            
            # Check if we have a valid table (at least header + separator)
            if len(table_buffer) >= 2 and self.is_table_separator(table_buffer[1]):
                result_lines.extend(self.format_table(table_buffer))
            else:
                # Not a real table, just output buffered lines
                for bl in table_buffer:
                    result_lines.append(self.format_line(bl))
            table_buffer = []
            in_table = False
        
        for line in lines:
            is_fence, fence_indent = self.detect_code_fence(line)
            
            if is_fence:
                # Flush any pending table
                flush_table_buffer()
                
                if not in_code_block:
                    in_code_block = True
                    code_indent = fence_indent
                    result_lines.append(self.format_codeblock_start())
                else:
                    result_lines.append(self.format_codeblock_end())
                    in_code_block = False
                    code_indent = ""
            else:
                if in_code_block:
                    formatted = self.format_line(line, mode="codeblock", indent=code_indent)
                    result_lines.append(formatted)
                else:
                    # Check for table
                    if self.is_table_row(line):
                        if not in_table:
                            in_table = True
                            table_buffer = [line]
                        else:
                            table_buffer.append(line)
                    else:
                        if in_table:
                            # Line breaks table - flush buffer
                            flush_table_buffer()
                        
                        formatted = self.format_line(line)
                        result_lines.append(formatted)
        
        # Handle unclosed structures
        if in_table:
            flush_table_buffer()
        
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
        
        # Table state
        self.in_table = False
        self.table_buffer = []
        self.table_row_widths = []  # Display width of each provisional table row
        
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
            # Flush any pending table before code fence
            if self.in_table:
                self._flush_table()
            
            if not self.in_code_block:
                self.in_code_block = True
                self.code_fence_indent = fence_indent
                self._clear_provisional()
                self._write_formatted(self.formatter.format_codeblock_start())
            else:
                self._clear_provisional()
                self._write_formatted(self.formatter.format_codeblock_end())
                self.in_code_block = False
                self.code_fence_indent = ""
            
            self.stream.write('\n')
            self.stream.flush()
            return
        
        if self.in_code_block:
            # Inside code block - format and output
            self._clear_provisional()
            formatted = self.formatter.format_line(line, mode="codeblock", indent=self.code_fence_indent)
            self._write_formatted(formatted)
            self.stream.write('\n')
            self.stream.flush()
            return
        
        # Check for table handling
        if self.formatter.is_table_row(line):
            if not self.in_table:
                # Starting potential table
                self.in_table = True
                self.table_buffer = [line]
                self.table_row_widths = []
                # Output provisionally and track row width
                provisional_line = line + '\n'
                self._write_provisional(provisional_line)
                # Store just the content width (excluding newline which adds 0 physical lines visually)
                self.table_row_widths.append(display_width(line))
            else:
                # Continuing table
                self.table_buffer.append(line)
                provisional_line = line + '\n'
                self._write_provisional(provisional_line)
                self.table_row_widths.append(display_width(line))
        else:
            # Not a table row
            if self.in_table:
                # Check if we have a valid table
                if len(self.table_buffer) >= 2 and self.formatter.is_table_separator(self.table_buffer[1]):
                    self._flush_table()
                else:
                    # Not a real table - just clear provisional and output buffered lines formatted
                    self._clear_provisional()
                    for bl in self.table_buffer:
                        formatted = self.formatter.format_line(bl)
                        self._write_formatted(formatted)
                        self.stream.write('\n')
                        self.stream.flush()
                    self.in_table = False
                    self.table_buffer = []
                    self.table_row_widths = []
                    # Continue to format current line
                    self._clear_provisional()
                    formatted = self.formatter.format_line(line)
                    self._write_formatted(formatted)
                    self.stream.write('\n')
                    self.stream.flush()
            else:
                # Regular line
                self._clear_provisional()
                formatted = self.formatter.format_line(line)
                self._write_formatted(formatted)
                self.stream.write('\n')
                self.stream.flush()
    
    def _flush_table(self) -> None:
        """Clear provisional table lines and output formatted table."""
        if not self.in_table or len(self.table_buffer) < 2:
            return
        
        # Calculate how many physical terminal lines the provisional output occupies
        # Each row: 1 line (hard newline) + wrapped lines from content exceeding term_width
        lines_up = 0
        for row_width in self.table_row_widths:
            # A row of width W occupies ceil(W / term_width) physical lines
            lines_up += max(1, (row_width + self._term_width - 1) // self._term_width)
        
        if lines_up > 0:
            self.stream.write(self.CURSOR_UP.format(lines_up))
        
        # Carriage return and clear to end
        self.stream.write('\r' + self.CLEAR_TO_END)
        self.stream.flush()
        
        # Output formatted table
        formatted_lines = self.formatter.format_table(self.table_buffer)
        for fl in formatted_lines:
            self._write_formatted(fl)
            self.stream.write('\n')
            self.stream.flush()
        
        # Reset state
        self.in_table = False
        self.table_buffer = []
        self.table_row_widths = []
        self._provisional_width = 0
        self._provisional_active = False
    
    def _clear_provisional(self) -> None:
        if not self._provisional_active: return
        
        # Calculate how many terminal lines the provisional output occupies
        if self._provisional_width == 0: lines_up = 0
        else:
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
        # Flush any pending table first
        if self.in_table:
            if len(self.table_buffer) >= 2 and self.formatter.is_table_separator(self.table_buffer[1]):
                self._flush_table()
            else:
                # Not a real table - output buffered lines
                for bl in self.table_buffer:
                    formatted = self.formatter.format_line(bl)
                    self._write_formatted(formatted)
                    self.stream.write('\n')
                    self.stream.flush()
                self.in_table = False
                self.table_buffer = []
                self.table_row_widths = []
        
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
        self.in_table = False
        self.table_buffer = []
        self.table_row_widths = []
        self._provisional_width = 0
        self._provisional_active = False
