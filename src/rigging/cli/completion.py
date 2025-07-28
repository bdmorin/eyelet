"""Shell completion support for Rigging"""

import click
import os
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

console = Console()

SHELLS = ['bash', 'zsh', 'fish', 'powershell']

COMPLETION_SCRIPTS = {
    'bash': '''
# Rigging completion for Bash
_rigging_completion() {
    local IFS=$'\\n'
    local response
    
    response=$(env COMP_WORDS="${COMP_WORDS[*]}" COMP_CWORD=$COMP_CWORD _RIGGING_COMPLETE=bash_complete $1)
    
    for completion in $response; do
        IFS=' ' read type value <<< "$completion"
        
        if [[ $type == 'dir' ]]; then
            COMPREPLY=()
            compopt -o dirnames
        elif [[ $type == 'file' ]]; then
            COMPREPLY=()
            compopt -o default
        elif [[ $type == 'plain' ]]; then
            COMPREPLY+=($value)
        fi
    done
    
    return 0
}

complete -F _rigging_completion -o nosort rigging
''',
    'zsh': '''
# Rigging completion for Zsh
_rigging_completion() {
    local -a completions
    local -a completions_with_descriptions
    local -a response
    (( ! $+commands[rigging] )) && return 1
    
    response=("${(@f)$(env COMP_WORDS="${words[*]}" COMP_CWORD=$((CURRENT-1)) _RIGGING_COMPLETE=zsh_complete rigging)}")
    
    for type key descr in ${response}; do
        if [[ "$type" == "plain" ]]; then
            if [[ "$descr" == "_" ]]; then
                completions+=("$key")
            else
                completions_with_descriptions+=("$key":"$descr")
            fi
        elif [[ "$type" == "dir" ]]; then
            _path_files -/
        elif [[ "$type" == "file" ]]; then
            _path_files -f
        fi
    done
    
    if [ -n "$completions_with_descriptions" ]; then
        _describe -V unsorted completions_with_descriptions -U
    fi
    
    if [ -n "$completions" ]; then
        compadd -U -V unsorted -a completions
    fi
}

compdef _rigging_completion rigging
''',
    'fish': '''
# Rigging completion for Fish
function _rigging_completion
    set -l response (env COMP_WORDS=(commandline -cp) COMP_CWORD=(commandline -t) _RIGGING_COMPLETE=fish_complete rigging)
    
    for completion in $response
        set -l metadata (string split "," $completion)
        
        if test $metadata[1] = "dir"
            __fish_complete_directories (commandline -ct)
        else if test $metadata[1] = "file"
            __fish_complete_path (commandline -ct)
        else if test $metadata[1] = "plain"
            echo $metadata[2]
        end
    end
end

complete -c rigging -f -a "(_rigging_completion)"
''',
    'powershell': '''
# Rigging completion for PowerShell
Register-ArgumentCompleter -Native -CommandName rigging -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)
    
    $env:COMP_WORDS = $commandAst.ToString()
    $env:COMP_CWORD = $wordToComplete
    $env:_RIGGING_COMPLETE = "powershell_complete"
    
    rigging | ForEach-Object {
        $type, $value = $_ -split " ", 2
        
        if ($type -eq "dir") {
            Get-ChildItem -Directory | Where-Object Name -like "$wordToComplete*"
        } elseif ($type -eq "file") {
            Get-ChildItem | Where-Object Name -like "$wordToComplete*"
        } elseif ($type -eq "plain") {
            [System.Management.Automation.CompletionResult]::new($value, $value, 'ParameterValue', $value)
        }
    }
}
'''
}


@click.group()
def completion():
    """Manage shell completion for Rigging"""
    pass


