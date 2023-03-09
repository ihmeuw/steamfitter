"""
==================
Source Column List
==================

Lists all source columns for a project. Source columns are known output fields for formatted
source data and are use for validating the results of extraction scripts.

"""
from typing import Union

import click

from steamfitter.app import options
from steamfitter.app.utilities import get_project_directory
from steamfitter.lib.cli_tools import (
    click_options,
    configure_logging_to_terminal,
    logger,
    monitoring,
)


def main(project_name: Union[str, None]):
    """List all source columns for a project."""
    project_directory = get_project_directory(project_name)
    project_name = project_directory["name"]
    extracted_data_directory = project_directory.data_directory.extracted_data_directory
    source_columns = extracted_data_directory["source_columns"]

    if source_columns:
        title = f"Source columns for project {project_name}"
        click.echo(title)
        click.echo("=" * len(title))
        header = f"{'Name':<20}: {'Type':<10} {'Nullable':<10} {'Description'}"
        click.echo(header)
        click.echo("-" * len(header))
        for source_column, (col_type, is_nullable, description) in source_columns.items():
            click.echo(f"{source_column:<20}: {col_type:<10} {is_nullable:<10} {description}")
    else:
        click.echo("No source columns found.")


@click.command()
@options.project_name
@click_options.verbose_and_with_debugger
def list_source_columns(
    project_name: Union[str, None],
    verbose: int,
    with_debugger: bool,
):
    """List all source columns for a project."""
    configure_logging_to_terminal(verbose)
    main_ = monitoring.handle_exceptions(main, logger, with_debugger)
    main_(project_name)
