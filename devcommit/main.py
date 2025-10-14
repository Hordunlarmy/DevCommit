import os
import subprocess

# Suppress Google gRPC/ALTS warnings before any imports
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '3'
os.environ['GRPC_ENABLE_FORK_SUPPORT'] = '1'

from InquirerPy import get_style, inquirer
from rich.console import Console

from devcommit.app.gemini_ai import generateCommitMessage
from devcommit.utils.git import (KnownError, assert_git_repo,
                                 get_detected_message, get_diff_for_files,
                                 get_staged_diff, group_files_by_directory)
from devcommit.utils.logger import Logger, config
from devcommit.utils.parser import CommitFlag, parse_arguments

logger_instance = Logger("__devcommit__")
logger = logger_instance.get_logger()


# Function to check if any commits exist
def has_commits() -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.returncode == 0


# Main function
def main(flags: CommitFlag = None):
    if flags is None:
        flags = parse_arguments()

    try:
        assert_git_repo()
        console = Console()
        
        # Print stylish header with gradient effect
        console.print()
        console.print("╭" + "─" * 60 + "╮", style="bold cyan")
        console.print("│" + " " * 60 + "│", style="bold cyan")
        console.print("│" + "  🚀 [bold white on cyan] DevCommit [/bold white on cyan]  [bold white]AI-Powered Commit Generator[/bold white]".ljust(76) + "│", style="bold cyan")
        console.print("│" + " " * 60 + "│", style="bold cyan")
        console.print("╰" + "─" * 60 + "╯", style="bold cyan")
        
        # Display provider and model info
        provider = config("AI_PROVIDER", default="gemini").lower()
        model = ""
        
        if provider == "ollama":
            model = config("OLLAMA_MODEL", default="llama3")
        elif provider == "gemini":
            model = config("GEMINI_MODEL", default=None) or config("MODEL_NAME", default="gemini-1.5-flash")
        elif provider == "openai":
            model = config("OPENAI_MODEL", default="gpt-4o-mini")
        elif provider == "groq":
            model = config("GROQ_MODEL", default="llama-3.3-70b-versatile")
        elif provider == "anthropic":
            model = config("ANTHROPIC_MODEL", default="claude-3-haiku-20240307")
        elif provider == "custom":
            model = config("CUSTOM_MODEL", default="default")
        
        console.print(f"[dim]Provider:[/dim] [bold magenta]{provider}[/bold magenta] [dim]│[/dim] [dim]Model:[/dim] [bold magenta]{model}[/bold magenta]")
        console.print()

        if flags["stageAll"]:
            stage_changes(console)

        staged = detect_staged_files(console, flags["excludeFiles"])
        
        # Determine commit strategy
        # Priority: CLI flag > config (file or env) > interactive prompt
        use_per_directory = flags.get("directory", False)
        
        # If not explicitly set via CLI, check config (file or environment variable)
        if not use_per_directory:
            commit_mode = config("COMMIT_MODE", default="auto").lower()
            if commit_mode == "directory":
                use_per_directory = True
            elif commit_mode == "global":
                use_per_directory = False
            # If "auto" or not set, fall through to interactive prompt
        
        # If still not set, check if there are multiple directories and prompt
        if not use_per_directory and config("COMMIT_MODE", default="auto").lower() == "auto":
            grouped = group_files_by_directory(staged["files"])
            if len(grouped) > 1:
                use_per_directory = prompt_commit_strategy(console, grouped)
        
        if use_per_directory:
            process_per_directory_commits(console, staged, flags)
        else:
            process_global_commit(console, flags)
        
        # Print stylish completion message
        console.print()
        console.print("╭" + "─" * 60 + "╮", style="bold green")
        console.print("│" + " " * 60 + "│", style="bold green")
        console.print("│" + "     ✨ [bold white]All commits completed successfully![/bold white] ✨     ".ljust(68) + "│", style="bold green")
        console.print("│" + " " * 60 + "│", style="bold green")
        console.print("╰" + "─" * 60 + "╯", style="bold green")
        console.print()

    except KeyboardInterrupt:
        console.print("\n\n[bold yellow]⚠️  Operation cancelled by user[/bold yellow]\n")
        return
    except KnownError as error:
        logger.error(str(error))
        console.print(f"\n[bold red]❌ Error:[/bold red] [red]{error}[/red]\n")
    except subprocess.CalledProcessError as error:
        logger.error(str(error))
        console.print(f"\n[bold red]❌ Git command failed:[/bold red] [red]{error}[/red]\n")
    except Exception as error:
        logger.error(str(error))
        console.print(f"\n[bold red]❌ Unexpected error:[/bold red] [red]{error}[/red]\n")


