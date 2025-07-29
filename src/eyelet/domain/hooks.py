"""Domain models for hooks."""

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class ExecutionResult(BaseModel):
    """Result of hook execution."""

    status: str
    duration_ms: int | None = None
    output_data: dict[str, Any] | None = None
    error_message: str | None = None


class HookData(BaseModel):
    """Complete hook data structure."""

    # Core fields
    timestamp: str
    timestamp_unix: float
    hook_type: str
    tool_name: str | None = None
    session_id: str
    transcript_path: str
    cwd: Path

    # Environment and context
    environment: dict[str, Any] = Field(default_factory=dict)
    input_data: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    # Execution results (added after completion)
    execution: ExecutionResult | None = None
    completed_at: str | None = None

    class Config:
        """Pydantic config."""

        arbitrary_types_allowed = True
