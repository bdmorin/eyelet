#!/usr/bin/env python3
"""
Test script to verify all Claude Code hook logging is working.
This script generates unique identifiers for each tool call and
then verifies the logs contain those identifiers.
"""

import json
import random
import sys
from datetime import datetime
from pathlib import Path

# Generate unique test identifier
TEST_ID = f"zebra-{random.randint(1000,9999)}-flamingo-{random.randint(1000,9999)}"
print(f"Test ID: {TEST_ID}")

# Tools to test with their expected hook types
TOOLS_TO_TEST = {
    "Bash": {
        "hooks": ["PreToolUse", "PostToolUse"],
        "test_command": f'echo "Hook test {TEST_ID}"'
    },
    "Read": {
        "hooks": ["PreToolUse", "PostToolUse"],
        "test_file": "/tmp/hook_test.txt"
    },
    "Write": {
        "hooks": ["PreToolUse", "PostToolUse"],
        "test_file": "/tmp/hook_test_write.txt",
        "content": f"Test content {TEST_ID}"
    },
    "Edit": {
        "hooks": ["PreToolUse", "PostToolUse"],
        "test_file": "/tmp/hook_test_edit.txt",
        "old_string": "original",
        "new_string": f"edited {TEST_ID}"
    },
    "MultiEdit": {
        "hooks": ["PreToolUse", "PostToolUse"],
        "test_file": "/tmp/hook_test_multiedit.txt"
    },
    "Grep": {
        "hooks": ["PreToolUse", "PostToolUse"],
        "pattern": TEST_ID
    },
    "Glob": {
        "hooks": ["PreToolUse", "PostToolUse"],
        "pattern": "*.py"
    },
    "LS": {
        "hooks": ["PreToolUse", "PostToolUse"],
        "path": "/tmp"
    },
    "TodoWrite": {
        "hooks": ["PreToolUse", "PostToolUse"],
        "todos": [{"content": f"Test todo {TEST_ID}", "status": "pending", "priority": "low", "id": "test1"}]
    },
    "WebSearch": {
        "hooks": ["PreToolUse", "PostToolUse"],
        "query": f"test search {TEST_ID}"
    },
    "WebFetch": {
        "hooks": ["PreToolUse", "PostToolUse"],
        "url": "https://example.com",
        "prompt": f"Find {TEST_ID}"
    }
}

# Other hook types to test
OTHER_HOOKS = {
    "UserPromptSubmit": {
        "description": "Triggered when user submits a prompt"
    },
    "Notification": {
        "description": "Triggered for notifications"
    },
    "Stop": {
        "description": "Triggered when stopping"
    },
    "SubagentStop": {
        "description": "Triggered when subagent stops"
    },
    "PreCompact": {
        "description": "Triggered before compacting context"
    }
}

def find_logs_with_test_id(base_dir, start_time, test_id):
    """Find all log files created after start_time containing test_id."""
    found_logs = {}
    base_path = Path(base_dir)

    if not base_path.exists():
        return found_logs

    for log_file in base_path.rglob("*.json"):
        # Skip files created before our test
        if log_file.stat().st_mtime < start_time.timestamp():
            continue

        try:
            with open(log_file) as f:
                content = f.read()
                data = json.loads(content)

                # Check if our test ID appears anywhere in the log
                if test_id in content:
                    hook_type = data.get("hook_type", "unknown")
                    tool_name = data.get("tool_name", "unknown")

                    key = f"{hook_type}:{tool_name}"
                    if key not in found_logs:
                        found_logs[key] = []

                    found_logs[key].append({
                        "file": str(log_file),
                        "timestamp": data.get("timestamp"),
                        "tool_input": data.get("input_data", {}).get("tool_input", {}),
                        "status": data.get("execution", {}).get("status")
                    })
        except Exception as e:
            print(f"Error reading {log_file}: {e}")

    return found_logs

def print_test_plan():
    """Print the test plan."""
    print("\n=== HOOK TESTING PLAN ===")
    print(f"Test ID: {TEST_ID}")
    print(f"Start Time: {datetime.now()}")
    print("\nTools to test:")
    for tool, config in TOOLS_TO_TEST.items():
        print(f"  - {tool}: {', '.join(config['hooks'])}")

    print("\nOther hooks to observe:")
    for hook, config in OTHER_HOOKS.items():
        print(f"  - {hook}: {config['description']}")

    print("\n=== INSTRUCTIONS ===")
    print("1. This script has created test files and printed test commands")
    print("2. Please execute each of the following tool calls:")
    print("3. After execution, verify the results with:")
    print(f"   mise run test-hooks-verify {TEST_ID}")

