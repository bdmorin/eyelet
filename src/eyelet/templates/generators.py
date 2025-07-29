"""Template generators for common hook patterns."""

from typing import Any

# Template metadata
TEMPLATES = {
    "safety-check": {
        "name": "Safety Check Hook",
        "description": "Prevents dangerous commands from executing",
        "hook_types": ["PreToolUse"],
        "languages": ["python", "rust"],
        "pattern": "safety",
        "example_use_cases": [
            "Block 'rm -rf /' commands",
            "Prevent sudo without approval",
            "Validate file paths",
            "Check for destructive operations",
        ],
    },
    "logger": {
        "name": "Universal Logger Hook",
        "description": "Logs all tool usage for analysis and debugging",
        "hook_types": ["PreToolUse", "PostToolUse"],
        "languages": ["python"],
        "pattern": "logging",
        "example_use_cases": [
            "Command history tracking",
            "Performance monitoring",
            "Usage analytics",
            "Debugging tool interactions",
        ],
    },
    "enhancer": {
        "name": "Output Enhancement Hook",
        "description": "Modifies or enhances tool outputs",
        "hook_types": ["PostToolUse"],
        "languages": ["python"],
        "pattern": "enhancement",
        "example_use_cases": [
            "Format command outputs",
            "Add context to results",
            "Filter sensitive information",
            "Add metadata",
        ],
    },
    "workflow": {
        "name": "Workflow Coordination Hook",
        "description": "Coordinates multi-step workflows",
        "hook_types": ["PreToolUse", "PostToolUse", "UserPromptSubmit"],
        "languages": ["python"],
        "pattern": "workflow",
        "example_use_cases": [
            "Multi-step processes",
            "State machine management",
            "Dependency tracking",
            "Conditional execution",
        ],
    },
}


def list_available_templates() -> list[dict[str, Any]]:
    """List all available hook templates."""
    return [
        {"id": template_id, **template_info}
        for template_id, template_info in TEMPLATES.items()
    ]


def get_template_info(template_id: str) -> dict[str, Any]:
    """Get detailed information about a specific template."""
    if template_id not in TEMPLATES:
        raise ValueError(f"Template '{template_id}' not found")

    return {"id": template_id, **TEMPLATES[template_id]}


def generate_safety_hook(
    language: str = "python",
    tool_filter: str = "Bash",
    dangerous_patterns: list[str] = None,
    custom_message: str = None,
) -> str:
    """Generate a safety check hook.

    Based on the tenx-hooks Rust example that blocks dangerous commands.

    Args:
        language: Programming language ("python" or "rust")
        tool_filter: Tool to monitor (default: "Bash")
        dangerous_patterns: List of dangerous command patterns
        custom_message: Custom block message
    """
    if dangerous_patterns is None:
        dangerous_patterns = [
            "rm -rf /",
            "sudo rm -rf",
            "mkfs.",
            "dd if=/dev/zero",
            ":(){ :|:& };:",  # Fork bomb
            "curl.*|.*sh",  # Pipe to shell
            "wget.*|.*sh",  # Pipe to shell
        ]

    if custom_message is None:
        custom_message = "Command blocked for safety"

    if language == "python":
        return _generate_python_safety_hook(
            tool_filter, dangerous_patterns, custom_message
        )
    elif language == "rust":
        return _generate_rust_safety_hook(
            tool_filter, dangerous_patterns, custom_message
        )
    else:
        raise ValueError(f"Unsupported language: {language}")


def generate_logging_hook(
    log_location: str = "eyelet-hooks",
    include_outputs: bool = True,
    hook_types: list[str] = None,
) -> str:
    """Generate a comprehensive logging hook.

    Args:
        log_location: Directory to store logs
        include_outputs: Whether to log tool outputs
        hook_types: Hook types to support
    """
    if hook_types is None:
        hook_types = ["PreToolUse", "PostToolUse"]

    return _generate_python_logging_hook(log_location, include_outputs, hook_types)


def generate_enhancement_hook(
    enhancement_type: str = "format", target_tools: list[str] = None
) -> str:
    """Generate an output enhancement hook.

    Args:
        enhancement_type: Type of enhancement ("format", "filter", "annotate")
        target_tools: Tools to enhance (default: all)
    """
    if target_tools is None:
        target_tools = ["Bash", "Read", "Write"]

    return _generate_python_enhancement_hook(enhancement_type, target_tools)


def generate_workflow_hook(
    workflow_type: str = "sequential", state_storage: str = "file"
) -> str:
    """Generate a workflow coordination hook.

    Args:
        workflow_type: Type of workflow ("sequential", "conditional", "parallel")
        state_storage: How to store state ("file", "memory")
    """
    return _generate_python_workflow_hook(workflow_type, state_storage)


