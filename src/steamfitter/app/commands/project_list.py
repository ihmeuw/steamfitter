"""
=============
List Projects
=============

List all projects managed by steamfitter.

"""
import click

from steamfitter.app.utilities import get_configuration
from steamfitter.lib.cli_tools import (
    click_options,
    configure_logging_to_terminal,
    logger,
    monitoring,
)


def main():
    config = get_configuration()
    if config.projects:
        click.echo("Projects")
        click.echo("========")
        for project_number, project_name in config.projects.items():
            click.echo(f"{project_number:<8}: {project_name}")
    else:
        click.echo("No projects found.")


@click.command()
@click_options.verbose_and_with_debugger
def list_projects(
    verbose: int,
    with_debugger: bool,
):
    """Prints the status of the steamfitter configuration."""
    configure_logging_to_terminal(verbose)
    main_ = monitoring.handle_exceptions(main, logger, with_debugger)
    main_()