def generate_test_commands():
    """Generate the commands for testing each tool."""
    print("\n=== TEST COMMANDS TO EXECUTE ===\n")

    # Create test files first
    Path("/tmp/hook_test.txt").write_text(f"Test file content {TEST_ID}")
    Path("/tmp/hook_test_edit.txt").write_text("original content")
    Path("/tmp/hook_test_multiedit.txt").write_text("line1\nline2\nline3")

    commands = []

    # Bash
    commands.append("# Bash tool test")
    commands.append(f"Run bash command: echo 'Hook test {TEST_ID}'")

    # Read
    commands.append("\n# Read tool test")
    commands.append("Read file: /tmp/hook_test.txt")

    # Write
    commands.append("\n# Write tool test")
    commands.append(f"Write to file /tmp/hook_test_write.txt with content: Test content {TEST_ID}")

    # Edit
    commands.append("\n# Edit tool test")
    commands.append(f"Edit file /tmp/hook_test_edit.txt, replace 'original' with 'edited {TEST_ID}'")

    # MultiEdit
    commands.append("\n# MultiEdit tool test")
    commands.append(f"MultiEdit file /tmp/hook_test_multiedit.txt, replace 'line2' with 'modified {TEST_ID}'")

    # Grep
    commands.append("\n# Grep tool test")
    commands.append(f"Search for pattern '{TEST_ID}' in /tmp/")

    # Glob
    commands.append("\n# Glob tool test")
    commands.append(f"Find files matching '*{TEST_ID}*.txt' in /tmp/")

    # LS
    commands.append("\n# LS tool test")
    commands.append("List files in /tmp/")

    # TodoWrite
    commands.append("\n# TodoWrite tool test")
    commands.append(f"Add todo: 'Test todo {TEST_ID}'")

    # WebSearch
    commands.append("\n# WebSearch tool test")
    commands.append(f"Search web for: 'test search {TEST_ID}'")

    # WebFetch
    commands.append("\n# WebFetch tool test")
    commands.append(f"Fetch https://example.com with prompt 'Find {TEST_ID}'")

    for cmd in commands:
        print(cmd)

    # Save timestamp for verification
    timestamp_file = Path("/tmp/hook_test_timestamp.txt")
    timestamp_file.write_text(str(datetime.now().timestamp()))

def verify_logs(test_id):
    """Verify that all expected logs were created."""
    print(f"\n=== VERIFYING LOGS FOR TEST ID: {test_id} ===")

    # Read the timestamp
    timestamp_file = Path("/tmp/hook_test_timestamp.txt")
    if not timestamp_file.exists():
        print("ERROR: No timestamp file found. Did you run the test first?")
        return False

    start_time = datetime.fromtimestamp(float(timestamp_file.read_text()))
    print(f"Searching for logs created after: {start_time}")

    # Find all logs with our test ID
    base_dir = Path.cwd() / "eyelet-hooks"
    found_logs = find_logs_with_test_id(base_dir, start_time, test_id)

    print(f"\nFound {len(found_logs)} unique tool/hook combinations")

    # Check expected vs found
    expected_count = 0
    found_count = 0

    print("\n=== DETAILED RESULTS ===")
    for tool, config in TOOLS_TO_TEST.items():
        print(f"\n{tool}:")
        for hook in config['hooks']:
            expected_count += 1
            key = f"{hook}:{tool}"
            if key in found_logs:
                found_count += 1
                print(f"  ✓ {hook} - {len(found_logs[key])} log(s)")
                for log in found_logs[key]:
                    print(f"    - {log['file']}")
            else:
                print(f"  ✗ {hook} - NOT FOUND")

    # Check for other hooks
    print("\n=== OTHER HOOKS ===")
    for hook in OTHER_HOOKS:
        found_any = False
        for key in found_logs:
            if key.startswith(f"{hook}:"):
                print(f"  ✓ {hook} - Found in {key}")
                found_any = True
        if not found_any:
            print(f"  - {hook} - Not triggered during test")

    # Summary
    print("\n=== SUMMARY ===")
    print(f"Expected tool hooks: {expected_count}")
    print(f"Found tool hooks: {found_count}")
    print(f"Coverage: {found_count}/{expected_count} ({found_count/expected_count*100:.1f}%)")

    # List any unexpected logs
    unexpected = []
    for key in found_logs:
        hook_type, tool_name = key.split(":", 1)
        if tool_name not in TOOLS_TO_TEST and hook_type not in OTHER_HOOKS:
            unexpected.append(key)

    if unexpected:
        print(f"\nUnexpected logs found: {', '.join(unexpected)}")

    return found_count == expected_count

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        test_id = sys.argv[2] if len(sys.argv) > 2 else TEST_ID
        success = verify_logs(test_id)
        sys.exit(0 if success else 1)
    else:
        print_test_plan()
        generate_test_commands()
        print("\n\nAfter executing all commands above, run:")
        print(f"mise run test-hooks-verify {TEST_ID}")
