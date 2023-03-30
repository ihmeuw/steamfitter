"""
====================
Create Configuration
====================

Configure steamfitter for the first time.

"""
import click

from steamfitter.app import options
from steamfitter.app.configuration import Configuration
from steamfitter.app.validation import ConfigurationExistsError
from steamfitter.app.utilities import setup_projects_root
from steamfitter.lib.cli_tools import (
    click_options,
    configure_logging_to_terminal,
    logger,
    monitoring,
)


def main(projects_root: str):
    if Configuration.exists():
        raise ConfigurationExistsError()

    projects_root = setup_projects_root(projects_root)
    config = Configuration.create(str(projects_root.path))
    config.projects = projects_root.projects
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
