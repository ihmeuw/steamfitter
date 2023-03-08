"""
=========
Configure
=========

Configure steamfitter for the first time.

"""
from pathlib import Path
import click

from steamfitter.app.configuration import Configuration
from steamfitter.app import options
from steamfitter.lib.cli_tools import (
    logger,
    configure_logging_to_terminal,
    click_options,
    monitoring,
)
from steamfitter.lib.shell_tools import mkdir


def main(projects_root: str):
    if Configuration.exists():
        click.echo("Configuration file already exists. Aborting.")
        raise click.Abort()

    projects_root = Path(projects_root).expanduser().resolve()
    if not projects_root.exists():
        click.echo(f"Projects root {projects_root} does not exist. Creating it.")
        mkdir(projects_root, parents=True)
    config = Configuration.create(str(projects_root))
    click.echo(f"Configuration file written to {config.path}")


@click.command()
@options.projects_root_arg
@click_options.verbose_and_with_debugger
def configure(
    projects_root: str,
    verbose: int,
    with_debugger: bool,
):
    """First time configuration for steamfitter.

    This will create a configuration file in the user's home directory and build a root
    directory for projects managed by steamfitter if one does not exist already.

    Usage:

         steamfitter configure /path/to/projects/root

    """
    configure_logging_to_terminal(verbose)
    main_ = monitoring.handle_exceptions(main, logger, with_debugger)
    main_(projects_root)
