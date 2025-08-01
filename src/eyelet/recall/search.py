"""Search functionality for Claude Code conversations."""

import json
from pathlib import Path
from typing import Any

from eyelet.recall.models import ConversationData, MessageData, SearchFilter, SearchResult
from eyelet.services.sqlite_connection import ProcessLocalConnection


class ConversationSearch:
    """Search conversations using SQLite FTS5."""
    
    def __init__(self, db_path: Path):
        """Initialize search with database path.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self._conn_manager = ProcessLocalConnection(db_path)
    
    def search(self, query: str, filter: SearchFilter | None = None) -> list[SearchResult]:
        """Perform full-text search with optional filters.
        
        Args:
            query: Search query string
            filter: Optional search filters
            
        Returns:
            List of search results sorted by relevance
        """
        if not filter:
            filter = SearchFilter()
        
        conn = self._conn_manager.connection
        
        # Build the search query
        sql_parts = ["""
            SELECT 
                m.id,
                m.session_id,
                m.uuid,
                m.parent_uuid,
                m.timestamp,
                m.timestamp_iso,
                m.role,
                m.message_type,
                m.content,
                m.tool_name,
                m.model,
                m.search_text,
                c.project_path,
                c.start_time,
                c.end_time,
                c.message_count,
                c.version,
                c.git_branch,
                c.working_directory,
                c.summary,
                snippet(messages_fts, 2, '[', ']', '...', 64) as snippet,
                bm25(messages_fts) as relevance_score
            FROM messages_fts
            JOIN messages m ON messages_fts.rowid = m.id
            JOIN conversations c ON m.session_id = c.session_id
        """]
        
        where_clauses = []
        params = []
        
        # Add FTS query
        if query:
            where_clauses.append("messages_fts MATCH ?")
            # Escape special FTS characters and prepare query
            fts_query = self._prepare_fts_query(query)
            params.append(fts_query)
        
        # Add filters
        if filter.role:
            where_clauses.append("m.role = ?")
            params.append(filter.role)
        
        if filter.tool_name:
            where_clauses.append("m.tool_name = ?")
            params.append(filter.tool_name)
        
        if filter.session_id:
            where_clauses.append("m.session_id = ?")
            params.append(filter.session_id)
        
        if filter.project_path:
            where_clauses.append("c.project_path = ?")
            params.append(filter.project_path)
        
        if filter.since:
            where_clauses.append("m.timestamp >= ?")
            params.append(filter.since.timestamp())
        
        if filter.until:
            where_clauses.append("m.timestamp <= ?")
            params.append(filter.until.timestamp())
        
        # Combine WHERE clauses
        if where_clauses:
            sql_parts.append("WHERE " + " AND ".join(where_clauses))
        
        # Add ordering and limits
        sql_parts.append("ORDER BY relevance_score DESC")
        
        if filter.limit > 0:
            sql_parts.append(f"LIMIT {filter.limit}")
            if filter.offset > 0:
                sql_parts.append(f"OFFSET {filter.offset}")
        
        # Execute query
        sql = " ".join(sql_parts)
        cursor = conn.execute(sql, params)
        
        # Build results
        results = []
        for row in cursor:
            # Create MessageData
            message = MessageData(
                uuid=row[2],
                session_id=row[1],
                parent_uuid=row[3],
                timestamp=row[4],
                timestamp_iso=row[5],
                role=row[6],
                message_type=row[7],
                content=json.loads(row[8]),
                tool_name=row[9],
                model=row[10],
                search_text=row[11]
            )
            
            # Create ConversationData
            conversation = ConversationData(
                session_id=row[1],
                project_path=row[12],
                start_time=row[13],
                end_time=row[14],
                message_count=row[15],
                version=row[16],
                git_branch=row[17],
                working_directory=row[18],
                summary=row[19]
            )
            
            # Create SearchResult
            result = SearchResult(
                message=message,
                conversation=conversation,
                snippet=row[20],
                relevance_score=row[21] if row[21] else 0.0
            )
            
            results.append(result)
        
        return results
    
    def _prepare_fts_query(self, query: str) -> str:
        """Prepare query for FTS5.
        
        Args:
            query: Raw search query
            
        Returns:
            FTS5-compatible query string
        """
        # Escape special FTS characters
        special_chars = ['"', '*', '-']
        for char in special_chars:
            query = query.replace(char, f'"{char}"')
        
        # Split into terms and quote phrases
        terms = []
        for term in query.split():
            # Quote terms with special characters
            if any(c in term for c in ['(', ')', ':']):
                terms.append(f'"{term}"')
            else:
                terms.append(term)
        
        return ' '.join(terms)
    
    def get_recent_conversations(self, limit: int = 10) -> list[ConversationData]:
        """Get most recent conversations.
        
        Args:
            limit: Maximum number of conversations to return
            
        Returns:
            List of recent conversations
        """
        conn = self._conn_manager.connection
        
        cursor = conn.execute("""
            SELECT 
                session_id,
                project_path,
                start_time,
                end_time,
                message_count,
                version,
                git_branch,
                working_directory,
                summary
            FROM conversations
            ORDER BY start_time DESC
            LIMIT ?
        """, (limit,))
        
        conversations = []
        for row in cursor:
            conversation = ConversationData(
                session_id=row[0],
                project_path=row[1],
                start_time=row[2],
                end_time=row[3],
                message_count=row[4],
                version=row[5],
                git_branch=row[6],
                working_directory=row[7],
                summary=row[8]
            )
            conversations.append(conversation)
        
        return conversations
    
    def get_conversation_messages(self, session_id: str) -> list[MessageData]:
        """Get all messages for a conversation.
        
        Args:
            session_id: Conversation session ID
            
        Returns:
            List of messages in chronological order
        """
        conn = self._conn_manager.connection
        
        cursor = conn.execute("""
            SELECT 
                uuid,
                session_id,
                parent_uuid,
                timestamp,
                timestamp_iso,
                role,
                message_type,
                content,
                tool_name,
                model,
                search_text
            FROM messages
            WHERE session_id = ?
            ORDER BY timestamp ASC
        """, (session_id,))
        
        messages = []
        for row in cursor:
            message = MessageData(
                uuid=row[0],
                session_id=row[1],
                parent_uuid=row[2],
                timestamp=row[3],
                timestamp_iso=row[4],
                role=row[5],
                message_type=row[6],
                content=json.loads(row[7]),
                tool_name=row[8],
                model=row[9],
                search_text=row[10]
            )
            messages.append(message)
        
        return messages
    
    def get_search_suggestions(self, partial_query: str, limit: int = 10) -> list[str]:
        """Get search suggestions based on partial query.
        
        Args:
            partial_query: Partial search query
            limit: Maximum suggestions to return
            
        Returns:
            List of suggested search terms
        """
        conn = self._conn_manager.connection
        
        # Get tool names that match
        tool_suggestions = []
        if partial_query:
            cursor = conn.execute("""
                SELECT DISTINCT tool_name 
                FROM messages 
                WHERE tool_name LIKE ? 
                AND tool_name IS NOT NULL
                LIMIT ?
            """, (f"{partial_query}%", limit // 2))
            tool_suggestions = [f"tool:{row[0]}" for row in cursor]
        
        # Get common terms from search text
        # This is a simplified approach - in production you might want
        # to maintain a separate terms index
        return tool_suggestions[:limit]
    
    def get_statistics(self) -> dict[str, Any]:
        """Get search statistics.
        
        Returns:
            Dictionary with search statistics
        """
        conn = self._conn_manager.connection
        
        stats = {}
        
        # Total searchable messages
        cursor = conn.execute("SELECT COUNT(*) FROM messages")
        stats['total_messages'] = cursor.fetchone()[0]
        
        # Messages by role
        cursor = conn.execute("""
            SELECT role, COUNT(*) 
            FROM messages 
            GROUP BY role
        """)
        stats['messages_by_role'] = dict(cursor.fetchall())
        
        # Top tools
        cursor = conn.execute("""
            SELECT tool_name, COUNT(*) as count
            FROM messages 
            WHERE tool_name IS NOT NULL
            GROUP BY tool_name
            ORDER BY count DESC
            LIMIT 10
        """)
        stats['top_tools'] = list(cursor.fetchall())
        
        # Database size
        cursor = conn.execute("SELECT page_count * page_size FROM pragma_page_count(), pragma_page_size()")
        stats['database_size'] = cursor.fetchone()[0]
        
        return stats