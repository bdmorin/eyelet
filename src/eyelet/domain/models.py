"""Core domain models for Eyelet"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class HookType(str, Enum):
    """Available hook types in Claude Code"""
    PRE_TOOL_USE = "PreToolUse"
    POST_TOOL_USE = "PostToolUse"
    NOTIFICATION = "Notification"
    USER_PROMPT_SUBMIT = "UserPromptSubmit"
    STOP = "Stop"
    SUBAGENT_STOP = "SubagentStop"
    PRE_COMPACT = "PreCompact"


class ToolMatcher(str, Enum):
    """Available tool matchers for hooks"""
    TASK = "Task"
    BASH = "Bash"
    GLOB = "Glob"
    GREP = "Grep"
    READ = "Read"
    EDIT = "Edit"
    MULTI_EDIT = "MultiEdit"
    WRITE = "Write"
    WEB_FETCH = "WebFetch"
    WEB_SEARCH = "WebSearch"
    ALL = ".*"  # Wildcard matcher


class PreCompactMatcher(str, Enum):
    """Special matchers for PreCompact hooks"""
    MANUAL = "manual"
    AUTO = "auto"


class HandlerType(str, Enum):
    """Types of hook handlers"""
    COMMAND = "command"
    WORKFLOW = "workflow"
    INLINE = "inline"


class Handler(BaseModel):
    """Hook handler configuration"""
    type: HandlerType
    command: str | None = None
    workflow: str | None = None
    script: str | None = None

    model_config = ConfigDict(use_enum_values=True)


class Hook(BaseModel):
    """A configured hook"""
    id: str | None = Field(default=None, description="Unique identifier")
    type: HookType
    matcher: str | None = Field(default=None, description="Tool or event matcher")
    handler: Handler
    description: str | None = None
    enabled: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(use_enum_values=True)

    def is_valid_matcher(self) -> bool:
        """Check if the matcher is valid for this hook type"""
        if self.type in [HookType.PRE_TOOL_USE, HookType.POST_TOOL_USE]:
            return self.matcher is not None
        elif self.type == HookType.PRE_COMPACT:
            return self.matcher in [PreCompactMatcher.MANUAL.value, PreCompactMatcher.AUTO.value]
        else:
            return self.matcher is None


class HookExecution(BaseModel):
    """Record of a hook execution"""
    id: int | None = None
    hook_id: str
    hook_type: HookType
    tool_name: str | None = None
    timestamp: datetime = Field(default_factory=datetime.now)
    input_data: dict[str, Any]
    output_data: dict[str, Any] | None = None
    duration_ms: int | None = None
    status: str = "pending"  # pending, success, error
    error_message: str | None = None

    model_config = ConfigDict(use_enum_values=True)


class Workflow(BaseModel):
    """A workflow definition"""
    id: str
    name: str
    description: str | None = None
    steps: list[dict[str, Any]]  # Workflow step definitions
    variables: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Template(BaseModel):
    """A hook configuration template"""
    id: str
    name: str
    description: str
    category: str
    hooks: list[Hook]
    variables: dict[str, Any] = Field(default_factory=dict)
    version: str = "1.0.0"
    author: str | None = None
    tags: list[str] = Field(default_factory=list)


class HookConfiguration(BaseModel):
    """Complete hook configuration"""
    hooks: list[Hook] = Field(default_factory=list)
    version: str = "1.0"
    metadata: dict[str, Any] = Field(default_factory=dict)

    def add_hook(self, hook: Hook) -> None:
        """Add a hook to the configuration"""
        if not hook.id:
            hook.id = f"{hook.type}_{hook.matcher or 'default'}_{len(self.hooks)}"
        self.hooks.append(hook)

    def remove_hook(self, hook_id: str) -> bool:
        """Remove a hook by ID"""
        original_length = len(self.hooks)
        self.hooks = [h for h in self.hooks if h.id != hook_id]
        return len(self.hooks) < original_length

    def get_hooks_by_type(self, hook_type: HookType) -> list[Hook]:
        """Get all hooks of a specific type"""
        return [h for h in self.hooks if h.type == hook_type]
