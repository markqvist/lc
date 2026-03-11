# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

"""Filesystem resolver for lc."""
import RNS

from pathlib import Path
from typing import Dict, Any, Optional, List

from lc.resolver import Resolver, Context


class FilesystemResolver(Resolver):
    """Provides filesystem context information."""
    
    MAX_TREE_DEPTH   = 2
    MAX_ENTRIES      = 50
    MAX_RECENT_FILES = 10
    NO_DESCENT       = [".git", ".cache", "__pycache__", ".tox", ".venv", ".hg"]
    
    def resolve(self, context: Context) -> Optional[Dict[str, Any]]:
        """Generate filesystem context variables."""
        base_path = context.session.working_dir if context.session else Path.cwd()
        
        try:
            tree = self._build_tree(base_path, depth=0, no_descent=self.NO_DESCENT)
            entries = list(base_path.iterdir()) if base_path.exists() else []
            
            files = [e for e in entries if e.is_file()]
            dirs = [e for e in entries if e.is_dir()]
            
            # Get recently modified files
            recent_files = sorted(
                [f for f in files],
                key=lambda f: f.stat().st_mtime,
                reverse=True
            )[:self.MAX_RECENT_FILES]
            
            return {
                "filesystem": {
                    "tree": tree,
                    "file_count": len(files),
                    "dir_count": len(dirs),
                    "total_entries": len(entries),
                    "recent_files": [f.name for f in recent_files],
                }
            }
            
        except Exception as e:
            RNS.log("An error occurred while resolving filesystem information:")
            RNS.trace_exception(e)
            return None

    def _count_entries(self, path: Path) -> int:
        """Count total entries in a directory (used for non-descended directories)."""
        try:
            if not path.exists() or not path.is_dir():
                return 0
            return sum(1 for _ in path.iterdir())
        except Exception:
            return 0
    
    def _count_entries(self, path: Path) -> int:
        """Count total entries in a directory (used for non-descended directories)."""
        try:
            if not path.exists() or not path.is_dir():
                return 0
            return sum(1 for _ in path.iterdir())
        except Exception:
            return 0

    def _build_tree(self, path: Path, depth: int, prefix: str = "", no_descent: Optional[List[str]] = None) -> str:
        """Build ASCII tree representation."""
        if depth > self.MAX_TREE_DEPTH:
            return ""
        
        if not path.exists() or not path.is_dir():
            return ""
        
        # Default no-descent list (can be overridden by caller)
        if no_descent is None:
            no_descent = [".git", ".cache", "__pycache__", ".tox", ".venv"]
        
        lines = []
        entries = sorted(path.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))
        
        # Limit visible entries but preserve non-descended dirs in count
        total_entries = len(entries)
        if len(entries) > self.MAX_ENTRIES:
            visible_entries = entries[:self.MAX_ENTRIES]
            truncated = True
        else:
            visible_entries = entries
            truncated = False
        
        for i, entry in enumerate(visible_entries):
            # Determine if this is the last visible entry and whether truncation is active
            is_last = (i == len(visible_entries) - 1) and not truncated
            connector = "└── " if is_last else "├── "
            
            # Handle non-descent directories specially
            if entry.is_dir() and entry.name in no_descent:
                item_count = self._count_entries(entry)
                lines.append(f"{prefix}{connector}📁 {entry.name}/ ({item_count} items)")
                continue
            
            if entry.is_dir():
                lines.append(f"{prefix}{connector}📁 {entry.name}/")
                if depth < self.MAX_TREE_DEPTH:
                    extension = "    " if is_last else "│   "
                    subtree = self._build_tree(entry, depth + 1, prefix + extension, no_descent)
                    if subtree:
                        lines.append(subtree)
            else:
                lines.append(f"{prefix}{connector}📄 {entry.name}")
        
        if truncated:
            hidden_count = total_entries - self.MAX_ENTRIES
            # Count how many non-descent dirs are hidden for accurate summary
            hidden_dir_count = sum(1 for e in entries[self.MAX_ENTRIES:] if e.name in no_descent)
            lines.append(f"{prefix}└── ... ({hidden_count - hidden_dir_count + hidden_dir_count*10} more items)")  # Simplified: just show total
        
        return "\n".join(lines)
