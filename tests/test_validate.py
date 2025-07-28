"""Tests for the validate command"""

import json
import tempfile
from pathlib import Path

from click.testing import CliRunner

from eyelet.cli.main import cli


def test_validate_valid_settings():
    """Test validation of a valid settings file"""
    runner = CliRunner()

    valid_settings = {
        "hooks": [
            {
                "type": "PreToolUse",
                "handler": {
                    "type": "command",
                    "command": "echo test"
                },
                "matcher": ".*"
            }
        ]
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(valid_settings, f)
        temp_path = f.name

    try:
        result = runner.invoke(cli, ['validate', 'settings', temp_path])
        assert result.exit_code == 0
        assert "is valid!" in result.output
    finally:
        Path(temp_path).unlink()


def test_validate_invalid_settings():
    """Test validation of an invalid settings file"""
    runner = CliRunner()

    invalid_settings = {
        "hooks": [
            {
                "type": "InvalidHookType",
                "handler": {
                    "type": "command",
                    "command": "echo test"
                }
            }
        ]
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(invalid_settings, f)
        temp_path = f.name

    try:
        result = runner.invoke(cli, ['validate', 'settings', temp_path])
        assert result.exit_code == 0  # We don't fail, just report
        assert "Validation failed" in result.output
    finally:
        Path(temp_path).unlink()
