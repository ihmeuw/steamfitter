"""
Test the happy paths of the CLI commands.

Steamfitter commands generally require some combination of configuration,
projects, and sources to be present in order to work. This module tests the
happy paths for those commands sequentially so that testing error messages are informative
in the presence of fixtures that use these commands to set up the environment.

"""
from steamfitter.app import commands
from steamfitter.app.configuration import Configuration
from steamfitter.lib.testing import invoke_cli


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
