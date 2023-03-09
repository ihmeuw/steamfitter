from pathlib import Path

import pytest


@pytest.fixture()
def config_path(tmpdir):
    return Path(tmpdir) / "config.yaml"


@pytest.fixture
def projects_root(tmpdir):
    return Path(tmpdir) / "sf_projects"


@pytest.fixture(autouse=True)
def configuration_with_patched_path(monkeypatch, config_path):
    monkeypatch.setattr(
        "steamfitter.app.configuration.Configuration._path",
        config_path,
    )




