"""
====================
Update Configuration
====================

Update the steamfitter configuration.

"""
from typing import Union

import click

from steamfitter.app import options
from steamfitter.app.utilities import get_configuration, setup_projects_root
from steamfitter.app.validation import (
    NoConfigurationUpdateError,
    ProjectDoesNotExistError,
)
from steamfitter.lib.cli_tools import (
    click_options,
    configure_logging_to_terminal,
    logger,
    monitoring,
)


def main(projects_root: Union[str, None], default_project_name: Union[str, None]):
    """Update the user configuration for steamfitter."""
    config = get_configuration()

    if projects_root is None and default_project_name is None:
        raise NoConfigurationUpdateError()

    if default_project_name is not None and default_project_name not in config.projects:
        raise ProjectDoesNotExistError(default_project_name)

    if projects_root is not None:
        projects_root, projects = setup_projects_root(projects_root)
        config.projects_root = str(projects_root)
        config.projects = projects
        config.default_project = ""
        click.echo(f"Projects root updated to {config.projects_root}.")

    if default_project_name is not None:
        config.default_project = default_project_name
        click.echo(f"Default project updated to {config.default_project}.")

    config.persist()


@click.command()
@options.projects_root
@options.default_project_name
@click_options.verbose_and_with_debugger
def update_config(
    projects_root: Union[str, None],
    default_project_name: Union[str, None],
    verbose: int,
    with_debugger: bool,
):
    """Update the user configuration for steamfitter."""
    configure_logging_to_terminal(verbose)
    main_ = monitoring.handle_exceptions(main, logger, with_debugger)
    main_(projects_root, default_project_name)