# Internal template generators


def _generate_python_safety_hook(
    tool_filter: str, dangerous_patterns: list[str], message: str
) -> str:
    """Generate Python safety hook based on tenx-hooks pattern."""
    patterns_code = ",\\n        ".join(
        [f'"{pattern}"' for pattern in dangerous_patterns]
    )

    return f'''#!/usr/bin/env python3
"""
Safety check hook for Claude Code.
Blocks dangerous commands based on pattern matching.

Based on the tenx-hooks Rust example:
https://github.com/tenxhq/tenx-hooks
"""

import json
import sys
import re
from typing import Dict, Any, List


def is_dangerous_command(command: str, patterns: List[str]) -> bool:
    """Check if a command matches dangerous patterns."""
    for pattern in patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return True
    return False


def main():
    """Main hook entry point."""
    try:
        # Read hook input from stdin
        input_data = json.load(sys.stdin)

        # Extract tool information
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {{}})

        # Only check specified tools
        if tool_name == "{tool_filter}":
            command = tool_input.get("command", "")

            # Define dangerous patterns
            dangerous_patterns = [
                {patterns_code}
            ]

            # Check for dangerous commands
            if is_dangerous_command(command, dangerous_patterns):
                print("{message}", file=sys.stderr)
                sys.exit(2)  # Block execution and show message to Claude

        # Allow execution
        sys.exit(0)

    except Exception as e:
        # Log error but fail open for safety
        print(f"Hook error: {{e}}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
'''


def _generate_rust_safety_hook(
    tool_filter: str, dangerous_patterns: list[str], message: str
) -> str:
    """Generate Rust safety hook based on tenx-hooks example."""
    patterns_rust = ", \n        ".join(
        [f'"{pattern}"' for pattern in dangerous_patterns]
    )

    return f"""// Rust safety hook for Claude Code
// Based on tenx-hooks example: https://github.com/tenxhq/tenx-hooks

use code_hooks::*;

fn main() -> Result<()> {{
    let input = PreToolUse::read()?;

    if input.tool_name == "{tool_filter}" {{
        if let Some(cmd) = input.tool_input.get("command").and_then(|v| v.as_str()) {{
            let dangerous_patterns = [
                {patterns_rust}
            ];

            for pattern in &dangerous_patterns {{
                if cmd.contains(pattern) {{
                    return input.block("{message}").respond();
                }}
            }}
        }}
    }}

    input.approve("OK").respond()
}}
"""


def _generate_python_logging_hook(
    log_location: str, include_outputs: bool, hook_types: list[str]
) -> str:
    """Generate comprehensive logging hook."""
    return f'''#!/usr/bin/env python3
"""
Universal logging hook for Claude Code.
Logs all tool usage to structured JSON files.
"""

import json
import sys
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any


def get_hook_type() -> str:
    """Detect hook type from environment or script name."""
    # Check environment variable first
    hook_type = os.environ.get("EYELET_HOOK_TYPE")
    if hook_type:
        return hook_type

    # Fallback to script name detection
    script_name = Path(sys.argv[0]).name.lower()
    if "pretool" in script_name or "pre-tool" in script_name:
        return "PreToolUse"
    elif "posttool" in script_name or "post-tool" in script_name:
        return "PostToolUse"
    else:
        return "Unknown"


def log_hook_data(hook_type: str, input_data: Dict[str, Any], log_dir: str = "{log_location}"):
    """Log hook data to structured files."""
    try:
        # Create log directory
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        # Create timestamped log entry
        timestamp = datetime.now(timezone.utc)
        log_entry = {{
            "timestamp": timestamp.isoformat(),
            "hook_type": hook_type,
            "tool_name": input_data.get("tool_name"),
            "tool_input": input_data.get("tool_input"),
            "context": input_data.get("context", {{}})
        }}

        # Write to daily log file
        date_str = timestamp.strftime("%Y-%m-%d")
        log_file = log_path / f"{{hook_type.lower()}}-{{date_str}}.jsonl"

        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\\n")

    except Exception as e:
        print(f"Logging error: {{e}}", file=sys.stderr)


def main():
    """Main hook entry point."""
    try:
        # Read input
        input_data = json.load(sys.stdin)
        hook_type = get_hook_type()

        # Log the hook data
        log_hook_data(hook_type, input_data)

        # Allow execution
        sys.exit(0)

    except Exception as e:
        print(f"Hook error: {{e}}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
'''


