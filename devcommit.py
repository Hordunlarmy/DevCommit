import subprocess

from InquirerPy import prompt
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from rich.console import Console
from src.utils.parser import CommitFlag, parse_arguments

from src.app.gemini_ai import generateCommitMessage
from src.utils.git import (KnownError, assert_git_repo,
                           get_detected_message, get_staged_diff)
from src import Logger


logger_instance = Logger("__devcommit__")
logger = logger_instance.get_logger()


# Function to check if any commits exist
def has_commits() -> bool:
    result = subprocess.run(["git", "rev-parse", "HEAD"],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode == 0


# Main function
def main(flags: CommitFlag):
    try:
        # Ensure current directory is a git repository
        assert_git_repo()

        console = Console()

        # Detect staged files
        with console.status(
            "[bold green]Detecting staged files...[/bold green]",
                spinner="dots") as status:
            staged = get_staged_diff(flags["excludeFiles"])

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

        # Stage all changes if flag is set
        if flags["stageAll"]:
            subprocess.run(["git", "add", "--update"], check=True)

        # Analyze changes
        with console.status(
                "[bold green]The AI is analyzing your changes...[/bold green]",
                spinner="dots"):
            diff = subprocess.run(
                ["git", "diff", "--staged"],
                stdout=subprocess.PIPE,
                text=True,
            ).stdout

            if not diff:
                raise KnownError(
                    "No diff could be generated. "
                    "Ensure you have changes staged.")

            commit_message = generateCommitMessage(diff)
            if isinstance(commit_message, str):
                commit_message = commit_message.split('|')

            if not commit_message:
                raise KnownError(
                    "No commit messages were generated. Try again.")

        # Prompt user to select a commit message
        logger.info(f"Commit messages: {commit_message}")
        if len(commit_message) == 1:
            # message = commit_message[0]
            # confirm = prompt(
            #     [
            #         {
            #             "type": "confirm",
            #             "message": f"Use this commit message?\n"
            #             f"{message}\n",
            #             "default": True,
            #         }
            #     ]
            # )
            action = inquirer.select(
                message="Select a commit message or cancel:",
                choices=[*commit_message, Choice("Cancel", value='cancel')],
                default=None,
            ).execute()

            # Check user selection
            if action == 'cancel':
                console.print("[bold red]Commit cancelled[/bold red]")
                return
            else:
                commit = action

        else:
            action = inquirer.select(
                message="Select an action:",
                choices=[*commit_message,
                         Choice("Cancel", 'cancel'),
                         ],
                default=None,
            ).execute()
            if action == 'cancel':
                console.print("[bold red]Commit cancelled[/bold red]")
                return
            else:
                commit = action

        # Commit changes
        subprocess.run(["git", "commit", "-m", commit, *flags["rawArgv"]])
        console.print("[bold green]✔ Successfully committed![/bold green]")

    except KnownError as error:
        console.print(f"[bold red]✖ {error}[/bold red]")
    except subprocess.CalledProcessError as error:
        console.print(f"[bold red]✖ Git command failed: {error}[/bold red]")
    except Exception as error:
        console.print(f"[bold red]✖ {error}[/bold red]")


if __name__ == "__main__":
    commit_flags = parse_arguments()
    main(commit_flags)
