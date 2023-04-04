"""
==============
Extract Source
==============

Extract data for a steamfitter project source

"""
from pathlib import Path

import click

from steamfitter.app import options
from steamfitter.app.directory_structure import ExtractionSourceVersionDirectory
from steamfitter.app.utilities import get_project_directory
from steamfitter.app.validation import SourceDoesNotExistError
from steamfitter.lib.cli_tools import (
    click_options,
    configure_logging_to_terminal,
    logger,
    monitoring,
)


def run(source_name, project_name) -> Path:
    """Extract a steamfitter project source."""
    project_directory = get_project_directory(project_name)
    project_name = project_directory["name"]
    extracted_data_directory = project_directory.data_directory.extracted_data_directory

    if source_name not in extracted_data_directory.sources:
        raise SourceDoesNotExistError(source_name=source_name, project_name=project_name)

    source_directory = extracted_data_directory.get_source_directory(source_name)

    # Make version subdirectory
    source_version_directory = ExtractionSourceVersionDirectory.create(
        source_directory.path,
        parent=source_directory,
        parent_name=source_name,
    )

    extractor = source_version_directory.get_extractor()
    extractor.run()

    return source_version_directory.path


def unrun(source_version_directory_path: Path):
    """Undo extraction of a steamfitter project source."""
    ExtractionSourceVersionDirectory.remove(source_version_directory_path)


@click.command(name="extract_source")
@options.source_name
@options.project_name
@click_options.verbose_and_with_debugger
def main(
    source_name: str,
    project_name: str,
    verbose: int,
    with_debugger: bool,
):
    """Extract a steamfitter project source."""
    configure_logging_to_terminal(verbose)
    main_ = monitoring.handle_exceptions(run, logger, with_debugger)
    return main_(source_name, project_name)
