"""
=============
Remove Source
=============

Removes a source from a steamfitter managed project.

"""
import click

from steamfitter.app import options
from steamfitter.app.utilities import get_project_directory
from steamfitter.app.validation import SourceDoesNotExistError
from steamfitter.lib.cli_tools import (
    click_options,
    configure_logging_to_terminal,
    logger,
    monitoring,
)
from steamfitter.app.directory_structure import ExtractionSourceDirectory


def run(source_name: str, project_name: str, serialize: bool):
    """Remove a data source from a project."""
    project_directory = get_project_directory(project_name)
    project_name = project_directory["name"]
    extracted_data_dir = project_directory.data_directory.extracted_data_directory

    if source_name not in extracted_data_dir.sources:
        raise SourceDoesNotExistError(project_name=project_name, source_name=source_name)

    source_directory_dict = extracted_data_dir.remove_source(
        source_name=source_name, serialize=serialize
    )

    click.echo(f"Source {source_name} removed from project {project_name}.")
    return source_directory_dict


def unrun(source_directory_dict: dict, *_) -> None:
    ExtractionSourceDirectory.deserialize(source_directory_dict)


@click.command(name="remove_source")
@options.source_name
@options.project_name
@options.serialize
@click_options.verbose_and_with_debugger
def main(
    source_name: str,
    project_name: str,
    serialize: bool,
    verbose: int,
    with_debugger: bool,
):
    """Removes a source from a steamfitter managed project."""
    configure_logging_to_terminal(verbose)
    main_ = monitoring.handle_exceptions(run, logger, with_debugger)
    return main_(source_name, project_name, serialize)
