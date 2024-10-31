#!/usr/bin/env python3
"""Prompt for generating a git commit message"""

from typing import Dict

CommitType = str

commit_type_formats: Dict[CommitType, str] = {
    "": "<commit message>",
    "conventional": "<type>(<optional scope>): <commit message>",
}

commit_types: Dict[CommitType, str] = {
    "normal": "",
    "conventional": """
                    Choose a type from the type-to-description JSON below \
                    that best describes the git diff:
                    {
                    "docs": "Documentation only changes",
                    "style": "Changes that do not affect the meaning of the \
                            code (white-space, formatting, missing \
                            semi-colons, etc)",
                    "refactor": "A code change that neither fixes a bug nor \
                                adds a feature",
                    "perf": "A code change that improves performance",
                    "test": "Adding missing tests or correcting existing \
                            tests",
                    "build": "Changes that affect the build system or \
                            external dependencies",
                    "ci": "Changes to our CI configuration files and scripts",
                    "chore": "Other changes that don't modify src or test \
                            files",
                    "revert": "Reverts a previous commit",
                    "feat": "A new feature",
                    "fix": "A bug fix"
                    }
                    """,
    # References:
    # Commitlint:
    # https://github.com/conventional-changelog/commitlint/blob/18fbed7ea86ac0ec9d5449b4979b762ec4305a92/%40commitlint/config-conventional/index.js#L40-L100
    #
    # Conventional Changelog:
    # https://github.com/conventional-changelog/conventional-changelog/blob/d0e5d5926c8addba74bc962553dd8bcfba90e228/packages/conventional-changelog-conventionalcommits/writer-opts.js#L182-L193
}


def specify_commit_format(commit_type: CommitType) -> str:
    """Specify the commit format for the given commit type"""

    return (
        f"The output response must be in format:\n"
        f"{commit_type_formats[commit_type]}"
    )


def generate_prompt(
    max_length: int, max_no: int, locale: str, commit_type: CommitType
) -> str:
    """Prompt Passed to Gemini for Generating a Git Commit Message"""

    prompt_parts = [
        "Generate a concise git commit message written in present tense for the following code diff with the given specifications below:",
        f"Message language: {locale}",
        f"Commit count: {max_no}",
        "Max_line_per_commit: 1",
        "Separator: '|'",
        f"Commit message must be a maximum of {max_length} characters.",
        "You are to generate commit message or messages based on the count passed. Reply with only the commit message or messages. Exclude anything unnecessary such as translation or description. Only return the commit message or messages. Separation should only be done with Separator not newline.",
        commit_types[commit_type],
        specify_commit_format(commit_type),
    ]

    return "\n".join(filter(bool, prompt_parts))