@completion.command()
@click.argument('shell', type=click.Choice(SHELLS), required=False)
@click.option('--path', help='Path to install completion script')
def install(shell, path):
    """
    Install shell completion - Ready the rigging for smooth sailing!
    
    Examples:
    
        # Auto-detect shell and install
        rigging completion install
        
        # Install for specific shell
        rigging completion install bash
        rigging completion install zsh
        
        # Install to custom location
        rigging completion install --path ~/.config/fish/completions/
    """
    if not shell:
        shell = _detect_shell()
        if not shell:
            console.print("[red]Could not detect shell. Please specify: bash, zsh, fish, or powershell[/red]")
            sys.exit(1)
    
    console.print(f"[bold]Installing completion for {shell}...[/bold]")
    
    completion_script = COMPLETION_SCRIPTS[shell]
    
    if path:
        # Install to specified path
        install_path = Path(path)
        if install_path.is_dir():
            install_path = install_path / f"rigging.{shell}"
    else:
        # Determine default installation path
        install_path = _get_completion_path(shell)
    
    try:
        # Ensure directory exists
        install_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write completion script
        with open(install_path, 'w') as f:
            f.write(completion_script)
        
        console.print(f"[green]✓ Completion script installed to: {install_path}[/green]")
        
        # Shell-specific instructions
        if shell == 'bash':
            rc_file = Path.home() / '.bashrc'
            source_line = f'source {install_path}'
            console.print(f"\n[yellow]Add this line to your {rc_file}:[/yellow]")
            console.print(f"[cyan]{source_line}[/cyan]")
        elif shell == 'zsh':
            rc_file = Path.home() / '.zshrc'
            source_line = f'source {install_path}'
            console.print(f"\n[yellow]Add this line to your {rc_file}:[/yellow]")
            console.print(f"[cyan]{source_line}[/cyan]")
        elif shell == 'fish':
            console.print("\n[green]Fish will automatically load the completion.[/green]")
        elif shell == 'powershell':
            console.print("\n[yellow]Add this line to your PowerShell profile:[/yellow]")
            console.print(f"[cyan]. {install_path}[/cyan]")
        
        console.print("\n[dim]Restart your shell or source the file to enable completion.[/dim]")
        
    except Exception as e:
        console.print(f"[red]Failed to install completion: {e}[/red]")
        sys.exit(1)


@completion.command()
@click.argument('shell', type=click.Choice(SHELLS))
def show(shell):
    """
    Show completion script for a shell - Inspect the rigging!
    
    This displays the completion script without installing it.
    """
    completion_script = COMPLETION_SCRIPTS[shell]
    
    console.print(Panel(
        completion_script,
        title=f"{shell.title()} Completion Script",
        border_style="cyan"
    ))
    
    console.print(f"\n[dim]To install, run: rigging completion install {shell}[/dim]")


@completion.command()
def status():
    """Check completion installation status - Survey the rigging!"""
    console.print("[bold]Shell Completion Status[/bold]\n")
    
    for shell in SHELLS:
        install_path = _get_completion_path(shell)
        if install_path.exists():
            console.print(f"[green]✓[/green] {shell:12} Installed at {install_path}")
        else:
            console.print(f"[red]✗[/red] {shell:12} Not installed")
    
    current_shell = _detect_shell()
    if current_shell:
        console.print(f"\n[dim]Detected shell: {current_shell}[/dim]")


def _detect_shell():
    """Detect the current shell"""
    shell_env = os.environ.get('SHELL', '')
    
    if 'bash' in shell_env:
        return 'bash'
    elif 'zsh' in shell_env:
        return 'zsh'
    elif 'fish' in shell_env:
        return 'fish'
    elif sys.platform == 'win32':
        return 'powershell'
    
    # Try to detect from parent process
    try:
        import psutil
        parent = psutil.Process(os.getppid())
        parent_name = parent.name().lower()
        
        for shell in SHELLS:
            if shell in parent_name:
                return shell
    except:
        pass
    
    return None


def _get_completion_path(shell):
    """Get the default completion installation path for a shell"""
    home = Path.home()
    
    if shell == 'bash':
        # Try common bash completion directories
        dirs = [
            home / '.bash_completion.d',
            Path('/etc/bash_completion.d'),
            Path('/usr/local/etc/bash_completion.d'),
            home / '.config' / 'bash_completion.d'
        ]
        for d in dirs:
            if d.exists() and os.access(d, os.W_OK):
                return d / 'rigging'
        # Fallback
        return home / '.rigging-completion.bash'
    
    elif shell == 'zsh':
        # Zsh completion paths
        dirs = [
            home / '.zsh' / 'completions',
            home / '.config' / 'zsh' / 'completions',
            Path('/usr/local/share/zsh/site-functions'),
        ]
        for d in dirs:
            if d.exists() and os.access(d, os.W_OK):
                return d / '_rigging'
        # Fallback
        return home / '.rigging-completion.zsh'
    
    elif shell == 'fish':
        return home / '.config' / 'fish' / 'completions' / 'rigging.fish'
    
    elif shell == 'powershell':
        return home / '.rigging-completion.ps1'
    
    return home / f'.rigging-completion.{shell}'