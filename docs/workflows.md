# Creating Workflows in Eyelet

> **Note**: Workflows are an upcoming feature in Eyelet. This documentation describes the planned implementation and design. While the infrastructure is in place, full workflow execution is still under development.

## Overview

Workflows in Eyelet provide a powerful way to orchestrate complex multi-step operations triggered by hooks. Instead of simple command execution, workflows allow you to chain multiple actions, implement conditional logic, handle errors gracefully, and maintain state between operations.

Think of workflows as sophisticated automation pipelines that can:
- Execute sequences of commands with proper error handling
- Make decisions based on previous results
- Parse and transform data between steps
- Interact with external services
- Maintain state across hook invocations

## Workflow File Structure

Workflows are defined in YAML format and stored in the `~/.config/eyelet/workflows/` directory. Each workflow file contains:

```yaml
# ~/.config/eyelet/workflows/code-review.yaml
id: code-review-workflow
name: "Automated Code Review"
description: "Performs comprehensive code review on file changes"
version: "1.0.0"

# Global variables available to all steps
variables:
  review_tool: "ruff"
  max_line_length: 88
  severity_threshold: "warning"

# Workflow steps executed in order
steps:
  - id: detect-language
    type: command
    command: "file -b {{ file_path }} | cut -d' ' -f1"
    output: language_type
    
  - id: run-linter
    type: conditional
    conditions:
      - when: "{{ language_type }} == 'Python'"
        steps:
          - type: command
            command: "{{ review_tool }} check {{ file_path }}"
            capture_output: true
            output: lint_results
            
  - id: check-security
    type: command
    command: "bandit -f json {{ file_path }}"
    output: security_scan
    continue_on_error: true
    
  - id: format-results
    type: transform
    input: 
      lint: "{{ lint_results }}"
      security: "{{ security_scan }}"
    script: |
      import json
      results = {
        "file": context["file_path"],
        "issues": []
      }
      # Process lint results
      if context.get("lint"):
        results["issues"].extend(parse_lint(context["lint"]))
      # Process security results  
      if context.get("security"):
        results["issues"].extend(parse_security(json.loads(context["security"])))
      return results
```

### Key Components

1. **Metadata Section**
   - `id`: Unique identifier for the workflow
   - `name`: Human-readable name
   - `description`: What the workflow does
   - `version`: Semantic versioning for workflow updates

2. **Variables Section**
   - Global variables accessible throughout the workflow
   - Can be overridden by hook configuration
   - Support environment variable expansion

3. **Steps Section**
   - Ordered list of operations to perform
   - Each step has a unique ID
   - Steps can reference outputs from previous steps

## Supported Workflow Steps

### 1. Command Execution

Execute shell commands with full control over environment and error handling:

```yaml
- id: run-tests
  type: command
  command: "pytest {{ test_path }} -v --json-report"
  environment:
    PYTHONPATH: "{{ project_root }}"
    TEST_ENV: "ci"
  working_dir: "{{ project_root }}"
  timeout: 300  # seconds
  capture_output: true
  output: test_results
  continue_on_error: false
```

### 2. Conditional Logic

Make decisions based on previous results or context:

```yaml
- id: deploy-decision
  type: conditional
  conditions:
    - when: "{{ test_results.passed }} == true and {{ branch }} == 'main'"
      steps:
        - type: command
          command: "deploy-to-staging.sh"
          
    - when: "{{ test_results.failed }} > 0"
      steps:
        - type: notify
          message: "Tests failed: {{ test_results.failed }} failures"
          
    - else:
      steps:
        - type: command
          command: "echo 'Skipping deployment'"
```

### 3. Input/Output Handling

Capture and transform data between steps:

```yaml
- id: parse-json
  type: transform
  input: "{{ previous_step.stdout }}"
  format: json
  output: parsed_data
  
- id: extract-field
  type: extract
  input: "{{ parsed_data }}"
  path: "results[0].score"
  output: score_value
  default: 0
```

### 4. Environment Variables

Manage environment variables across steps:

