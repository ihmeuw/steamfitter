from steamfitter.app import commands
from steamfitter.app.utilities import get_configuration
from steamfitter.app.directory_structure import ProjectDirectory
from steamfitter.lib.testing import invoke_cli


def test_remove_project_no_config():
    project_name = "test-project"
    result = invoke_cli(commands.remove_project, [project_name], exit_zero=False)
    assert "Configuration file does not exist." in result.output


def test_remove_project_no_project(projects_root):
    project_name = "test-project"
    invoke_cli(commands.create_config, [str(projects_root)])

    result = invoke_cli(commands.remove_project, [project_name], exit_zero=False)
    assert f"Project {project_name} does not exist in the configuration." in result.output


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
