"""
=============
Self-destruct
=============

This command will remove all steamfitter projects and configuration from the system.

"""
import click

from steamfitter.app.utilities import (
    get_configuration,
)
from steamfitter.app.structure import ProjectDirectory
from steamfitter.lib.cli_tools import (
    logger,
    configure_logging_to_terminal,
    click_options,
    monitoring,
)


def main():
    configuration = get_configuration()
    click.confirm(
        "Are you sure you want to destroy all projects and configuration?",
        abort=True,
    )
    for project in configuration.projects:
        click.echo(f"Removing project: {project}")
        ProjectDirectory.remove(configuration.projects_root / project)
    click.echo("Removing configuration file.")
    configuration.remove()
    click.echo("All projects and configuration removed.")


@click.command
@click_options.verbose_and_with_debugger
def self_destruct(verbose: int, with_debugger: bool):
    """Destroy the configuration file and all projects managed by steamfitter."""
    configure_logging_to_terminal(verbose)
    main_ = monitoring.handle_exceptions(main, logger, with_debugger)
    main_()
