"""
Test the happy paths of the CLI commands.

Steamfitter commands generally require some combination of configuration,
projects, and sources to be present in order to work. This module tests the
happy paths for those commands sequentially so that testing error messages are informative
in the presence of fixtures that use these commands to set up the environment.

"""
import pytest

from steamfitter.app import commands
from steamfitter.app.configuration import Configuration
from steamfitter.app.directory_structure import ProjectDirectory
from steamfitter.app.utilities import get_configuration
from steamfitter.lib.filesystem import ARCHIVE_POLICIES, SteamfitterDirectoryError
from steamfitter.app.testing import invoke_cli


@pytest.fixture()
def projects_root(tmp_path):
    return tmp_path / "projects"


@pytest.fixture()
def new_root(tmp_path):
    return tmp_path / "projects2"


@pytest.fixture()
def config_path(tmp_path):
    return tmp_path / "config.yaml"


@pytest.fixture(scope="session")
def project_name():
    return "test-project"





@pytest.fixture(autouse=True)
def configuration_with_patched_path(config_path):
    Configuration._path = config_path


def test_config_create(config_path, projects_root):
    assert not config_path.exists()
    assert not projects_root.exists()

    result = invoke_cli(commands.create_config, [str(projects_root)])

    assert config_path.exists()
    assert projects_root.exists()

    config = Configuration()
    assert config.projects_root == projects_root
    assert config.projects == []
    assert config.default_project == ""

    assert f"Projects root {str(projects_root)} does not exist" in result.output
    assert f"Configuration file written to {str(config_path)}" in result.output


def test_config_create_with_existing_projects_root(config_path, projects_root):
    projects_root.mkdir(parents=True)
    assert projects_root.exists()

    result = invoke_cli(commands.create_config, [str(projects_root)])
    assert f"Configuration file written to {str(config_path)}" in result.output
    assert f"Projects root {str(projects_root)} already exists. Using it." in result.output

    config = Configuration()
    assert config.projects_root == projects_root
    assert config.projects == []
    assert config.default_project == ""


def test_config_create_with_existing_projects(config_path, projects_root, project_name):
    invoke_cli(commands.create_config, [str(projects_root)])
    invoke_cli(commands.add_project, [project_name, "-m", "test"])

    # Now delete the config so this is like a new user running the command against
    # an existing projects root
    config_path.unlink()

    result = invoke_cli(commands.create_config, [str(projects_root)])
    assert f"Configuration file written to {str(config_path)}" in result.output
    assert f"Projects root {str(projects_root)} already exists. Using it." in result.output
    assert f"Found project {project_name} in {projects_root}. Adding it." in result.output

    config = Configuration()
    assert config.projects_root == projects_root
    assert config.projects == [project_name]
    assert config.default_project == ""


def test_config_list(config_path, projects_root):
    invoke_cli(commands.create_config, [str(projects_root)])

    result = invoke_cli(commands.list_config)
    assert f"Projects root: {str(projects_root)}" in result.output
    assert "Default project: \n" in result.output
    assert "Projects: \n" in result.output

    config = Configuration()
    assert config.projects_root == projects_root
    assert config.projects == []
    assert config.default_project == ""


def test_config_list_with_projects(config_path, projects_root):
    project_name = "test-project"

    invoke_cli(commands.create_config, [str(projects_root)])
    invoke_cli(commands.add_project, [project_name, "-m", "test"])

    result = invoke_cli(commands.list_config)
    assert f"Projects root: {str(projects_root)}" in result.output
    assert "Default project: \n" in result.output
    assert "Projects: test-project\n" in result.output

    config = Configuration()
    assert config.projects_root == projects_root
    assert config.projects == [project_name]
    assert config.default_project == ""


def test_config_list_with_default_project(config_path, projects_root):
    project_name = "test-project"

    invoke_cli(commands.create_config, [str(projects_root)])
    invoke_cli(commands.add_project, [project_name, "-m", "test", "-d"])

    result = invoke_cli(commands.list_config)
    assert f"Projects root: {str(projects_root)}" in result.output
    assert f"Default project: {project_name}\n" in result.output
    assert "Projects: test-project\n" in result.output

    config = Configuration()
    assert config.projects_root == projects_root
    assert config.projects == [project_name]
    assert config.default_project == project_name


def test_config_list_with_multiple_projects(config_path, projects_root):
    project_names = ["test-project", "test-project-2", "test-project-3"]

    invoke_cli(commands.create_config, [str(projects_root)])
    for project_name in project_names[:-1]:
        invoke_cli(commands.add_project, [project_name, "-m", "test"])
    invoke_cli(commands.add_project, [project_names[-1], "-m", "test", "-d"])

    result = invoke_cli(commands.list_config)
    assert f"Projects root: {str(projects_root)}" in result.output
    assert f"Default project: {project_names[-1]}\n" in result.output
    assert "Projects: test-project, test-project-2, test-project-3\n" in result.output

    config = Configuration()
    assert config.projects_root == projects_root
    assert config.projects == project_names
    assert config.default_project == project_names[-1]


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


