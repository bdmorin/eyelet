# WakaTime/ActivityWatch Integration for Eyelet

## Overview

This document describes how Eyelet integrates with the WakaTime/ActivityWatch metrics stack located at `~/src/wakatime/`.

## What is the WakaTime Stack?

A comprehensive, self-hosted metrics tracking system that includes:
- **ActivityWatch**: Tracks all computer activity (apps, browser, terminal)
- **Wakapi**: Self-hosted WakaTime server for code metrics
- **Custom Trackers**: Terminal commands, Claude Code usage

## Why Integrate?

Eyelet captures hook events from Claude Code, providing:
- Precise timestamps of interactions
- Git context (project, branch, files)
- Session boundaries
- Prompt metadata

This data can enhance metrics tracking by:
- Eliminating polling-based tracking
- Providing accurate project attribution
- Enabling prompt-to-productivity analytics

## Hook Examples

### Send Wakapi Heartbeat

```bash
#!/bin/bash
# ~/.config/claude-hooks/user-prompt-submit-hook.d/50-wakatime-heartbeat.sh

# Use Eyelet context for accurate project info
PROJECT=$(eyelet context get project)
BRANCH=$(eyelet context get git.branch)

# Send to Wakapi (see ~/src/wakatime/hooks/ for full implementation)
```

### Track in ActivityWatch

```python
#!/usr/bin/env python3
# ~/.config/claude-hooks/user-prompt-submit-hook.d/51-activitywatch-event.py

# Get rich context from Eyelet
context = eyelet.get_context()

# Send structured event to ActivityWatch
# (see ~/src/wakatime/hooks/ for full implementation)
```

## Installation

The WakaTime stack provides hooks that Eyelet can install:

```bash
# Install Eyelet hooks first
uvx eyelet configure install-all

# Then add WakaTime integration hooks
cd ~/src/wakatime
./install-eyelet-hooks.sh  # Coming soon
```

## Data Flow

```
Claude Code → Eyelet Hooks → WakaTime/ActivityWatch
                ↓
         SQLite Database
                ↓
         Analytics & Reports
```

## See Also

- Full integration docs: `~/src/wakatime/EYELET-INTEGRATION.md`
- WakaTime stack README: `~/src/wakatime/README.md`
- Hook implementations: `~/src/wakatime/hooks/`