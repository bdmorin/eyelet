#!/usr/bin/env python3
"""Test script to validate eyelet package before publishing"""

import json
import subprocess
import sys


def run_test(description, command, stdin=None):
    """Run a test command and check if it succeeds"""
    print(f"Testing: {description}...")
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, input=stdin, timeout=5
        )
        if result.returncode == 0:
            print(f"  ✓ {description}")
            return True
        else:
            print(f"  ✗ {description}")
            print(f"    Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ✗ {description}")
        print(f"    Exception: {e}")
        return False


def main():
    """Run all package validation tests"""
    tests_passed = []
    tests_failed = []

    # Test 1: Import the package
    test_name = "Import eyelet package"
    if run_test(test_name, "python -c 'import eyelet; print(eyelet.__version__)'"):
        tests_passed.append(test_name)
    else:
        tests_failed.append(test_name)

    # Test 2: CLI help
    test_name = "CLI help command"
    if run_test(test_name, "eyelet --help"):
        tests_passed.append(test_name)
    else:
        tests_failed.append(test_name)

    # Test 3: Execute with hook_type (new format)
    test_name = "Execute with hook_type"
    test_input = json.dumps(
        {
            "hook_type": "PreToolUse",
            "tool_name": "Bash",
            "input": {"command": "echo test"},
        }
    )
    if run_test(test_name, "eyelet execute --log-only", stdin=test_input):
        tests_passed.append(test_name)
    else:
        tests_failed.append(test_name)

    # Test 4: Execute with hook_event_name (Claude Code format)
    test_name = "Execute with hook_event_name"
    test_input = json.dumps(
        {
            "hook_event_name": "PostToolUse",
            "tool_name": "Read",
            "output": {"content": "test"},
        }
    )
    if run_test(test_name, "eyelet execute --log-only", stdin=test_input):
        tests_passed.append(test_name)
    else:
        tests_failed.append(test_name)

    # Test 5: TUI module import
    test_name = "Import TUI module"
    if run_test(test_name, "python -c 'from eyelet.tui import app'"):
        tests_passed.append(test_name)
    else:
        tests_failed.append(test_name)

    # Test 6: Recall module import
    test_name = "Import recall module"
    if run_test(test_name, "python -c 'from eyelet.recall import ConversationSearch'"):
        tests_passed.append(test_name)
    else:
        tests_failed.append(test_name)

    # Test 7: Doctor command (skip since it's interactive)
    test_name = "Validate command"
    if run_test(test_name, "eyelet validate --help"):
        tests_passed.append(test_name)
    else:
        tests_failed.append(test_name)

    # Print summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"✓ Passed: {len(tests_passed)}")
    print(f"✗ Failed: {len(tests_failed)}")

    if tests_failed:
        print("\nFailed tests:")
        for test in tests_failed:
            print(f"  - {test}")
        sys.exit(1)
    else:
        print("\n🎉 All tests passed! Package is ready for publishing.")
        sys.exit(0)


if __name__ == "__main__":
    main()
