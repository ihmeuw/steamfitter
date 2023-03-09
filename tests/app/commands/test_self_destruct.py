from steamfitter.app import commands
from steamfitter.app.directory_structure import ProjectDirectory
from steamfitter.lib.testing import invoke_cli


def test_self_destruct_no_config():
    result = invoke_cli(commands.self_destruct, exit_zero=False)
    assert "Configuration file does not exist." in result.output


def test_self_destruct(config_path, projects_root):
    invoke_cli(commands.create_config, [str(projects_root)])
    assert config_path.exists()

    result = invoke_cli(commands.self_destruct, input="y")
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

    result = invoke_cli(commands.self_destruct, input="y")
    assert f"Removing project: {project_name}" in result.output
    assert "Removing configuration file." in result.output
    assert "All projects and configuration removed." in result.output
    assert not config_path.exists()
    assert not project_path.exists()
    assert not ProjectDirectory.is_directory_type(project_path)



