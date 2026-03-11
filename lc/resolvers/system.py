# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

"""System resolver for lc."""

import sys
import platform
from typing import Dict, Any, Optional

from lc.resolver import Resolver, Context
from lc import __version__ as lc_version


class SystemResolver(Resolver):
    """Provides system information."""
    
    def resolve(self, context: Context) -> Optional[Dict[str, Any]]:
        """Generate system context variables."""
        return {
            "system": {
                "platform": platform.system(),
                "platform_release": platform.release(),
                "python_version": platform.python_version(),
                "lc_version": lc_version,
                "architecture": platform.machine(),
                "processor": platform.processor() or "unknown",
            }
        }
