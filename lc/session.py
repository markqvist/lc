# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

import os
import sys
import RNS
import uuid
import time
import json
from lc.vendor import jinja2
from pathlib import Path
from typing import Optional, Dict, Any, List
from types import SimpleNamespace
from dataclasses import dataclass, field

from RNS.vendor import umsgpack as mp

from lc.config import Config
from lc.agent import Agent
from lc.models.openai import OpenAIBackend
from lc.models.mock import MockBackend
from lc.context import ContextAnalyzer, ContextShiftManager
from lc.editor import InlineEditor


@dataclass
class ExecutionResult:
    success: bool
    output: str = ""
    error: Optional[str] = None
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)


class SessionManager:
    @classmethod
    def list_sessions(cls, config: Config) -> List[Dict[str, Any]]:
        sessions_dir = config.path / "sessions"
        if not sessions_dir.exists(): return []
        
        sessions = []
        for session_file in sessions_dir.glob("*.msgpack"):
            try:
                with open(session_file, "rb") as f: data = mp.unpack(f)
                data["_file"] = session_file.name
                sessions.append(data)
            
            # Skip corrupted session files
            except Exception: continue
        
        sessions.sort(key=lambda s: s.get("updated_at", 0), reverse=True)
        return sessions
    
    @classmethod
    def find_session_by_name(cls, config: Config, name: str) -> Optional[Path]:
        sessions = cls.list_sessions(config)
        for session in sessions:
            if session.get("name") == name:
                session_id = session.get("session_id")
                if session_id: return config.path / "sessions" / f"{session_id}.msgpack"
        
        return None
    
    @classmethod
    def get_active_session(cls, config: Config) -> Optional[Path]:
        active_link = config.path / "sessions" / "active"
        if active_link.exists():
            target = active_link.resolve()
            if target.exists(): return target            
            else: active_link.unlink()

        return None
    
    @classmethod
    def set_active_session(cls, config: Config, session_id: str) -> None:
        RNS.log(f"Updating active session symlink to {session_id}", RNS.LOG_DEBUG) # TODO: Clean initial debug logging

        sessions_dir = config.path / "sessions"
        active_link = sessions_dir / "active"
        session_file = sessions_dir / f"{session_id}.msgpack"
        
        if not session_file.exists(): return        
        if active_link.exists() or active_link.is_symlink(): active_link.unlink()
        
        try: active_link.symlink_to(session_file.name)
        except Exception as e: RNS.log(f"Could not update active session symlink: {e}", RNS.LOG_ERROR)


