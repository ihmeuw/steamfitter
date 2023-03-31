import itertools
from typing import Tuple, Type, List, NamedTuple

import pytest

from steamfitter.app import commands
from steamfitter.app.configuration import Configuration
from steamfitter.app.testing import invoke_cli
from steamfitter.app.validation import (
    SteamfitterCLIException,
    ConfigurationExistsError,
    ConfigurationDoesNotExistError,
    NoConfigurationUpdateError,
    ProjectExistsError,
    ProjectDoesNotExistError,
    NoDefaultProjectError,
    NoProjectsExistError,
    SourceExistsError,
    SourceDoesNotExistError,
    NoSourcesExistError,
    SourceColumnExistsError,
    SourceColumnDoesNotExistError,
)


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


@pytest.fixture(params=VALID_ENVIRONMENT_CONFIGURATIONS,
                ids=[str(e) for e in VALID_ENVIRONMENT_CONFIGURATIONS],
                scope="session")
def environment_configuration(request):
    return request.param


@pytest.fixture(scope="session")
def environment_root(environment_configuration, tmp_path_factory):
    return tmp_path_factory.mktemp(f"{environment_configuration}")


@pytest.fixture(scope="session")
def root_path(environment_root):
    return environment_root / "root"


@pytest.fixture(scope="session")
def config_path(environment_root):
    return environment_root / "user" / "config.yaml"


@pytest.fixture(autouse=True, scope="session")
def configuration_with_patched_path(config_path):
    Configuration._path = config_path


@pytest.fixture(scope="session")
def projects_root(root_path):
    return root_path / "sf-projects"


@pytest.fixture(scope="session")
def project_name():
    return "test-project"


@pytest.fixture(scope="session")
def project_path(project_name, projects_root):
    return projects_root / project_name


@pytest.fixture(scope="session")
def source_name():
    return "test-source"


@pytest.fixture(scope="session")
def source_column_name():
    return "test_source_column"





@pytest.fixture(autouse=True, scope="session")
def config_exists(environment_configuration, configuration_with_patched_path, projects_root):
    if environment_configuration.config:
        invoke_cli(commands.create_config, [str(projects_root)])
        return True
    return False


@pytest.fixture(autouse=True, scope="session")
def projects(environment_configuration, project_name, config_exists):
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


@pytest.fixture(autouse=True, scope="session")
def sources(environment_configuration, source_name, projects):
    if not environment_configuration.source:
        return []

    source_suffix = ['', '1', '2'] if environment_configuration.multi_source else ['']
    args = [[f"{source_name}{s}", "-m", "test", '-P', project]
            for s, project
            in itertools.product(source_suffix, projects)]

    sources = []
    for add_source_args in args:
        sources.append(add_source_args[0])
        invoke_cli(commands.add_source, add_source_args)

    return sources


@pytest.fixture(autouse=True, scope="session")
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


class CommandArgSpec(NamedTuple):
    """Specification of the Error boundaries of a cli command with a particular set of args.

    Attributes
    ----------
    command
        The command to be invoked.
    args
        The arguments to be passed to the command.
    requires
        A tuple of tuples of the form (resource, exception). The resources represent
        elements of the steamfitter environment that the command requires to be present in
        order to execute successfully and the exception is what happens if they are not
        present.
    excludes
        A tuple of tuples of the form (resource, exception). The resources represent
        elements of the steamfitter environment that the command requires to be absent in
        order to execute successfully and the exception is what happens if they are present.
    exception
        The exception that the command is expected to raise when all required resources
        are present and all missing resources are absent.  If not provided, the command
        is expected to execute without error.

    """
    command: commands.SteamfitterCommand
    args: List[str]
    requires: Tuple[Tuple[str, Type[SteamfitterCLIException]], ...] = tuple()
    excludes: Tuple[Tuple[str, Type[SteamfitterCLIException]], ...] = tuple()
    exception: Type[SteamfitterCLIException] = None
    extra_id: str = None

    def __repr__(self):
        return f"{self.command.cli.name}{': ' + str(self.extra_id) if self.extra_id else ''}"


