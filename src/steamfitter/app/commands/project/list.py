"""
=============
List Projects
=============

List all projects managed by steamfitter.

"""
import click

from steamfitter.app.utilities import get_configuration
from steamfitter.app.validation import NoProjectsExistError
from steamfitter.lib.cli_tools import (
    click_options,
    configure_logging_to_terminal,
    logger,
    monitoring,
)


def run() -> None:
    config = get_configuration()

    if not config.projects:
        raise NoProjectsExistError()

    click.echo("Projects")
    click.echo("========")
    for project_number, project_name in enumerate(config.projects):
        click.echo(f"{project_number+1:<8}: {project_name}")


def unrun(*_) -> None:
    pass


@click.command(name="list_project")
@click_options.verbose_and_with_debugger
def main(
    verbose: int,
    with_debugger: bool,
):
    """Prints the status of the steamfitter configuration."""
    configure_logging_to_terminal(verbose)
    main_ = monitoring.handle_exceptions(run, logger, with_debugger)
    return main_()
