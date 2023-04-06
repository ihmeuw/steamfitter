from pathlib import Path
from typing import Union

from git import Repo, InvalidGitRepositoryError

from steamfitter.lib.filesystem import templates

GIT_ENABLED = True

##################
# Public methods #
##################


def init(path: Path, git_remote: Union[str, None]) -> None:
    """Initialize the git repository."""
    if GIT_ENABLED:
        repo = Repo.init(path, shared='group')

        gitignore_path = path / ".gitignore"
        gitignore_path.touch(mode=0o664)

        with open(gitignore_path, "w") as f:
            f.write(templates.GITIGNORE)
        repo.git.add(A=True)
        repo.index.commit("Initial commit.")
        _create_remote(path, git_remote)


def commit_and_push(path: Path, message: str) -> None:
    """Add and commit changes to the git repository."""
    if GIT_ENABLED:
        repo = _find_repo(path)
        repo.git.add(A=True)
        repo.index.commit(message)
        _push(path)


###########
# Helpers #
###########

def _find_repo(path: Path) -> Repo:
    """Find the git repository."""
    try:
        return Repo(path)
    except InvalidGitRepositoryError:
        return _find_repo(path.parent)


def _create_remote(path: Path, git_remote: str) -> None:
    """Create the git remote."""
    if GIT_ENABLED:
        repo = _find_repo(path)
        repo.git.remote('add', 'origin', git_remote)
        repo.git.push('-u', 'origin', 'HEAD:main')


def _push(path: Path) -> None:
    """Push changes to the git repository."""
    if GIT_ENABLED:
        repo = _find_repo(path)
        if 'origin' in repo.remotes:
            repo.git.push()
