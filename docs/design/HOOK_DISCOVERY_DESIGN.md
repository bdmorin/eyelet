# Hook Discovery and Generation System Design

## Overview

The Rigging needs to dynamically discover and generate all possible hook combinations to ensure comprehensive coverage as Claude Code evolves. This document outlines our approach to creating a maintainable, extensible system.

## Hook Taxonomy

### Hook Types (7 total)
1. **PreToolUse** - Before tool execution
2. **PostToolUse** - After tool execution
3. **Notification** - UI notifications and idle events
4. **UserPromptSubmit** - Before processing user prompts
5. **Stop** - Main agent completion
6. **SubagentStop** - Subagent completion
7. **PreCompact** - Before context compaction

### Tool Matchers (Currently 10+)
- Task
- Bash
- Glob
- Grep
- Read
- Edit
- MultiEdit
- Write
- WebFetch
- WebSearch
- (Additional tools as Claude Code adds them)

### Special Matchers
- PreCompact: "manual" | "auto"
- Regex patterns: ".*" (match all)
- Custom patterns for specific use cases

## Hook Combination Matrix

### Total Combinations
- PreToolUse: 10+ tools × multiple match patterns
- PostToolUse: 10+ tools × multiple match patterns
- PreCompact: 2 specific matchers
- Others: No specific matchers (simpler)

This creates potentially 100+ unique hook combinations that our system must handle.

## Discovery System Architecture

### 1. Hook Registry
```python
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional, Any
import json

@dataclass
class HookRegistry:
    hook_types: List['HookType']
    tool_matchers: List['ToolMatcher']
    combinations: List['HookCombination']
    last_updated: datetime

@dataclass
class HookType:
    name: str
    description: str
    has_matchers: bool
    matcher_types: List[str]  # "tool", "event", "custom"

@dataclass
class ToolMatcher:
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]

@dataclass
class HookCombination:
    hook_type: str
    matcher: str
    is_valid: bool
    template: str
```

### 2. Discovery Methods

#### A. Documentation Scraping
```python
from typing import List
import httpx
from bs4 import BeautifulSoup

class DocScraper:
    """Automatically fetch and parse Claude Code documentation"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.Client()
    
    def discover_hooks(self) -> List[HookType]:
        """Discover available hook types from documentation"""
        pass
    
    def discover_tools(self) -> List[ToolMatcher]:
        """Discover available tools from documentation"""
        pass
```

#### B. Runtime Discovery
```python
from pathlib import Path
from typing import List, Optional
import json

class RuntimeDiscovery:
    """Probe Claude Code installation for available tools"""
    
    def __init__(self, claude_path: Optional[Path] = None, config_path: Optional[Path] = None):
        self.claude_path = claude_path or Path.home() / ".claude"
        self.config_path = config_path or self.claude_path / "settings.json"
    
    def probe_available_tools(self) -> List[str]:
        """Probe for available tools in the Claude installation"""
        pass
    
    def validate_hook_type(self, hook_type: str) -> bool:
        """Validate if a hook type is supported"""
        pass
```

#### C. Schema Inference
```python
from pathlib import Path
from typing import Dict, Any, Optional
import sqlite3
import json

class SchemaInferrer:
    """Analyze hook execution logs to infer data schemas"""
    
    def __init__(self, log_path: Path, db_path: Optional[Path] = None):
        self.log_path = log_path
        self.db_path = db_path or Path("rigging.db")
        self.connection = sqlite3.connect(self.db_path)
    
    def infer_input_schema(self, hook_type: str, tool: str) -> Dict[str, Any]:
        """Infer input schema from execution logs"""
        pass
    
    def infer_output_schema(self, hook_type: str) -> Dict[str, Any]:
        """Infer output schema from execution logs"""
        pass
```

### 3. Generation System

#### A. Template Generator
```python
from typing import List, Dict, Optional
from jinja2 import Template, Environment, FileSystemLoader

class TemplateGenerator:
    """Generate hook configurations from templates"""
    
    def __init__(self, registry: HookRegistry):
        self.registry = registry
        self.env = Environment(loader=FileSystemLoader('templates'))
        self.templates: Dict[str, Template] = {}
    
    def generate_all_combinations(self) -> List['HookConfig']:
        """Generate all possible hook configurations"""
        pass
    
    def generate_pattern(self, pattern: str) -> List['HookConfig']:
        """Generate hook configurations matching a pattern"""
        pass
```

#### B. Hook Configuration Builder
```python
from dataclasses import dataclass
from typing import Optional, Dict, Any
import json

@dataclass
class HookConfigBuilder:
    """Builder for hook configurations"""
    hook_type: str
    matcher: str
    handler: str  # Command to execute
    
    def build(self) -> 'HookConfig':
        """Build the hook configuration"""
        pass
    
    def validate(self) -> None:
        """Validate the configuration"""
        pass
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.__dict__, indent=2)
```

### 4. Update Detection System

