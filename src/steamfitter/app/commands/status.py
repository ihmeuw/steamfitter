"""
======
Status
======

Prints the status of the steamfitter configuration.

"""
import click

from steamfitter.app.utilities import get_configuration
from steamfitter.lib.cli_tools import (
    logger,
    configure_logging_to_terminal,
    click_options,
    monitoring,
)


def main():
    config = get_configuration()

    click.echo(f"Projects root: {config.projects_root}")
    click.echo(f"Default project: {config.default_project}")
    click.echo(f"Projects: {', '.join(config.projects)}")


@click.command()
@click_options.verbose_and_with_debugger
def status(
    verbose: int,
    with_debugger: bool,
):
    """Prints the status of the steamfitter configuration."""
    configure_logging_to_terminal(verbose)
    main_ = monitoring.handle_exceptions(main, logger, with_debugger)
    main_()
