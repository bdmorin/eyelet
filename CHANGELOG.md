# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2025-01-29

### Added
- Complete SQLite logging implementation with WAL mode and retry logic
- Configuration file system (eyelet.yaml) for global and project settings
- `eyelet doctor` command for comprehensive health checks and diagnostics
- `eyelet query` command suite for searching and analyzing hook logs
  - `query search` - Full-text search with multiple filters
  - `query summary` - Session and hook type statistics
  - `query errors` - Error analysis and debugging
  - `query session` - View specific session logs
  - `query grep` - Pattern matching across logs
- `eyelet configure logging` command to manage logging settings
- Git metadata enrichment for all logged hooks
- Process-safe SQLite connections with fork detection
- Hybrid logging support (JSON files, SQLite, or both)
- PyYAML dependency for configuration management

### Fixed
- SubagentStop hooks now properly logged when using Task tool
- Hook testing includes SubagentStop verification
- PosixPath JSON serialization errors
- Rich console.print() stderr output issues
- Query commands handle missing execution data gracefully

### Changed
- Logging format configuration now accepts comma-separated values (e.g., `--format json,sqlite`)
- Archive directory removed (tagged as `archive-removal` in git history)
- Improved error handling with fallback to legacy logging on failures

## [0.2.0] - 2025-01-28

### Changed
- Complete rebrand from Rigging to Eyelet
- Package name changed to `eyelet` on PyPI
- All commands now use `uvx eyelet`
- Updated all documentation and examples to use new branding

### Added
- Comprehensive hook testing infrastructure
  - `test_all_hooks.py` script for testing all Claude Code tools
  - Unique test identifier generation for tracking
  - Hook coverage reporting (100% coverage achieved)
- mise configuration with testing tasks
  - `mise run test-hooks`: Interactive hook testing
  - `mise run test-hooks-verify`: Verify test results
  - `mise run hook-stats`: Show hook statistics
  - `mise run hook-coverage`: Generate coverage report
  - `mise run hook-clean`: Clean old logs
- Testing documentation in README.md

### Fixed
- Claude Code hook format updated to new nested object structure
- Fixed settings.json generation for compatibility with latest Claude Code
- Updated JSON schema for new hook format
- Backwards compatibility maintained for loading old settings

## [0.1.3] - 2025-01-28

### Added
- Comprehensive GitHub Actions workflows for CI/CD
- Automated PyPI publishing on GitHub releases
- Multi-platform testing (Ubuntu, macOS, Windows)
- Post-publish validation workflow
- Automatic release creation from version tags

### Fixed  
- Updated all documentation to use correct uvx commands
- Fixed markdown linting issues in documentation

## [0.1.2] - 2025-01-28

### Changed
- Package name changed to `rigging-cli` on PyPI
- All commands now use `uvx --from rigging-cli rigging`
- Updated documentation to reflect new package name

### Fixed
- Correct executable name in PyPI package

## [0.1.1] - 2025-01-28

### Added
- JSON schema validation for Claude settings files
- `uvx --from rigging-cli rigging validate settings` command for universal settings validation
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

[Unreleased]: https://github.com/bdmorin/eyelet/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/bdmorin/eyelet/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/bdmorin/eyelet/compare/v0.1.3...v0.2.0
[0.1.3]: https://github.com/bdmorin/eyelet/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/bdmorin/eyelet/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/bdmorin/eyelet/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/bdmorin/eyelet/releases/tag/v0.1.0