def stage_changes(console):
    with console.status(
        "[cyan]🔄 Staging changes...[/cyan]",
        spinner="dots",
        spinner_style="cyan"
    ):
        subprocess.run(["git", "add", "--update"], check=True)


def detect_staged_files(console, exclude_files):
    with console.status(
        "[cyan]🔍 Detecting staged files...[/cyan]",
        spinner="dots",
        spinner_style="cyan"
    ):
        staged = get_staged_diff(exclude_files)
        if not staged:
            raise KnownError(
                "No staged changes found. Stage your changes manually, or "
                "automatically stage all changes with the `--stageAll` flag."
            )
        console.print(
            f"\n[bold green]✅ {get_detected_message(staged['files'])}[/bold green]"
        )
        console.print("[dim]" + "─" * 60 + "[/dim]")
        for file in staged["files"]:
            console.print(f"  [cyan]▸[/cyan] [white]{file}[/white]")
        console.print("[dim]" + "─" * 60 + "[/dim]")
        return staged


def analyze_changes(console):
    import sys
    
    with console.status(
        "[magenta]🤖 AI analyzing changes...[/magenta]",
        spinner="dots",
        spinner_style="magenta"
    ):
        diff = subprocess.run(
            ["git", "diff", "--staged"],
            stdout=subprocess.PIPE,
            text=True,
        ).stdout

        if not diff:
            raise KnownError(
                "No diff could be generated. Ensure you have changes staged."
            )

        # Suppress stderr during AI call to hide ALTS warnings
        _stderr = sys.stderr
        _devnull = open(os.devnull, 'w')
        sys.stderr = _devnull
        
        try:
            commit_message = generateCommitMessage(diff)
        finally:
            sys.stderr = _stderr
            _devnull.close()
        
        if isinstance(commit_message, str):
            commit_message = commit_message.split("|")

        if not commit_message:
            raise KnownError("No commit messages were generated. Try again.")

        return commit_message


def prompt_commit_message(console, commit_message):
    tag = (
        "Select commit message"
        if len(commit_message) > 1
        else "Confirm commit message"
    )
    style = get_style({
        "question": "#00d7ff bold",
        "questionmark": "#00d7ff bold",
        "pointer": "#00d7ff bold",
        "instruction": "#7f7f7f",
        "answer": "#00d7ff bold",
        "fuzzy_info": ""  # Hide the counter
    }, style_override=False)
    
    console.print()
    console.print("[bold cyan]📝 Generated Commit Messages:[/bold cyan]")
    console.print()
    
    # Add numbered options (plain text since InquirerPy doesn't support ANSI in choices)
    numbered_choices = []
    for idx, msg in enumerate(commit_message, 1):
        if isinstance(msg, str):
            numbered_choices.append({"name": f"  {idx}. {msg}", "value": msg})
        else:
            numbered_choices.append(msg)
    
    choices = [
        *numbered_choices,
        {"name": "  ❌ [Cancel]", "value": "cancel"}
    ]
    
    action = inquirer.fuzzy(
        message=tag,
        style=style,
        choices=choices,
        default=None,
        instruction="(Type to filter or use arrows)",
        qmark="❯",
        info=False  # Disable info/counter
    ).execute()

    if action == "cancel":
        console.print("\n[bold yellow]⚠️  Commit cancelled[/bold yellow]\n")
        return None
    return action


def commit_changes(console, commit, raw_argv):
    subprocess.run(["git", "commit", "-m", commit, *raw_argv])
    console.print("\n[bold green]✅ Committed successfully![/bold green]")


def prompt_commit_strategy(console, grouped):
    """Prompt user to choose between global or directory-based commits."""
    console.print()
    console.print("╭" + "─" * 60 + "╮", style="bold yellow")
    console.print("│" + "  📂 [bold white]Multiple directories detected[/bold white]".ljust(70) + "│", style="bold yellow")
    console.print("╰" + "─" * 60 + "╯", style="bold yellow")
    console.print()
    
    for directory, files in grouped.items():
        console.print(f"  [yellow]▸[/yellow] [bold white]{directory}[/bold white] [dim]({len(files)} file(s))[/dim]")
    console.print()
    
    style = get_style({
        "question": "#00d7ff bold",
        "questionmark": "#00d7ff bold",
        "pointer": "#00d7ff bold",
        "instruction": "#7f7f7f",
        "answer": "#00d7ff bold"
    }, style_override=False)
    
    strategy = inquirer.select(
        message="Commit strategy",
        style=style,
        choices=[
            {"name": "  🌐 One commit for all changes", "value": False},
            {"name": "  📁 Separate commits per directory", "value": True},
        ],
        default=None,
        instruction="(Use arrow keys)",
        qmark="❯"
    ).execute()
    
    return strategy


