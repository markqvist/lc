# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

"""Session management for lc."""

import RNS
import uuid
import time
import jinja2
from pathlib import Path
from typing import Optional, Dict, Any, List
from types import SimpleNamespace
from dataclasses import dataclass, field

from RNS.vendor import umsgpack

from lc.config import Config
from lc.agent import Agent
from lc.models.openai import OpenAIBackend


@dataclass
class ExecutionResult:
    """Result of command execution."""
    success: bool
    output: str = ""
    error: Optional[str] = None
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)


class Session:
    """Manages agent session state and execution flow."""
    
    SESSION_VERSION = 1
    
    def __init__(self, config: Config, session_id: Optional[str] = None):
        self.config = config
        self.session_id = session_id or str(uuid.uuid4())
        self.created_at = time.time()
        self.updated_at = self.created_at
        self.working_dir = Path.cwd()
        self.jinja = jinja2.Environment(undefined=jinja2.Undefined)
        
        # Conversation state
        self.conversation: List[Dict[str, Any]] = []
        self.system_prompt: str = ""
        
        # Tool and skill state
        self.tool_context: Dict[str, Any] = {}
        self.loaded_skills: List[str] = []
        
        # Statistics
        self.turn_count = 0
        self.token_count = 0
        self.tool_call_count = 0
    
    @classmethod
    def get_version(cls) -> str:
        from lc import __version__
        return __version__
    
    @classmethod
    def create(cls, config: Config) -> "Session":
        session = cls(config)
        session._initialize()
        return session
    
    @classmethod
    def create_or_resume(cls, config: Config, resume: bool = False, session_id: Optional[str] = None) -> "Session":
        if resume or session_id:
            existing = cls.load(config, session_id)
            if existing: return existing
        
        return cls.create(config)
    
    @classmethod
    def load(cls, config: Config, session_id: Optional[str] = None) -> Optional["Session"]:
        sessions_dir = config.path / "sessions"
        
        if session_id: session_file = sessions_dir / f"{session_id}.msgpack"
        else:
            # Try to load most recent session
            session_files = sorted(sessions_dir.glob("*.msgpack"), key=lambda p: p.stat().st_mtime)
            if not session_files: return None
            session_file = session_files[-1]
        
        if not session_file.exists(): return None
        
        try:
            data = umsgpack.unpack(session_file.read_bytes())
            session = cls._from_dict(config, data)
            return session

        except Exception: return None
    
    def _initialize(self) -> None:
        self._load_skill_registry()
        self._build_system_prompt()
        self.conversation.append({"role": "system", "content": self.system_prompt})
    
    def _load_skill_registry(self) -> None:
        """Initialize skill registry with all skill directories."""
        from lc.skills import SkillRegistry
        from pathlib import Path
        
        skill_dirs = []
        loading_config = self.config.loading
        
        # Built-in skills (always loaded)
        builtin_dir = Path(__file__).parent / "skills"
        if builtin_dir.exists():
            skill_dirs.append(builtin_dir)
        
        # User skills in config directory (configurable, default: enabled)
        if loading_config.get("user_skills", True):
            user_dir = self.config.path / "skills"
            if user_dir.exists():
                skill_dirs.append(user_dir)
        
        # Project-level skills (configurable, default: disabled)
        if loading_config.get("project_skills", False):
            project_dir = Path.cwd() / ".lc" / "skills"
            if project_dir.exists():
                skill_dirs.append(project_dir)
        
        # Custom directories from config (always enabled if specified)
        for custom_dir in self.config.skills.get("directories", []):
            path = Path(custom_dir).expanduser()
            if path.exists():
                skill_dirs.append(path)
        
        # Apply config-level pinned overrides
        pinned_list = self.config.skills.get("pinned", [])
        self.skill_registry = SkillRegistry(skill_dirs, pinned=pinned_list)
    
    def _build_system_prompt(self) -> None:
        from lc.resolver import Context as ResolverContext
        from lc.resolvers import TemplateResolver, EnvironmentResolver, FilesystemResolver, SystemResolver, ToolsResolver, SkillsResolver
        
        resolver_ctx = ResolverContext(session=self, config=self.config)
        resolved_context = {}
        
        for resolver_class in [TemplateResolver, ToolsResolver, SkillsResolver, EnvironmentResolver, FilesystemResolver, SystemResolver]:
            try:
                resolver = resolver_class()
                result = resolver.resolve(resolver_ctx)
                if result: resolved_context.update(result)
            
            except Exception as e:
                print(f"An error occurred while resolving variables from {resolver_class}. This resolver was skipped.")
                RNS.trace_exception(e)
        
        # Build system prompt
        sysprompt_key = self.config.model["sysprompt"].replace(".jinja", "")
        if not sysprompt_key in resolved_context["templates"]: raise KeyError("System prompt template \"{sysprompt}.jinja\" not resolvable")
        else:
            system_template = self.jinja.from_string(resolved_context["templates"][sysprompt_key])
            self.system_prompt = system_template.render(**resolved_context)

            # RNS.log(f"SYSTEM PROMPT RESOLVED:\n{self.system_prompt}")
    
    def save(self) -> None:
        if not self.config.session.get("persistence", True): return
        
        sessions_dir = self.config.path / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)
        
        session_file = sessions_dir / f"{self.session_id}.msgpack"
        temp_file = session_file.with_suffix(".msgpack.tmp")
        
        data = self._to_dict()
        packed = umsgpack.packb(data)
        temp_file.write_bytes(packed)
        temp_file.rename(session_file)
    
    def _to_dict(self) -> Dict[str, Any]:
        return { "version": self.SESSION_VERSION,
                 "session_id": self.session_id,
                 "created_at": self.created_at,
                 "updated_at": time.time(),
                 "config_path": str(self.config.path),
                 "config_snapshot": {},  # TODO: Include relevant config
                 "working_dir": str(self.working_dir),
                 "conversation": self.conversation,
                 "tool_context": self.tool_context,
                 "loaded_skills": self.loaded_skills,
                 "stats": {
                     "turn_count": self.turn_count,
                     "token_count": self.token_count,
                     "tool_call_count": self.tool_call_count,
                 } }
    
    @classmethod
    def _from_dict(cls, config: Config, data: Dict[str, Any]) -> "Session":
        session = cls(config, data.get("session_id"))
        session.created_at = data.get("created_at", time.time())
        session.updated_at = time.time()
        session.working_dir = Path(data.get("working_dir", "."))
        session.conversation = data.get("conversation", [])
        session.tool_context = data.get("tool_context", {})
        session.loaded_skills = data.get("loaded_skills", [])
        
        stats = data.get("stats", {})
        session.turn_count = stats.get("turn_count", 0)
        session.token_count = stats.get("token_count", 0)
        session.tool_call_count = stats.get("tool_call_count", 0)
        
        return session
    
    def _load_toolkits(self) -> Dict[str, Any]:
        from lc.tools import FileSystemTools, ShellTools
        from lc.toolloader import ToolLoader
        
        toolkits = {}
        toolkit_config = self.config.toolkits
        builtin_names = toolkit_config.get("builtin", ["filesystem", "shell"])
        
        if "filesystem" in builtin_names: toolkits["FileSystemTools"] = FileSystemTools()
        if "shell" in builtin_names:      toolkits["ShellTools"] = ShellTools()
        
        # Load standalone tools from configured directories
        tool_dirs = self._get_tool_directories()
        if tool_dirs:
            loader = ToolLoader(tool_dirs)
            toolkits.update(loader.get_toolkits())
        
        return toolkits
    
    def _get_tool_directories(self) -> List[Path]:
        """Get list of tool directories based on loading configuration."""
        from pathlib import Path
        
        tool_dirs = []
        loading_config = self.config.loading
        
        # User tools in config directory (configurable, default: disabled)
        if loading_config.get("user_tools", False):
            user_dir = self.config.path / "tools"
            if user_dir.exists():
                tool_dirs.append(user_dir)
        
        # Project-level tools (configurable, default: disabled)
        if loading_config.get("project_tools", False):
            project_dir = Path.cwd() / ".lc" / "tools"
            if project_dir.exists():
                tool_dirs.append(project_dir)
        
        return tool_dirs
    
    def _create_model_backend(self, force_mock: bool = False):
        model_config = self.config.model
        backend_type = model_config.get("backend", "openai")
        
        if force_mock or backend_type == "mock":
            from lc.models.mock import MockBackend
            return MockBackend(model_config)

        elif backend_type == "openai": return OpenAIBackend(model_config)
        else:                          raise ValueError(f"Unknown backend type: {backend_type}")
    
    # Executes a single command
    def execute(self, command: str, gate_level: Optional[int] = None) -> ExecutionResult:
        self.conversation.append({"role": "user", "content": command})
        
        try:
            # Setup
            model_backend = self._create_model_backend()
            toolkits = self._load_toolkits()
            
            # Create agent and run turn
            agent = Agent(session=self, model_backend=model_backend, toolkits=toolkits, gate_level=gate_level)
            output = agent.run_turn(command)
            
            self.turn_count += 1
            self.save()
            
            return ExecutionResult(success=True, output=output)
            
        except Exception as e: return ExecutionResult(success=False, error=str(e))
    
    def run_interactive(self, gate_level: Optional[int] = None) -> int:
        import sys
        
        print(f"lc {self.get_version()} - Interactive Mode")
        print(f"Session: {self.session_id}")
        print("Type 'exit' or press Ctrl+C to quit.\n")
        
        while True:
            try:
                user_input = input("lc> ").strip()
                if not user_input: continue
                if user_input.lower() in ("exit", "quit"): break
                result = self.execute(user_input, gate_level=gate_level)
                if result.error: print(f"Error: {result.error}", file=sys.stderr)
                
            except KeyboardInterrupt: print("\nUse 'exit' to quit.")
            except EOFError: break
        
        return 0
