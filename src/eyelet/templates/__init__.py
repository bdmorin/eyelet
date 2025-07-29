"""Hook template system for eyelet.

This module provides templates for common Claude Code hook patterns,
based on analysis of real-world examples and best practices.
"""

from .generators import (
    generate_enhancement_hook,
    generate_logging_hook,
    generate_safety_hook,
    generate_workflow_hook,
    get_template_info,
    list_available_templates,
)

__all__ = [
    "generate_safety_hook",
    "generate_logging_hook",
    "generate_enhancement_hook",
    "generate_workflow_hook",
    "list_available_templates",
    "get_template_info"
]
