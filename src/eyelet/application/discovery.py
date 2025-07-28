"""Hook and tool discovery service"""

from datetime import datetime
from pathlib import Path
from typing import Any

from eyelet.domain.models import HookType, ToolMatcher


class DiscoveryService:
    """Service for discovering available hooks and tools"""

    def __init__(self):
        self.docs_url = "https://docs.anthropic.com/en/docs/claude-code/hooks"
        self.cache_dir = Path.home() / ".eyelet" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_static_hooks(self) -> list[HookType]:
        """Get statically defined hook types"""
        return list(HookType)

    def get_static_tools(self) -> list[ToolMatcher]:
        """Get statically defined tool matchers"""
        return list(ToolMatcher)

    def discover_from_docs(self) -> list[HookType]:
        """Discover hook types from documentation"""
        # This would scrape the docs, but for now return static
        return self.get_static_hooks()

    def discover_tools_from_docs(self) -> list[ToolMatcher]:
        """Discover tools from documentation"""
        # This would scrape the docs, but for now return static
        return self.get_static_tools()

    def discover_from_runtime(self) -> list[HookType]:
        """Discover hooks from Claude Code runtime"""
        # This would probe the runtime, but for now return static
        return self.get_static_hooks()

    def discover_tools_from_runtime(self) -> list[ToolMatcher]:
        """Discover tools from Claude Code runtime"""
        # This would probe the runtime, but for now return static
        return self.get_static_tools()

    def discover_all_hooks(self) -> list[HookType]:
        """Discover hooks from all sources"""
        # In a full implementation, this would merge results from all sources
        return self.get_static_hooks()

    def discover_all_tools(self) -> list[ToolMatcher]:
        """Discover tools from all sources"""
        # In a full implementation, this would merge results from all sources
        return self.get_static_tools()

    def generate_combination_matrix(self) -> dict[str, list[str]]:
        """Generate all valid hook/tool combinations"""
        matrix = {}

        # Pre/Post tool use hooks can use any tool matcher
        tool_names = [t.value for t in ToolMatcher if t != ToolMatcher.ALL]
        tool_names.append(ToolMatcher.ALL.value)  # Add wildcard

        matrix[HookType.PRE_TOOL_USE.value] = tool_names
        matrix[HookType.POST_TOOL_USE.value] = tool_names

        # PreCompact has specific matchers
        matrix[HookType.PRE_COMPACT.value] = ["manual", "auto"]

        # Other hooks don't use matchers
        matrix[HookType.NOTIFICATION.value] = []
        matrix[HookType.USER_PROMPT_SUBMIT.value] = []
        matrix[HookType.STOP.value] = []
        matrix[HookType.SUBAGENT_STOP.value] = []

        return matrix

    def validate_discovery(self) -> dict[str, dict[str, Any]]:
        """Validate discovered hooks and tools"""
        results = {}

        # Validate hook types
        hooks = self.get_static_hooks()
        results['hook_types'] = {
            'valid': len(hooks) == 7,
            'count': len(hooks),
            'message': f"Found {len(hooks)} hook types (expected 7)"
        }

        # Validate tool matchers
        tools = self.get_static_tools()
        results['tools'] = {
            'valid': len(tools) >= 10,
            'count': len(tools),
            'message': f"Found {len(tools)} tools"
        }

        # Validate combinations
        matrix = self.generate_combination_matrix()
        total_combinations = sum(
            len(matchers) if matchers else 1
            for matchers in matrix.values()
        )
        results['combinations'] = {
            'valid': total_combinations > 20,
            'count': total_combinations,
            'message': f"Generated {total_combinations} combinations"
        }

        return results

    def check_for_updates(self) -> dict[str, Any] | None:
        """Check if there are updates to hooks/tools"""
        # This would check against a version endpoint or changelog
        # For now, return None (no updates)
        return None

    def export_discovery_data(self) -> dict[str, Any]:
        """Export all discovery data for caching/sharing"""
        return {
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat(),
            'hooks': [h.value for h in self.get_static_hooks()],
            'tools': [t.value for t in self.get_static_tools()],
            'matrix': self.generate_combination_matrix()
        }
