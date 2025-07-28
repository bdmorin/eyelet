# Language Choice Analysis for Rigging

## Critical Factor: Claude Code SDK Availability

### Available SDKs
- **Python**: Full SDK support via `claude-code-sdk-python`
- **TypeScript/Node**: Full SDK support via `@anthropic-ai/claude-code`
- **Go**: No SDK - would require building our own or shelling out

## Language Comparison

### Python + uvx
**Pros:**
- Native Claude Code SDK
- Excellent TUI options (Textual is world-class)
- uvx provides easy distribution/installation
- Rich ecosystem for data processing (SQLite, JSON)
- Fast development with SDK available

**Cons:**
- Slower startup time for hooks (100-300ms)
- Python runtime dependency
- GIL limitations (though not critical for this use case)

**TUI Options:**
- Textual (fantastic, used by many modern CLI tools)
- Rich (great for simpler interfaces)
- Python Prompt Toolkit

### TypeScript/Node + npx
**Pros:**
- Native Claude Code SDK
- npx distribution is widely adopted
- Ink (React-based TUI) is excellent
- Fast async/event-driven architecture
- Great for real-time hook processing

**Cons:**
- Node runtime dependency
- More complex type management
- Slightly slower startup than Go (50-150ms)

**TUI Options:**
- Ink (React for CLI)
- Blessed
- Vorpal

### Go (Original Choice)
**Pros:**
- Single binary distribution
- Fast startup time (<50ms)
- Excellent cross-platform support
- Bubbletea is fantastic

**Cons:**
- **NO CLAUDE CODE SDK** - This is a dealbreaker
- Would need to implement API client from scratch
- Or shell out to Python/Node for Claude operations
- Significantly more development work

## Recommendation: Python with Textual

### Why Python?
1. **Native SDK Access**: Direct integration with Claude Code
2. **Textual TUI**: As good as Bubbletea, very modern
3. **uvx Distribution**: Nearly as convenient as Go binaries
4. **Fast Development**: SDK + rich ecosystem
5. **Hook Performance**: While slower than Go, still acceptable

### Addressing Concerns

**Startup Performance:**
- Use lazy imports
- Consider nuitka/pyinstaller for compiled distribution
- Cache imports with py_compile
- For critical hooks, could have a Go wrapper that calls Python

**Distribution:**
```bash
# Users can install with:
uvx rigging
# or
pipx install rigging
```

**Cross-Platform:**
- Python works everywhere Claude Code works
- No platform-specific code needed

## Hybrid Approach (If Needed)

```
┌─────────────────────┐
│   Go Binary         │  <- Fast hook endpoint
│   (Optional)        │     Minimal logic
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Python Core       │  <- Main logic
│   - Claude SDK      │     TUI interface
│   - Textual TUI     │     Workflow engine
│   - SQLite logging  │
└─────────────────────┘
```

## Migration Path

If we start with Python and need Go later:
1. Python prototype validates the concept
2. Critical hooks can be rewritten in Go
3. Python remains for TUI and complex operations
4. Go handles performance-critical paths

## Decision Matrix

| Factor | Python | TypeScript | Go |
|--------|--------|------------|-----|
| Claude SDK | ✅ Native | ✅ Native | ❌ None |
| TUI Quality | ✅ Textual | ✅ Ink | ✅ Bubbletea |
| Distribution | ✅ uvx/pipx | ✅ npx | ✅ Binary |
| Startup Time | 🟡 100-300ms | 🟡 50-150ms | ✅ <50ms |
| Dev Velocity | ✅ Fast | ✅ Fast | ❌ Slow (no SDK) |
| Hook Performance | 🟡 Good | ✅ Good | ✅ Best |

## Final Recommendation

**Use Python with Textual** because:
1. The Claude Code SDK is the most critical dependency
2. Textual provides an excellent TUI experience
3. uvx makes distribution nearly as easy as Go binaries
4. We can optimize performance later if needed
5. Development will be 3-5x faster with the SDK

The lack of a Go SDK would force us to either:
- Spend weeks building our own SDK
- Shell out to Python/Node anyway (defeating the purpose)
- Use only CLI commands (limiting functionality)

Python gives us the best balance of features, performance, and development speed.