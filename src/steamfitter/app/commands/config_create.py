"""
====================
Create Configuration
====================

Configure steamfitter for the first time.

"""
from pathlib import Path
import click

from steamfitter.app.configuration import Configuration
from steamfitter.app.directory_structure import ProjectDirectory
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
    projects = []
    if not projects_root.exists():
        click.echo(f"Projects root {projects_root} does not exist. Creating it.")
        mkdir(projects_root, parents=True)
    else:
        click.echo(f"Projects root {projects_root} already exists. Using it.")
        for child in projects_root.iterdir():
            if child.is_dir() and ProjectDirectory.is_directory_type(child):
                click.echo(f"Found project {child.name} in {projects_root}. Adding it.")
                projects.append(child.name)

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