#### A. Version Monitoring
```python
from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple

@dataclass
class ChangeEntry:
    version: str
    date: datetime
    changes: List[str]

class VersionMonitor:
    """Monitor Claude Code version for updates"""
    
    def __init__(self, current_version: str):
        self.current_version = current_version
        self.last_check = datetime.now()
    
    def check_for_updates(self) -> Tuple[bool, str]:
        """Check if updates are available"""
        pass
    
    def get_changelog(self) -> List[ChangeEntry]:
        """Get changelog entries"""
        pass
```

#### B. Diff Analysis
```python
from dataclasses import dataclass
from typing import List

@dataclass
class MigrationPlan:
    added_hooks: List[HookType]
    removed_hooks: List[HookType]
    added_tools: List[ToolMatcher]
    removed_tools: List[ToolMatcher]
    migration_steps: List[str]

class DiffAnalyzer:
    """Analyze differences between registry versions"""
    
    def __init__(self, old_registry: HookRegistry, new_registry: HookRegistry):
        self.old_registry = old_registry
        self.new_registry = new_registry
    
    def find_new_hooks(self) -> List[HookType]:
        """Find newly added hook types"""
        pass
    
    def find_new_tools(self) -> List[ToolMatcher]:
        """Find newly added tools"""
        pass
    
    def generate_migration(self) -> MigrationPlan:
        """Generate migration plan between versions"""
        pass
```

## Implementation Strategy

### Phase 1: Static Registry
1. Hardcode known hooks and tools
2. Manual updates based on documentation
3. Basic combination generation

### Phase 2: Semi-Automatic Discovery
1. Documentation scraping
2. Configuration file parsing
3. Update notifications

### Phase 3: Fully Automatic System
1. Runtime discovery
2. Schema inference from logs
3. Automatic template generation
4. Self-updating capability

## Data Structures

### Hook Definition Format
```json
{
  "hook_type": "PreToolUse",
  "matcher": "Bash",
  "handler": {
    "type": "command",
    "command": "rigging execute --workflow bash-validation"
  },
  "metadata": {
    "description": "Validate bash commands before execution",
    "created_by": "generator",
    "version": "1.0"
  }
}
```

### Combination Matrix Storage
```sql
CREATE TABLE hook_combinations (
    id INTEGER PRIMARY KEY,
    hook_type TEXT NOT NULL,
    matcher TEXT,
    is_valid BOOLEAN DEFAULT true,
    template_id TEXT,
    discovered_at DATETIME,
    last_verified DATETIME,
    metadata JSON
);

CREATE TABLE hook_schemas (
    id INTEGER PRIMARY KEY,
    hook_type TEXT NOT NULL,
    tool_name TEXT,
    input_schema JSON,
    output_schema JSON,
    examples JSON,
    updated_at DATETIME
);
```

## Update Workflow

1. **Detection Phase**
   - Monitor Claude Code version
   - Check documentation updates
   - Analyze new log entries

2. **Analysis Phase**
   - Compare with existing registry
   - Identify new combinations
   - Validate compatibility

3. **Generation Phase**
   - Create new templates
   - Update configuration builders
   - Generate migration scripts

4. **Notification Phase**
   - Alert user to changes
   - Provide update options
   - Show impact analysis

## CLI Commands for Discovery

```bash
# Discover all available hooks
rigging discover hooks

# Discover all available tools
rigging discover tools

# Generate combination matrix
rigging generate matrix

# Check for updates
rigging update check

# Apply updates
rigging update apply

# Export current registry
rigging export registry

# Validate hook configurations
rigging validate
```

## Example Usage

```python
# Initialize discovery system
registry = HookRegistry(
    hook_types=[],
    tool_matchers=[],
    combinations=[],
    last_updated=datetime.now()
)
scraper = DocScraper("https://docs.anthropic.com/en/docs/claude-code")

# Discover available hooks
hooks = scraper.discover_hooks()
tools = scraper.discover_tools()

# Generate combinations
generator = TemplateGenerator(registry)
combinations = generator.generate_all_combinations()

# Create hook configuration
for combo in combinations:
    builder = HookConfigBuilder(
        hook_type=combo.hook_type,
        matcher=combo.matcher,
        handler=f"rigging execute --workflow {combo.hook_type}-{combo.matcher}"
    )
    config = builder.build()
    
    # Add to user's configuration
    config_manager.add_hook(config)
```

## Maintenance Considerations

1. **Backward Compatibility**
   - Maintain support for deprecated hooks
   - Provide migration paths
   - Version configuration files

2. **Error Handling**
   - Graceful degradation for unknown hooks
   - Clear error messages
   - Fallback mechanisms

3. **Performance**
   - Cache discovery results
   - Lazy loading of schemas
   - Efficient combination generation

4. **Extensibility**
   - Plugin system for custom discoveries
   - User-defined hook types
   - Community contributions

## Future Enhancements

1. **AI-Powered Discovery**
   - Use Claude to analyze documentation
   - Automatic schema generation
   - Intelligent combination suggestions

2. **Live Monitoring**
   - Real-time hook execution tracking
   - Performance metrics per combination
   - Usage analytics

3. **Community Registry**
   - Share hook configurations
   - Crowd-sourced discoveries
   - Best practice templates