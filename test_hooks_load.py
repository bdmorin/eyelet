#!/usr/bin/env python3
"""Test hook loading from configuration"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from eyelet.application.services import ConfigurationService

# Test loading hooks
config_service = ConfigurationService(Path.cwd())
try:
    config = config_service.load_configuration()
    print(f"Loaded {len(config.hooks)} hooks:")
    for i, hook in enumerate(config.hooks):
        print(
            f"{i + 1}. {hook.type} - Handler: {hook.handler.type} - Matcher: {hook.matcher or 'None'}"
        )
except Exception as e:
    print(f"Error loading hooks: {e}")
    import traceback

    traceback.print_exc()
