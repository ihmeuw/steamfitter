"""
====================
Source Column Remove
====================

Removes a source column from a project. Source columns are known output fields for formatted
source data and are use for validating the results of extraction scripts.

"""
from typing import Union

import click

from steamfitter.app import options
from steamfitter.app.utilities import (
    clean_string,
    get_project_directory,
)
from steamfitter.lib.exceptions import SteamfitterException
from steamfitter.lib.cli_tools import (
    click_options,
    configure_logging_to_terminal,
    logger,
    monitoring,
)


def main(
    source_column_name: str,
    project_name: Union[str, None],
):
    """Remove a source column from a project."""
    source_column_name = clean_string(source_column_name).replace('-', '_')
    project_directory = get_project_directory(project_name)
    project_name = project_directory["name"]
    extracted_data_directory = project_directory.data_directory.extracted_data_directory
    try:
        extracted_data_directory.remove_source_column(source_column_name)
    except SteamfitterException as e:
        click.echo(str(e))
        raise click.Abort()

    click.echo(f"Source column {source_column_name} removed from project {project_name}.")


@click.command
@options.source_column_name
@options.project_name
@click_options.verbose_and_with_debugger
def remove_source_column(
    source_column_name: str,
    project_name: Union[str, None],
    verbose: int,
    with_debugger: bool,
):
    """Removes a source column from the steamfitter managed project."""
    configure_logging_to_terminal(verbose)
    main_ = monitoring.handle_exceptions(main, logger, with_debugger)
    main_(source_column_name, project_name)
