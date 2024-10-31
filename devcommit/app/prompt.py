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
    """Generate a detailed prompt for Gemini to create a strict Git commit message."""

    prompt_parts = [
        "You are tasked with generating Git commit messages based solely on the following code diff.",
        "Please adhere to the following specifications meticulously:",
        # Language of the commit message
        f"1. The language of the commit message should be: {locale}. This specifies the linguistic format of the message.",
        # Number of commit messages
        f"2. The total number of commit messages required is: {max_no}. Ensure that you generate exactly this number of messages.",
        # Line and message formatting
        "3. Each commit message must be succinct and limited to a single line. Do not exceed one line per message.",
        # Separator specifications
        "4. If multiple messages are generated, they must be separated using the character '|' only. Do not use any other characters or new lines for separation.",
        # Length restrictions
        f"5. Each individual commit message must not exceed {max_length} characters in length. This is a strict upper limit.",
        # Exclusions from response
        "6. Generate only the commit message(s) as specified. Do not include any additional information, context, translations, or descriptions in your response.",
        # Commit Type instructions
        f"7. Refer to the following commit type specification: {commit_types[commit_type]}. This will guide the nature of the commit messages you produce.",
        # Formatting requirements
        f"8. Follow the specific format required for the given commit type, which is defined as follows: {specify_commit_format(commit_type)}.",
    ]

    # Return the fully constructed prompt as a single formatted string
    return "\n".join(filter(bool, prompt_parts))
