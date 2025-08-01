"""SQLite migrations for conversation search feature."""

# Conversation search schema
CONVERSATION_SCHEMA_V1 = """
-- Conversations table
CREATE TABLE IF NOT EXISTS conversations (
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
CREATE TABLE IF NOT EXISTS messages (
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
    FOREIGN KEY (session_id) REFERENCES conversations(session_id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_conversations_project ON conversations(project_path);
CREATE INDEX IF NOT EXISTS idx_conversations_time ON conversations(start_time);

CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_messages_role ON messages(role);
CREATE INDEX IF NOT EXISTS idx_messages_tool ON messages(tool_name) WHERE tool_name IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_messages_uuid ON messages(uuid);

-- Full-text search virtual table
CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
    session_id UNINDEXED,
    role UNINDEXED,
    search_text,
    content=messages,
    content_rowid=id
);

-- Triggers to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS messages_ai AFTER INSERT ON messages BEGIN
    INSERT INTO messages_fts(rowid, session_id, role, search_text)
    VALUES (new.id, new.session_id, new.role, new.search_text);
END;

CREATE TRIGGER IF NOT EXISTS messages_ad AFTER DELETE ON messages BEGIN
    DELETE FROM messages_fts WHERE rowid = old.id;
END;

CREATE TRIGGER IF NOT EXISTS messages_au AFTER UPDATE ON messages BEGIN
    DELETE FROM messages_fts WHERE rowid = old.id;
    INSERT INTO messages_fts(rowid, session_id, role, search_text)
    VALUES (new.id, new.session_id, new.role, new.search_text);
END;

-- Metadata table for tracking loaded files
CREATE TABLE IF NOT EXISTS loaded_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL UNIQUE,
    file_size INTEGER NOT NULL,
    file_mtime REAL NOT NULL,
    loaded_at REAL NOT NULL,
    message_count INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_loaded_files_path ON loaded_files(file_path);
"""

# Add to the main migrations list
CONVERSATION_MIGRATIONS = [
    (2, "Add conversation search tables", CONVERSATION_SCHEMA_V1),
]