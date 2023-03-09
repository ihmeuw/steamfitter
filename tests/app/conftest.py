import itertools
from pathlib import Path
from typing import NamedTuple

import pytest

from steamfitter.app import commands
from steamfitter.lib.testing import invoke_cli


class __EnvironmentConfigurations(NamedTuple):
    """Enumeration of possible environment configurations."""
    bare: str
    config_exists: str

    single_project: str
    single_project_with_default: str

    single_project_single_source: str
    single_project_single_source_with_default: str
    single_project_multi_source: str
    single_project_multi_source_with_default: str

    single_project_single_column: str
    single_project_single_column_with_default: str
    single_project_multi_column: str
    single_project_multi_column_with_default: str

    single_project_single_source_single_column: str
    single_project_single_source_single_column_with_default: str
    single_project_single_source_multi_column: str
    single_project_single_source_multi_column_with_default: str

    single_project_multi_source_single_column: str
    single_project_multi_source_single_column_with_default: str
    single_project_multi_source_multi_column: str
    single_project_multi_source_multi_column_with_default: str

    multi_project: str
    multi_project_with_default: str

    multi_project_single_source: str
    multi_project_single_source_with_default: str
    multi_project_multi_source: str
    multi_project_multi_source_with_default: str

    multi_project_single_column: str
    multi_project_single_column_with_default: str
    multi_project_multi_column: str
    multi_project_multi_column_with_default: str

    multi_project_single_source_single_column: str
    multi_project_single_source_single_column_with_default: str
    multi_project_single_source_multi_column: str
    multi_project_single_source_multi_column_with_default: str

    multi_project_multi_source_single_column: str
    multi_project_multi_source_single_column_with_default: str
    multi_project_multi_source_multi_column: str
    multi_project_multi_source_multi_column_with_default: str


ENVIRONMENT_CONFIGURATIONS = __EnvironmentConfigurations(
    *__EnvironmentConfigurations._fields
)


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


@pytest.fixture(autouse=True)
def configuration_with_patched_path(monkeypatch, config_path):
    monkeypatch.setattr(
        "steamfitter.app.configuration.Configuration._path",
        config_path,
    )


@pytest.fixture(params=ENVIRONMENT_CONFIGURATIONS)
def config_exists(request, projects_root):
    if request.param != ENVIRONMENT_CONFIGURATIONS.bare:
        invoke_cli(commands.create_config, [str(projects_root)])
        return True
    return False


@pytest.fixture(params=ENVIRONMENT_CONFIGURATIONS)
def has_default_project(request):
    return 'default' in request.param


@pytest.fixture(params=ENVIRONMENT_CONFIGURATIONS)
def projects(request, project_name, projects_root):
    if 'project' not in request.param:
        return []

    default = ['-d'] if 'with_default' in request.param else []
    project_count = 1 if 'single_project' in request.param else 3
    args = [[f"{project_name}{i+1}", "-m", "test"] for i in range(project_count)]
    args[0] += default

    projects = []
    for add_project_args in args:
        projects.append(add_project_args[0])
        invoke_cli(commands.add_project, add_project_args)

    return projects


@pytest.fixture
def project_exists(projects):
    return bool(projects)


@pytest.fixture(params=ENVIRONMENT_CONFIGURATIONS)
def sources(request, source_name, projects):
    if 'source' not in request.param:
        return []

    source_count = 1 if 'single_source' in request.param else 3
    args = [[f"{project}-{source_name}{i+1}", "-m", "test", '-P', project]
            for i, project
            in itertools.product(range(source_count), projects)]

    sources = []
    for add_source_args in args:
        sources.append(add_source_args[0])
        invoke_cli(commands.add_source, add_source_args)

    return sources


@pytest.fixture()
def source_exists(sources):
    return bool(sources)


@pytest.fixture(params=ENVIRONMENT_CONFIGURATIONS)
def columns(request, projects):
    if 'column' not in request.param:
        return []

    column_types = ['int'] if 'single_column' in request.param else ['int', 'float', 'str']
    is_nullable = ['', '-n', '-n']
    args = [[f"{project}-column{i+1}", column_types[i], is_nullable[i], '-P', project]
            for i, project
            in itertools.product(range(len(column_types)), projects)]

    columns = []
    for add_column_args in args:
        columns.append(add_column_args[0])
        invoke_cli(commands.add_source_column, add_column_args)

    return columns


@pytest.fixture()
def column_exists(columns):
    return bool(columns)



@pytest.fixture(params=[
    (commands.create_config, ["{projects_root}"]),
    (commands.list_config, []),
    (commands.update_config, ['--projects-root', '{projects_root}']),
    (commands.update_config, ['--default-project', '{project_name}']),
    (commands.update_config, ['--projects-root', '{projects_root}',
                              '--default-project', '{project_name}' ]),
    (commands.add_project, ['{project_name}', '-m', 'test']),
    (commands.add_project, ['{project_name}', '-m', 'test', '-d']),
    (commands.list_projects, []),
    (commands.remove_project, ['{project_name}']),
    (commands.add_source, ['{source_name}', '-m', 'test']),
    (commands.add_source, ['{source_name}', '-m', 'test',
                           '--project-name', '{project_name}']),
    (commands.list_sources, []),
    (commands.list_sources, ['--project-name', '{project_name}']),
    (commands.remove_source, ['{source_name}']),
    (commands.remove_source, ['{source_name}', '--project-name', '{project_name}']),
    (commands.add_source_column, ['{source_column_name}', '{source_column_type}',
                                  '-m', 'test']),
    (commands.add_source_column, ['{source_column_name}', '{source_column_type}',
                                    '-m', 'test', '-n']),
    (commands.add_source_column, ['{source_column_name}', '{source_column_type}',
                                      '-m', 'test', '--project-name', '{project_name}']),
    (commands.add_source_column, ['{source_column_name}', '{source_column_type}',
                                    '-m', 'test', '-n', '--project-name', '{project_name}']),
    (commands.list_source_columns, []),
    (commands.list_source_columns, ['--project-name', '{project_name}']),
    (commands.remove_source_column, ['{source_column_name}']),
    (commands.remove_source_column, ['{source_column_name}', '--project-name', '{project_name}']),
])
def good_commands(request, projects_root, project_name, source_name):
    command, args = request.param
    format_args = {
        'projects_root': str(projects_root),
        'project_name': project_name,
        'source_name': source_name,
    }
    args = [args.format(**format_args) for args in args]
    return command, args





@pytest.fixture(params=[



@pytest.fixture(