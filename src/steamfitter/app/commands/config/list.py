"""
==================
List Configuration
==================

Prints the status of the steamfitter configuration.

"""
import click

from steamfitter.app.utilities import get_configuration
from steamfitter.lib.cli_tools import (
    click_options,
    configure_logging_to_terminal,
    logger,
    monitoring,
)


def run() -> None:
    config = get_configuration()
    click.echo(f"Projects root: {config.projects_root}")
    click.echo(f"Default project: {config.default_project}")
    click.echo(f"Projects: {', '.join(config.projects)}")


def unrun(*_) -> None:
    pass


@click.command(name="list_config")
@click_options.verbose_and_with_debugger
def main(
    verbose: int,
    with_debugger: bool,
):
    """Prints the status of the steamfitter configuration."""
    configure_logging_to_terminal(verbose)
    main_ = monitoring.handle_exceptions(run, logger, with_debugger)
    return main_()
