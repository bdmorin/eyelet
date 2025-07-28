# Technology Guide for Rigging Development

## Core Philosophy: Retreat Only With Human Approval

When facing technical challenges, we troubleshoot and solve problems rather than abandoning approaches. If a method truly cannot work, we present the evidence and alternatives to the human for approval before retreating. This guide documents our technology decisions and the reasoning behind them to ensure consistent, resilient development.

## Language Choice: Python 3.11+

### Decision
We chose Python over Go, despite Go's performance advantages.

### Reasoning
1. **Native SDK Access**: Claude Code provides official Python SDK (`claude-code-sdk-python`), eliminating weeks of reverse-engineering work
2. **Rapid Development**: Python's ecosystem enables 3-5x faster feature development
3. **Distribution via uvx**: Modern Python tooling (uv/uvx) provides near-instant updates for users
4. **TUI Excellence**: Textual rivals Go's Bubbletea in quality while offering better documentation

### Troubleshooting Approach
- If startup performance becomes an issue: Implement lazy imports, use Nuitka compilation, or create a thin Go wrapper for the hook endpoint
- If distribution is problematic: Fall back to pipx, provide platform-specific installers, or use PyInstaller
- If SDK limitations arise: Extend the SDK, contribute upstream, or implement missing features

## Architecture: Vertical Slice

### Decision
Vertical slice architecture with clear separation of concerns:
```
domain/       - Business entities and rules
application/  - Use cases and services  
infrastructure/ - External integrations
cli/          - Command interface
presentation/ - TUI layer
```

### Reasoning
1. **Testability**: Each layer can be tested in isolation
2. **Flexibility**: Easy to swap implementations (e.g., SQLite → PostgreSQL)
3. **Maintainability**: Clear boundaries prevent coupling
4. **Extensibility**: New features slot in cleanly

### Troubleshooting Approach
- If layers become too rigid: Introduce cross-cutting concerns via dependency injection
- If performance suffers: Profile and optimize hot paths, consider caching layers
- If complexity grows: Extract shared functionality to common modules

## Data Storage: SQLite + File System

### Decision
- SQLite for high-volume hook execution logs
- JSON files for templates and configuration
- File system for workflows

### Reasoning
1. **Zero Configuration**: Works out of the box, no server required
2. **Performance**: SQLite handles millions of records efficiently
3. **Portability**: Single file database, easy backup/restore
4. **Flexibility**: JSON files for human-editable configuration

### Troubleshooting Approach
- If SQLite performance degrades: Implement partitioning, archive old data, or migrate to PostgreSQL
- If file conflicts occur: Implement file locking, use atomic writes
- If data corruption happens: Add checksums, implement backup strategies

## CLI Framework: Click

### Decision
Click over alternatives like argparse or typer.

### Reasoning
1. **Maturity**: Battle-tested in production
2. **Decorators**: Clean, readable command definitions
3. **Extensibility**: Easy to add custom types and validators
4. **Documentation**: Excellent docs and community support

### Troubleshooting Approach
- If Click limitations arise: Extend with custom decorators
- If performance is an issue: Profile command startup, lazy-load heavy imports
- If testing is difficult: Use Click's testing utilities

## TUI Framework: Textual

### Decision
Textual over alternatives like urwid or Python Prompt Toolkit.

### Reasoning
1. **Modern Architecture**: Reactive, CSS-based styling
2. **Rich Ecosystem**: Built on Rich, excellent terminal support
3. **Active Development**: Rapidly improving with strong community
4. **Developer Experience**: Hot reload, browser-based devtools

### Troubleshooting Approach
- If Textual bugs arise: Pin to stable version, report issues upstream
- If performance degrades: Use virtual scrolling, optimize render cycles
- If styling limitations: Extend with custom widgets

## AI Integration: Claude Code SDK

### Decision
Direct SDK usage over CLI wrapping or API reimplementation.

### Reasoning
1. **Reliability**: Official SDK is maintained and tested
2. **Features**: Full access to Claude Code capabilities
3. **Type Safety**: Proper models and type hints
4. **Updates**: Automatic compatibility with new features

