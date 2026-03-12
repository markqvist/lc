# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

"""Skills resolver for lc."""

import RNS

from typing import Dict, Any, Optional, List
from lc.resolver import Resolver, Context


class SkillsResolver(Resolver):
    """Provides skill information for system prompt templates."""
    
    def resolve(self, context: Context) -> Optional[Dict[str, Any]]:
        """Generate skill context variables from skill registry."""
        if not hasattr(context.session, 'skill_registry'):
            return {"skills": {"all": [], "pinned": [], "unpinned": [], "loaded": [], "count": 0}}
        
        registry = context.session.skill_registry
        loaded = getattr(context.session, 'loaded_skills', [])
        
        all_skills = []
        pinned = []
        unpinned = []
        loaded_skills = []
        
        for name, skill in registry.skills.items():
            skill_info = {
                "name": skill.name,
                "description": skill.description,
                "content": skill.content,
                "version": skill.version,
                "pinned": skill.pinned,
                "loaded": name in loaded,
                "tool_count": len(skill.tools),
            }
            
            all_skills.append(skill_info)
            
            if skill.pinned: pinned.append(skill_info)
            else:            unpinned.append(skill_info)
            
            if name in loaded: loaded_skills.append(skill_info)
        
        # Sort each list alphabetically by name
        all_skills.sort(key=lambda s: s["name"])
        pinned.sort(key=lambda s: s["name"])
        unpinned.sort(key=lambda s: s["name"])
        loaded_skills.sort(key=lambda s: s["name"])
        
        return {
            "skills": {
                "all": all_skills,
                "pinned": pinned,
                "unpinned": unpinned,
                "loaded": loaded_skills,
                "count": len(all_skills),
                "pinned_count": len(pinned),
                "unpinned_count": len(unpinned),
                "loaded_count": len(loaded_skills),
                "pinned_names": [s["name"] for s in pinned],
                "unpinned_names": [s["name"] for s in unpinned],
                "summary": self._format_summary(pinned, unpinned),
            }
        }
    
    def _format_summary(self, pinned: List[Dict], unpinned: List[Dict]) -> str:
        """Format skills as readable summary."""
        lines = []
        
        if pinned:
            lines.append("## Pinned Skills")
            lines.append("")
            for skill in pinned:
                try:
                    desc = skill.get("description", "").strip()
                    tool_info = f" ({skill['tool_count']} tools)" if skill['tool_count'] else ""
                    full_skill = skill.get("content", "").replace("\r\n", "\n")
                    if full_skill.startswith("#"): full_skill = f"##{full_skill}"
                    full_skill = full_skill.replace("\n#", "\n###")
                    if not full_skill: lines.append(f"Could not load full skill information for **{skill['name']}**")
                    else: lines.extend(full_skill.splitlines())
                
                except Exception as e: RNS.trace_exception(e)

            lines.append("")
        
        if unpinned:
            lines.append("## Loadable Skills (Load with skills.load_skill)")
            lines.append("")
            for skill in unpinned:
                desc = skill.get("description", "").strip()
                short_desc = desc.split('\n')[0][:50] if desc else ""
                if len(desc) > 50:
                    short_desc += "..."
                tool_info = f" [{skill['tool_count']} tools]" if skill['tool_count'] else ""
                lines.append(f"• {skill['name']}{tool_info}: {short_desc}")
            lines.append("")
        
        if not pinned and not unpinned:
            lines.append("*No skills installed*")
        
        summary = "\n".join(lines)
        RNS.log(f"Skills summary\n{summary}", RNS.LOG_DEBUG)
        return summary