```yaml
- id: setup-env
  type: environment
  action: set
  variables:
    NODE_ENV: "production"
    API_KEY: "{{ secrets.api_key }}"
    
- id: use-env
  type: command
  command: "node deploy.js"
  inherit_env: true  # Inherits from previous steps
```

## Creating Custom Workflows

### File Location and Naming

Workflows should be placed in:
```
~/.config/eyelet/workflows/
├── code-review.yaml
├── security-scan.yaml
├── test-automation.yaml
└── deployment/
    ├── staging.yaml
    └── production.yaml
```

Naming conventions:
- Use descriptive, lowercase names with hyphens
- Group related workflows in subdirectories
- Include version in filename for major versions (e.g., `deploy-v2.yaml`)

### Step Sequencing

Steps are executed in the order they appear in the file:

```yaml
steps:
  # Step 1: Always executes first
  - id: prepare
    type: command
    command: "mkdir -p {{ work_dir }}"
    
  # Step 2: Can reference step 1's output
  - id: download
    type: command
    command: "wget -O {{ work_dir }}/data.json {{ url }}"
    depends_on: [prepare]  # Explicit dependency
    
  # Step 3: Parallel execution with step 2
  - id: notify-start
    type: notify
    message: "Download started"
    parallel: true  # Runs alongside download
```

### Error Handling

Workflows support sophisticated error handling:

```yaml
steps:
  - id: risky-operation
    type: command
    command: "risky-command.sh"
    error_handlers:
      - on_error: "exit_code != 0"
        steps:
          - type: command
            command: "cleanup.sh"
          - type: notify
            message: "Operation failed with code {{ exit_code }}"
            
      - on_error: "timeout"
        steps:
          - type: command
            command: "kill-hanging-processes.sh"
            
    retry:
      attempts: 3
      delay: 5  # seconds
      backoff: exponential
```

### Conditional Logic

Implement complex branching:

```yaml
steps:
  - id: check-branch
    type: command
    command: "git rev-parse --abbrev-ref HEAD"
    output: current_branch
    
  - id: branch-logic
    type: switch
    input: "{{ current_branch }}"
    cases:
      - value: "main"
        steps:
          - type: command
            command: "run-production-checks.sh"
            
      - value: "develop"
        steps:
          - type: command
            command: "run-integration-tests.sh"
            
      - pattern: "feature/.*"
        steps:
          - type: command
            command: "run-unit-tests.sh"
            
      - default:
        steps:
          - type: notify
            message: "Unknown branch type: {{ current_branch }}"
```

## Using Workflows with Hooks

### Configuring a Hook to Use a Workflow

```json
{
  "hooks": [
    {
      "type": "PreToolUse",
      "matcher": "Write",
      "handler": {
        "type": "workflow",
        "workflow": "code-review"
      },
      "description": "Run code review before file writes"
    }
  ]
}
```

### Passing Context to Workflows

Hooks automatically pass context to workflows:

```yaml
# In your workflow, you can access:
# - {{ hook_type }}: The type of hook that triggered this
# - {{ tool_name }}: For tool-based hooks
# - {{ tool_input }}: Input parameters to the tool
# - {{ user_message }}: For notification hooks
# - Any custom variables from hook configuration
```

### Workflow Return Values

Workflows can affect hook behavior through return values:

```yaml
steps:
  - id: validate
    type: command
    command: "validate-input.py '{{ tool_input }}'"
    
  - id: decision
    type: return
    conditions:
      - when: "{{ validate.exit_code }} != 0"
        action: block  # Blocks the tool execution
        message: "Validation failed: {{ validate.stderr }}"
        
      - else:
        action: allow  # Allows tool to proceed
        metadata:
          validated: true
          validator_version: "1.0"
```

## Advanced Workflow Patterns

### Chaining Commands

Create pipelines of commands:

```yaml
steps:
  - id: pipeline
    type: pipeline
    commands:
      - "cat {{ file_path }}"
      - "grep -E '{{ pattern }}'"
      - "sort | uniq -c"
      - "awk '{ print $2, $1 }'"
    output: sorted_matches
```

### Parsing Output

Extract structured data from command output:

