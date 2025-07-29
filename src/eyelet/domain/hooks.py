"""Domain models for hooks."""

from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class ExecutionResult(BaseModel):
    """Result of hook execution."""
    status: str
    duration_ms: Optional[int] = None
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class HookData(BaseModel):
    """Complete hook data structure."""
    
    # Core fields
    timestamp: str
    timestamp_unix: float
    hook_type: str
    tool_name: Optional[str] = None
    session_id: str
    transcript_path: str
    cwd: Path
    
    # Environment and context
    environment: Dict[str, Any] = Field(default_factory=dict)
    input_data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Execution results (added after completion)
    execution: Optional[ExecutionResult] = None
    completed_at: Optional[str] = None
    
    class Config:
        """Pydantic config."""
        arbitrary_types_allowed = True