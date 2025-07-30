"""Hook execution command with unified logging - the main runtime endpoint"""

import json
import sys
from datetime import datetime
from pathlib import Path

import click
from rich.console import Console

from eyelet.services.config_service import ConfigService
from eyelet.services.hook_logger import HookLogger

console = Console()


@click.command()
@click.option("--workflow", help="Workflow to execute")
@click.option("--log-only", is_flag=True, help="Only log, no processing")
@click.option("--log-result", is_flag=True, help="Log result after execution")
@click.option("--debug", is_flag=True, help="Enable debug output")
@click.option("--no-logging", is_flag=True, help="Disable all logging")
@click.pass_context
def execute(ctx, workflow, log_only, log_result, debug, no_logging):
    """
    Execute as a hook endpoint

    This command is called by Claude Code when hooks are triggered.
    It reads JSON from stdin and processes according to configuration.
    """
    start_time = datetime.now()
    project_dir = ctx.obj.get("config_dir", Path.cwd()) if ctx.obj else Path.cwd()

    # Initialize services
    config_service = ConfigService(project_dir)
    hook_logger = HookLogger(config_service, project_dir)

    # Read input from stdin
    try:
        if sys.stdin.isatty():
            # For testing: if no stdin, create sample data
            input_data = {
                "hook_event_name": "test",
                "test_mode": True,
                "timestamp": start_time.isoformat(),
            }
        else:
            input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        if debug:
            console.print(
                f"[red]Failed to parse JSON input: {e}[/red]", file=sys.stderr
            )
        # Still log what we received
        input_data = {
            "hook_event_name": "parse_error",
            "error": str(e),
            "raw_input": sys.stdin.read() if not sys.stdin.isatty() else "no input",
        }
    except Exception as e:
        if debug:
            console.print(f"[red]Failed to read input: {e}[/red]", file=sys.stderr)
        input_data = {"hook_event_name": "read_error", "error": str(e)}

    # Extract hook information
    # hook_type = input_data.get('hook_event_name', 'unknown')
    # tool_name = input_data.get('tool_name', None)

    # Log the hook (unless disabled)
    log_results = None
    if not no_logging:
        try:
            log_results = hook_logger.log_hook(input_data, start_time)
            if debug:
                console.print(f"[dim]Logged to: {log_results}[/dim]", file=sys.stderr)
        except Exception as e:
            if debug:
                console.print(f"[yellow]Logging failed: {e}[/yellow]", file=sys.stderr)
            # Continue execution even if logging fails

    # Process based on options
    status = "success"
    output_data = {}
    error_message = None

    try:
        if log_only:
            # Just log and exit successfully
            output_data = {"action": "logged"}

        elif log_result:
            # Log the result of a previous execution
            output_data = {"action": "result_logged"}

        elif workflow:
            # Execute specified workflow
            # TODO: Integrate WorkflowService when available
            output_data = {"action": "workflow_executed", "workflow": workflow}

        else:
            # Default processing
            output_data = {"action": "processed"}

        # Check for blocking directives in hook data
        if input_data.get("block", False):
            if debug:
                console.print(
                    "[yellow]Blocking action requested[/yellow]", file=sys.stderr
                )
            sys.exit(2)  # Exit code 2 indicates blocked action

    except Exception as e:
        status = "error"
        error_message = str(e)
        if debug:
            console.print(f"[red]Execution error: {e}[/red]", file=sys.stderr)

    # Calculate duration
    duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)

    # Update hook with results (if we logged)
    if log_results and hasattr(hook_logger, "_last_hook_data"):
        try:
            hook_logger.update_hook_result(
                hook_logger._last_hook_data,
                status=status,
                duration_ms=duration_ms,
                output_data=output_data,
                error_message=error_message,
            )
        except Exception as e:
            if debug:
                console.print(
                    f"[yellow]Failed to update hook result: {e}[/yellow]",
                    file=sys.stderr,
                )

    # Output any required response
    if output_data and not log_only:
        # Check for response data to output
        if "response" in output_data:
            print(json.dumps(output_data["response"]))

    # Exit based on status
    if status == "error" and error_message:
        # Exit with success to not disrupt Claude Code
        # The error is logged for later analysis
        sys.exit(0)
    else:
        sys.exit(0)