```yaml
steps:
  - id: get-stats
    type: command
    command: "git log --oneline --since='1 week ago'"
    output: git_log
    
  - id: parse-commits
    type: parse
    input: "{{ git_log }}"
    parser: regex
    pattern: '^([a-f0-9]+)\s+(.+)$'
    fields: ["hash", "message"]
    output: commits
    
  - id: analyze
    type: transform
    input: "{{ commits }}"
    script: |
      # Python script to analyze commit patterns
      import re
      feat_count = sum(1 for c in input if c["message"].startswith("feat:"))
      fix_count = sum(1 for c in input if c["message"].startswith("fix:"))
      return {
        "total": len(input),
        "features": feat_count,
        "fixes": fix_count
      }
```

### Branching Logic

Implement complex decision trees:

```yaml
steps:
  - id: check-multiple
    type: parallel
    steps:
      - id: check-tests
        type: command
        command: "pytest --co -q | grep -c 'test_'"
        output: test_count
        
      - id: check-docs
        type: command
        command: "find . -name '*.md' | wc -l"
        output: doc_count
        
      - id: check-coverage
        type: command
        command: "coverage report | grep TOTAL | awk '{print $4}'"
        output: coverage
        
  - id: quality-gate
    type: evaluate
    expressions:
      has_tests: "{{ test_count }} > 0"
      has_docs: "{{ doc_count }} > 0"
      good_coverage: "{{ coverage | int }} >= 80"
      
  - id: proceed
    type: conditional
    conditions:
      - when: "{{ has_tests }} and {{ has_docs }} and {{ good_coverage }}"
        steps:
          - type: notify
            message: "✅ All quality checks passed!"
            
      - else:
        steps:
          - type: notify
            message: "❌ Quality checks failed"
          - type: return
            action: block
```

## Example Workflows

### Code Review Workflow

```yaml
id: comprehensive-code-review
name: "Comprehensive Code Review"
description: "Multi-tool code analysis for Python projects"

variables:
  min_coverage: 80
  max_complexity: 10

steps:
  - id: syntax-check
    type: command
    command: "python -m py_compile {{ file_path }}"
    continue_on_error: false
    
  - id: style-check
    type: command
    command: "ruff check {{ file_path }} --output-format json"
    output: style_issues
    continue_on_error: true
    
  - id: type-check
    type: command
    command: "mypy {{ file_path }} --json"
    output: type_issues
    continue_on_error: true
    
  - id: complexity-check
    type: command
    command: "radon cc {{ file_path }} -j"
    output: complexity_data
    
  - id: evaluate-results
    type: transform
    inputs:
      style: "{{ style_issues }}"
      types: "{{ type_issues }}"
      complexity: "{{ complexity_data }}"
    script: |
      # Aggregate all issues
      issues = []
      
      # Process each type of issue
      # ... (parsing logic)
      
      return {
        "status": "pass" if len(issues) == 0 else "fail",
        "issues": issues,
        "summary": f"Found {len(issues)} issues"
      }
```

### Security Scanning Workflow

```yaml
id: security-scan
name: "Security Vulnerability Scanner"
description: "Comprehensive security analysis"

steps:
  - id: detect-secrets
    type: command
    command: "detect-secrets scan {{ file_path }}"
    output: secrets_found
    
  - id: dependency-check
    type: conditional
    conditions:
      - when: "{{ file_path | endswith('.py') }}"
        steps:
          - type: command
            command: "safety check --json"
            output: vulnerable_deps
            
      - when: "{{ file_path | endswith('package.json') }}"
        steps:
          - type: command
            command: "npm audit --json"
            output: npm_vulnerabilities
            
  - id: sast-scan
    type: command
    command: "semgrep --config=auto {{ file_path }} --json"
    output: static_analysis
    
  - id: report
    type: aggregate
    inputs:
      - secrets_found
      - vulnerable_deps
      - npm_vulnerabilities
      - static_analysis
    format: security_report
```

### Test Automation Workflow

