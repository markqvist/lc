"""Built-in resolvers for lc."""

from lc.resolvers.environment import EnvironmentResolver
from lc.resolvers.filesystem import FilesystemResolver
from lc.resolvers.system import SystemResolver

__all__ = ["EnvironmentResolver", "FilesystemResolver", "SystemResolver"]
