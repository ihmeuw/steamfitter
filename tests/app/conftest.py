from pathlib import Path

import pytest


#############################
# Concrete resource objects #
#############################

@pytest.fixture()
def config_path(tmpdir):
    return Path(tmpdir) / "config.yaml"


@pytest.fixture
def projects_root(tmpdir):
    return Path(tmpdir) / "sf-projects"


@pytest.fixture
def project_name(projects_root):
    return "test-project"


@pytest.fixture
def project_path(project_name, projects_root):
    return projects_root / project_name


@pytest.fixture
def source_name():
    return "test-source"


@pytest.fixture
def source_column_name():
    return "test_source_column"


@pytest.fixture(autouse=True)
def configuration_with_patched_path(monkeypatch, config_path):
    monkeypatch.setattr(
        "steamfitter.app.configuration.Configuration._path",
        config_path,
    )