```yaml
id: smart-test-runner
name: "Intelligent Test Execution"
description: "Runs relevant tests based on changes"

steps:
  - id: detect-changes
    type: command
    command: "git diff --name-only HEAD~1"
    output: changed_files
    
  - id: map-tests
    type: transform
    input: "{{ changed_files }}"
    script: |
      # Map source files to test files
      test_files = []
      for file in input.split('\n'):
          if file.endswith('.py'):
              test_file = file.replace('src/', 'tests/').replace('.py', '_test.py')
              test_files.append(test_file)
      return ' '.join(test_files)
    output: test_targets
    
  - id: run-tests
    type: command
    command: "pytest {{ test_targets }} -v --cov --cov-report=json"
    output: test_results
    
  - id: check-coverage
    type: evaluate
    input: "{{ test_results }}"
    expression: "coverage.percent >= {{ min_coverage }}"
    on_false:
      - type: notify
        message: "Coverage below threshold: {{ coverage.percent }}%"
```

### Deployment Checks Workflow

```yaml
id: pre-deployment-checks
name: "Pre-deployment Validation"
description: "Ensures code is ready for deployment"

steps:
  - id: check-branch
    type: command
    command: "git branch --show-current"
    output: current_branch
    
  - id: validate-branch
    type: assert
    condition: "{{ current_branch }} in ['main', 'release/*']"
    message: "Deployment only allowed from main or release branches"
    
  - id: check-migrations
    type: command
    command: "python manage.py showmigrations --plan"
    output: pending_migrations
    
  - id: run-smoke-tests
    type: command
    command: "pytest tests/smoke/ -v"
    timeout: 300
    
  - id: build-check
    type: command
    command: "docker build -t test-build ."
    
  - id: final-decision
    type: return
    action: allow
    metadata:
      branch: "{{ current_branch }}"
      migrations_pending: "{{ pending_migrations | length }}"
      build_success: true
```

## Best Practices and Tips

### 1. Workflow Design

- **Keep workflows focused**: Each workflow should have a single, clear purpose
- **Use descriptive IDs**: Step IDs should indicate what the step does
- **Plan for failure**: Always include error handling and cleanup steps
- **Make workflows idempotent**: Running twice should be safe

### 2. Performance Optimization

- **Use parallel steps** when operations are independent
- **Cache expensive operations** using workflow state
- **Set appropriate timeouts** to prevent hanging
- **Minimize external API calls** in frequently-run workflows

### 3. Security Considerations

- **Never hardcode secrets**: Use environment variables or secret management
- **Validate all inputs**: Especially when executing commands
- **Use least privilege**: Run commands with minimal required permissions
- **Audit workflow access**: Log who triggers workflows and when

### 4. Testing Workflows

```yaml
# Test your workflows with dry-run mode
steps:
  - id: test-step
    type: command
    command: "echo 'Would execute: {{ actual_command }}'"
    dry_run: true  # Won't actually execute
```

### 5. Debugging Workflows

Enable debug output in your workflows:

```yaml
variables:
  debug: true

steps:
  - id: debug-context
    type: debug
    when: "{{ debug }}"
    output:
      - "Current context: {{ _context }}"
      - "Available vars: {{ _variables }}"
      - "Previous outputs: {{ _outputs }}"
```

### 6. Workflow Composition

Create reusable workflow fragments:

```yaml
# ~/.config/eyelet/workflows/fragments/notify.yaml
id: notify-fragment
steps:
  - id: send-notification
    type: multi
    targets:
      - type: slack
        webhook: "{{ notifications.slack_webhook }}"
        message: "{{ message }}"
        
      - type: email
        to: "{{ notifications.email }}"
        subject: "Workflow: {{ workflow_name }}"
        body: "{{ message }}"
```

Then include in other workflows:

```yaml
steps:
  - id: include-notify
    type: include
    workflow: fragments/notify
    variables:
      message: "Deployment completed successfully"
```

## Future Enhancements

The workflow system is actively being developed. Planned features include:

- **Visual workflow editor** in the TUI
- **Workflow marketplace** for sharing workflows
- **Advanced scheduling** with cron-like syntax
- **Distributed execution** across multiple machines
- **Workflow versioning** with automatic migration
- **GraphQL API** for workflow management
- **Metrics and monitoring** integration
- **AI-assisted workflow generation**

Stay tuned for updates as these features are implemented!