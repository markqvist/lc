# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

"""Skill management for lc."""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any


class Skill:
    """Represents a loaded skill."""
    
    def __init__(self, path: Path, metadata: Dict[str, Any], content: str):
        self.path = path
        self.metadata = metadata
        self.content = content
        self.tools: Dict[str, Any] = {}  # Tool signatures only (lazy-loaded)
        self._toolkit = None  # Full toolkit (lazy-loaded)
    
    @property
    def name(self) -> str: return self.metadata.get('name', self.path.name)
    
    @property
    def version(self) -> str: return self.metadata.get('version', 'unknown')
    
    @property
    def description(self) -> str: return self.metadata.get('description', '')
    
    @property
    def triggers(self) -> List[str]: return self.metadata.get('triggers', [])
    
    @property
    def pinned(self) -> bool: return self.metadata.get('pinned', False)
    
    @pinned.setter
    def pinned(self, value: bool) -> None:
        self.metadata['pinned'] = value
    
    def load_toolkit(self):
        """Lazy-load the full toolkit implementation."""
        if self._toolkit is None:
            # TODO: Import and instantiate toolkit from skill directory
            pass
        
        return self._toolkit


class SkillRegistry:
    """Manages skill discovery and loading."""
    
    FRONTMATTER_PATTERN = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
    
    def __init__(self, skill_dirs: List[Path]):
        self.skill_dirs = skill_dirs
        self.skills: Dict[str, Skill] = {}
        self._discover_skills()
    
    def _discover_skills(self) -> None:
        """Discover all available skills."""
        for skill_dir in self.skill_dirs:
            if not skill_dir.exists(): continue
            
            for skill_path in skill_dir.iterdir():
                if skill_path.is_dir(): self._load_skill_metadata(skill_path)
    
    def _load_skill_metadata(self, path: Path) -> None:
        """Load skill metadata and instantiate toolkit."""
        skill_md = path / "SKILL.md"
        if not skill_md.exists(): return
        
        content = skill_md.read_text(encoding='utf-8')
        metadata, body = self._parse_frontmatter(content)
        
        skill = Skill(path, metadata, body)
        
        # Load toolkit implementation if __init__.py exists
        init_py = path / "__init__.py"
        if init_py.exists():
            self._load_skill_toolkit(skill, init_py)
        
        self.skills[skill.name] = skill
    
    def _parse_frontmatter(self, content: str) -> tuple:
        """Parse YAML frontmatter from markdown content."""
        match = self.FRONTMATTER_PATTERN.match(content)
        
        if not match: return {}, content
        
        # Simple YAML-like parsing
        # TODO: Use proper YAML parser if needed
        frontmatter = match.group(1)
        body = content[match.end():]
        
        metadata = {}
        for line in frontmatter.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Handle lists
                if value.startswith('[') and value.endswith(']'): value = [v.strip().strip('"\'') for v in value[1:-1].split(',')]
                elif value.lower() == 'true':  value = True
                elif value.lower() == 'false': value = False
                
                metadata[key] = value
        
        return metadata, body
    
    def _load_skill_toolkit(self, skill: Skill, init_py: Path) -> None:
        """Load and instantiate skill toolkit from __init__.py."""
        import importlib.util
        import sys
        from lc.toolkit import Toolkit
        
        skill_name = skill.path.name
        module_name = f"lc.skill.{skill_name}"
        
        try:
            # Load module from file
            spec = importlib.util.spec_from_file_location(module_name, init_py)
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not load spec from {init_py}")
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Find Toolkit subclass in module
            toolkit_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, Toolkit) and 
                    attr is not Toolkit):
                    toolkit_class = attr
                    break
            
            if toolkit_class is None:
                raise ValueError(f"No Toolkit subclass found in {init_py}")
            
            # Instantiate toolkit - signatures extracted automatically
            skill._toolkit = toolkit_class()
            skill.tools = skill._toolkit.tools
            
        except Exception as e:
            raise RuntimeError(f"Failed to load skill toolkit from {skill.path}: {e}") from e
    
    def get_skill(self, name: str) -> Optional[Skill]:
        """Get a skill by name."""
        return self.skills.get(name)
    
    def get_all_signatures(self) -> Dict[str, Any]:
        """Get all tool signatures from all skills (for KV-cache)."""
        signatures = {}
        for skill in self.skills.values():
            signatures.update(skill.tools)
        return signatures
    
    def get_all_toolkits(self) -> Dict[str, Any]:
        """Get all skill toolkit instances keyed by skill name."""
        toolkits = {}
        for name, skill in self.skills.items():
            if skill._toolkit is not None:
                toolkits[name] = skill._toolkit
        return toolkits
    
    def find_by_trigger(self, text: str) -> List[Skill]:
        """Find skills matching trigger keywords in text."""
        matching = []
        text_lower = text.lower()
        
        for skill in self.skills.values():
            for trigger in skill.triggers:
                if trigger.lower() in text_lower:
                    matching.append(skill)
                    break
        
        return matching
    
    def get_pinned_skills(self) -> List[Skill]:
        """Get all pinned skills."""
        return [s for s in self.skills.values() if s.pinned]
