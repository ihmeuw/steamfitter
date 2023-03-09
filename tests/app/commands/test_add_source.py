from steamfitter.app import commands
from steamfitter.lib.testing import invoke_cli


def test_add_source_no_config():
    source_name = "test-source"
    result = invoke_cli(commands.add_source, [source_name], exit_zero=False)
    assert "Configuration file does not exists" in result.output


def test_add_source_no_projects(projects_root):
    source_name = "test-source"
    invoke_cli(commands.create_config, [str(projects_root)])

    result = invoke_cli(commands.add_source, [source_name], exit_zero=False)
    assert "No projects found" in result.output


def test_add_source_no_project_name_no_default_project(projects_root):
    source_name = "test-source"
    project_name = "test-project"
    invoke_cli(commands.create_config, [str(projects_root)])
    invoke_cli(commands.add_project, [project_name, "-m", "test"])

    result = invoke_cli(commands.add_source, [source_name], exit_zero=False)
    assert "No project provided and no default project set" in result.output


def test_add_source_no_project_name_with_default_project(projects_root):
    source_name = "test-source"
    project_name = "test-project"
    invoke_cli(commands.create_config, [str(projects_root)])
    invoke_cli(commands.add_project, [project_name, "-m", "test", "-d"])

    result = invoke_cli(commands.add_source, [source_name])
    assert f"Source {source_name} added to project {project_name}" in result.output


def test_add_source_with_project_name_no_default(projects_root):
    source_name = "test-source"
    project_name = "test-project"
    invoke_cli(commands.create_config, [str(projects_root)])
    invoke_cli(commands.add_project, [project_name, "-m", "test"])

    result = invoke_cli(commands.add_source, [source_name, "-p", project_name])
    assert f"Source {source_name} added to project {project_name}" in result.output
