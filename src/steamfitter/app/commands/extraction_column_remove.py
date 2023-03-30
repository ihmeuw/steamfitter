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
from steamfitter.app.utilities import clean_string, get_project_directory
from steamfitter.app.validation import (
    SourceColumnDoesNotExistError,
)
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
    source_column_name = clean_string(source_column_name).replace("-", "_")
    project_directory = get_project_directory(project_name)
    project_name = project_directory["name"]
    extracted_data_directory = project_directory.data_directory.extracted_data_directory

    if source_column_name not in extracted_data_directory.source_columns:
        raise SourceColumnDoesNotExistError(
            project_name=project_name,
            source_column_name=source_column_name,
        )

    extracted_data_directory.remove_source_column(source_column_name)

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
