"""Parser for Claude Code JSONL conversation files."""

import json
import re
from pathlib import Path
from typing import Any, Iterator

from eyelet.recall.models import ConversationData, MessageData


class ConversationParser:
    """Parses Claude Code JSONL files, skipping binary data."""
    
    # Pattern to identify base64 data
    BASE64_PATTERN = re.compile(r'"data":\s*"[A-Za-z0-9+/=]{100,}"')
    
    def parse_file(self, jsonl_path: Path) -> Iterator[MessageData]:
        """Parse a JSONL file, yielding message data.
        
        Args:
            jsonl_path: Path to JSONL file
            
        Yields:
            MessageData objects for each valid message
        """
        session_id = jsonl_path.stem
        
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    # Skip empty lines
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Parse JSON
                    data = json.loads(line)
                    
                    # Skip non-message entries
                    if data.get('type') not in ['user', 'assistant', 'system', 'summary']:
                        continue
                    
                    # Extract message data
                    message = self._extract_message(data, session_id)
                    if message:
                        yield message
                        
                except json.JSONDecodeError as e:
                    # Log error but continue processing
                    print(f"Error parsing line {line_num} in {jsonl_path}: {e}")
                except Exception as e:
                    print(f"Unexpected error at line {line_num} in {jsonl_path}: {e}")
    
    def _extract_message(self, data: dict[str, Any], session_id: str) -> MessageData | None:
        """Extract message data from parsed JSON.
        
        Args:
            data: Parsed JSON data
            session_id: Session ID from filename
            
        Returns:
            MessageData or None if not a valid message
        """
        # Handle summary entries
        if data.get('type') == 'summary':
            return None  # We'll use these for conversation metadata later
        
        # Extract base fields
        message_type = data.get('type')
        if message_type not in ['user', 'assistant', 'system']:
            return None
        
        # Get message content
        message_data = data.get('message', {})
        if not message_data:
            return None
        
        # Clean content (remove binary data)
        content = self._clean_content(message_data)
        
        # Extract searchable text
        search_text = self._extract_search_text(content)
        
        # Extract tool information if present
        tool_name = None
        if message_type == 'assistant':
            tool_uses = content.get('content', [])
            if isinstance(tool_uses, list):
                for item in tool_uses:
                    if isinstance(item, dict) and item.get('type') == 'tool_use':
                        tool_name = item.get('name')
                        break
        
        return MessageData(
            uuid=data.get('uuid', ''),
            session_id=session_id,
            parent_uuid=data.get('parentUuid'),
            timestamp=self._parse_timestamp(data.get('timestamp', '')),
            timestamp_iso=data.get('timestamp', ''),
            role=message_type,
            message_type=data.get('userType'),
            content=content,
            tool_name=tool_name,
            model=message_data.get('model'),
            search_text=search_text
        )
    
    def _clean_content(self, content: dict[str, Any]) -> dict[str, Any]:
        """Remove binary data from content.
        
        Args:
            content: Raw content dictionary
            
        Returns:
            Cleaned content without base64 data
        """
        # Deep copy to avoid modifying original
        cleaned = json.loads(json.dumps(content))
        
        # Remove base64 image data
        if 'content' in cleaned and isinstance(cleaned['content'], list):
            cleaned_items = []
            for item in cleaned['content']:
                if isinstance(item, dict):
                    # Skip image items with base64 data
                    if (item.get('type') == 'image' and 
                        isinstance(item.get('source'), dict) and
                        item['source'].get('type') == 'base64'):
                        # Keep metadata but remove data
                        cleaned_item = {
                            'type': 'image',
                            'source': {
                                'type': 'base64',
                                'media_type': item['source'].get('media_type', 'image/png'),
                                'data': '[BINARY_DATA_REMOVED]'
                            }
                        }
                        cleaned_items.append(cleaned_item)
                    else:
                        cleaned_items.append(item)
                else:
                    cleaned_items.append(item)
            cleaned['content'] = cleaned_items
        
        return cleaned
    
    def _extract_search_text(self, content: dict[str, Any]) -> str:
        """Extract searchable text from message content.
        
        Args:
            content: Cleaned message content
            
        Returns:
            Searchable text string
        """
        texts = []
        
        # Extract from content array
        if 'content' in content:
            items = content['content']
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        if item.get('type') == 'text':
                            texts.append(item.get('text', ''))
                        elif item.get('type') == 'tool_use':
                            # Include tool name and inputs
                            texts.append(f"Tool: {item.get('name', '')}")
                            inputs = item.get('input', {})
                            if isinstance(inputs, dict):
                                # Extract command for Bash tool
                                if 'command' in inputs:
                                    texts.append(f"Command: {inputs['command']}")
                                # Extract other string inputs
                                for key, value in inputs.items():
                                    if isinstance(value, str) and len(value) < 1000:
                                        texts.append(f"{key}: {value}")
            elif isinstance(items, str):
                texts.append(items)
        
        # Extract role
        role = content.get('role', '')
        if role:
            texts.append(f"Role: {role}")
        
        return ' '.join(texts)
    
    def _parse_timestamp(self, timestamp_str: str) -> float:
        """Parse ISO timestamp to Unix timestamp.
        
        Args:
            timestamp_str: ISO format timestamp
            
        Returns:
            Unix timestamp as float
        """
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            return dt.timestamp()
        except Exception:
            return 0.0
    
    def extract_conversation_metadata(self, jsonl_path: Path) -> ConversationData | None:
        """Extract conversation metadata from JSONL file.
        
        Args:
            jsonl_path: Path to JSONL file
            
        Returns:
            ConversationData or None if no valid data found
        """
        session_id = jsonl_path.stem
        project_path = str(jsonl_path.parent)
        
        first_timestamp = None
        last_timestamp = None
        message_count = 0
        summary = None
        version = None
        git_branch = None
        working_directory = None
        
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    
                    # Extract summary
                    if data.get('type') == 'summary':
                        summary = data.get('summary', '')
                    
                    # Extract metadata from messages
                    elif data.get('type') in ['user', 'assistant']:
                        message_count += 1
                        
                        # Track timestamps
                        timestamp = self._parse_timestamp(data.get('timestamp', ''))
                        if timestamp:
                            if first_timestamp is None or timestamp < first_timestamp:
                                first_timestamp = timestamp
                            if last_timestamp is None or timestamp > last_timestamp:
                                last_timestamp = timestamp
                        
                        # Extract metadata from first user message
                        if not version and data.get('type') == 'user':
                            version = data.get('version')
                            git_branch = data.get('gitBranch')
                            working_directory = data.get('cwd')
                            
                except Exception:
                    continue
        
        if first_timestamp is None:
            return None
        
        return ConversationData(
            session_id=session_id,
            project_path=project_path,
            start_time=first_timestamp,
            end_time=last_timestamp,
            message_count=message_count,
            version=version,
            git_branch=git_branch,
            working_directory=working_directory,
            summary=summary
        )