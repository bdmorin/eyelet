"""Multi-threaded loader for Claude Code conversation files."""

import json
import os
import sqlite3
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Iterator

from eyelet.recall.models import ConversationData, MessageData
from eyelet.recall.parser import ConversationParser
from eyelet.services.sqlite_connection import ProcessLocalConnection, sqlite_retry


class ConversationLoader:
    """Multi-threaded loader for JSONL conversation files."""
    
    def __init__(self, db_path: Path):
        """Initialize loader with database path.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self._conn_manager = ProcessLocalConnection(db_path)
        self._parser = ConversationParser()
        self._claude_projects_dir = Path.home() / ".claude" / "projects"
    
    def load_all_projects(self, progress_callback=None) -> dict[str, Any]:
        """Load all conversations from ~/.claude/projects.
        
        Args:
            progress_callback: Optional callback(current, total, message)
            
        Returns:
            Dictionary with loading statistics
        """
        stats = {
            'files_processed': 0,
            'files_skipped': 0,
            'messages_loaded': 0,
            'conversations_loaded': 0,
            'errors': []
        }
        
        # Find all JSONL files
        jsonl_files = list(self._find_jsonl_files())
        total_files = len(jsonl_files)
        
        if progress_callback:
            progress_callback(0, total_files, "Starting conversation import...")
        
        # Process files in parallel
        max_workers = min(os.cpu_count() or 4, 8)  # Cap at 8 workers
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Submit all parsing jobs
            future_to_file = {
                executor.submit(self._parse_file_data, file_path): file_path
                for file_path in jsonl_files
            }
            
            # Process results as they complete
            for i, future in enumerate(as_completed(future_to_file)):
                file_path = future_to_file[future]
                
                try:
                    result = future.result()
                    if result:
                        # Load parsed data into database
                        self._load_file_data(result, file_path)
                        stats['files_processed'] += 1
                        stats['conversations_loaded'] += 1
                        stats['messages_loaded'] += result['message_count']
                    else:
                        stats['files_skipped'] += 1
                        
                except Exception as e:
                    stats['errors'].append(f"{file_path}: {str(e)}")
                    
                if progress_callback:
                    progress_callback(
                        i + 1, 
                        total_files, 
                        f"Processed {file_path.name}"
                    )
        
        # Optimize database after bulk load
        self._optimize_database()
        
        return stats
    
    def _find_jsonl_files(self) -> Iterator[Path]:
        """Find all JSONL files in Claude projects directory.
        
        Yields:
            Path objects for each JSONL file
        """
        if not self._claude_projects_dir.exists():
            return
        
        for project_dir in self._claude_projects_dir.iterdir():
            if project_dir.is_dir():
                for file_path in project_dir.glob("*.jsonl"):
                    # Skip if already loaded and unchanged
                    if not self._should_load_file(file_path):
                        continue
                    yield file_path
    
    def _should_load_file(self, file_path: Path) -> bool:
        """Check if file should be loaded based on modification time.
        
        Args:
            file_path: Path to JSONL file
            
        Returns:
            True if file should be loaded
        """
        conn = self._conn_manager.connection
        
        # Get file stats
        try:
            stat = file_path.stat()
            file_size = stat.st_size
            file_mtime = stat.st_mtime
        except OSError:
            return False
        
        # Check if already loaded
        cursor = conn.execute(
            "SELECT file_size, file_mtime FROM loaded_files WHERE file_path = ?",
            (str(file_path),)
        )
        row = cursor.fetchone()
        
        if row:
            # Skip if unchanged
            if row[0] == file_size and row[1] == file_mtime:
                return False
        
        return True
    
    @staticmethod
    def _parse_file_data(file_path: Path) -> dict[str, Any] | None:
        """Parse a single file (runs in worker process).
        
        Args:
            file_path: Path to JSONL file
            
        Returns:
            Parsed data dictionary or None if error
        """
        parser = ConversationParser()
        
        try:
            # Extract conversation metadata
            conversation = parser.extract_conversation_metadata(file_path)
            if not conversation:
                return None
            
            # Parse all messages
            messages = list(parser.parse_file(file_path))
            
            return {
                'conversation': conversation,
                'messages': messages,
                'message_count': len(messages)
            }
            
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None
    
    @sqlite_retry(max_attempts=5)
    def _load_file_data(self, data: dict[str, Any], file_path: Path) -> None:
        """Load parsed data into database.
        
        Args:
            data: Parsed conversation data
            file_path: Path to source file
        """
        conn = self._conn_manager.connection
        conversation: ConversationData = data['conversation']
        messages: list[MessageData] = data['messages']
        
        # Start transaction
        conn.execute("BEGIN EXCLUSIVE")
        
        try:
            # Delete existing data for this session
            conn.execute(
                "DELETE FROM messages WHERE session_id = ?",
                (conversation.session_id,)
            )
            conn.execute(
                "DELETE FROM conversations WHERE session_id = ?",
                (conversation.session_id,)
            )
            
            # Insert conversation
            conn.execute("""
                INSERT INTO conversations (
                    session_id, project_path, start_time, end_time,
                    message_count, version, git_branch, working_directory, summary
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                conversation.session_id,
                conversation.project_path,
                conversation.start_time,
                conversation.end_time,
                conversation.message_count,
                conversation.version,
                conversation.git_branch,
                conversation.working_directory,
                conversation.summary
            ))
            
            # Batch insert messages
            message_data = [
                (
                    msg.session_id,
                    msg.uuid,
                    msg.parent_uuid,
                    msg.timestamp,
                    msg.timestamp_iso,
                    msg.role,
                    msg.message_type,
                    json.dumps(msg.content),
                    msg.tool_name,
                    msg.model,
                    msg.search_text
                )
                for msg in messages
            ]
            
            conn.executemany("""
                INSERT INTO messages (
                    session_id, uuid, parent_uuid, timestamp, timestamp_iso,
                    role, message_type, content, tool_name, model, search_text
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, message_data)
            
            # Update loaded files tracking
            stat = file_path.stat()
            conn.execute("""
                INSERT OR REPLACE INTO loaded_files (
                    file_path, file_size, file_mtime, loaded_at, message_count
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                str(file_path),
                stat.st_size,
                stat.st_mtime,
                conversation.start_time,  # Use start time as loaded_at
                len(messages)
            ))
            
            # Commit transaction
            conn.execute("COMMIT")
            
        except Exception as e:
            # Rollback on error
            conn.execute("ROLLBACK")
            raise
    
    def _optimize_database(self) -> None:
        """Optimize database after bulk loading."""
        conn = self._conn_manager.connection
        
        # Analyze tables for query optimizer
        conn.execute("ANALYZE conversations")
        conn.execute("ANALYZE messages")
        conn.execute("ANALYZE messages_fts")
        
        # Checkpoint WAL to reduce file size
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        
        # Optimize FTS index
        conn.execute("INSERT INTO messages_fts(messages_fts) VALUES('optimize')")
    
    def get_loading_stats(self) -> dict[str, Any]:
        """Get statistics about loaded data.
        
        Returns:
            Dictionary with loading statistics
        """
        conn = self._conn_manager.connection
        
        stats = {}
        
        # Count conversations
        cursor = conn.execute("SELECT COUNT(*) FROM conversations")
        stats['total_conversations'] = cursor.fetchone()[0]
        
        # Count messages
        cursor = conn.execute("SELECT COUNT(*) FROM messages")
        stats['total_messages'] = cursor.fetchone()[0]
        
        # Count by role
        cursor = conn.execute("""
            SELECT role, COUNT(*) 
            FROM messages 
            GROUP BY role
        """)
        stats['messages_by_role'] = dict(cursor.fetchall())
        
        # Count loaded files
        cursor = conn.execute("SELECT COUNT(*) FROM loaded_files")
        stats['files_loaded'] = cursor.fetchone()[0]
        
        # Get date range
        cursor = conn.execute("""
            SELECT MIN(start_time), MAX(end_time)
            FROM conversations
        """)
        row = cursor.fetchone()
        if row and row[0]:
            from datetime import datetime
            stats['earliest_conversation'] = datetime.fromtimestamp(row[0])
            stats['latest_conversation'] = datetime.fromtimestamp(row[1]) if row[1] else None
        
        return stats