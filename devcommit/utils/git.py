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
    
    # No default exclusions; rely entirely on user configuration.
    return []


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


def get_files_from_paths(paths: List[str]) -> List[str]:
    """
    Gets all files from given paths (handles both files and directories).
    Returns a list of file paths relative to the repository root.
    """
    repo_root = assert_git_repo()
    all_files = []
    
    for path in paths:
        # Normalize path
        normalized_path = os.path.normpath(path)
        full_path = os.path.join(repo_root, normalized_path) if not os.path.isabs(path) else path
        
        if not os.path.exists(full_path):
            raise KnownError(f"Path does not exist: {path}")
        
        if os.path.isfile(full_path):
            # It's a file, get relative path
            rel_path = os.path.relpath(full_path, repo_root)
            all_files.append(rel_path)
        elif os.path.isdir(full_path):
            # It's a directory, get all files in it
            try:
                result = subprocess.run(
                    ['git', 'ls-files', '--', normalized_path],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=repo_root
                )
                files_in_dir = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
                all_files.extend(files_in_dir)
            except subprocess.CalledProcessError:
                # If git ls-files fails, try to find files manually
                for root, dirs, files in os.walk(full_path):
                    # Skip .git directories
                    if '.git' in dirs:
                        dirs.remove('.git')
                    for file in files:
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, repo_root)
                        all_files.append(rel_path)
    
    # Remove duplicates and return
    return list(set(all_files))


def stage_files(files: List[str]) -> None:
    """
    Stages specific files.
    """
    if not files:
        return
    
    try:
        subprocess.run(
            ['git', 'add', '--'] + files,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    except subprocess.CalledProcessError as e:
        raise KnownError(f"Failed to stage files: {e.stderr}")


def get_current_branch() -> str:
    """
    Gets the current git branch name.
    """
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        raise KnownError("Failed to get current branch name")


def has_commits_to_push(branch: Optional[str] = None, remote: str = "origin") -> bool:
    """
    Checks if there are commits ahead of the remote that need to be pushed.
    Returns True if there are commits to push, False otherwise.
    """
    if branch is None:
        branch = get_current_branch()
    
    try:
        # Check if remote tracking branch exists
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', f'{branch}@{{upstream}}'],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        upstream = result.stdout.strip()
    except subprocess.CalledProcessError:
        # No upstream branch, assume we need to push
        return True
    
    try:
        # Check if local branch is ahead of remote
        result = subprocess.run(
            ['git', 'rev-list', '--count', f'{upstream}..{branch}'],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        ahead_count = int(result.stdout.strip())
        return ahead_count > 0
    except (subprocess.CalledProcessError, ValueError):
        # If we can't determine, assume we need to push
        return True


def push_to_remote(branch: Optional[str] = None, remote: str = "origin") -> None:
    """
    Pushes the current branch to the remote repository.
    """
    if branch is None:
        branch = get_current_branch()
    
    try:
        # Check if remote exists
        result = subprocess.run(
            ['git', 'remote', 'get-url', remote],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    except subprocess.CalledProcessError:
        raise KnownError(f"Remote '{remote}' does not exist. Please add a remote first.")
    
    # Check if there are commits to push
    if not has_commits_to_push(branch, remote):
        return  # Nothing to push
    
    try:
        # Don't capture stdout/stderr to allow interactive prompts (e.g., for authentication)
        # This allows the user to see what's happening and enter credentials if needed
        subprocess.run(
            ['git', 'push', remote, branch],
            check=True
        )
    except subprocess.CalledProcessError as e:
        raise KnownError(f"Failed to push to remote. Please check your authentication and try again.")
