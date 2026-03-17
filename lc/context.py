# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

import os
import RNS
import shutil
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from dataclasses import dataclass, field
from pathlib import Path

if TYPE_CHECKING:
    from lc.session import Session


@dataclass
class MessageTokenInfo:
    role: str
    index: int  # Index in conversation list
    estimated_tokens: int
    is_estimated: bool = True  # True if heuristic, False if from actual API data


@dataclass
class TurnTokenBreakdown:
    turn: int
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    timestamp: float
    message_tokens: List[MessageTokenInfo] = field(default_factory=list)


class ContextAnalyzer:
    # Conservative estimate: ~4 chars per token
    # This varies by content (code is denser, prose is lighter)
    CHARS_PER_TOKEN = 4.0

    def __init__(self, session: "Session"):
        self.session = session
        self.turn_breakdowns: List[TurnTokenBreakdown] = []
        self._last_conversation_length = 0
        self._last_prompt_tokens = 0
        RNS.log(f"ContextAnalyzer initialized for session {session.session_id[:8]}...", RNS.LOG_DEBUG)

    def record_turn(self, usage: Dict[str, Any], conversation: List[Dict[str, Any]]) -> TurnTokenBreakdown:
        """Record token usage for a turn and compute per-message estimates.

        Args:
            usage: Dict with 'prompt_tokens', 'completion_tokens', 'total_tokens'
            conversation: Current conversation state after this turn

        Returns:
            TurnTokenBreakdown with per-message token estimates
        """
        import time

        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)

        # Calculate how many new messages were added since last turn
        new_message_count = len(conversation) - self._last_conversation_length

        # Calculate the token delta attributed to new messages
        token_delta = prompt_tokens - self._last_prompt_tokens

        message_tokens = []

        if new_message_count > 0 and token_delta > 0:
            # Get the new messages
            new_messages = conversation[-new_message_count:]

            # Calculate character counts for proportional distribution
            char_counts = []
            for msg in new_messages:
                content = msg.get("content", "")
                if isinstance(content, str): char_counts.append(len(content))
                
                # Multimodal content - count text parts
                elif isinstance(content, list):
                    total_chars = 0
                    for item in content:
                        if item.get("type") == "text": total_chars += len(item.get("text", ""))
                    char_counts.append(max(total_chars, 1))  # At least 1 char
                
                else: char_counts.append(1)

            total_chars = sum(char_counts)

            # Distribute tokens proportionally by character count
            for i, (msg, chars) in enumerate(zip(new_messages, char_counts)):
                # Proportional allocation
                if total_chars > 0:
                    ratio = chars / total_chars
                    estimated_tokens = int(token_delta * ratio)
                
                else: estimated_tokens = max(1, token_delta // new_message_count)

                # Find the actual index in conversation
                msg_index = len(conversation) - new_message_count + i

                message_tokens.append(MessageTokenInfo(role=msg.get("role", "unknown"),
                                                       index=msg_index,
                                                       estimated_tokens=estimated_tokens,
                                                       is_estimated=False)) # Based on actual API data 
        elif new_message_count > 0:
            # No token delta but new messages (edge case: zero tokens somehow)
            # Use character-based heuristic
            new_messages = conversation[-new_message_count:]
            for i, msg in enumerate(new_messages):
                msg_index = len(conversation) - new_message_count + i
                estimated = self._estimate_message_tokens(msg)
                message_tokens.append(MessageTokenInfo(role=msg.get("role", "unknown"),
                                                       index=msg_index,
                                                       estimated_tokens=estimated,
                                                       is_estimated=True))
        # Handle the completion/assistant message
        if completion_tokens > 0:
            # Find the last assistant message
            for i in range(len(conversation) - 1, -1, -1):
                if conversation[i].get("role") == "assistant":
                    message_tokens.append(MessageTokenInfo(role="assistant",
                                                           index=i,
                                                           estimated_tokens=completion_tokens,
                                                           is_estimated=False))
                    break

        breakdown = TurnTokenBreakdown(turn=self.session.turn_count + 1,
                                       prompt_tokens=prompt_tokens,
                                       completion_tokens=completion_tokens,
                                       total_tokens=total_tokens,
                                       timestamp=time.time(),
                                       message_tokens=message_tokens)

        self.turn_breakdowns.append(breakdown)

        # Update tracking state
        self._last_conversation_length = len(conversation)
        self._last_prompt_tokens = prompt_tokens

        RNS.log(f"ContextAnalyzer recorded turn {breakdown.turn}: "
                f"prompt={prompt_tokens}, completion={completion_tokens}, "
                f"total={total_tokens}, new_msgs={new_message_count}, "
                f"tracked={len(message_tokens)}", RNS.LOG_DEBUG)

        return breakdown

    def _estimate_message_tokens(self, message: Dict[str, Any]) -> int:
        content = message.get("content", "")
        role = message.get("role", "unknown")

        if isinstance(content, str): char_count = len(content)
        
        # Multimodal - count text parts, add estimate for image overhead
        elif isinstance(content, list):
            char_count = 0
            image_count = 0
            for item in content:
                if item.get("type") == "text":        char_count += len(item.get("text", ""))
                elif item.get("type") == "image_url": image_count += 1
            # Add token estimate for image (typically ~200-500 tokens depending on model)
            char_count += image_count * 300
        
        else: char_count = 0

        # Add overhead for message structure (role, etc.)
        overhead = 10

        estimated = max(1, int((char_count + overhead) / self.CHARS_PER_TOKEN))
        RNS.log(f"ContextAnalyzer estimated {role} message: {char_count} chars ~ {estimated} tokens", RNS.LOG_EXTREME)

        return estimated

    def estimate_current_tokens(self, conversation: List[Dict[str, Any]]) -> int:
        """Estimate total tokens for current conversation state.

        Uses actual tracked data where available, falls back to heuristic for
        messages added since last API call.

        Args:
            conversation: Current conversation list

        Returns:
            Estimated total token count
        """

        # No history - use pure heuristic
        if not self.turn_breakdowns:
            total = sum(self._estimate_message_tokens(msg) for msg in conversation)
            RNS.log(f"ContextAnalyzer estimated total (no history): {total} tokens for {len(conversation)} messages", RNS.LOG_EXTREME)
            return total

        # Start with last known prompt token count
        last_breakdown = self.turn_breakdowns[-1]
        total = last_breakdown.prompt_tokens

        # Add any new messages since last turn
        new_count = len(conversation) - self._last_conversation_length
        if new_count > 0:
            new_messages = conversation[-new_count:]
            estimated_new = sum(self._estimate_message_tokens(msg) for msg in new_messages)
            total += estimated_new
            RNS.log(f"ContextAnalyzer estimated total: {last_breakdown.prompt_tokens} (known) + {estimated_new} ({new_count} new) = {total} tokens", RNS.LOG_EXTREME)
        
        else: RNS.log(f"ContextAnalyzer estimated total: {total} tokens (no new messages)", RNS.LOG_EXTREME)

        return total

    def get_message_token_count(self, conversation_index: int) -> int:
        """Get token count for a specific message by index.

        Returns tracked value if available, otherwise estimates.
        """
        # Search through turn breakdowns
        for breakdown in self.turn_breakdowns:
            for msg_info in breakdown.message_tokens:
                if msg_info.index == conversation_index: return msg_info.estimated_tokens

        # Not tracked - estimate from current conversation
        if 0 <= conversation_index < len(self.session.conversation): return self._estimate_message_tokens(self.session.conversation[conversation_index])

        return 0

    def recalculate_from_messages(self, conversation: List[Dict[str, Any]]) -> int:
        """Recalculate total token estimate from message estimates.

        Used after context shift to update input_tokens estimate.

        Args:
            conversation: Current conversation list after shift

        Returns:
            Estimated total token count
        """
        total = 0
        for i, msg in enumerate(conversation):
            count = self.get_message_token_count(i)
            if count == 0: count = self._estimate_message_tokens(msg)
            total += count

        RNS.log(f"ContextAnalyzer recalculated after shift: {total} tokens for {len(conversation)} messages", RNS.LOG_DEBUG)
        return total

    def rebuild_indices_after_shift(self, removed_start: int, removed_end: int):
        """Update indices in turn_breakdowns after removing messages."""
        RNS.log(f"Rebuilding analyzer stats indices after context shift from {removed_start} to {removed_end}...", RNS.LOG_DEBUG)
        removed_count = removed_end - removed_start
        
        for breakdown in self.turn_breakdowns:
            new_message_tokens = []
            for mt in breakdown.message_tokens:
                # Message was removed - skip it
                if removed_start <= mt.index < removed_end: continue
                
                # Shift index down
                elif mt.index >= removed_end:
                    new_message_tokens.append(MessageTokenInfo(role=mt.role,
                                                               index=mt.index - removed_count,
                                                               estimated_tokens=mt.estimated_tokens,
                                                               is_estimated=mt.is_estimated))
                
                # Before removal zone - keep as-is
                else: new_message_tokens.append(mt)
            
            breakdown.message_tokens = new_message_tokens

        self._last_conversation_length -= removed_count

    def to_dict(self) -> List[Dict[str, Any]]:
        result = []
        for bd in self.turn_breakdowns:
            result.append( {"turn": bd.turn,
                            "prompt_tokens": bd.prompt_tokens,
                            "completion_tokens": bd.completion_tokens,
                            "total_tokens": bd.total_tokens,
                            "timestamp": bd.timestamp,
                            "message_tokens": [ {"role": mt.role,
                                                 "index": mt.index,
                                                 "estimated_tokens": mt.estimated_tokens,
                                                 "is_estimated": mt.is_estimated}
                                                 for mt in bd.message_tokens ] })
        return result

    @classmethod
    def from_dict(cls, session: "Session", data: List[Dict[str, Any]]) -> "ContextAnalyzer":
        analyzer = cls(session)
        for item in data:
            breakdown = TurnTokenBreakdown(turn=item.get("turn", 0),
                                           prompt_tokens=item.get("prompt_tokens", 0),
                                           completion_tokens=item.get("completion_tokens", 0),
                                           total_tokens=item.get("total_tokens", 0),
                                           timestamp=item.get("timestamp", 0),
                                           message_tokens=[ MessageTokenInfo(role=mt.get("role", "unknown"),
                                                                             index=mt.get("index", 0),
                                                                             estimated_tokens=mt.get("estimated_tokens", 0),
                                                                             is_estimated=mt.get("is_estimated", True))
                                                            for mt in item.get("message_tokens", []) ])
            analyzer.turn_breakdowns.append(breakdown)

        # Restore tracking state from last breakdown
        if analyzer.turn_breakdowns:
            last = analyzer.turn_breakdowns[-1]
            analyzer._last_prompt_tokens = last.prompt_tokens
            # We can't know exact conversation length from breakdown alone
            # This will be corrected on next record_turn call
            analyzer._last_conversation_length = 0  # Will be set correctly on next record
            RNS.log(f"ContextAnalyzer restored from dict: {len(analyzer.turn_breakdowns)} turns, "
                    f"last_prompt={analyzer._last_prompt_tokens}", RNS.LOG_DEBUG)
        
        else: RNS.log("ContextAnalyzer restored from dict: no turn data", RNS.LOG_DEBUG)

        return analyzer


class ContextShiftManager:
    # TODO: Future enhancement - guarantee last N messages are preserved
    # regardless of token count, for continuity of recent context

    def __init__(self, session: "Session"):
        self.session = session
        self.shift_count = 0
        self.cumulative_removed_messages = 0
        self.cumulative_removed_tokens = 0
        self.cumulative_removed_turns = 0

    def _get_config(self) -> tuple[int, float]:
        context_limit = self.session.config.model.get("context_limit", 128000)
        shift_factor = self.session.config.model.get("context_shift_factor", 0.35)
        return context_limit, shift_factor

    def should_shift(self, estimated_tokens: int) -> bool:
        context_limit, shift_factor = self._get_config()

        # shift_factor = 0 disables context shifting
        if shift_factor <= 0: return False

        return estimated_tokens >= context_limit

    def _find_backup_path(self) -> Optional[Path]:
        sessions_dir = self.session.config.path / "sessions"
        if not sessions_dir.exists(): return None

        base_name = f"{self.session.session_id}.msgpack"
        counter = 1

        while True:
            backup_path = sessions_dir / f"{base_name}.{counter}"
            if not backup_path.exists(): return backup_path
            counter += 1

    def _create_backup(self) -> Optional[Path]:
        sessions_dir = self.session.config.path / "sessions"
        session_file = sessions_dir / f"{self.session.session_id}.msgpack"

        if not session_file.exists():
            RNS.log("ContextShiftManager: No session file to backup", RNS.LOG_DEBUG)
            return None

        backup_path = self._find_backup_path()
        if backup_path is None: return None

        try:
            shutil.copy2(session_file, backup_path)
            RNS.log(f"ContextShiftManager: Session backed up to {backup_path.name}", RNS.LOG_DEBUG)
            return backup_path
        
        except Exception as e:
            RNS.log(f"ContextShiftManager: Failed to create backup: {e}", RNS.LOG_ERROR)
            return None

    def _find_shift_point(self, target_tokens: int) -> tuple[int, int, int]:
        """Find the index to shift at, preserving system and first user message."""
        RNS.log("Finding context shift point target...", RNS.LOG_DEBUG)
        conversation = self.session.conversation

        if not conversation: return 0, 0, 0

        # Find first user message index
        first_user_idx = None
        for i, msg in enumerate(conversation):
            if msg.get("role") == "user":
                first_user_idx = i
                break

        # No user message found - can't shift meaningfully
        if first_user_idx is None: return 0, 0, 0

        # Start removing after first user message
        start_idx = first_user_idx + 1

        # Accumulate tokens until we reach target
        accumulated = 0
        end_idx = start_idx
        removed_turns = 0

        analyzer = self.session.context_analyzer

        for i in range(start_idx, len(conversation)):
            msg = conversation[i]

            # Count turns being removed (user messages indicate new turns)
            if msg.get("role") == "user":
                removed_turns += 1

            # Get token count for this message
            token_count = 0
            if analyzer:
                token_count = analyzer.get_message_token_count(i)
            if token_count == 0:
                # Estimate from message content
                token_count = analyzer._estimate_message_tokens(msg) if analyzer else 10

            accumulated += token_count
            end_idx = i + 1

            if accumulated >= target_tokens: break

        RNS.log(f"Context shift target at index {end_idx}, accumulated {accumulated} tokens, removing {removed_turns} turns", RNS.LOG_DEBUG)
        return start_idx, end_idx, accumulated, removed_turns

    def _create_shift_notification(self, removed_messages: int, removed_tokens: int,
                                   removed_turns: int, backup_file: Optional[Path]) -> Dict[str, Any]:

        backup_info = f" Original session preserved in {backup_file.name}." if backup_file else ""

        # Include cumulative stats if this isn't the first shift
        if self.shift_count > 0:
            total_messages = self.cumulative_removed_messages + removed_messages
            total_tokens = self.cumulative_removed_tokens + removed_tokens
            total_turns = self.cumulative_removed_turns + removed_turns
            
            content = (f"[Context shifted: removed {removed_messages} messages with ~{removed_tokens:,} tokens "
                       f"this shift, {total_messages} messages with ~{total_tokens:,} tokens total, "
                       f"{removed_turns} turns condensed this shift, {total_turns} total.{backup_info}]")
        
        else:
            content = (f"[Context shifted: removed {removed_messages} messages (~{removed_tokens:,} tokens), "
                       f"{removed_turns} prior turns condensed.{backup_info}]")

        return {"role": "user", "content": content}

    def perform_shift(self) -> tuple[bool, str]:
        analyzer = self.session.context_analyzer
        if not analyzer:
            RNS.log("ContextShiftManager: No analyzer available", RNS.LOG_WARNING)
            return False, "No context analyzer available"

        estimated_tokens = analyzer.estimate_current_tokens(self.session.conversation)
        if not self.should_shift(estimated_tokens): return False, ""

        context_limit, shift_factor = self._get_config()
        target_remove = int(context_limit * shift_factor)

        RNS.log(f"ContextShiftManager: Shifting context. Current estimate: {estimated_tokens}, "
                f"limit: {context_limit}, target removal: {target_remove}", RNS.LOG_INFO)

        # Check edge cases
        if len(self.session.conversation) < 3: return False, "Cannot shift: conversation too short"

        # Find first user message
        first_user_idx = None
        for i, msg in enumerate(self.session.conversation):
            if msg.get("role") == "user":
                first_user_idx = i
                break

        if first_user_idx is None: return False, "Cannot shift: no user message found"

        # Check if there's anything to remove after first user
        if first_user_idx + 1 >= len(self.session.conversation): return False, "Cannot shift: no messages after first user message"

        # Create backup
        backup_path = self._create_backup()

        # Find shift point
        start_idx, end_idx, removed_tokens, removed_turns = self._find_shift_point(target_remove)
        if end_idx == 0: return False, "Cannot shift: unable to find valid shift point"

        pre_shift_count = len(self.session.conversation)
        removed_messages = pre_shift_count - (2+len(self.session.conversation[end_idx:]))
        RNS.log(f"Removing {removed_messages} from session...", RNS.LOG_DEBUG)
        if removed_messages <= 0: return False, "Cannot shift: no messages to remove"

        # Update cumulative stats BEFORE creating notification
        self.cumulative_removed_messages += removed_messages
        self.cumulative_removed_tokens += removed_tokens
        self.cumulative_removed_turns += removed_turns

        # Perform the shift
        new_conversation = [ self.session.conversation[0],               # System prompt
                             self.session.conversation[first_user_idx] ] # First user message

        # Add shift notification
        notification = self._create_shift_notification(removed_messages, removed_tokens, removed_turns, backup_path)
        new_conversation.append(notification)

        # Add remaining messages
        new_conversation.extend(self.session.conversation[end_idx:])

        # Update conversation
        removed_count = len(self.session.conversation) - len(new_conversation) + 2  # +2 for kept messages
        self.session.conversation = new_conversation

        # Rebuild analyzer indices
        analyzer.rebuild_indices_after_shift(start_idx, end_idx)

        # Recalculate token estimate
        new_estimate = analyzer.recalculate_from_messages(self.session.conversation)
        self.session.input_tokens = new_estimate

        # Rebuild loaded_skills to match what's still in context
        self.session.rebuild_loaded_skills()

        self.shift_count += 1

        msg = f"Context shifted: removed {removed_messages} messages (~{removed_tokens} tokens)"
        RNS.log(f"ContextShiftManager: {msg}", RNS.LOG_INFO)

        return True, msg