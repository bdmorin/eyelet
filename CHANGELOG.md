# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2025-01-28

### Added
- JSON schema validation for Claude settings files
- `rigging validate settings` command for universal settings validation
- VS Code integration with automatic schema mapping
- Embedded schema for zero-dependency validation

### Fixed
- Handler import issue in services.py
- Context initialization for uvx execution

## [0.1.0] - 2025-01-28

### Added
- Initial release of Rigging
- Universal hook handler with HMS logging
- `configure install-all` command for one-click setup
- Comprehensive CLI with naval-themed commands
- Hook configuration management
- Execution logging to structured directories
- Shell completion support
- Help system with examples
- uvx distribution support

### Features
- Support for all Claude Code hook types
- JSON-based logging with full hook data
- Project and user scope configuration
- Automatic backup of settings
- Rich terminal output with tables
- Error handling with helpful messages

[Unreleased]: https://github.com/bdmorin/rigging/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/bdmorin/rigging/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/bdmorin/rigging/releases/tag/v0.1.0