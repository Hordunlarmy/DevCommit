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
        
        # Print header
        console.print("\n[bold cyan]DevCommit[/bold cyan] [dim]│ AI-powered commit generator[/dim]")
        console.print("[dim]" + "─" * 50 + "[/dim]\n")

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
        
        # Print completion message
        console.print("\n[bold green]═══════════════════════════════════════════════════[/bold green]")
        console.print("[bold green]✓[/bold green] [green]All commits completed successfully![/green]")
        console.print("[bold green]═══════════════════════════════════════════════════[/bold green]\n")

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Operation cancelled by user[/yellow]")
        return
    except KnownError as error:
        logger.error(str(error))
        console.print(f"\n[red]Error: {error}[/red]")
    except subprocess.CalledProcessError as error:
        logger.error(str(error))
        console.print(f"\n[red]Git command failed: {error}[/red]")
    except Exception as error:
        logger.error(str(error))
        console.print(f"\n[red]Error: {error}[/red]")


def stage_changes(console):
    with console.status(
        "→ Staging changes...",
        spinner="dots",
    ):
        subprocess.run(["git", "add", "--update"], check=True)


def detect_staged_files(console, exclude_files):
    with console.status(
        "→ Detecting staged files...",
        spinner="dots",
    ):
        staged = get_staged_diff(exclude_files)
        if not staged:
            raise KnownError(
                "No staged changes found. Stage your changes manually, or "
                "automatically stage all changes with the `--stageAll` flag."
            )
        console.print(
            f"\n[bold green]✓[/bold green] {get_detected_message(staged['files'])}"
        )
        for file in staged["files"]:
            console.print(f"  • {file}")
        return staged


def analyze_changes(console):
    import sys
    
    with console.status(
        "→ AI analyzing changes...",
        spinner="dots",
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
        "question": "#00afaf bold",
        "questionmark": "#00afaf bold",
        "pointer": "#00afaf",
        "instruction": "#808080",
        "answer": "#00afaf bold",
        "fuzzy_info": ""  # Hide the counter
    }, style_override=False)
    
    # Add numbered options (plain text since InquirerPy doesn't support ANSI in choices)
    numbered_choices = []
    for idx, msg in enumerate(commit_message, 1):
        if isinstance(msg, str):
            numbered_choices.append({"name": f"  {idx}. {msg}", "value": msg})
        else:
            numbered_choices.append(msg)
    
    choices = [
        *numbered_choices,
        {"name": "  [Cancel]", "value": "cancel"}
    ]
    
    action = inquirer.fuzzy(
        message=tag,
        style=style,
        choices=choices,
        default=None,
        instruction="(Type to filter)",
        qmark="❯",
        info=False  # Disable info/counter
    ).execute()

    if action == "cancel":
        console.print("\n[yellow]Commit cancelled[/yellow]")
        return None
    return action


def commit_changes(console, commit, raw_argv):
    subprocess.run(["git", "commit", "-m", commit, *raw_argv])
    console.print("[bold green]✓[/bold green] Committed successfully")


def prompt_commit_strategy(console, grouped):
    """Prompt user to choose between global or directory-based commits."""
    console.print("\n[bold cyan]═══ Multiple directories detected ═══[/bold cyan]")
    for directory, files in grouped.items():
        console.print(f"  [cyan]▸[/cyan] [bold]{directory}[/bold] [dim]({len(files)} file(s))[/dim]")
    console.print()
    
    style = get_style({
        "question": "#00afaf bold",
        "questionmark": "#00afaf bold",
        "pointer": "#00afaf",
        "instruction": "#808080",
        "answer": "#00afaf bold"
    }, style_override=False)
    
    strategy = inquirer.select(
        message="Commit strategy",
        style=style,
        choices=[
            {"name": "  One commit for all changes", "value": False},
            {"name": "  Separate commits per directory", "value": True},
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
    
    console.print(f"\n[bold cyan]═══ Processing {len(grouped)} directories ═══[/bold cyan]")
    
    # Ask if user wants to commit all or select specific directories
    style = get_style({
        "question": "#00afaf bold",
        "questionmark": "#00afaf bold",
        "pointer": "#00afaf",
        "instruction": "#808080",
        "answer": "#00afaf bold",
        "checkbox": "#00afaf"
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
        console.print("\n[yellow]No directories selected[/yellow]")
        return
    
    # Process each selected directory
    for idx, directory in enumerate(selected_directories, 1):
        files = grouped[directory]
        console.print(f"\n[cyan]{'═' * 50}[/cyan]")
        console.print(f"[bold cyan]▸[/bold cyan] [bold][{idx}/{len(selected_directories)}] {directory}[/bold]")
        console.print(f"[dim]{'─' * 50}[/dim]")
        
        for file in files:
            console.print(f"  [cyan]•[/cyan] {file}")
        
        # Get diff for this directory's files
        with console.status(
            f"→ Analyzing {directory}...",
            spinner="dots",
        ):
            diff = get_diff_for_files(files, flags["excludeFiles"])
            
            if not diff:
                console.print(f"[yellow]No diff for {directory}, skipping[/yellow]")
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
                console.print(f"[yellow]No commit message generated for {directory}, skipping[/yellow]")
                continue
        
        # Prompt for commit message selection
        selected_commit = prompt_commit_message(console, commit_message)
        
        if selected_commit:
            # Commit only the files in this directory
            subprocess.run(["git", "commit", "-m", selected_commit, *flags["rawArgv"], "--"] + files)
            console.print(f"\n[bold green]✓[/bold green] [green]Committed {directory}[/green]")
        else:
            console.print(f"\n[yellow]⊘ Skipped {directory}[/yellow]")


if __name__ == "__main__":
    main()