COMMAND_ARG_SPECS = [
    CommandArgSpec(
        command=commands.create_config,
        args=["{projects_root}"],
        excludes=((RESOURCE.config, ConfigurationExistsError),),
    ),
    CommandArgSpec(
        command=commands.list_config,
        args=[],
        requires=((RESOURCE.config, ConfigurationDoesNotExistError),),
    ),
    CommandArgSpec(
        command=commands.update_config,
        args=['--projects-root', '{projects_root}'],
        requires=((RESOURCE.config, ConfigurationDoesNotExistError),),
        extra_id='root',
    ),
    CommandArgSpec(
        command=commands.update_config,
        args=['--default-project-name', '{project_name}'],
        requires=((RESOURCE.config, ConfigurationDoesNotExistError),
                  (RESOURCE.project, ProjectDoesNotExistError)),
        extra_id='default',
    ),
    CommandArgSpec(
        command=commands.update_config,
        args=['--projects-root', '{projects_root}', '--default-project-name', '{project_name}'],
        requires=((RESOURCE.config, ConfigurationDoesNotExistError),
                  (RESOURCE.project, ProjectDoesNotExistError)),
        extra_id='both',
    ),
    CommandArgSpec(
        command=commands.update_config,
        args=[],
        requires=(),
        exception=NoConfigurationUpdateError,
        extra_id='no_config',
    ),
    CommandArgSpec(
        command=commands.add_project,
        args=['{project_name}', '-m', 'test'],
        requires=((RESOURCE.config, ConfigurationDoesNotExistError),),
        excludes=((RESOURCE.project, ProjectExistsError),),
    ),
    CommandArgSpec(
        command=commands.add_project,
        args=['{project_name}', '-m', 'test', '-d'],
        requires=((RESOURCE.config, ConfigurationDoesNotExistError),),
        excludes=((RESOURCE.project, ProjectExistsError),),
        extra_id='default',
    ),
    CommandArgSpec(
        command=commands.list_project,
        args=[],
        requires=((RESOURCE.config, ConfigurationDoesNotExistError),
                  (RESOURCE.project, NoProjectsExistError)),
    ),
    CommandArgSpec(
        command=commands.remove_project,
        args=['{project_name}', '-s'],
        requires=((RESOURCE.config, ConfigurationDoesNotExistError),
                  (RESOURCE.project, ProjectDoesNotExistError)),
    ),
    CommandArgSpec(
        command=commands.add_source,
        args=['{source_name}', '-m', 'test'],
        requires=((RESOURCE.config, ConfigurationDoesNotExistError),
                  (RESOURCE.project, NoProjectsExistError),
                  (RESOURCE.default_project, NoDefaultProjectError)),
        excludes=((RESOURCE.source, SourceExistsError),),
    ),
    CommandArgSpec(
        command=commands.add_source,
        args=['{source_name}', '-m', 'test', '--project-name', '{project_name}'],
        requires=((RESOURCE.config, ConfigurationDoesNotExistError),
                  (RESOURCE.project, NoProjectsExistError)),
        excludes=((RESOURCE.source, SourceExistsError),),
        extra_id='project',
    ),
    CommandArgSpec(
        command=commands.list_source,
        args=[],
        requires=((RESOURCE.config, ConfigurationDoesNotExistError),
                  (RESOURCE.project, NoProjectsExistError),
                  (RESOURCE.default_project, NoDefaultProjectError),
                  (RESOURCE.source, NoSourcesExistError)),
    ),
    CommandArgSpec(
        command=commands.list_source,
        args=['--project-name', '{project_name}'],
        requires=((RESOURCE.config, ConfigurationDoesNotExistError),
                  (RESOURCE.project, NoProjectsExistError),
                  (RESOURCE.source, NoSourcesExistError)),
        extra_id='project',
    ),
    CommandArgSpec(
        command=commands.remove_source,
        args=['{source_name}', '-s'],
        requires=((RESOURCE.config, ConfigurationDoesNotExistError),
                  (RESOURCE.project, NoProjectsExistError),
                  (RESOURCE.default_project, NoDefaultProjectError),
                  (RESOURCE.source, SourceDoesNotExistError)),
    ),
    CommandArgSpec(
        command=commands.remove_source,
        args=['{source_name}', '--project-name', '{project_name}', '-s'],
        requires=((RESOURCE.config, ConfigurationDoesNotExistError),
                  (RESOURCE.project, NoProjectsExistError),
                  (RESOURCE.source, SourceDoesNotExistError)),
        extra_id='project',
    ),
    CommandArgSpec(
        command=commands.add_source_column,
        args=['{source_column_name}', 'str', '-m', 'test'],
        requires=((RESOURCE.config, ConfigurationDoesNotExistError),
                  (RESOURCE.project, NoProjectsExistError),
                  (RESOURCE.default_project, NoDefaultProjectError)),
        excludes=((RESOURCE.source_column, SourceColumnExistsError),),
    ),
    CommandArgSpec(
        command=commands.add_source_column,
        args=['{source_column_name}', 'str', '-n', '-m', 'test'],
        requires=((RESOURCE.config, ConfigurationDoesNotExistError),
                  (RESOURCE.project, NoProjectsExistError),
                  (RESOURCE.default_project, NoDefaultProjectError)),
        excludes=((RESOURCE.source_column, SourceColumnExistsError),),
        extra_id='nullable'
    ),
    CommandArgSpec(
        command=commands.add_source_column,
        args=['{source_column_name}', 'str', '-m', 'test', '--project-name',
              '{project_name}'],
        requires=((RESOURCE.config, ConfigurationDoesNotExistError),
                  (RESOURCE.project, NoProjectsExistError)),
        excludes=((RESOURCE.source_column, SourceColumnExistsError),),
        extra_id='project'
    ),
    CommandArgSpec(
        command=commands.add_source_column,
        args=['{source_column_name}', 'str', '-n', '-m', 'test', '--project-name', '{project_name}'],
        requires=((RESOURCE.config, ConfigurationDoesNotExistError),
                  (RESOURCE.project, NoProjectsExistError)),
        excludes=((RESOURCE.source_column, SourceColumnExistsError),),
        extra_id='nullable_project'
    ),
    CommandArgSpec(
        command=commands.list_source_column,
        args=[],
        requires=((RESOURCE.config, ConfigurationDoesNotExistError),
                  (RESOURCE.project, NoProjectsExistError),
                  (RESOURCE.default_project, NoDefaultProjectError)),
    ),
    CommandArgSpec(
        command=commands.list_source_column,
        args=['--project-name', '{project_name}'],
        requires=((RESOURCE.config, ConfigurationDoesNotExistError),
                  (RESOURCE.project, NoProjectsExistError)),
        extra_id='project',
    ),
    CommandArgSpec(
        command=commands.remove_source_column,
        args=['{source_column_name}'],
        requires=((RESOURCE.config, ConfigurationDoesNotExistError),
                  (RESOURCE.project, NoProjectsExistError),
                  (RESOURCE.default_project, NoDefaultProjectError),
                  (RESOURCE.source_column, SourceColumnDoesNotExistError),),
    ),
    CommandArgSpec(
        command=commands.remove_source_column,
        args=['{source_column_name}', '--project-name', '{project_name}'],
        requires=((RESOURCE.config, ConfigurationDoesNotExistError),
                  (RESOURCE.project, NoProjectsExistError),
                  (RESOURCE.source_column, SourceColumnDoesNotExistError),),
        extra_id='project',
    ),
]


