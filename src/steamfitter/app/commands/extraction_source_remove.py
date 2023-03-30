"""
=============
Remove Source
=============

Removes a source from a steamfitter managed project.

"""
import click

from steamfitter.app import options
from steamfitter.app.utilities import clean_string, get_project_directory
from steamfitter.app.validation import SourceDoesNotExistError
from steamfitter.lib.cli_tools import (
    click_options,
    configure_logging_to_terminal,
    logger,
    monitoring,
)


def main(source_name: str, project_name: str):
    """Remove a data source from a project."""
    project_directory = get_project_directory(project_name)
    source_name = clean_string(source_name)
    extracted_data_dir = project_directory.data_directory.extracted_data_directory

    if source_name not in extracted_data_dir.sources:
        raise SourceDoesNotExistError(project_name=project_name, source_name=source_name)

    extracted_data_dir.remove_source(source_name=source_name)

    click.echo(f"Source {source_name} removed from project {project_name}.")


@click.command
@options.source_name
@options.project_name
@click_options.verbose_and_with_debugger
def remove_source(
    source_name: str,
    project_name: str,
    verbose: int,
    with_debugger: bool,
):
    """Removes a source from a steamfitter managed project."""
    configure_logging_to_terminal(verbose)
    main_ = monitoring.handle_exceptions(main, logger, with_debugger)
    main_(source_name, project_name)
