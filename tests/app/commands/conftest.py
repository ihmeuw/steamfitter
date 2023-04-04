import pytest

from steamfitter.app import git


@pytest.fixture(scope="session", autouse=True)
def disable_git():
    git.GIT_ENABLED = False