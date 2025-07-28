"""Template management commands"""

import json
from pathlib import Path

import click
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

from eyelet.application.services import ConfigurationService, TemplateService
from eyelet.domain.exceptions import TemplateError
from eyelet.infrastructure.repositories import FileTemplateRepository

console = Console()


@click.group()
def template():
    """Manage hook templates - Run out the guns!"""
    pass


@template.command()
@click.option('--category', help='Filter by category')
def list(category):
    """List available templates - Check the armory"""
    template_dir = Path.home() / ".eyelet" / "templates"
    template_service = TemplateService(FileTemplateRepository(template_dir))

    templates = template_service.list_templates(category)

    if not templates:
        console.print("[yellow]No templates found[/yellow]")
        if category:
            console.print("Try running without --category filter")
        return

    table = Table(title="Available Templates")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Category", style="yellow")
    table.add_column("Description", style="white")
    table.add_column("Hooks", style="magenta", justify="right")

    for tmpl in templates:
        table.add_row(
            tmpl.id,
            tmpl.name,
            tmpl.category,
            tmpl.description,
            str(len(tmpl.hooks))
        )

    console.print(table)


@template.command()
@click.argument('template_id')
def show(template_id):
    """Show template details - Inspect the ordinance"""
    template_dir = Path.home() / ".eyelet" / "templates"
    template_service = TemplateService(FileTemplateRepository(template_dir))

    tmpl = template_service.get_template(template_id)
    if not tmpl:
        console.print(f"[red]Template '{template_id}' not found[/red]")
        return

    console.print(f"[bold cyan]{tmpl.name}[/bold cyan]")
    console.print(f"[dim]{tmpl.description}[/dim]")
    console.print()
    console.print(f"[bold]Category:[/bold] {tmpl.category}")
    console.print(f"[bold]Version:[/bold] {tmpl.version}")
    if tmpl.author:
        console.print(f"[bold]Author:[/bold] {tmpl.author}")
    if tmpl.tags:
        console.print(f"[bold]Tags:[/bold] {', '.join(tmpl.tags)}")

    console.print(f"\n[bold]Hooks ({len(tmpl.hooks)}):[/bold]")
    for i, hook in enumerate(tmpl.hooks, 1):
        console.print(f"\n  {i}. [cyan]{hook.type}[/cyan]")
        if hook.matcher:
            console.print(f"     Matcher: [green]{hook.matcher}[/green]")
        console.print(f"     Handler: [yellow]{hook.handler.type}[/yellow]")
        if hook.description:
            console.print(f"     Description: {hook.description}")

    if tmpl.variables:
        console.print("\n[bold]Variables:[/bold]")
        for key, default in tmpl.variables.items():
            console.print(f"  - {key}: {default}")


@template.command()
@click.argument('template_id')
@click.option('--scope', type=click.Choice(['project', 'user']), default='project',
              help='Installation scope')
@click.option('--var', '-v', multiple=True, help='Set template variables (key=value)')
@click.pass_context
def install(ctx, template_id, scope, var):
    """Install a template - Load the cannons!"""
    config_dir = ctx.obj['config_dir'] if scope == 'project' else Path.home()
    template_dir = Path.home() / ".eyelet" / "templates"

    template_service = TemplateService(FileTemplateRepository(template_dir))
    config_service = ConfigurationService(config_dir)

    # Parse variables
    variables = {}
    for var_str in var:
        if '=' in var_str:
            key, value = var_str.split('=', 1)
            variables[key] = value

    try:
        # Get template
        tmpl = template_service.get_template(template_id)
        if not tmpl:
            console.print(f"[red]Template '{template_id}' not found[/red]")
            return

        # Check for required variables
        if tmpl.variables:
            for var_name, default_value in tmpl.variables.items():
                if var_name not in variables:
                    value = Prompt.ask(
                        f"Value for '{var_name}'",
                        default=str(default_value) if default_value else None
                    )
                    variables[var_name] = value

        # Install template
        hooks = template_service.install_template(template_id, variables)

        # Load current configuration
        config = config_service.load_configuration()

        # Add hooks from template
        for hook in hooks:
            config.add_hook(hook)

        # Save configuration
        config_service.save_configuration(config)

        console.print(f"[green]✓ Template '{tmpl.name}' installed successfully![/green]")
        console.print(f"Added {len(hooks)} hooks to {scope} configuration")

    except TemplateError as e:
        console.print(f"[red]Template error: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Installation failed: {e}[/red]")