def assert_project_metadata_complete(project_dir_path, description):
    project_dir = ProjectDirectory(project_dir_path)
    assert project_dir["archive_policy"] == ARCHIVE_POLICIES.invalid
    assert project_dir["name"] == project_dir_path.name
    assert project_dir["description"] == description
    assert (
        project_dir["directory_class"]
        == f"{ProjectDirectory.__module__}.{ProjectDirectory.__name__}"
    )
    assert project_dir["directory_type"] == "project"
    assert project_dir["root"] == str(project_dir_path)


def test_add_project(projects_root):
    project_name = "test-project"
    project_description = "test message"

    invoke_cli(commands.create_config, [str(projects_root)])

    with pytest.raises(SteamfitterDirectoryError):
        ProjectDirectory(projects_root / "test-project")

    result = invoke_cli(commands.add_project, [project_name, "-m", project_description])
    assert f"Project {project_name} added to the configuration." in result.output

    assert_project_metadata_complete(projects_root / project_name, project_description)


def test_add_project_default(projects_root):
    project_name = "test-project"
    project_description = "test message"

    invoke_cli(commands.create_config, [str(projects_root)])

    with pytest.raises(SteamfitterDirectoryError):
        ProjectDirectory(projects_root / "test-project")

    result = invoke_cli(commands.add_project, [project_name, "-m", project_description, "-d"])
    assert f"Project {project_name} added to the configuration." in result.output
    assert f"Project {project_name} set as the default project." in result.output

    assert_project_metadata_complete(projects_root / project_name, project_description)

    config = Configuration()
    assert config.default_project == project_name


def test_list_projects(projects_root):
    invoke_cli(commands.create_config, [str(projects_root)])
    invoke_cli(commands.add_project, ["test-project-1", "-m", "test message"])
    invoke_cli(commands.add_project, ["test-project-2", "-m", "test message"])

    result = invoke_cli(commands.list_project)
    expected = "Projects\n========\n1       : test-project-1\n2       : test-project-2\n"
    assert expected == result.output


def test_remove_project(projects_root):
    project_name = "test-project"
    project_description = "test message"

    invoke_cli(commands.create_config, [str(projects_root)])
    invoke_cli(commands.add_project, [project_name, "-m", project_description])

    project_path = projects_root / project_name
    assert project_path.exists()
    ProjectDirectory.is_directory_type(project_path)

    result = invoke_cli(commands.remove_project, [project_name])
    assert f"Project {project_name} removed from the configuration." in result.output
    assert not project_path.exists()
    assert not ProjectDirectory.is_directory_type(project_path)


def test_remove_project_default(projects_root):
    project_name = "test-project"
    project_description = "test message"

    invoke_cli(commands.create_config, [str(projects_root)])
    config = get_configuration()

    invoke_cli(commands.add_project, [project_name, "-m", project_description, "-d"])

    project_path = projects_root / project_name
    assert project_path.exists()
    ProjectDirectory.is_directory_type(project_path)
    assert config.default_project == project_name

    result = invoke_cli(commands.remove_project, [project_name])
    assert f"Project {project_name} removed from the configuration." in result.output
    assert not project_path.exists()
    assert not ProjectDirectory.is_directory_type(project_path)
    assert config.default_project == ""


def test_add_source_no_project_name_with_default_project(projects_root):
    source_name = "test-source"
    project_name = "test-project"
    invoke_cli(commands.create_config, [str(projects_root)])
    invoke_cli(commands.add_project, [project_name, "-m", "test", "-d"])

    result = invoke_cli(commands.add_source, [source_name, "-m", "test"])
    assert f"Source {source_name} added to project {project_name}" in result.output


def test_add_source_with_project_name_no_default(projects_root):
    source_name = "test-source"
    project_name = "test-project"
    invoke_cli(commands.create_config, [str(projects_root)])
    invoke_cli(commands.add_project, [project_name, "-m", "test"])

    result = invoke_cli(commands.add_source, [source_name, "-P", project_name, "-m", "test"])
    assert f"Source {source_name} added to project {project_name}" in result.output


def test_self_destruct_no_config():
    result = invoke_cli(commands.self_destruct, exit_zero=False)
    assert "Configuration file does not exist." in result.output


def test_self_destruct(config_path, projects_root):
    invoke_cli(commands.create_config, [str(projects_root)])
    assert config_path.exists()

    result = invoke_cli(commands.self_destruct, input_="y")
    assert "Removing configuration file." in result.output
    assert "All projects and configuration removed." in result.output
    assert not config_path.exists()


def test_self_destruct_with_projects(config_path, projects_root):
    project_name = "test-project"
    invoke_cli(commands.create_config, [str(projects_root)])
    assert config_path.exists()

    invoke_cli(commands.add_project, [project_name, "-m", "test message"])
    project_path = projects_root / project_name
    assert project_path.exists()
    ProjectDirectory.is_directory_type(project_path)

    result = invoke_cli(commands.self_destruct, input_="y")
    assert f"Removing project: {project_name}" in result.output
    assert "Removing configuration file." in result.output
    assert "All projects and configuration removed." in result.output
    assert not config_path.exists()
    assert not project_path.exists()
    assert not ProjectDirectory.is_directory_type(project_path)
