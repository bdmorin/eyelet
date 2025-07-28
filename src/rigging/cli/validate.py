"""Validation commands for Claude settings files"""

import click
import json
import jsonschema
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def get_embedded_schema():
    """Return the embedded Claude settings schema"""
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Claude Code Settings",
        "description": "Schema for Claude Code settings.json configuration files",
        "type": "object",
        "properties": {
            "hooks": {
                "type": "array",
                "description": "Array of hook configurations",
                "items": {"$ref": "#/definitions/hook"}
            }
        },
        "additionalProperties": True,
        "definitions": {
            "hook": {
                "type": "object",
                "required": ["type", "handler"],
                "properties": {
                    "type": {
                        "type": "string",
                        "description": "The type of hook event",
                        "enum": [
                            "PreToolUse", "PostToolUse", "UserPromptSubmit",
                            "Notification", "Stop", "SubagentStop", "PreCompact"
                        ]
                    },
                    "handler": {"$ref": "#/definitions/handler"},
                    "matcher": {
                        "type": "string",
                        "description": "Regex pattern for tool matching or 'manual'/'auto' for PreCompact"
                    }
                },
                "allOf": [
                    {
                        "if": {"properties": {"type": {"enum": ["PreToolUse", "PostToolUse"]}}},
                        "then": {
                            "required": ["matcher"],
                            "properties": {"matcher": {"type": "string", "description": "Regex pattern to match tool names"}}
                        }
                    },
                    {
                        "if": {"properties": {"type": {"const": "PreCompact"}}},
                        "then": {
                            "required": ["matcher"],
                            "properties": {"matcher": {"type": "string", "enum": ["manual", "auto"], "description": "Type of compaction trigger"}}
                        }
                    },
                    {
                        "if": {"properties": {"type": {"enum": ["UserPromptSubmit", "Notification", "Stop", "SubagentStop"]}}},
                        "then": {"properties": {"matcher": {"not": {}}}}
                    }
                ]
            },
            "handler": {
                "type": "object",
                "required": ["type"],
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["command", "workflow", "script"],
                        "description": "Type of handler"
                    }
                },
                "oneOf": [
                    {
                        "properties": {
                            "type": {"const": "command"},
                            "command": {"type": "string", "description": "Command to execute"}
                        },
                        "required": ["command"],
                        "additionalProperties": False
                    },
                    {
                        "properties": {
                            "type": {"const": "workflow"},
                            "workflow": {"type": "string", "description": "Path to workflow file"}
                        },
                        "required": ["workflow"],
                        "additionalProperties": False
                    },
                    {
                        "properties": {
                            "type": {"const": "script"},
                            "script": {"type": "string", "description": "Script content to execute"}
                        },
                        "required": ["script"],
                        "additionalProperties": False
                    }
                ]
            }
        }
    }


@click.group(name='validate')
def validate():
    """Validate configurations - Check the ship's papers!"""
    pass


@validate.command(name='settings')
@click.argument('settings_file', type=click.Path(exists=True, path_type=Path), required=False)
@click.option('--schema', type=click.Path(exists=True, path_type=Path), 
              help='Path to JSON schema file')
