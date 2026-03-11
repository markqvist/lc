# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

"""Model backend implementations for lc."""

from lc.agent import ModelBackend
from lc.models.mock import MockBackend

__all__ = ["ModelBackend", "MockBackend"]
