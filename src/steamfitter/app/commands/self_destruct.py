"""
=============
Self-destruct
=============

This command will remove all steamfitter projects and configuration from the system.

"""
import click

from steamfitter.app.directory_structure import ProjectDirectory
from steamfitter.app.utilities import get_configuration
from steamfitter.lib.cli_tools import (
    click_options,
    configure_logging_to_terminal,
    logger,
    monitoring,
)


def run(yes: bool):
    configuration = get_configuration()
    if not yes:
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


def unrun(*_):
    raise NotImplementedError("Cannot unrun self-destruct.")


@click.command(hidden=True, name="self_destruct")
@click.option('--yes', '-y', is_flag=True, help="Skip confirmation prompt.")
@click_options.verbose_and_with_debugger
def main(yes: bool, verbose: int, with_debugger: bool):
    """Destroy the configuration file and all projects managed by steamfitter."""
    configure_logging_to_terminal(verbose)
    main_ = monitoring.handle_exceptions(run, logger, with_debugger)
    return main_(yes)
