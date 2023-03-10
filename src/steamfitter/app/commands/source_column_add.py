"""
=================
Add Source Column
=================

Adds a new source column to a project. Source columns are known output fields for formatted
source data and are use for validating the results of extraction scripts.

"""
from typing import Union

import click

from steamfitter.app import options
from steamfitter.app.utilities import clean_string, get_project_directory
from steamfitter.lib.cli_tools import (
    click_options,
    configure_logging_to_terminal,
    logger,
    monitoring,
)
from steamfitter.lib.exceptions import SteamfitterException


def main(
    source_column_name: str,
    source_column_type: str,
    is_nullable: bool,
    description: str,
    project_name: Union[str, None],
):
    """Add a source column to a project."""
    source_column_name = clean_string(source_column_name).replace("-", "_")
    project_directory = get_project_directory(project_name)
    project_name = project_directory["name"]
    extracted_data_directory = project_directory.data_directory.extracted_data_directory
    try:
        extracted_data_directory.add_source_column(
            source_column_name=source_column_name,
            source_column_type=source_column_type,
            is_nullable=is_nullable,
            description=description,
        )
    except SteamfitterException as e:
        click.echo(str(e))
        raise click.Abort()

    click.echo(f"Source column {source_column_name} added to project {project_name}.")


@click.command
@options.source_column_name
@options.source_column_type
@options.is_nullable
@options.description
@options.project_name
@click_options.verbose_and_with_debugger
def add_source_column(
    source_column_name: str,
    source_column_type: str,
    is_nullable: bool,
    description: str,
    project_name: Union[str, None],
    verbose: int,
    with_debugger: bool,
):
    """Adds a source column to the steamfitter managed project."""
    configure_logging_to_terminal(verbose)
    main_ = monitoring.handle_exceptions(main, logger, with_debugger)
    main_(source_column_name, source_column_type, is_nullable, description, project_name)
