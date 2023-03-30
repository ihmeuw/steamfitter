import itertools
from pathlib import Path
from typing import Callable, Tuple, Type, List, NamedTuple

import pytest

from steamfitter.app import commands
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
    NoSourceColumnsExistError,
)
from steamfitter.lib.testing import invoke_cli


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
    command: Callable
    args: List[str]
    requires: Tuple[Tuple[str, Type[SteamfitterCLIException]], ...] = tuple()
    excludes: Tuple[Tuple[str, Type[SteamfitterCLIException]], ...] = tuple()
    exception: Type[SteamfitterCLIException] = None
    extra_id: str = None

    def __repr__(self):
        return f"{self.command.name}{': ' + str(self.extra_id) if self.extra_id else ''}"


class __Resource(NamedTuple):
    """Enumeration of possible steamfitter environment resources."""
    config: str
    project: str
    default_project: str
    source: str
    source_column: str


RESOURCE = __Resource(*__Resource._fields)


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
        requires=((RESOURCE.config, ConfigurationDoesNotExistError),),
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
        command=commands.list_projects,
        args=[],
        requires=((RESOURCE.config, ConfigurationDoesNotExistError),
                  (RESOURCE.project, NoProjectsExistError)),
    ),
    CommandArgSpec(
        command=commands.remove_project,
        args=['{project_name}'],
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
        command=commands.list_sources,
        args=[],
        requires=((RESOURCE.config, ConfigurationDoesNotExistError),
                  (RESOURCE.project, NoProjectsExistError),
                  (RESOURCE.default_project, NoDefaultProjectError),
                  (RESOURCE.source, NoSourcesExistError)),
    ),
    CommandArgSpec(
        command=commands.list_sources,
        args=['--project-name', '{project_name}'],
        requires=((RESOURCE.config, ConfigurationDoesNotExistError),
                  (RESOURCE.project, NoProjectsExistError),
                  (RESOURCE.source, NoSourcesExistError)),
        extra_id='project',
    ),
    CommandArgSpec(
        command=commands.remove_source,
        args=['{source_name}'],
        requires=((RESOURCE.config, ConfigurationDoesNotExistError),
                  (RESOURCE.project, NoProjectsExistError),
                  (RESOURCE.default_project, NoDefaultProjectError),
                  (RESOURCE.source, SourceDoesNotExistError)),
    ),
    CommandArgSpec(
        command=commands.remove_source,
        args=['{source_name}', '--project-name', '{project_name}'],
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
        command=commands.list_source_columns,
        args=[],
        requires=((RESOURCE.config, ConfigurationDoesNotExistError),
                  (RESOURCE.project, NoProjectsExistError),
                  (RESOURCE.default_project, NoDefaultProjectError)),
    ),
    CommandArgSpec(
        command=commands.list_source_columns,
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


def test_error_boundaries(environment_configuration, command_specs):
    command, args, expected_error = command_specs

    if expected_error is None:
        invoke_cli(command, args)
    else:
        result = invoke_cli(command, args, exit_zero=False)
        assert expected_error.message in result.output
