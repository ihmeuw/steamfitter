import textwrap

from steamfitter.app import commands
from steamfitter.lib.testing import invoke_cli


def test_list_projects_no_config():
    result = invoke_cli(commands.list_projects, exit_zero=False)
    assert "Configuration file does not exist." in result.output


def test_list_projects_no_projects(projects_root):
    invoke_cli(commands.create_config, [str(projects_root)])

    result = invoke_cli(commands.list_projects)
    assert "No projects found." in result.output


def test_list_projects(projects_root):
    invoke_cli(commands.create_config, [str(projects_root)])
    invoke_cli(commands.add_project, ["test-project-1", "-m", "test message"])
    invoke_cli(commands.add_project, ["test-project-2", "-m", "test message"])

    result = invoke_cli(commands.list_projects)
    expected = 'Projects\n========\n1       : test-project-1\n2       : test-project-2\n'
    assert expected == result.output