def process_global_commit(console, flags):
    """Process a single global commit for all changes."""
    commit_message = analyze_changes(console)
    selected_commit = prompt_commit_message(console, commit_message)
    if selected_commit:
        commit_changes(console, selected_commit, flags["rawArgv"])


def process_per_directory_commits(console, staged, flags):
    """Process separate commits for each directory."""
    grouped = group_files_by_directory(staged["files"])
    
    console.print()
    console.print("╭" + "─" * 60 + "╮", style="bold magenta")
    console.print("│" + f"  🔮 [bold white]Processing {len(grouped)} directories[/bold white]".ljust(71) + "│", style="bold magenta")
    console.print("╰" + "─" * 60 + "╯", style="bold magenta")
    console.print()
    
    # Ask if user wants to commit all or select specific directories
    style = get_style({
        "question": "#00d7ff bold",
        "questionmark": "#00d7ff bold",
        "pointer": "#00d7ff bold",
        "instruction": "#7f7f7f",
        "answer": "#00d7ff bold",
        "checkbox": "#00d7ff bold"
    }, style_override=False)
    
    if len(grouped) > 1:
        commit_all = inquirer.confirm(
            message="Commit all directories?",
            style=style,
            default=True,
            instruction="(y/n)",
            qmark="❯"
        ).execute()
        
        if commit_all:
            selected_directories = list(grouped.keys())
        else:
            # Let user select which directories to commit
            directory_choices = [
                {"name": f"{directory} ({len(files)} file(s))", "value": directory}
                for directory, files in grouped.items()
            ]
            
            selected_directories = inquirer.checkbox(
                message="Select directories to commit",
                style=style,
                choices=directory_choices,
                default=list(grouped.keys()),
                instruction="(Space to select, Enter to confirm)",
                qmark="❯"
            ).execute()
    else:
        selected_directories = list(grouped.keys())
    
    if not selected_directories:
        console.print("\n[bold yellow]⚠️  No directories selected[/bold yellow]\n")
        return
    
    # Process each selected directory
    for idx, directory in enumerate(selected_directories, 1):
        files = grouped[directory]
        console.print()
        console.print("┌" + "─" * 60 + "┐", style="bold cyan")
        console.print("│" + f"  📂 [{idx}/{len(selected_directories)}] [bold white]{directory}[/bold white]".ljust(69) + "│", style="bold cyan")
        console.print("└" + "─" * 60 + "┘", style="bold cyan")
        console.print()
        
        for file in files:
            console.print(f"  [cyan]▸[/cyan] [white]{file}[/white]")
        
        # Get diff for this directory's files
        with console.status(
            f"[magenta]🤖 Analyzing {directory}...[/magenta]",
            spinner="dots",
            spinner_style="magenta"
        ):
            diff = get_diff_for_files(files, flags["excludeFiles"])
            
            if not diff:
                console.print(f"\n[bold yellow]⚠️  No diff for {directory}, skipping[/bold yellow]\n")
                continue
            
            # Suppress stderr during AI call to hide ALTS warnings
            import sys
            _stderr = sys.stderr
            _devnull = open(os.devnull, 'w')
            sys.stderr = _devnull
            
            try:
                commit_message = generateCommitMessage(diff)
            finally:
                sys.stderr = _stderr
                _devnull.close()
            
            if isinstance(commit_message, str):
                commit_message = commit_message.split("|")
            
            if not commit_message:
                console.print(f"\n[bold yellow]⚠️  No commit message generated for {directory}, skipping[/bold yellow]\n")
                continue
        
        # Prompt for commit message selection
        selected_commit = prompt_commit_message(console, commit_message)
        
        if selected_commit:
            # Commit only the files in this directory
            subprocess.run(["git", "commit", "-m", selected_commit, *flags["rawArgv"], "--"] + files)
            console.print(f"\n[bold green]✅ Committed {directory}[/bold green]")
        else:
            console.print(f"\n[bold yellow]⊘ Skipped {directory}[/bold yellow]")


if __name__ == "__main__":
    main()
