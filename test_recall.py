#!/usr/bin/env python3
"""Test the recall command locally."""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import and run the recall command
from eyelet.cli.recall import recall

if __name__ == "__main__":
    # Run with Click's standalone mode
    recall.main(standalone_mode=False)
