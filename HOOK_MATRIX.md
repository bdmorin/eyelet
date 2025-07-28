# Rigging Hook Combination Matrix

## Current Hook/Tool Combinations

Based on Claude Code documentation and runtime analysis, here are all possible hook combinations:

### PreToolUse Hooks
| Tool | Matcher Pattern | Purpose | Example Use Case |
|------|----------------|---------|------------------|
| Task | `"Task"` | Before subagent tasks | Validate task descriptions |
| Bash | `"Bash"` | Before shell commands | Command validation/sandboxing |
| Glob | `"Glob"` | Before file pattern matching | Path restrictions |
| Grep | `"Grep"` | Before text search | Search term filtering |
| Read | `"Read"` | Before file reading | Access control |
| Edit | `"Edit"` | Before file editing | Change validation |
| MultiEdit | `"MultiEdit"` | Before multiple edits | Bulk change review |
| Write | `"Write"` | Before file writing | Content filtering |
| WebFetch | `"WebFetch"` | Before web requests | URL allowlisting |
| WebSearch | `"WebSearch"` | Before web searches | Query filtering |
| * | `".*"` | Match all tools | Universal pre-processing |

### PostToolUse Hooks
| Tool | Matcher Pattern | Purpose | Example Use Case |
|------|----------------|---------|------------------|
| Task | `"Task"` | After subagent completion | Result processing |
| Bash | `"Bash"` | After command execution | Output logging |
| Glob | `"Glob"` | After file listing | Result caching |
| Grep | `"Grep"` | After search completion | Match analysis |
| Read | `"Read"` | After file reading | Content auditing |
| Edit | `"Edit"` | After file editing | Change tracking |
| MultiEdit | `"MultiEdit"` | After multiple edits | Batch logging |
| Write | `"Write"` | After file writing | Backup creation |
| WebFetch | `"WebFetch"` | After web fetch | Response caching |
| WebSearch | `"WebSearch"` | After search results | Result enhancement |
| * | `".*"` | Match all tools | Universal post-processing |

### Other Hook Types
| Hook Type | Matcher | Purpose | Example Use Case |
|-----------|---------|---------|------------------|
| Notification | N/A | UI notifications | User alerts |
| UserPromptSubmit | N/A | Before prompt processing | Context injection |
| Stop | N/A | Main agent completion | Session cleanup |
| SubagentStop | N/A | Subagent completion | Task finalization |
| PreCompact | `"manual"` | Manual compaction | User-triggered cleanup |
| PreCompact | `"auto"` | Auto compaction | Memory management |

## Total Combinations

- **PreToolUse**: 11 combinations (10 specific tools + wildcard)
- **PostToolUse**: 11 combinations (10 specific tools + wildcard)
- **PreCompact**: 2 combinations (manual/auto)
- **Other Hooks**: 4 combinations (no matchers)
- **Total**: 28 primary combinations

## Extended Patterns

### Regex Matchers
```json
{
  "matcher": "^(Read|Write|Edit)$",
  "description": "Match file operations only"
}
```

### Conditional Matchers
```json
{
  "matcher": "Bash",
  "condition": "command.includes('rm')",
  "description": "Only match destructive commands"
}
```

### Combined Hooks
```json
{
  "hooks": [
    {"type": "PreToolUse", "matcher": "Bash"},
    {"type": "PostToolUse", "matcher": "Bash"}
  ],
  "description": "Full command lifecycle monitoring"
}
```

## Discovery Strategies

### 1. Static Analysis
- Parse Claude Code source/documentation
- Extract tool definitions
- Map to hook types

### 2. Runtime Probing
```bash
# List available tools (using Rigging discovery)
rigging discover tools

# Test hook compatibility
rigging validate --hook-type PreToolUse --matcher NewTool
```

### 3. Log Analysis
```sql
-- Extract unique tool names from execution logs
SELECT DISTINCT 
    json_extract(payload, '$.tool_name') as tool
FROM executions
WHERE hook_type IN ('PreToolUse', 'PostToolUse');
```

### 4. Documentation Monitoring
- Watch https://docs.anthropic.com/en/docs/claude-code/hooks
- RSS/API monitoring for updates
- Changelog analysis

## Implementation Priority

### Phase 1: Core Tools (Week 1)
- Bash, Read, Write, Edit hooks
- Basic wildcard matchers
- Essential lifecycle hooks

### Phase 2: Extended Tools (Week 2)
- Glob, Grep, MultiEdit
- WebFetch, WebSearch
- Task hooks

### Phase 3: Advanced Patterns (Week 3)
- Regex matchers
- Conditional logic
- Combined hook chains

### Phase 4: Auto-Discovery (Week 4)
- Documentation scraper
- Runtime detection
- Update notifications

## Versioning Strategy

```yaml
# hooks-matrix.yaml
version: "1.0"
last_updated: "2024-01-20"
claude_code_version: "1.2.3"

hooks:
  PreToolUse:
    tools: [Task, Bash, Glob, ...]
    patterns: [".*", "^Web.*"]
  
  PostToolUse:
    tools: [Task, Bash, Glob, ...]
    patterns: [".*", "^Web.*"]
```

## Update Detection

```python
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class SchemaChange:
    field: str
    old_type: str
    new_type: str

@dataclass
class MatrixUpdate:
    added_tools: List[str]
    removed_tools: List[str]
    added_hooks: List[str]
    changed_schemas: Dict[str, SchemaChange]

def detect_updates(old_matrix: Matrix, new_matrix: Matrix) -> MatrixUpdate:
    """Compare matrices and return differences"""
    pass
```