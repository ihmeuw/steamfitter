import itertools
from typing import NamedTuple

import pytest

from steamfitter.app import commands
from steamfitter.lib.testing import invoke_cli


class __Resource(NamedTuple):
    """Enumeration of possible steamfitter environment resources."""
    config: str
    project: str
    default_project: str
    source: str
    source_column: str


RESOURCE = __Resource(*__Resource._fields)


class EnvironmentConfiguration:
    """Enumeration of possible steamfitter environment resources."""

    def __init__(
        self,
        config: bool = False,
        project: bool = False,
        multi_project: bool = False,
        default_project: bool = False,
        source: bool = False,
        multi_source: bool = False,
        source_column: bool = False,
        multi_source_column: bool = False,
    ):
        project = max(project, multi_project)
        source = max(source, multi_source)
        source_column = max(source_column, multi_source_column)

        assert config >= project, "Config must exist if project exists."
        assert project >= multi_project, "Project must exist if multi-project exists."
        assert project >= default_project, "Project must exist if default project exists."
        assert project >= source, "Project must exist if source exists."
        assert source >= multi_source, "Source must exist if multi-source exists."
        assert project >= source_column, "Project must exist if source column exists."
        assert source_column >= multi_source_column, "Source column must exist if multi-source column exists."

        self.config = config
        self.project = project
        self.multi_project = multi_project
        self.default_project = default_project
        self.source = source
        self.multi_source = multi_source
        self.source_column = source_column
        self.multi_source_column = multi_source_column

    def resource_exists(self, resource: str) -> bool:
        """Validate that the resource exists in the environment configuration."""
        if resource == RESOURCE.config:
            return self.config
        elif resource == RESOURCE.project:
            return self.project
        elif resource == RESOURCE.default_project:
            return self.default_project
        elif resource == RESOURCE.source:
            return self.source
        elif resource == RESOURCE.source_column:
            return self.source_column
        else:
            raise ValueError(f"Unknown resource: {resource}")

    def __repr__(self):
        keys = [k for k, v in self.__dict__.items() if v]
        for k in keys:
            if k.startswith("multi_"):
                keys.remove(k.replace("multi_", ""))
        if keys:
            return "_".join(keys)
        else:
            return "bare"


