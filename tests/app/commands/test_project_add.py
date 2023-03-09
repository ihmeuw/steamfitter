import pytest

from steamfitter.app import commands
from steamfitter.app.directory_structure import ProjectDirectory
from steamfitter.app.configuration import Configuration
from steamfitter.lib.testing import invoke_cli
from steamfitter.lib.filesystem import SteamfitterDirectoryError, ARCHIVE_POLICIES


def assert_project_metadata_complete(project_dir_path, description):
    project_dir = ProjectDirectory(project_dir_path)
    assert project_dir["archive_policy"] == ARCHIVE_POLICIES.invalid
    assert project_dir["name"] == project_dir_path.name
    assert project_dir["description"] == description
    assert project_dir["directory_class"] == f"{ProjectDirectory.__module__}.{ProjectDirectory.__name__}"
    assert project_dir["directory_type"] == "project"
    assert project_dir["root"] == str(project_dir_path)


def test_add_project_no_config():
    result = invoke_cli(
        commands.add_project,
        ["test-project", '-m', 'test message'],
        exit_zero=False,
    )
    assert "Configuration file does not exist" in result.output


def test_add_project(projects_root):
    project_name = "test-project"
    project_description = "test message"

    invoke_cli(commands.create_config, [str(projects_root)])

    with pytest.raises(SteamfitterDirectoryError):
        ProjectDirectory(projects_root / "test-project")

    result = invoke_cli(commands.add_project, [project_name, '-m', project_description])
    assert f"Project {project_name} added to the configuration." in result.output

    assert_project_metadata_complete(projects_root / project_name, project_description)


def test_add_project_default(projects_root):
    project_name = "test-project"
    project_description = "test message"

    invoke_cli(commands.create_config, [str(projects_root)])

    with pytest.raises(SteamfitterDirectoryError):
        ProjectDirectory(projects_root / "test-project")

    result = invoke_cli(commands.add_project, [project_name, '-m', project_description, '-d'])
    assert f"Project {project_name} added to the configuration." in result.output
    assert f"Project {project_name} set as the default project." in result.output

    assert_project_metadata_complete(projects_root / project_name, project_description)

    config = Configuration()
    assert config.default_project == project_name


def test_add_project_already_exists(projects_root):
    project_name = "test-project"
    project_description = "test message"

    invoke_cli(commands.create_config, [str(projects_root)])
    invoke_cli(commands.add_project, [project_name, '-m', project_description])

    result = invoke_cli(commands.add_project, [project_name, '-m', project_description], exit_zero=False)
    assert "Project test-project already exists." in result.output
