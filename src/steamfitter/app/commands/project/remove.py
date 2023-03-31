"""
==============
Remove Project
==============

Removes a steamfitter managed project.

"""
from typing import Tuple

import click

from steamfitter.app import options
from steamfitter.app.directory_structure import ProjectDirectory
from steamfitter.app.utilities import get_configuration
from steamfitter.app.validation import ProjectDoesNotExistError
from steamfitter.lib.cli_tools import (
    click_options,
    configure_logging_to_terminal,
    logger,
    monitoring,
)


def run(project_name: str, serialize: bool) -> Tuple[str, bool, dict]:
    """Remove a project"""
    config = get_configuration()
    if project_name not in config.projects:
        raise ProjectDoesNotExistError(project_name=project_name)
    was_default = config.default_project == project_name

    project_directory_path = config.projects_root / project_name
    if serialize:
        project_directory_dict = ProjectDirectory(project_directory_path).serialize()
    else:
        project_directory_dict = {}

    config.remove_project(project_name)
    ProjectDirectory.remove(config.projects_root / project_name)

    click.echo(f"Project {project_name} removed from the configuration.")

    return project_name, was_default, project_directory_dict


def unrun(project_name: str, was_default: bool, project_directory_dict: dict, *_) -> None:
    """Restore a deleted project to it's state after initial creation.  Does not restore
    any files that were deleted after the project was created."""
    config = get_configuration()
    config.add_project(project_name, set_default=was_default)
    ProjectDirectory.deserialize(project_directory_dict)

    click.echo(f"Project {project_name} restored to the configuration.")


@click.command(name="remove_project")
@options.project_name_required
@options.serialize
@click_options.verbose_and_with_debugger
def main(
    project_name: str,
    serialize: bool,
    verbose: int,
    with_debugger: bool,
):
    """Removes a steamfitter managed project."""
    configure_logging_to_terminal(verbose)
    main_ = monitoring.handle_exceptions(run, logger, with_debugger)
    return main_(project_name, serialize)