def _generate_python_enhancement_hook(
    enhancement_type: str, target_tools: list[str]
) -> str:
    """Generate output enhancement hook."""
    tools_list = ", ".join([f'"{tool}"' for tool in target_tools])

    return f'''#!/usr/bin/env python3
"""
Output enhancement hook for Claude Code.
Modifies tool outputs based on specified patterns.
"""

import json
import sys
from typing import Dict, Any, List


def enhance_output(tool_name: str, output_data: Any, enhancement_type: str = "{enhancement_type}") -> Any:
    """Apply enhancements to tool outputs."""
    if enhancement_type == "format":
        # Format output for better readability
        if isinstance(output_data, str):
            return output_data.strip() + "\\n[Enhanced by eyelet]"

    elif enhancement_type == "filter":
        # Filter sensitive information
        if isinstance(output_data, str):
            # Remove potential sensitive patterns
            import re
            filtered = re.sub(r'password[=:]\\s*\\S+', 'password=***', output_data, flags=re.IGNORECASE)
            filtered = re.sub(r'token[=:]\\s*\\S+', 'token=***', filtered, flags=re.IGNORECASE)
            return filtered

    elif enhancement_type == "annotate":
        # Add metadata annotations
        return {{
            "original_output": output_data,
            "tool_name": tool_name,
            "enhanced_at": "{{}}".format(datetime.now().isoformat()),
            "enhancement_note": "Output processed by eyelet"
        }}

    return output_data


def main():
    """Main hook entry point."""
    try:
        # Read input (PostToolUse hook receives both input and output)
        input_data = json.load(sys.stdin)

        tool_name = input_data.get("tool_name", "")
        target_tools = [{tools_list}]

        # Only enhance specified tools
        if tool_name in target_tools:
            # For PostToolUse, we might have output to enhance
            if "tool_output" in input_data:
                enhanced_output = enhance_output(
                    tool_name,
                    input_data["tool_output"],
                    "{enhancement_type}"
                )

                # Return enhanced output
                result = input_data.copy()
                result["tool_output"] = enhanced_output
                print(json.dumps(result))
            else:
                # Just pass through for PreToolUse
                print(json.dumps(input_data))
        else:
            # Pass through unchanged
            print(json.dumps(input_data))

        sys.exit(0)

    except Exception as e:
        print(f"Hook error: {{e}}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
'''


def _generate_python_workflow_hook(workflow_type: str, state_storage: str) -> str:
    """Generate workflow coordination hook."""
    return f'''#!/usr/bin/env python3
"""
Workflow coordination hook for Claude Code.
Manages multi-step workflows and state transitions.
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional


class WorkflowState:
    """Manages workflow state persistence."""

    def __init__(self, storage_type: str = "{state_storage}"):
        self.storage_type = storage_type
        self.state_file = Path("eyelet-hooks/workflow-state.json")

    def load_state(self) -> Dict[str, Any]:
        """Load current workflow state."""
        if self.storage_type == "file" and self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    return json.load(f)
            except Exception:
                pass
        return {{"current_step": 0, "completed_steps": [], "context": {{}}}}

    def save_state(self, state: Dict[str, Any]):
        """Save workflow state."""
        if self.storage_type == "file":
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, "w") as f:
                json.dump(state, f, indent=2)


def execute_workflow_logic(
    tool_name: str,
    tool_input: Dict[str, Any],
    workflow_state: Dict[str, Any],
    workflow_type: str = "{workflow_type}"
) -> Dict[str, Any]:
    """Execute workflow-specific logic."""

    if workflow_type == "sequential":
        # Sequential workflow: ensure steps happen in order
        required_steps = ["step1", "step2", "step3"]
        current_step = workflow_state.get("current_step", 0)

        if current_step < len(required_steps):
            step_name = required_steps[current_step]
            workflow_state["completed_steps"].append(step_name)
            workflow_state["current_step"] = current_step + 1
            workflow_state["context"][step_name] = {{
                "tool": tool_name,
                "input": tool_input
            }}

    elif workflow_type == "conditional":
        # Conditional workflow: steps depend on previous results
        last_tool = workflow_state.get("context", {{}}).get("last_tool")
        if last_tool == "Bash" and tool_name == "Read":
            workflow_state["context"]["bash_then_read"] = True

    return workflow_state


def main():
    """Main hook entry point."""
    try:
        # Read input
        input_data = json.load(sys.stdin)

        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {{}})

        # Load and update workflow state
        state_manager = WorkflowState()
        workflow_state = state_manager.load_state()

        # Execute workflow logic
        updated_state = execute_workflow_logic(
            tool_name,
            tool_input,
            workflow_state,
            "{workflow_type}"
        )

        # Save updated state
        state_manager.save_state(updated_state)

        # Log workflow progress
        print(f"Workflow step completed: {{tool_name}}", file=sys.stderr)

        # Allow execution
        sys.exit(0)

    except Exception as e:
        print(f"Workflow hook error: {{e}}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
'''