@pytest.fixture(params=COMMAND_ARG_SPECS, ids=[str(c) for c in COMMAND_ARG_SPECS])
def command_specs(
    request,
    projects_root,
    project_name,
    source_name,
    source_column_name,
    environment_configuration,
):
    spec = request.param

    command = spec.command
    args = spec.args
    format_args = {
        'projects_root': str(projects_root),
        'project_name': project_name,
        'source_name': source_name,
        'source_column_name': source_column_name,
    }
    args = [args.format(**format_args) for args in args]

    # Things are reversed here so they can be specified in order of precedence in the
    # definition of the CommandArgSpec.
    expected_error = spec.exception(**format_args) if spec.exception else None
    for resource, error in reversed(spec.excludes):
        if environment_configuration.resource_exists(resource):
            expected_error = error(**format_args)
    for resource, error in reversed(spec.requires):
        if not environment_configuration.resource_exists(resource):
            expected_error = error(**format_args)

    return command, args, expected_error


def test_error_boundaries(environment_configuration, command_specs, projects_root, environment_root, capsys):
    command, args_, expected_error = command_specs

    # with capsys.disabled():
    #     print('\n')
    #     list_files(str(environment_root))

    if expected_error is None:
        result = invoke_cli(command, args_)
        return_value = (result.return_value if isinstance(result.return_value, tuple)
                        else (result.return_value,))
        command.unrunner(*return_value)

    else:
        result = invoke_cli(command, args_, exit_zero=False)
        assert expected_error.message in result.output