@template.command()
@click.argument('template_file', type=click.Path(exists=True))
def import_template(template_file):
    """Import a template file - Bring aboard new ordinance"""
    template_dir = Path.home() / ".eyelet" / "templates"
    template_service = TemplateService(FileTemplateRepository(template_dir))

    try:
        with open(template_file) as f:
            template_data = json.load(f)

        # Validate and save
        from eyelet.domain.models import Template
        tmpl = Template(**template_data)

        # Check if already exists
        existing = template_service.get_template(tmpl.id)
        if existing:
            if not Confirm.ask(f"Template '{tmpl.id}' already exists. Overwrite?"):
                console.print("[yellow]Import cancelled[/yellow]")
                return

        # Save to repository
        template_repo = FileTemplateRepository(template_dir)
        template_repo.save(tmpl)

        console.print(f"[green]✓ Template '{tmpl.name}' imported successfully![/green]")

    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON in template file: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Import failed: {e}[/red]")


@template.command()
@click.argument('template_id')
@click.argument('output_file', type=click.Path())
def export(template_id, output_file):
    """Export a template - Share the wealth"""
    template_dir = Path.home() / ".eyelet" / "templates"
    template_service = TemplateService(FileTemplateRepository(template_dir))

    tmpl = template_service.get_template(template_id)
    if not tmpl:
        console.print(f"[red]Template '{template_id}' not found[/red]")
        return

    try:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(tmpl.model_dump(), f, indent=2, default=str)

        console.print(f"[green]✓ Template exported to {output_file}[/green]")

    except Exception as e:
        console.print(f"[red]Export failed: {e}[/red]")


@template.command()
def create():
    """Create a new template interactively - Forge new weapons"""
    console.print("[bold]Creating new template[/bold]")

    # Basic information
    template_id = Prompt.ask("Template ID (lowercase, no spaces)")
    name = Prompt.ask("Template name")
    description = Prompt.ask("Description")
    category = Prompt.ask(
        "Category",
        choices=["security", "monitoring", "development", "testing", "custom"],
        default="custom"
    )
    author = Prompt.ask("Author name (optional)", default="")

    # Tags
    tags_str = Prompt.ask("Tags (comma-separated, optional)", default="")
    tags = [tag.strip() for tag in tags_str.split(",") if tag.strip()]

    # Create template
    from eyelet.domain.models import Template
    tmpl = Template(
        id=template_id,
        name=name,
        description=description,
        category=category,
        author=author or None,
        tags=tags,
        hooks=[]
    )

    # Add hooks interactively
    console.print("\n[bold]Add hooks to template[/bold]")
    console.print("[dim]Press Ctrl+C when done adding hooks[/dim]")

    try:
        while True:
            console.print(f"\n[cyan]Hook #{len(tmpl.hooks) + 1}[/cyan]")

            # This would reuse the hook creation logic from configure.add
            # For now, we'll skip the interactive part
            if not Confirm.ask("Add another hook?", default=True):
                break

    except KeyboardInterrupt:
        pass

    # Save template
    template_dir = Path.home() / ".eyelet" / "templates"
    template_repo = FileTemplateRepository(template_dir)

    try:
        template_repo.save(tmpl)
        console.print(f"\n[green]✓ Template '{name}' created successfully![/green]")
        console.print(f"ID: {template_id}")
    except Exception as e:
        console.print(f"[red]Failed to save template: {e}[/red]")
