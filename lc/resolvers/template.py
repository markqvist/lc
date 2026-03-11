# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

"""Template resolver for lc."""

import os
import sys
import platform
from typing import Dict, Any, Optional

from lc.resolver import Resolver, Context

class TemplateResolver(Resolver):
    """Loads available templates."""
    TEMPLATE_EXT = ".jinja"
    
    def resolve(self, context: Context) -> Optional[Dict[str, Any]]:
        template_path = context.config.template_path
        templates = {}
        if os.path.isdir(template_path):
            for file in os.listdir(template_path):
                if file.lower().endswith(self.TEMPLATE_EXT):
                    name = os.path.basename(file)
                    with open(template_path / file, "rb") as fh:
                        templates[file.replace(self.TEMPLATE_EXT, "")] = fh.read().decode("utf-8")

        return {"templates": templates}