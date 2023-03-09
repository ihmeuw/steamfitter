from pathlib import Path

import pytest

from steamfitter.app import commands
from steamfitter.app.configuration import Configuration
from steamfitter.lib.testing import invoke_cli


@pytest.fixture
def new_root(tmpdir):
    return Path(tmpdir) / "new-root"


def test_config_update_no_args(config_path, projects_root):
    result = invoke_cli(commands.update_config, [], exit_zero=False)
    assert (
        "Must provide at least one of --projects-root or --default-project-name"
        in result.output
    )


def test_config_update_no_existing_config(new_root):
    result = invoke_cli(
        commands.update_config,
        ["--projects-root", str(new_root)],
        exit_zero=False,
    )
    assert "Configuration file does not exist" in result.output


def test_config_update_projects_root_empty(config_path, projects_root, new_root):
    invoke_cli(commands.create_config, [str(projects_root)])
    result = invoke_cli(commands.update_config, ["--projects-root", str(new_root)])
    assert f"Projects root updated to {str(new_root)}" in result.output

    config = Configuration()
    assert config.projects_root == new_root
    assert config.projects == []
    assert config.default_project == ""


def test_config_update_projects_root_non_empty_old(config_path, projects_root, new_root):
    invoke_cli(commands.create_config, [str(projects_root)])
    invoke_cli(commands.add_project, ["test-project", "-m", "test", "-d"])

    result = invoke_cli(commands.update_config, ["--projects-root", str(new_root)])
    assert f"Projects root updated to {str(new_root)}" in result.output

    config = Configuration()
    assert config.projects_root == new_root
    assert config.projects == []
    assert config.default_project == ""


def test_config_update_projects_root_non_empty_new(config_path, projects_root, new_root):
    invoke_cli(commands.create_config, [str(projects_root)])
    invoke_cli(commands.add_project, ["test-project", "-m", "test", "-d"])

    invoke_cli(commands.update_config, ["--projects-root", str(new_root)])
    # Now update back to the original root
    result = invoke_cli(commands.update_config, ["--projects-root", str(projects_root)])
    assert f"Projects root updated to {str(projects_root)}" in result.output

    config = Configuration()
    assert config.projects_root == projects_root
    assert config.projects == ["test-project"]
    assert config.default_project == ""


def test_config_update_default_project_name_empty(config_path, projects_root):
    invoke_cli(commands.create_config, [str(projects_root)])
    result = invoke_cli(
        commands.update_config,
        ["--default-project-name", "test-project"],
        exit_zero=False,
    )
    assert "Project test-project does not exist" in result.output


def test_config_update_default_project_name_non_empty(config_path, projects_root):
    invoke_cli(commands.create_config, [str(projects_root)])
    invoke_cli(commands.add_project, ["test-project", "-m", "test"])

    result = invoke_cli(
        commands.update_config,
        ["--default-project-name", "test-project"],
    )
    assert "Default project updated to test-project" in result.output

    config = Configuration()
    assert config.projects_root == projects_root
    assert config.projects == ["test-project"]
    assert config.default_project == "test-project"


def test_config_update_default_project_name_non_empty_no_change(config_path, projects_root):
    invoke_cli(commands.create_config, [str(projects_root)])
    invoke_cli(commands.add_project, ["test-project", "-m", "test"])

    invoke_cli(
        commands.update_config,
        ["--default-project-name", "test-project"],
    )
    result = invoke_cli(
        commands.update_config,
        ["--default-project-name", "test-project"],
    )
    assert "Default project updated to test-project" in result.output

    config = Configuration()
    assert config.projects_root == projects_root
    assert config.projects == ["test-project"]
    assert config.default_project == "test-project"
