"""
==============
Remove Project
==============

Removes a steamfitter managed project.

"""

import click

from steamfitter.app import options
from steamfitter.app.directory_structure import ProjectDirectory
from steamfitter.app.utilities import clean_string, get_configuration
from steamfitter.app.validation import ProjectDoesNotExistError
from steamfitter.lib.cli_tools import (
    click_options,
    configure_logging_to_terminal,
    logger,
    monitoring,
)


def main(project_name: str):
    """Remove a project from the configuration."""
    config = get_configuration()
    project_name = clean_string(project_name)

    if project_name not in config.projects:
        raise ProjectDoesNotExistError(project_name=project_name)

    config.remove_project(project_name)
    ProjectDirectory.remove(config.projects_root / project_name)

    click.echo(f"Project {project_name} removed from the configuration.")


@click.command
@options.project_name_required
@click_options.verbose_and_with_debugger
def remove_project(
    project_name: str,
    verbose: int,
    with_debugger: bool,
):
    """Removes a steamfitter managed project."""
    configure_logging_to_terminal(verbose)
    main_ = monitoring.handle_exceptions(main, logger, with_debugger)
    main_(project_name)
