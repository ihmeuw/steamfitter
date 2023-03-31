"""
====================
Source Column Remove
====================

Removes a source column from a project. Source columns are known output fields for formatted
source data and are use for validating the results of extraction scripts.

"""
from typing import Tuple, Union

import click

from steamfitter.app import options
from steamfitter.app.utilities import get_project_directory
from steamfitter.app.validation import (
    SourceColumnDoesNotExistError,
)
from steamfitter.lib.cli_tools import (
    click_options,
    configure_logging_to_terminal,
    logger,
    monitoring,
)


def run(
    source_column_name: str,
    project_name: Union[str, None],
) -> Tuple[str, str, Tuple[str, bool, str]]:
    """Remove a source column from a project."""
    project_directory = get_project_directory(project_name)
    project_name = project_directory["name"]
    extracted_data_directory = project_directory.data_directory.extracted_data_directory

    if source_column_name not in extracted_data_directory.source_columns:
        raise SourceColumnDoesNotExistError(
            project_name=project_name,
            source_column_name=source_column_name,
        )

    source_column_features = extracted_data_directory.remove_source_column(source_column_name)

    click.echo(f"Source column {source_column_name} removed from project {project_name}.")

    return source_column_name, project_name, source_column_features


def unrun(
    source_column_name: str,
    project_name: str,
    source_column_features: Tuple[str, bool, str],
    *_,
) -> None:
    project_directory = get_project_directory(project_name)
    extracted_data_directory = project_directory.data_directory.extracted_data_directory
    extracted_data_directory.add_source_column(source_column_name, *source_column_features)


@click.command(name="remove_source_column")
@options.source_column_name
@options.project_name
@click_options.verbose_and_with_debugger
def main(
    source_column_name: str,
    project_name: Union[str, None],
    verbose: int,
    with_debugger: bool,
):
    """Removes a source column from the steamfitter managed project."""
    configure_logging_to_terminal(verbose)
    main_ = monitoring.handle_exceptions(run, logger, with_debugger)
    return main_(source_column_name, project_name)
