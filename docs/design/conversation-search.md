# Conversation Search Design

## Overview
A feature to search and analyze Claude Code conversations from JSONL files in `~/.claude/projects`.

## Module Name: `recall`
- **Recall**: Search past conversations
- **Eavesdrop** (future): Watch live conversations

## Architecture

### 1. Module Structure
```
src/eyelet/recall/
├── __init__.py
├── models.py          # Conversation data models
├── parser.py          # JSONL parser (skips binary data)
├── loader.py          # Multi-threaded loader
├── search.py          # Search functionality
└── migrations.py      # SQLite schema for conversations
```

### 2. Database Schema
```sql
-- Conversations table
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL UNIQUE,
    project_path TEXT NOT NULL,
    start_time REAL NOT NULL,
    end_time REAL,
    message_count INTEGER DEFAULT 0,
    -- Metadata
    version TEXT,
    git_branch TEXT,
    working_directory TEXT,
    -- Full-text search
    summary TEXT
);

-- Messages table
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    uuid TEXT NOT NULL UNIQUE,
    parent_uuid TEXT,
    timestamp REAL NOT NULL,
    timestamp_iso TEXT NOT NULL,
    role TEXT NOT NULL,  -- 'user', 'assistant', 'system'
    message_type TEXT,   -- 'message', 'tool_use', etc.
    -- Content (excluding binary data)
    content TEXT,        -- JSON string without base64 data
    -- Extracted fields for searching
    tool_name TEXT,      -- For tool_use messages
    model TEXT,
    -- Full-text search
    search_text TEXT,    -- Extracted searchable text
    FOREIGN KEY (session_id) REFERENCES conversations(session_id)
);

-- Indexes
CREATE INDEX idx_messages_session ON messages(session_id);
CREATE INDEX idx_messages_timestamp ON messages(timestamp);
CREATE INDEX idx_messages_role ON messages(role);
CREATE INDEX idx_messages_tool ON messages(tool_name);

-- Full-text search
CREATE VIRTUAL TABLE messages_fts USING fts5(
    session_id,
    search_text,
    content=messages,
    content_rowid=id
);
```

### 3. Core Components

#### Parser (`parser.py`)
```python
class ConversationParser:
    """Parses Claude Code JSONL files, skipping binary data."""
    
    def parse_message(self, line: str) -> MessageData:
        """Parse a single JSONL line, removing base64 images."""
        
    def extract_search_text(self, message: dict) -> str:
        """Extract searchable text from message content."""
```

#### Loader (`loader.py`)
```python
class ConversationLoader:
    """Multi-threaded loader for JSONL files."""
    
    def load_all_projects(self) -> None:
        """Load all conversations from ~/.claude/projects."""
        
    def watch_for_updates(self) -> None:
        """Watch for new messages (future feature)."""
```

#### Search (`search.py`)
```python
class ConversationSearch:
    """Search conversations using SQLite FTS5."""
    
    def search(self, query: str, filters: SearchFilter) -> list[SearchResult]:
        """Perform full-text search with optional filters."""
```

### 4. CLI Integration
```bash
# Main command
uvx eyelet search-convo "error handling"

# Future options (not MVP)
uvx eyelet search-convo --role user --last 24h
uvx eyelet search-convo --tool Bash --session <id>
```

### 5. TUI Design
- Search box with real-time results (like fzf)
- Results show:
  - Message preview
  - Timestamp
  - Role (user/assistant)
  - Session info
- Keyboard shortcuts:
  - `/` - Focus search
  - `Enter` - View full message
  - `Ctrl+C` - Copy message
  - `Esc` - Exit

### 6. Performance Strategy
1. **Initial Load**:
   - Multi-threaded JSONL parsing
   - Batch SQLite inserts
   - Progress bar during loading
   
2. **Search Performance**:
   - SQLite FTS5 for fast full-text search
   - Indexed fields for filtering
   - Lazy loading of full content

3. **Memory Efficiency**:
   - Stream JSONL files
   - Skip base64 data during parsing
   - Store only searchable content

### 7. Integration Points
- Reuse `ProcessLocalConnection` from existing SQLite infrastructure
- Extend `QueryService` pattern for conversation queries
- Use existing migration system for schema management
- Integrate with existing TUI framework (Textual)

## Implementation Plan
1. Create `recall` module structure
2. Implement JSONL parser with binary data filtering
3. Build SQLite schema and migrations
4. Create multi-threaded loader
5. Implement search functionality
6. Add CLI command
7. Build TUI interface
8. Profile and optimize performance