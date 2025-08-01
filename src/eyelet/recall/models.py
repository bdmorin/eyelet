"""Data models for Claude Code conversations."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class MessageData:
    """Represents a single message in a conversation."""
    
    uuid: str
    session_id: str
    parent_uuid: str | None
    timestamp: float
    timestamp_iso: str
    role: str  # 'user', 'assistant', 'system'
    message_type: str | None  # 'message', 'tool_use', etc.
    content: dict[str, Any]  # JSON content without binary data
    tool_name: str | None = None
    model: str | None = None
    search_text: str = ""  # Extracted searchable text


@dataclass
class ConversationData:
    """Represents a conversation session."""
    
    session_id: str
    project_path: str
    start_time: float
    end_time: float | None = None
    message_count: int = 0
    version: str | None = None
    git_branch: str | None = None
    working_directory: str | None = None
    summary: str | None = None


@dataclass
class SearchResult:
    """Search result with context."""
    
    message: MessageData
    conversation: ConversationData
    snippet: str  # Text snippet with search terms highlighted
    relevance_score: float = 0.0


@dataclass
class SearchFilter:
    """Filter criteria for searching conversations."""
    
    role: str | None = None
    tool_name: str | None = None
    session_id: str | None = None
    since: datetime | None = None
    until: datetime | None = None
    project_path: str | None = None
    limit: int = 100
    offset: int = 0