"""
=================
Add Source Column
=================

Adds a new source column to a project. Source columns are known output fields for formatted
source data and are use for validating the results of extraction scripts.

"""
from typing import Tuple, Union

import click

from steamfitter.app import options
from steamfitter.app.utilities import get_project_directory
from steamfitter.app.validation import SourceColumnExistsError
from steamfitter.lib.cli_tools import (
    click_options,
    configure_logging_to_terminal,
    logger,
    monitoring,
)


def run(
    source_column_name: str,
    source_column_type: str,
    is_nullable: bool,
    description: str,
    project_name: Union[str, None],
) -> Tuple[str, str]:
    """Add a source column to a project."""
    project_directory = get_project_directory(project_name)
    project_name = project_directory["name"]
    extracted_data_directory = project_directory.data_directory.extracted_data_directory

    if source_column_name in extracted_data_directory["source_columns"]:
        raise SourceColumnExistsError(
            source_column_name=source_column_name,
            project_name=project_name,
        )

    extracted_data_directory.add_source_column(
        source_column_name=source_column_name,
        source_column_type=source_column_type,
        is_nullable=is_nullable,
        description=description,
    )

    click.echo(f"Source column {source_column_name} added to project {project_name}.")

    return project_name, source_column_name


def unrun(project_name: str, source_column_name: str, *_):
    """Remove a source column from a project."""
    project_directory = get_project_directory(project_name)
    extracted_data_directory = project_directory.data_directory.extracted_data_directory
    extracted_data_directory.remove_source_column(source_column_name)


@click.command(name="add_source_column")
@options.source_column_name
@options.source_column_type
@options.is_nullable
@options.description
@options.project_name
@click_options.verbose_and_with_debugger
def main(
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
    main_ = monitoring.handle_exceptions(run, logger, with_debugger)
    return main_(
        source_column_name, source_column_type, is_nullable, description, project_name
    )
