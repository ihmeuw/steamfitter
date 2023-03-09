"""
============
List Sources
============

List all extraction sources for a project managed by steamfitter.

"""

import click

from steamfitter.app import options
from steamfitter.app.utilities import get_project_directory
from steamfitter.lib.cli_tools import (
    click_options,
    configure_logging_to_terminal,
    logger,
    monitoring,
)


def main(project_name: str):
    project_directory = get_project_directory(project_name)
    extracted_data_directory = project_directory.data_directory.extracted_data_directory
    sources = extracted_data_directory["sources"]
    if sources:
        title = f"Sources for project {project_name}"
        click.echo(title)
        click.echo("=" * len(title))
        for source_number, source in sources.items():
            click.echo(f"{source_number:<8}: {source}")
    else:
        click.echo("No sources found.")


@click.command()
@options.project_name
@click_options.verbose_and_with_debugger
def list_sources(
    project_name: str,
    verbose: int,
    with_debugger: bool,
):
    """Prints the status of the steamfitter configuration."""
    configure_logging_to_terminal(verbose)
    main_ = monitoring.handle_exceptions(main, logger, with_debugger)
    main_(project_name)
