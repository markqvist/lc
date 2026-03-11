# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

"""Built-in resolvers for lc."""

from lc.resolvers.template import TemplateResolver
from lc.resolvers.environment import EnvironmentResolver
from lc.resolvers.filesystem import FilesystemResolver
from lc.resolvers.system import SystemResolver
from lc.resolvers.tools import ToolsResolver

__all__ = ["TemplateResolver", "EnvironmentResolver", "FilesystemResolver", "SystemResolver", "ToolsResolver"]