@click.pass_context
def validate_settings(ctx, settings_file, schema):
    """
    Validate Claude settings.json against schema
    
    Examples:
        rigging validate settings
        rigging validate settings .claude/settings.json
        rigging validate settings ~/.claude/settings.json
    """
    # Default to current directory's .claude/settings.json
    if not settings_file:
        settings_file = Path.cwd() / ".claude" / "settings.json"
        if not settings_file.exists():
            console.print("[red]No settings.json found in .claude/[/red]")
            console.print("[dim]Specify a file path or run from a directory with .claude/settings.json[/dim]")
            return
    
    # Find schema file
    skip_schema_load = False
    if not schema:
        # First try pkg_resources for installed package
        try:
            import pkg_resources
            schema_path = Path(pkg_resources.resource_filename('rigging', 'schemas/claude-settings.schema.json'))
            if not schema_path.exists():
                raise FileNotFoundError()
        except:
            # Fall back to embedded schema
            try:
                import importlib.resources as resources
                # For Python 3.9+
                schema_content = resources.files('rigging').joinpath('schemas/claude-settings.schema.json').read_text()
                schema_data = json.loads(schema_content)
                # Skip file loading since we have the data
                skip_schema_load = True
            except:
                # Last resort - embed the schema directly
                schema_data = get_embedded_schema()
                skip_schema_load = True
    else:
        schema_path = schema
    
    # Load files
    try:
        with open(settings_file, 'r') as f:
            settings_data = json.load(f)
        
        if not skip_schema_load:
            with open(schema_path, 'r') as f:
                schema_data = json.load(f)
    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON in {settings_file}:[/red]")
        console.print(f"[yellow]{e}[/yellow]")
        return
    except Exception as e:
        console.print(f"[red]Error reading files: {e}[/red]")
        return
    
    # Validate
    try:
        jsonschema.validate(instance=settings_data, schema=schema_data)
        console.print(f"[green]✓[/green] {settings_file} is valid!")
        
        # Show summary
        if 'hooks' in settings_data:
            hook_count = len(settings_data['hooks'])
            console.print(f"\n[bold]Summary:[/bold] {hook_count} hooks configured")
            
            # Group hooks by type
            hook_types = {}
            for hook in settings_data['hooks']:
                hook_type = hook['type']
                if hook_type not in hook_types:
                    hook_types[hook_type] = []
                hook_types[hook_type].append(hook)
            
            # Display table
            table = Table(title="Configured Hooks")
            table.add_column("Hook Type", style="cyan")
            table.add_column("Count", justify="right")
            table.add_column("Matchers", style="dim")
            
            for hook_type, hooks in sorted(hook_types.items()):
                matchers = [h.get('matcher', '-') for h in hooks]
                unique_matchers = list(set(matchers))
                table.add_row(
                    hook_type,
                    str(len(hooks)),
                    ", ".join(unique_matchers[:3]) + ("..." if len(unique_matchers) > 3 else "")
                )
            
            console.print(table)
            
    except jsonschema.exceptions.ValidationError as e:
        console.print(f"[red]✗[/red] Validation failed for {settings_file}")
        console.print(f"\n[bold red]Error:[/bold red] {e.message}")
        
        if e.path:
            path_str = " → ".join(str(p) for p in e.path)
            console.print(f"[bold]Location:[/bold] {path_str}")
        
        if e.schema_path:
            schema_path_str = " → ".join(str(p) for p in e.schema_path)
            console.print(f"[bold]Schema rule:[/bold] {schema_path_str}")
        
        # Provide helpful suggestions
        console.print("\n[bold]Common issues:[/bold]")
        if "enum" in str(e):
            console.print("• Check that hook types and handler types use correct values")
            console.print("• Valid hook types: PreToolUse, PostToolUse, UserPromptSubmit, etc.")
            console.print("• Valid handler types: command, workflow, script")
        if "required" in str(e):
            console.print("• Ensure all required fields are present")
            console.print("• Each hook needs 'type' and 'handler'")
            console.print("• PreToolUse/PostToolUse need 'matcher'")
        if "matcher" in str(e) and "PreCompact" in str(e):
            console.print("• PreCompact matcher must be 'manual' or 'auto'")


@validate.command(name='hooks')
@click.pass_context
def validate_hooks(ctx):
    """Validate all hooks in current configuration"""
    from rigging.application.services import ConfigurationService
    from rigging.domain.exceptions import HookConfigurationError
    
    config_dir = ctx.obj.get('config_dir', Path.cwd()) if ctx.obj else Path.cwd()
    config_service = ConfigurationService(config_dir)
    
    try:
        config = config_service.load_configuration()
        
        if not config.hooks:
            console.print("[yellow]No hooks configured[/yellow]")
            return
        
        console.print(f"[bold]Validating {len(config.hooks)} hooks...[/bold]\n")
        
        errors = []
        warnings = []
        
        for i, hook in enumerate(config.hooks):
            # Validate matcher
            if not hook.is_valid_matcher():
                errors.append(f"Hook {i+1} ({hook.type}): Invalid matcher '{hook.matcher}'")
            
            # Check handler
            if hook.handler.type == "command" and not hook.handler.command:
                errors.append(f"Hook {i+1} ({hook.type}): Command handler missing command")
            elif hook.handler.type == "workflow" and not hook.handler.workflow:
                errors.append(f"Hook {i+1} ({hook.type}): Workflow handler missing workflow path")
            elif hook.handler.type == "script" and not hook.handler.script:
                errors.append(f"Hook {i+1} ({hook.type}): Script handler missing script content")
            
            # Warnings
            if hook.handler.type == "command" and "uvx rigging" in (hook.handler.command or ""):
                if "execute" not in hook.handler.command:
                    warnings.append(f"Hook {i+1} ({hook.type}): Command should include 'execute' subcommand")
        
        # Display results
        if errors:
            console.print("[red]✗ Validation failed[/red]\n")
            for error in errors:
                console.print(f"[red]• {error}[/red]")
        else:
            console.print("[green]✓ All hooks are valid![/green]")
        
        if warnings:
            console.print("\n[yellow]Warnings:[/yellow]")
            for warning in warnings:
                console.print(f"[yellow]• {warning}[/yellow]")
                
    except HookConfigurationError as e:
        console.print(f"[red]Failed to load configuration: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")