### Troubleshooting Approach
- If SDK is missing features: Extend locally, contribute upstream
- If SDK has bugs: Pin version, implement workarounds, report issues
- If SDK is discontinued: Implement minimal API client focusing on our needs

## Hook Discovery Strategy

### Decision
Multi-layered discovery approach:
1. Static registry (baseline)
2. Documentation scraping
3. Runtime detection
4. Log analysis

### Reasoning
1. **Resilience**: Multiple discovery methods ensure completeness
2. **Adaptability**: Can handle Claude Code updates automatically
3. **Accuracy**: Cross-validation between methods
4. **Performance**: Static registry provides fast baseline

### Troubleshooting Approach
- If discovery fails: Fall back to static registry
- If false positives: Implement validation layer
- If performance degrades: Cache discovery results

## Testing Strategy

### Decision
Pytest with comprehensive test coverage:
- Unit tests for each layer
- Integration tests for workflows
- End-to-end tests for CLI commands

### Reasoning
1. **Confidence**: Catch regressions early
2. **Documentation**: Tests serve as usage examples
3. **Refactoring**: Safe to change implementation

### Troubleshooting Approach
- If tests are slow: Parallelize, use test fixtures
- If tests are flaky: Isolate state, mock external dependencies
- If coverage drops: Add pre-commit hooks, CI gates

## Distribution Strategy

### Decision
Primary distribution via uvx with fallbacks:
1. uvx (recommended)
2. pipx
3. pip install from PyPI
4. Git clone + uv install

### Reasoning
1. **User Experience**: One command to run latest version
2. **Updates**: Users always get latest fixes
3. **Isolation**: No dependency conflicts
4. **Fallbacks**: Multiple installation methods

### Troubleshooting Approach
- If uvx has issues: Document pipx alternative
- If dependencies conflict: Use stricter version pinning
- If installation fails: Provide platform-specific guides

## General Problem-Solving Principles

### 1. Understand Before Acting
- Read error messages completely
- Check logs and debug output
- Understand the root cause

### 2. Incremental Solutions
- Fix one issue at a time
- Test each fix thoroughly
- Document what worked

### 3. Multiple Approaches
- Try different solutions
- Research similar problems
- Ask for clarification if needed

### 4. Retreat Only With Approval
- Every problem has a solution worth trying
- Present evidence if an approach truly won't work
- Get human alignment before abandoning a path
- Document why retreat was necessary

### 5. Document Everything
- Record problems and solutions
- Update this guide with learnings
- Help future developers

## Common Issues and Solutions

### Import Errors
**Problem**: Module not found errors
**Solutions**:
1. Check PYTHONPATH
2. Verify package structure
3. Use relative imports correctly
4. Ensure __init__.py files exist

### Performance Issues
**Problem**: Slow startup or execution
**Solutions**:
1. Profile with cProfile
2. Implement lazy imports
3. Cache expensive operations
4. Use async where appropriate

### Dependency Conflicts
**Problem**: Package version incompatibilities
**Solutions**:
1. Use dependency groups
2. Pin problem packages
3. Create compatibility shims
4. Report issues upstream

### Platform Differences
**Problem**: Works on one OS, fails on another
**Solutions**:
1. Test on all platforms
2. Use pathlib for paths
3. Handle platform-specific code
4. Document platform requirements

## Conclusion

This guide represents our commitment to solving problems rather than avoiding them. When faced with challenges:

1. **Investigate thoroughly** - Understand the real issue
2. **Try multiple solutions** - Exhaust reasonable approaches  
3. **Present evidence** - If retreat seems necessary, show why
4. **Get alignment** - Confirm with human before abandoning approach
5. **Document findings** - Record both successes and approved retreats
6. **Contribute upstream** - Improve tools for everyone

Remember: We're building a robust tool that handles the complexity of hook orchestration. Challenges are opportunities to make Rigging better and more resilient. We retreat only when the human agrees it's the right strategic move.