VALID_ENVIRONMENT_CONFIGURATIONS = [
    EnvironmentConfiguration(),
    EnvironmentConfiguration(config=True),

    EnvironmentConfiguration(config=True, project=True),
    EnvironmentConfiguration(config=True, project=True, default_project=True),

    EnvironmentConfiguration(config=True, project=True, source=True),
    EnvironmentConfiguration(config=True, project=True, source=True, default_project=True),
    EnvironmentConfiguration(config=True, project=True, multi_source=True),
    EnvironmentConfiguration(config=True, project=True, multi_source=True, default_project=True),

    EnvironmentConfiguration(config=True, project=True, source_column=True),
    EnvironmentConfiguration(config=True, project=True, source_column=True, default_project=True),
    EnvironmentConfiguration(config=True, project=True, multi_source_column=True),
    EnvironmentConfiguration(config=True, project=True, multi_source_column=True, default_project=True),

    EnvironmentConfiguration(config=True, project=True, source=True, source_column=True),
    EnvironmentConfiguration(config=True, project=True, source=True, source_column=True, default_project=True),
    EnvironmentConfiguration(config=True, project=True, source=True, multi_source_column=True),
    EnvironmentConfiguration(config=True, project=True, source=True, multi_source_column=True, default_project=True),

    EnvironmentConfiguration(config=True, project=True, multi_source=True, source_column=True),
    EnvironmentConfiguration(config=True, project=True, multi_source=True, source_column=True, default_project=True),
    EnvironmentConfiguration(config=True, project=True, multi_source=True, multi_source_column=True),
    EnvironmentConfiguration(config=True, project=True, multi_source=True, multi_source_column=True, default_project=True),

    EnvironmentConfiguration(config=True, multi_project=True),
    EnvironmentConfiguration(config=True, multi_project=True, default_project=True),

    EnvironmentConfiguration(config=True, multi_project=True, source=True),
    EnvironmentConfiguration(config=True, multi_project=True, source=True, default_project=True),
    EnvironmentConfiguration(config=True, multi_project=True, multi_source=True),
    EnvironmentConfiguration(config=True, multi_project=True, multi_source=True, default_project=True),

    EnvironmentConfiguration(config=True, multi_project=True, source_column=True),
    EnvironmentConfiguration(config=True, multi_project=True, source_column=True, default_project=True),
    EnvironmentConfiguration(config=True, multi_project=True, multi_source_column=True),
    EnvironmentConfiguration(config=True, multi_project=True, multi_source_column=True, default_project=True),

    EnvironmentConfiguration(config=True, multi_project=True, source=True, source_column=True),
    EnvironmentConfiguration(config=True, multi_project=True, source=True, source_column=True, default_project=True),
    EnvironmentConfiguration(config=True, multi_project=True, source=True, multi_source_column=True),
    EnvironmentConfiguration(config=True, multi_project=True, source=True, multi_source_column=True, default_project=True),

    EnvironmentConfiguration(config=True, multi_project=True, multi_source=True, source_column=True),
    EnvironmentConfiguration(config=True, multi_project=True, multi_source=True, source_column=True, default_project=True),
    EnvironmentConfiguration(config=True, multi_project=True, multi_source=True, multi_source_column=True),
    EnvironmentConfiguration(config=True, multi_project=True, multi_source=True, multi_source_column=True, default_project=True),
]


@pytest.fixture(params=VALID_ENVIRONMENT_CONFIGURATIONS, ids=map(str, VALID_ENVIRONMENT_CONFIGURATIONS))
def environment_configuration(request):
    return request.param


@pytest.fixture(autouse=True)
def config_exists(environment_configuration, projects_root):
    if environment_configuration.config:
        invoke_cli(commands.create_config, [str(projects_root)])
        return True
    return False


@pytest.fixture(autouse=True)
def projects(environment_configuration, project_name, projects_root, config_exists):
    if not environment_configuration.project:
        return []

    default = ['-d'] if environment_configuration.default_project else []
    project_suffix = ['', '1', '2'] if environment_configuration.multi_project else ['']
    args = [[f"{project_name}{s}", "-m", "test"] for s in project_suffix]
    args[0] += default

    projects = []
    for add_project_args in args:
        projects.append(add_project_args[0])
        invoke_cli(commands.add_project, add_project_args)

    return projects


@pytest.fixture(autouse=True)
def sources(environment_configuration, source_name, projects):
    if not environment_configuration.source:
        return []

    source_count = 3 if environment_configuration.multi_source else 1
    args = [[f"{project}-{source_name}{i+1}", "-m", "test", '-P', project]
            for i, project
            in itertools.product(range(source_count), projects)]

    sources = []
    for add_source_args in args:
        sources.append(add_source_args[0])
        invoke_cli(commands.add_source, add_source_args)

    return sources


@pytest.fixture(autouse=True)
def columns(environment_configuration, source_column_name, projects):
    if not environment_configuration.source_column:
        return []

    column_types = (
        ['int', 'float', 'str'] if environment_configuration.multi_source_column else ['int']
    )
    is_nullable = ['', '-n', '-n']
    col_names = [source_column_name, f"{source_column_name}1", f"{source_column_name}2"]
    args = [[col_names[i], column_types[i], is_nullable[i], '-P', project, '-m', 'test']
            for i, project in itertools.product(range(len(column_types)), projects)]

    columns = []
    for add_column_args in args:
        add_column_args = [a for a in add_column_args if a]
        columns.append(add_column_args[0])
        invoke_cli(commands.add_source_column, add_column_args)

    return columns
