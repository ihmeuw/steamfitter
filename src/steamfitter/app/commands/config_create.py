"""
====================
Create Configuration
====================

Configure steamfitter for the first time.

"""
from pathlib import Path

import click

from steamfitter.app import options
from steamfitter.app.configuration import Configuration
from steamfitter.app.directory_structure import ProjectDirectory
from steamfitter.app.utilities import setup_projects_root
from steamfitter.lib.cli_tools import (
    click_options,
    configure_logging_to_terminal,
    logger,
    monitoring,
)
from steamfitter.lib.shell_tools import mkdir


def main(projects_root: str):
    if Configuration.exists():
        click.echo("Configuration file already exists. Aborting.")
        raise click.Abort()

    projects_root, projects = setup_projects_root(projects_root)
    config = Configuration.create(str(projects_root))
    config.projects = projects
    config.persist()
    click.echo(f"Configuration file written to {config.path}")


@click.command()
@options.projects_root_required
@click_options.verbose_and_with_debugger
def create_config(
    projects_root: str,
    verbose: int,
    with_debugger: bool,
):
    """Create the user configuration for steamfitter.

    This will create a configuration file in the user's home directory and build a root
    directory for projects managed by steamfitter if one does not exist already.

    Usage:

         steamfitter configure /path/to/projects/root

    """
    configure_logging_to_terminal(verbose)
    main_ = monitoring.handle_exceptions(main, logger, with_debugger)
    main_(projects_root)
