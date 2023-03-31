from pathlib import Path
from git import Repo

from steamfitter.lib.filesystem import templates


GIT_ENABLED = True


def init(path: Path) -> None:
    """Initialize the git repository."""
    if GIT_ENABLED:
        repo = Repo.init(path)
        gitignore_path = path / ".gitignore"
        gitignore_path.touch(mode=0o664)
        with open(gitignore_path, "w") as f:
            f.write(templates.GITIGNORE)
        repo.git.add(A=True)
        repo.index.commit("Initial commit.")
        # repo.git.push()


def add_and_commit(path: Path, message: str) -> None:
    """Add and commit changes to the git repository."""
    if GIT_ENABLED:
        repo = Repo(path)
        repo.git.add(A=True)
        repo.index.commit(message)
        # repo.git.push()