class Session:    
    SESSION_VERSION          = 1
    CONTEXT_PREVIEW_MESSAGES = 4 # Number of recent messages to show on resume

    SESSION_IDLE             = -1
    LOCK_EXT                 = ".lock"
    
    def __init__(self, config: Config, session_id: Optional[str] = None, session_name: Optional[str] = None):
        self.config = config
        self.degraded = False
        self.session_id = session_id or str(uuid.uuid4())
        self.session_name = session_name
        self.created_at = time.time()
        self.updated_at = self.created_at
        self.working_dir = Path.cwd()
        self.jinja = jinja2.Environment(undefined=jinja2.Undefined)

        if not os.path.isfile(self.config.identity_path):
            new_identity = RNS.Identity()
            new_identity.to_file(self.config.identity_path)

        self.identity = RNS.Identity.from_file(self.config.identity_path)
        self.conversation: List[Dict[str, Any]] = []
        self.system_prompt: str = ""
        self.tool_context: Dict[str, Any] = {}
        self.loaded_skills: List[str] = []

        self.turn_count = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self.total_tokens = 0
        self.tool_call_count = 0
        self.turn_usage: List[Dict[str, Any]] = []

        self.context_analyzer: Optional[ContextAnalyzer] = None
        self.context_shift_manager: Optional[ContextShiftManager] = None
        self.model_override: Optional[str] = None
        self.session_file_path = None
        self._is_resumed = False
    
    @classmethod
    def get_version(cls) -> str:
        from lc import __version__
        return __version__
    
    @classmethod
    def create(cls, config: Config, session_name: Optional[str] = None, model_override: Optional[str] = None) -> "Session":
        session = cls(config, session_name=session_name)
        session.model_override = model_override
        session._initialize()
        session.save()
        session._update_active_link()
        return session
    
    @classmethod
    def create_or_resume(cls,  config: Config,  resume: bool = False,  session_id: Optional[str] = None,
                         session_name: Optional[str] = None, rebuild_system_prompt: bool = False,
                         model_override: Optional[str] = None) -> "Session":

        if resume or session_id:
            existing = cls.load(config, session_id, rebuild_system_prompt=rebuild_system_prompt)
            if existing: 
                existing._is_resumed = True
                # CLI flag takes precedence over saved session model
                # If CLI flag provided, update session for future resumptions
                if model_override is not None: existing.model_override = model_override
                return existing

            elif session_id: raise ValueError(f"Session not found: {session_id}")
        
        return cls.create(config, session_name=session_name, model_override=model_override)
    
    @classmethod
    def load(cls,  config: Config,  session_id: Optional[str] = None, rebuild_system_prompt: bool = False) -> Optional["Session"]:
        sessions_dir = config.path / "sessions"
        
        if session_id:
            session_file = sessions_dir / f"{session_id}.msgpack"
            if not session_file.exists():
                named_file = SessionManager.find_session_by_name(config, session_id)
                if named_file: session_file = named_file
        
        else:
            # Try active symlink first
            active_file = SessionManager.get_active_session(config)
            if active_file: session_file = active_file
            else:
                # Fall back to most recent session
                session_files = sorted(sessions_dir.glob("*.msgpack"), key=lambda p: p.stat().st_mtime)
                if not session_files: return None
                session_file = session_files[-1]
        
        if not session_file.exists(): return None
        
        try:
            with open(session_file, "rb") as f: data = mp.unpack(f)
            session = cls._from_dict(config, data, rebuild_system_prompt=rebuild_system_prompt)
            session._update_active_link()
            session.session_file_path = session_file
            return session

        except Exception: return None
    
    def _update_active_link(self) -> None: SessionManager.set_active_session(self.config, self.session_id)

    def record_turn_usage(self, usage: Dict[str, Any]) -> None:
        import time

        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)

        turn_record = { "turn": self.turn_count + 1,
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": total_tokens,
                        "timestamp": time.time() }
        
        self.turn_usage.append(turn_record)

        # Cumulative totals:
        # - input_tokens: current conversation size (last turn's prompt_tokens)
        # - output_tokens: sum of all completion_tokens across turns
        # - total_tokens: use API's reported total (cumulative prompt + completion)
        if self.turn_usage:
            self.input_tokens = self.turn_usage[-1].get("prompt_tokens", 0)
            self.output_tokens = sum(t.get("completion_tokens", 0) for t in self.turn_usage)
            # Use the API's total_tokens from the most recent turn
            # This is the accurate cumulative count (not input + output, which double-counts)
            self.total_tokens = self.turn_usage[-1].get("total_tokens", self.input_tokens + self.output_tokens)

        # Also record detailed per-message breakdown via context analyzer
        if self.context_analyzer is None: self.context_analyzer = ContextAnalyzer(self)
        self.context_analyzer.record_turn(usage, self.conversation.copy())
    
    def _initialize(self) -> None:
        self._load_skill_registry()
        self._build_system_prompt()
        self.conversation.append({"role": "system", "content": self.system_prompt})
        self.context_analyzer = ContextAnalyzer(self)
        self.context_shift_manager = ContextShiftManager(self)
    
    def _load_skill_registry(self) -> None:
        from lc.skills import SkillRegistry
        from pathlib import Path
        
        skill_dirs = []
        loading_config = self.config.loading
        
        # Built-in skills (always loaded)
        builtin_dir = Path(__file__).parent / "skills"
        if builtin_dir.exists(): skill_dirs.append(builtin_dir)
        
        # User skills in config directory (configurable, default: enabled)
        if loading_config.get("user_skills", True):
            user_dir = self.config.path / "skills"
            if user_dir.exists(): skill_dirs.append(user_dir)
        
        # Project-level skills (configurable, default: disabled)
        if loading_config.get("project_skills", False):
            project_dir = Path.cwd() / ".lc" / "skills"
            if project_dir.exists(): skill_dirs.append(project_dir)
        
        # Custom directories from config (always enabled if specified)
        for custom_dir in self.config.skills.get("directories", []):
            path = Path(custom_dir).expanduser()
            if path.exists(): skill_dirs.append(path)
        
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

        sysprompt_key = self.config.model["sysprompt"].replace(".jinja", "")
        if not sysprompt_key in resolved_context["templates"]: raise KeyError("System prompt template \"{sysprompt}.jinja\" not resolvable")
        else:
            system_template    = self.jinja.from_string(resolved_context["templates"][sysprompt_key])
            self.system_prompt = system_template.render(**resolved_context)
            # RNS.log(f"SYSTEM PROMPT RESOLVED:\n{self.system_prompt}")
    
    def _rebuild_for_resume(self, rebuild_system_prompt: bool = False) -> None:
        self._load_skill_registry()
        
        if rebuild_system_prompt:
            self._build_system_prompt()
            if self.conversation and self.conversation[0].get("role") == "system": self.conversation[0]["content"] = self.system_prompt
            else: self.conversation.insert(0, {"role": "system", "content": self.system_prompt})
    
    def rebuild_loaded_skills(self) -> None:        
        active_skills = set()
        
        for msg in self.conversation:
            if msg.get("role") != "assistant": continue
            
            tool_calls = msg.get("tool_calls", [])
            if not tool_calls: continue
            
            for tool_call in tool_calls:
                function = tool_call.get("function", {})
                tool_name = function.get("name", "")
                if tool_name != "skills.load_skill": continue
                
                arguments_raw = function.get("arguments", "{}")
                if isinstance(arguments_raw, dict): arguments = arguments_raw
                elif isinstance(arguments_raw, str):
                    try: arguments = json.loads(arguments_raw)
                    except json.JSONDecodeError: continue
                else: continue
                
                skill_name = arguments.get("name", "")
                if skill_name: active_skills.add(skill_name)
        
        previous_skills = set(self.loaded_skills)
        self.loaded_skills = list(active_skills)
        
        removed = previous_skills - active_skills
        if removed: RNS.log(f"Skills shifted out of context: {', '.join(sorted(removed))}", RNS.LOG_DEBUG)

    def save(self) -> None:
        if not self.config.session.get("persistence", True): return
        
        sessions_dir = self.config.path / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)
        
        session_file = sessions_dir / f"{self.session_id}.msgpack"
        temp_file = session_file.with_suffix(".msgpack.tmp")
        
        data = self._to_dict()
        packed = mp.packb(data)
        with open(temp_file, "wb") as f: f.write(packed)
        temp_file.rename(session_file)
        self.session_file_path = session_file
    
    def _to_dict(self) -> Dict[str, Any]:
        data = { "version": self.SESSION_VERSION,
                 "session_id": self.session_id,
                 "name": self.session_name,
                 "created_at": self.created_at,
                 "updated_at": time.time(),
                 "config_path": str(self.config.path),
                 "config_snapshot": {},  # TODO: Include relevant config
                 "working_dir": str(self.working_dir),
                 "conversation": self.conversation,
                 "tool_context": self.tool_context,
                 "loaded_skills": self.loaded_skills,
                 "model_override": self.model_override,
                 "stats": { "turn_count": self.turn_count,
                            "input_tokens": self.input_tokens,
                            "output_tokens": self.output_tokens,
                            "total_tokens": self.total_tokens,
                            "tool_call_count": self.tool_call_count,
                            "turn_usage": self.turn_usage } }

        if self.context_analyzer is not None: data["context_analysis"] = self.context_analyzer.to_dict()
        return data
    
    @classmethod
    def _from_dict(cls,  config: Config,  data: Dict[str, Any], rebuild_system_prompt: bool = False) -> "Session":
        session = cls(config, data.get("session_id"), data.get("name"))
        session.created_at = data.get("created_at", time.time())
        session.updated_at = data.get("updated_at", time.time())
        session.working_dir = Path(data.get("working_dir", "."))
        session.conversation = data.get("conversation", [])
        session.tool_context = data.get("tool_context", {})
        session.loaded_skills = data.get("loaded_skills", [])
        session.model_override = data.get("model_override", None)
        
        stats = data.get("stats", {})
        session.turn_count = stats.get("turn_count", 0)
        session.tool_call_count = stats.get("tool_call_count", 0)

        # Token usage (new fields, backward compatible)
        session.input_tokens = stats.get("input_tokens", 0)
        session.output_tokens = stats.get("output_tokens", 0)
        session.total_tokens = stats.get("total_tokens", stats.get("token_count", 0))
        session.turn_usage = stats.get("turn_usage", [])

        # Restore context analyzer if available
        context_analysis = data.get("context_analysis")
        if context_analysis is not None: session.context_analyzer = ContextAnalyzer.from_dict(session, context_analysis)
        
        # Create fresh analyzer - will sync on next turn
        else: session.context_analyzer = ContextAnalyzer(session)

        # Initialize context shift manager
        session.context_shift_manager = ContextShiftManager(session)

        # Rebuild registry/system prompt if requested
        session._rebuild_for_resume(rebuild_system_prompt=rebuild_system_prompt)

        return session
    
    def _display_resume_context(self) -> None:
        import shutil
        
        # Header
        print(f"\n{'─' * 60}")
        print(f"  Resuming Session: {self.session_name or self.session_id[:8]}...")
        print(f"{'─' * 60}")
        
        # Metadata
        msg_count = len([m for m in self.conversation if m.get("role") in ("user", "assistant")])
        tool_count = self.tool_call_count

        token_info = f"Tokens: {self.total_tokens:,}" if self.total_tokens else "Tokens: -"
        print(f"  Messages: {msg_count} | {token_info} | Tools: {tool_count} | Turns: {self.turn_count}")
        
        # Working directory warning
        current_dir = Path.cwd()
        if current_dir != self.working_dir:
            print(f"\n  ⚠ Working directory differs!")
            print(f"    Session: {self.working_dir}")
            print(f"    Current: {current_dir}")
        
        # Recent context
        non_system_msgs = [m for m in self.conversation if m.get("role") != "system"]
        
        if len(non_system_msgs) > self.CONTEXT_PREVIEW_MESSAGES:
            skipped = len(non_system_msgs) - self.CONTEXT_PREVIEW_MESSAGES
            print(f"\n  (... {skipped} previous messages)")
        
        # Show recent messages
        recent = non_system_msgs[-self.CONTEXT_PREVIEW_MESSAGES:]
        for msg in recent:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            tool_calls = msg.get("tool_calls", [])
            
            if role == "user":
                preview = content[:100] + "..." if len(content) > 100 else content
                print(f"\n  [You]: {preview}")
            
            elif role == "assistant":
                if tool_calls:
                    for tc in tool_calls:
                        fn = tc.get("function", {})
                        name = fn.get("name", "unknown")
                        print(f"\n  [Tool]: {name}")
                elif content:
                    preview = content[:100].replace('\n', ' ') + "..." if len(content) > 100 else content
                    print(f"\n  [lc]: {preview}")
            
            elif role == "tool":
                result_preview = content[:80].replace('\n', ' ') + "..." if len(content) > 80 else content
                print(f"  → {result_preview}")
        
        print(f"\n{'─' * 60}\n")
    
    def _load_toolkits(self) -> Dict[str, Any]:
        from lc.tools import Filesystem, Shell, Cryptography
        from lc.toolloader import ToolLoader
        
        toolkits = {}
        toolkit_config = self.config.toolkits
        builtin_names = toolkit_config.get("builtin", ["filesystem", "shell", "cryptography"])
        
        if "filesystem" in builtin_names:   toolkits["Filesystem"]   = Filesystem()
        if "shell" in builtin_names:        toolkits["Shell"]        = Shell()
        if "cryptography" in builtin_names: toolkits["Cryptography"] = Cryptography()
        
        # Load standalone tools from configured directories
        tool_dirs = self._get_tool_directories()
        if tool_dirs:
            loader = ToolLoader(tool_dirs)
            toolkits.update(loader.get_toolkits())
        
        return toolkits
    
    def _get_tool_directories(self) -> List[Path]:
        from pathlib import Path
        
        tool_dirs = []
        loading_config = self.config.loading
        
        # User tools in config directory (configurable, default: enabled)
        if loading_config.get("user_tools", True):
            user_dir = self.config.path / "tools"
            if user_dir.exists(): tool_dirs.append(user_dir)
        
        # Project-level tools (configurable, default: disabled)
        if loading_config.get("project_tools", False):
            project_dir = Path.cwd() / ".lc" / "tools"
            if project_dir.exists(): tool_dirs.append(project_dir)
        
        return tool_dirs
    
    def _create_model_backend(self, force_mock: bool = False, model_name: Optional[str] = None):
        # CLI override takes precedence, then explicit parameter, then session override
        target_model = model_name or self.model_override
        model_config = self.config.get_model_config(target_model)
        
        backend_type = model_config.get("backend", "openai")
        
        if force_mock or backend_type == "mock": return MockBackend(model_config)
        elif backend_type == "openai":           return OpenAIBackend(model_config)
        else:                                    raise  ValueError(f"Unknown backend type: {backend_type}")
    
    def _check_and_shift_context(self) -> tuple[bool, str]:
        if self.context_shift_manager is None: return False, ""
        if self.context_analyzer is None: return False, ""

        estimated = self.context_analyzer.estimate_current_tokens(self.conversation)
        return self.context_shift_manager.perform_shift()

    def _lock(self) -> int:
        pid           = os.getpid()
        lock_time     = time.time()
        lockfile_path = Path(self.session_file_path).expanduser().with_name(self.session_file_path.name + self.LOCK_EXT)
        
        if os.path.exists(lockfile_path):
            lock_info = None
            try:
                with open(lockfile_path, "rb") as fh: lock_info = mp.unpackb(fh.read())
                locking_pid  = lock_info["pid"]
                locked_at    = lock_info["ts"]
                lock_timeout = self.config.session.get("lock_timeout", 10800)

                if time.time() < locked_at+lock_timeout: return locking_pid
                else:
                    RNS.log(f"Removing timed out session lock {lockfile_path}", RNS.LOG_WARNING)
                    try: lockfile_path.unlink()
                    except Exception as e:
                        RNS.log(f"Could not clean timed out session lock file {lockfile_path}: {e}", RNS.LOG_ERROR)
                        self.degraded = True

            except Exception as e:
                RNS.log(f"Undecodable session lock data: {e}", RNS.LOG_ERROR)
                RNS.log(f"Discarding session lock {lockfile_path}", RNS.LOG_ERROR)
                try: lockfile_path.unlink()
                except Exception as e:
                    RNS.log(f"Could not clean invalid session lock file {lockfile_path}: {e}", RNS.LOG_ERROR)
                    self.degraded = True

                return self.SESSION_IDLE

        RNS.log(f"Locking session: {lockfile_path}", RNS.LOG_VERBOSE)
        lock_info = {"pid": pid, "ts": lock_time}
        try:
            with open(lockfile_path, "wb") as fh: fh.write(mp.packb(lock_info))
        except Exception as e:
            RNS.log(f"Could not write session lock file {lockfile_path}: {e}", RNS.LOG_ERROR)
            self.degraded = True

        return self.SESSION_IDLE

    def _unlock(self) -> bool:
        lockfile_path = Path(self.session_file_path).expanduser().with_name(self.session_file_path.name + self.LOCK_EXT)
        RNS.log(f"Unlocking session: {lockfile_path}", RNS.LOG_VERBOSE)
        try: lockfile_path.unlink()
        except Exception as e:
            RNS.log(f"Could not remove session lock {lockfile_path}, the contained exception was: {e}", RNS.LOG_ERROR)
            self.degraded = True

    def execute(self, command: str, gate_level: Optional[int] = None, can_prompt: bool = False, output_mode: str = "tty", stdin_context: Optional[str] = None) -> ExecutionResult:
        pid = self._lock()
        if not pid == self.SESSION_IDLE: return ExecutionResult(success=False, error=f"Session in execution and locked by PID {pid}")
        else:
            if stdin_context: self.conversation.append({"role": "user", "content": f"[Received via stdin]:\n{stdin_context}"})
            self.conversation.append({"role": "user", "content": command})

            shifted, shift_msg = self._check_and_shift_context()
            if shifted: RNS.log(f"Context shift performed: {shift_msg}", RNS.LOG_INFO)

            try:
                model_backend = self._create_model_backend()
                toolkits = self._load_toolkits()

                agent = Agent(session=self, model_backend=model_backend, toolkits=toolkits, gate_level=gate_level, can_prompt=can_prompt, output_mode=output_mode)
                output = agent.run_turn(command, checkpoint_callback=self.save)

                self.turn_count += 1
                self.save()

                return ExecutionResult(success=True, output=output)

            except Exception as e: return ExecutionResult(success=False, error=str(e))
            finally: self._unlock()
    
    def run_interactive(self, gate_level: Optional[int] = None, can_prompt: bool = True, output_mode: str = "tty") -> int:
        if self._is_resumed: self._display_resume_context()

        print(f"lc {self.get_version()} - Interactive Mode")
        if self.session_name: print(f"Session: {self.session_name} ({self.session_id[:8]}...)")
        else:                 print(f"Session: {self.session_id}")
        
        print("Use \"exit\" or \"quit\" to detach session.")
        print("Ctrl+D or Alt+Enter executes.\n")
        
        while True:
            try:
                # user_input = input("lc> ").strip()
                editor = InlineEditor(history_file=None)
                user_input = editor.read("lc> ").strip()

                if not user_input:
                    print()
                    break
                
                if user_input.lower() in ("exit", "quit"):
                    print()
                    break
                
                result = self.execute(user_input, gate_level=gate_level, can_prompt=can_prompt)
                if result.error: print(f"\nError: {result.error}", file=sys.stderr)
                else: print(f"\n")
                
            except KeyboardInterrupt: print("\nUse 'exit' to quit.")
            except EOFError:
                print()
                break
        
        return 0
