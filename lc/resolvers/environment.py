"""Environment resolver for lc."""

import os
import getpass
import socket
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from lc.resolver import Resolver, Context


class EnvironmentResolver(Resolver):
    """Provides basic environment information."""
    
    def resolve(self, context: Context) -> Optional[Dict[str, Any]]:
        """Generate environment context variables."""
        now = datetime.now()
        
        return {
            "environment": {
                "cwd": str(context.session.working_dir) if context.session else str(Path.cwd()),
                "user": getpass.getuser(),
                "hostname": socket.gethostname(),
                "shell": os.environ.get("SHELL", "unknown"),
                "date": now.strftime("%Y-%m-%d"),
                "time": now.strftime("%H:%M:%S"),
                "datetime_iso": now.isoformat(),
            }
        }
