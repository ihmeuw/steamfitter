"""
===========
Add Project
===========

Adds a new steamfitter project.

"""
import click

from steamfitter.app import options
from steamfitter.app.directory_structure import ProjectDirectory
from steamfitter.app.utilities import clean_string, get_configuration
from steamfitter.app.validation import ProjectExistsError
from steamfitter.lib.cli_tools import (
    click_options,
    configure_logging_to_terminal,
    logger,
    monitoring,
)


def main(project_name: str, description: str, set_default: bool):
    config = get_configuration()
    project_name = clean_string(project_name)

    if project_name in config.projects:
        raise ProjectExistsError(project_name)

    config.add_project(project_name, set_default=set_default)
    ProjectDirectory.create(
        config.projects_root,
        name=project_name,
        description=description,
    )

    click.echo(f"Project {project_name} added to the configuration.")
    if set_default:
        click.echo(f"Project {project_name} set as the default project.")


@click.command
@options.project_name_required
@options.description
@options.set_default
@click_options.verbose_and_with_debugger
def add_project(
    project_name: str,
    description: str,
    set_default: bool,
    verbose: int,
    with_debugger: bool,
):
    """Adds a steamfitter managed project."""
    configure_logging_to_terminal(verbose)
    main_ = monitoring.handle_exceptions(main, logger, with_debugger)
    main_(project_name, description, set_default)
