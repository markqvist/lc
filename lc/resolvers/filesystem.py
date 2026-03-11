"""Filesystem resolver for lc."""

from pathlib import Path
from typing import Dict, Any, Optional, List

from lc.resolver import Resolver, Context


class FilesystemResolver(Resolver):
    """Provides filesystem context information."""
    
    MAX_TREE_DEPTH = 2
    MAX_ENTRIES = 50
    MAX_RECENT_FILES = 10
    
    def resolve(self, context: Context) -> Optional[Dict[str, Any]]:
        """Generate filesystem context variables."""
        base_path = context.session.working_dir if context.session else Path.cwd()
        
        try:
            tree = self._build_tree(base_path, depth=0)
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
            
        except Exception:
            return None
    
    def _build_tree(self, path: Path, depth: int, prefix: str = "") -> str:
        """Build ASCII tree representation."""
        if depth > self.MAX_TREE_DEPTH:
            return ""
        
        if not path.exists() or not path.is_dir():
            return ""
        
        lines = []
        entries = sorted(path.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))
        
        # Limit entries
        if len(entries) > self.MAX_ENTRIES:
            entries = entries[:self.MAX_ENTRIES]
            truncated = True
        else:
            truncated = False
        
        for i, entry in enumerate(entries):
            is_last = (i == len(entries) - 1) and not truncated
            connector = "└── " if is_last else "├── "
            
            if entry.is_dir():
                lines.append(f"{prefix}{connector}📁 {entry.name}/")
                if depth < self.MAX_TREE_DEPTH:
                    extension = "    " if is_last else "│   "
                    subtree = self._build_tree(entry, depth + 1, prefix + extension)
                    if subtree:
                        lines.append(subtree)
            else:
                lines.append(f"{prefix}{connector}📄 {entry.name}")
        
        if truncated:
            lines.append(f"{prefix}└── ... ({len(path.iterdir()) - self.MAX_ENTRIES} more items)")
        
        return "\n".join(lines)
