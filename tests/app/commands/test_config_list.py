from steamfitter.app import commands
from steamfitter.app.configuration import Configuration
from steamfitter.lib.testing import invoke_cli


def test_config_list_no_config():
    result = invoke_cli(commands.list_config, exit_zero=False)
    assert "Configuration file does not exist" in result.output


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
