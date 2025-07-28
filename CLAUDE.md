# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Rigging is a sophisticated Python-based hook orchestration system for Claude Code. Built with a naval theme, it provides comprehensive management, templating, and execution handling for AI agent hooks. Like a ship's rigging that controls the sails, Rigging controls and orchestrates your AI agent's behavior.

## Repository Structure

The repository is transitioning from research/testing utilities to a full Python implementation:

- **archive/**: Historical documentation and research materials
- **src/rigging/**: Python implementation (in development)
- **TECHNOLOGY_GUIDE.md**: Core development philosophy and technology choices
- **PRD.md**: Product requirements document
- **README.md**: User-facing documentation

## Technology Stack

- **Language**: Python 3.11+
- **Distribution**: uvx/pipx (PyPI package: rigging-cli)
- **TUI**: Textual (not Bubbletea)
- **CLI**: Click
- **Architecture**: Vertical slice with separation of concerns
- **Philosophy**: "Retreat Only With Human Approval"

## Development Guidelines

### Hook System Implementation

Rigging will support all seven Claude Code hook types:
- PreToolUse/PostToolUse: Tool execution monitoring and control
- Notification: User interaction tracking
- UserPromptSubmit: Prompt validation and context injection
- Stop/SubagentStop: Session and subtask completion handling
- PreCompact: Context management monitoring

### Naval Theming

The project embraces naval terminology:
- "All hands to the rigging!" - Launch the TUI
- "Run out the guns!" - Deploy templates
- "Check the ship's log" - View logs
- "Scan the horizon" - Discover new hooks
- "Steady as she goes" - Maintain current configuration

## Current Status

The repository is in transition from Go concept to Python implementation. Historical research and utilities are preserved in the archive directory for reference.

## Responsibilities

- You are 100% responsible for this directory, its management, and how it's implemented. The user will guide you, however it's your responsibility to maintain it to the high standards you would expect.
- When implementing Rigging, follow the TECHNOLOGY_GUIDE.md philosophy: troubleshoot and solve problems rather than abandoning approaches.
- Maintain consistency with the naval theme and Python technology choices outlined in our documentation.

## Documentation Guidelines

- You must keep documentation up to date in this repository. If we dont' update documentation future context will get confused.

## Design Considerations

- It's really important to me that this CLI autocomplete options, even stuff the user doesn't know.