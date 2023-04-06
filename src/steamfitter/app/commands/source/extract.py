"""
==============
Extract Source
==============

Extract data for a steamfitter project source

"""
from pathlib import Path

import click
import pandas as pd

from steamfitter.app import options
from steamfitter.app.directory_structure import ExtractionSourceVersionDirectory
from steamfitter.app.utilities import get_project_directory
from steamfitter.app.validation import SourceDoesNotExistError, NoSourceColumnsError
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

    source_columns = extracted_data_directory.source_columns
    if source_columns.empty:
        raise NoSourceColumnsError(
            source_column_path=extracted_data_directory.source_columns_path,
        )

    source_directory = extracted_data_directory.get_source_directory(source_name)
    source_version_directory = source_directory.extract_new_version()

    return source_version_directory.path


def _validate_extracted_data(
    version_directory: Path,
    source_columns: pd.DataFrame,
):
    """Validate extracted data."""
    formatted_data = pd.read_csv(version_directory / "formatted_data.csv")
    import pdb; pdb.set_trace()
    expected_cols = set(formatted_data.columns).intersection(set(source_columns["name"]))





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
