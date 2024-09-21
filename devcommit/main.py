import subprocess

from InquirerPy import get_style, inquirer
from rich.console import Console

from devcommit.app.gemini_ai import generateCommitMessage
from devcommit.utils.git import (KnownError, assert_git_repo,
                                 get_detected_message, get_staged_diff)
from devcommit.utils.logger import Logger
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

        if flags["stageAll"]:
            stage_changes(console)

        detect_staged_files(console, flags["excludeFiles"])
        commit_message = analyze_changes(console)

        selected_commit = prompt_commit_message(console, commit_message)
        if selected_commit:
            commit_changes(console, selected_commit, flags["rawArgv"])

    except KnownError as error:
        logger.error(str(error))
        console.print(f"[bold red]✖ {error}[/bold red]")
    except subprocess.CalledProcessError as error:
        logger.error(str(error))
        console.print(f"[bold red]✖ Git command failed: {error}[/bold red]")
    except Exception as error:
        logger.error(str(error))
        console.print(f"[bold red]✖ {error}[/bold red]")


def stage_changes(console):
    with console.status(
        "[bold green]Staging all changes...[/bold green]",
        spinner="dots",
    ):
        subprocess.run(["git", "add", "--update"], check=True)


def detect_staged_files(console, exclude_files):
    with console.status(
        "[bold green]Detecting staged files...[/bold green]",
        spinner="dots",
    ):
        staged = get_staged_diff(exclude_files)
        if not staged:
            raise KnownError(
                "No staged changes found. Stage your changes manually, or "
                "automatically stage all changes with the `--stageAll` flag."
            )
        console.print(
            f"[bold green]{get_detected_message(staged['files'])}:"
            f"[/bold green]"
        )
        for file in staged["files"]:
            console.print(f" - {file}")
        return staged


def analyze_changes(console):
    with console.status(
        "[bold green]The AI is analyzing your changes...[/bold green]",
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

        commit_message = generateCommitMessage(diff)
        if isinstance(commit_message, str):
            commit_message = commit_message.split("|")

        if not commit_message:
            raise KnownError("No commit messages were generated. Try again.")

        return commit_message


def prompt_commit_message(console, commit_message):
    tag = (
        "Use This Commit Message? "
        if len(commit_message) == 1
        else "Select A Commit Message:"
    )
    style = get_style({"instruction": "#abb2bf"}, style_override=False)
    action = inquirer.fuzzy(
        message=tag,
        style=style,
        choices=[*commit_message, "cancel"],
        default=None,
    ).execute()

    if action == "cancel":
        console.print("[bold red]Commit cancelled[/bold red]")
        return None
    return action


def commit_changes(console, commit, raw_argv):
    subprocess.run(["git", "commit", "-m", commit, *raw_argv])
    console.print("[bold green]✔ Successfully committed![/bold green]")


if __name__ == "__main__":
    main()
