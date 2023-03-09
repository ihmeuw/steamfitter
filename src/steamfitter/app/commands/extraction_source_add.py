"""
==========
Add Source
==========

Adds a new source to a steamfitter project.

"""
from typing import Union

import click

from steamfitter.app import options
from steamfitter.app.utilities import clean_string, get_project_directory
from steamfitter.app.validation import SourceExistsError
from steamfitter.lib.cli_tools import (
    click_options,
    configure_logging_to_terminal,
    logger,
    monitoring,
)
from steamfitter.lib.exceptions import SteamfitterException


def main(source_name: str, project_name: Union[str, None], description: str):
    """Add a data source to a project."""
    source_name = clean_string(source_name)
    project_directory = get_project_directory(project_name)
    project_name = project_directory["name"]
    extracted_data_directory = project_directory.data_directory.extracted_data_directory

    if source_name in extracted_data_directory.sources:
        raise SourceExistsError(source_name)

    extracted_data_directory.add_source(source_name=source_name, description=description)

    click.echo(f"Source {source_name} added to project {project_name}.")


@click.command
@options.source_name
@options.project_name
@options.description
@click_options.verbose_and_with_debugger
def add_source(
    source_name: str,
    project_name: Union[str, None],
    description: str,
    verbose: int,
    with_debugger: bool,
):
    """Adds a source to the steamfitter managed project."""
    configure_logging_to_terminal(verbose)
    main_ = monitoring.handle_exceptions(main, logger, with_debugger)
    main_(source_name, project_name, description)
