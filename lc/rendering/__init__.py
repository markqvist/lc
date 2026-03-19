# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

"""
Terminal rendering system for lc.

Provides TTY-aware output with optional markdown formatting.
"""

import sys
from typing import Optional, TextIO

from .terminal import TTYRenderer
from .markdown import MarkdownFormatter, StreamingMarkdownRenderer

__all__ = ["TTYRenderer", "MarkdownFormatter", "StreamingMarkdownRenderer"]
