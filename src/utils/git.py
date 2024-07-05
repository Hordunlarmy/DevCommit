#!/usr/bin/env python3
"""Git utilities"""

import subprocess
from typing import List, Optional


class KnownError(Exception):
    pass


def assert_git_repo() -> str:
    """
    Asserts that the current directory is a Git repository.
    Returns the top-level directory path of the repository.
    """

    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        raise KnownError('The current directory must be a Git repository!')


def exclude_from_diff(path: str) -> str:
    """
    Prepares a Git exclusion path string for the diff command.
    """

    return f':(exclude){path}'


# List of default files to exclude from the diff
files_to_exclude = [
    'package-lock.json',
    'pnpm-lock.yaml',
    '*.lock'
]


def get_staged_diff(
        exclude_files: Optional[List[str]] = None) -> Optional[dict]:
    """
    Gets the list of staged files and their diff, excluding specified files.
    """
    exclude_files = exclude_files or []
    diff_cached = ['git', 'diff', '--cached', '--diff-algorithm=minimal']
    excluded_from_diff = (
        [exclude_from_diff(f) for f in files_to_exclude + exclude_files])

    try:
        # Get the list of staged files excluding specified files
        files = subprocess.run(
            diff_cached + ['--name-only'] + excluded_from_diff,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        files_result = (
            files.stdout.strip().split('\n') if files.stdout.strip() else []
        )
        if not files_result:
            return None

        # Get the staged diff excluding specified files
        diff = subprocess.run(
            diff_cached + excluded_from_diff,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        diff_result = diff.stdout.strip()

        return {
            'files': files_result,
            'diff': diff_result
        }
    except subprocess.CalledProcessError:
        return None


def get_detected_message(files: List[str]) -> str:
    """
    Returns a message indicating the number of staged files.
    """
    return (
        f"Detected {len(files):,} staged file{'s' if len(files) > 1 else ''}"
    )
