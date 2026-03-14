# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

"""Context management for lc sessions."""

import RNS
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from lc.session import Session


@dataclass
class MessageTokenInfo:
    """Token information for a single message."""
    role: str
    index: int  # Index in conversation list
    estimated_tokens: int
    is_estimated: bool = True  # True if heuristic, False if from actual API data


@dataclass
class TurnTokenBreakdown:
    """Token breakdown for a single turn."""
    turn: int
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    timestamp: float
    message_tokens: List[MessageTokenInfo] = field(default_factory=list)


class ContextAnalyzer:
    """Analyzes and tracks per-message token usage for context management."""

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
                if isinstance(content, str):
                    char_counts.append(len(content))
                elif isinstance(content, list):
                    # Multimodal content - count text parts
                    total_chars = 0
                    for item in content:
                        if item.get("type") == "text":
                            total_chars += len(item.get("text", ""))
                    char_counts.append(max(total_chars, 1))  # At least 1 char
                else:
                    char_counts.append(1)

            total_chars = sum(char_counts)

            # Distribute tokens proportionally by character count
            for i, (msg, chars) in enumerate(zip(new_messages, char_counts)):
                # Proportional allocation
                if total_chars > 0:
                    ratio = chars / total_chars
                    estimated_tokens = int(token_delta * ratio)
                else:
                    estimated_tokens = max(1, token_delta // new_message_count)

                # Find the actual index in conversation
                msg_index = len(conversation) - new_message_count + i

                message_tokens.append(MessageTokenInfo(
                    role=msg.get("role", "unknown"),
                    index=msg_index,
                    estimated_tokens=estimated_tokens,
                    is_estimated=False  # Based on actual API data
                ))
        elif new_message_count > 0:
            # No token delta but new messages (edge case: zero tokens somehow)
            # Use character-based heuristic
            new_messages = conversation[-new_message_count:]
            for i, msg in enumerate(new_messages):
                msg_index = len(conversation) - new_message_count + i
                estimated = self._estimate_message_tokens(msg)
                message_tokens.append(MessageTokenInfo(
                    role=msg.get("role", "unknown"),
                    index=msg_index,
                    estimated_tokens=estimated,
                    is_estimated=True
                ))

        # Handle the completion/assistant message
        if completion_tokens > 0:
            # Find the last assistant message
            for i in range(len(conversation) - 1, -1, -1):
                if conversation[i].get("role") == "assistant":
                    message_tokens.append(MessageTokenInfo(
                        role="assistant",
                        index=i,
                        estimated_tokens=completion_tokens,
                        is_estimated=False
                    ))
                    break

        breakdown = TurnTokenBreakdown(
            turn=self.session.turn_count + 1,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            timestamp=time.time(),
            message_tokens=message_tokens
        )

        self.turn_breakdowns.append(breakdown)

        # Update tracking state
        self._last_conversation_length = len(conversation)
        self._last_prompt_tokens = prompt_tokens

        RNS.log(f"ContextAnalyzer recorded turn {breakdown.turn}: "
                f"prompt={prompt_tokens}, completion={completion_tokens}, "
                f"total={total_tokens}, new_msgs={new_message_count}, "
                f"tracked={len(message_tokens)}", RNS.LOG_DEBUG)
        
        for m in message_tokens:
            RNS.log(f"{m.index} {m.role}: {m.estimated_tokens}")

        return breakdown

    def _estimate_message_tokens(self, message: Dict[str, Any]) -> int:
        """Estimate token count for a single message using character heuristic."""
        content = message.get("content", "")
        role = message.get("role", "unknown")

        if isinstance(content, str):
            char_count = len(content)
        elif isinstance(content, list):
            # Multimodal - count text parts, add estimate for image overhead
            char_count = 0
            image_count = 0
            for item in content:
                if item.get("type") == "text":
                    char_count += len(item.get("text", ""))
                elif item.get("type") == "image_url":
                    image_count += 1
            # Add token estimate for image (typically ~200-500 tokens depending on model)
            char_count += image_count * 300
        else:
            char_count = 0

        # Add overhead for message structure (role, etc.)
        overhead = 10

        estimated = max(1, int((char_count + overhead) / self.CHARS_PER_TOKEN))
        RNS.log(f"ContextAnalyzer estimated {role} message: {char_count} chars ~ {estimated} tokens", RNS.LOG_DEBUG)

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
        if not self.turn_breakdowns:
            # No history - use pure heuristic
            total = sum(self._estimate_message_tokens(msg) for msg in conversation)
            RNS.log(f"ContextAnalyzer estimated total (no history): {total} tokens for {len(conversation)} messages", RNS.LOG_DEBUG)
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
            RNS.log(f"ContextAnalyzer estimated total: {last_breakdown.prompt_tokens} (known) + {estimated_new} ({new_count} new) = {total} tokens", RNS.LOG_DEBUG)
        else:
            RNS.log(f"ContextAnalyzer estimated total: {total} tokens (no new messages)", RNS.LOG_DEBUG)

        return total

    def get_message_token_count(self, conversation_index: int) -> int:
        """Get token count for a specific message by index.

        Returns tracked value if available, otherwise estimates.
        """
        # Search through turn breakdowns
        for breakdown in self.turn_breakdowns:
            for msg_info in breakdown.message_tokens:
                if msg_info.index == conversation_index:
                    return msg_info.estimated_tokens

        # Not tracked - estimate from current conversation
        if 0 <= conversation_index < len(self.session.conversation):
            return self._estimate_message_tokens(self.session.conversation[conversation_index])

        return 0

    def to_dict(self) -> List[Dict[str, Any]]:
        """Serialize turn breakdowns for persistence."""
        result = []
        for bd in self.turn_breakdowns:
            result.append({
                "turn": bd.turn,
                "prompt_tokens": bd.prompt_tokens,
                "completion_tokens": bd.completion_tokens,
                "total_tokens": bd.total_tokens,
                "timestamp": bd.timestamp,
                "message_tokens": [
                    {
                        "role": mt.role,
                        "index": mt.index,
                        "estimated_tokens": mt.estimated_tokens,
                        "is_estimated": mt.is_estimated
                    }
                    for mt in bd.message_tokens
                ]
            })
        return result

    @classmethod
    def from_dict(cls, session: "Session", data: List[Dict[str, Any]]) -> "ContextAnalyzer":
        """Deserialize turn breakdowns."""
        analyzer = cls(session)

        for item in data:
            breakdown = TurnTokenBreakdown(
                turn=item.get("turn", 0),
                prompt_tokens=item.get("prompt_tokens", 0),
                completion_tokens=item.get("completion_tokens", 0),
                total_tokens=item.get("total_tokens", 0),
                timestamp=item.get("timestamp", 0),
                message_tokens=[
                    MessageTokenInfo(
                        role=mt.get("role", "unknown"),
                        index=mt.get("index", 0),
                        estimated_tokens=mt.get("estimated_tokens", 0),
                        is_estimated=mt.get("is_estimated", True)
                    )
                    for mt in item.get("message_tokens", [])
                ]
            )
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
        else:
            RNS.log("ContextAnalyzer restored from dict: no turn data", RNS.LOG_DEBUG)

        return analyzer
