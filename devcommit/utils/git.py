#!/usr/bin/env python3
"""Git utilities"""

import os
import subprocess
from collections import defaultdict
from typing import Dict, List, Optional


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


def get_default_excludes() -> List[str]:
    """
    Get list of files to exclude from diff.
    Priority: Config > Defaults
    """
    try:
        from devcommit.utils.logger import config
        
        # Get from config (supports comma-separated list)
        exclude_config = config("EXCLUDE_FILES", default="")
        
        if exclude_config:
            # Parse comma-separated values and strip whitespace
            config_excludes = [f.strip() for f in exclude_config.split(",") if f.strip()]
            return config_excludes
    except:
        pass
    
    # Default exclusions
    return [
        'package-lock.json',
        'pnpm-lock.yaml',
        'yarn.lock',
        '*.lock'
    ]


# Get default files to exclude (can be overridden via config)
files_to_exclude = get_default_excludes()


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


def group_files_by_directory(files: List[str]) -> Dict[str, List[str]]:
    """
    Groups files by their root directory (first-level directory).
    Files in the repository root are grouped under 'root'.
    """
    grouped = defaultdict(list)
    
    for file_path in files:
        # Get the first directory in the path
        parts = file_path.split(os.sep)
        if len(parts) > 1:
            root_dir = parts[0]
        else:
            root_dir = 'root'
        grouped[root_dir].append(file_path)
    
    return dict(grouped)


def get_diff_for_files(files: List[str], exclude_files: Optional[List[str]] = None) -> str:
    """
    Gets the diff for specific files.
    """
    exclude_files = exclude_files or []
    
    # Filter out excluded files from the list
    all_excluded = files_to_exclude + exclude_files
    filtered_files = [
        f for f in files 
        if not any(f.endswith(excl.replace('*', '')) or excl.replace(':(exclude)', '') in f 
                   for excl in all_excluded)
    ]
    
    if not filtered_files:
        return ""
    
    try:
        diff = subprocess.run(
            ['git', 'diff', '--cached', '--diff-algorithm=minimal', '--'] + filtered_files,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return diff.stdout.strip()
    except subprocess.CalledProcessError:
        return ""
