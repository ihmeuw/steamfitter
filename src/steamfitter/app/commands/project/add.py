"""
===========
Add Project
===========

Adds a new steamfitter project.

"""
from typing import Tuple

import click

from steamfitter.app import options
from steamfitter.app.directory_structure import ProjectDirectory
from steamfitter.app.utilities import get_configuration
from steamfitter.app.validation import ProjectExistsError
from steamfitter.lib.cli_tools import (
    click_options,
    configure_logging_to_terminal,
    logger,
    monitoring,
)


def run(
    project_name: str,
    description: str,
    set_default: bool,
    git_remote: str,
) -> Tuple[str, str]:
    config = get_configuration()

    if project_name in config.projects:
        raise ProjectExistsError(project_name=project_name)

    old_default = config.default_project

    config.add_project(project_name, set_default=set_default)
    ProjectDirectory.create(
        config.projects_root,
        name=project_name,
        description=description,
        git_remote=git_remote,
    )

    click.echo(f"Project {project_name} added to the configuration.")
    if set_default:
        click.echo(f"Project {project_name} set as the default project.")
    return project_name, old_default


def unrun(project_name: str, old_default: str, *_) -> None:
    config = get_configuration()
    config.remove_project(project_name, new_default=old_default)
    ProjectDirectory.remove(config.projects_root / project_name)


@click.command(name="add_project")
@options.project_name_required
@options.description
@options.set_default
@options.git_remote
@click_options.verbose_and_with_debugger
def main(
    project_name: str,
    description: str,
    set_default: bool,
    git_remote: str,
    verbose: int,
    with_debugger: bool,
):
    """Adds a steamfitter managed project."""
    configure_logging_to_terminal(verbose)
    main_ = monitoring.handle_exceptions(run, logger, with_debugger)
    return main_(project_name, description, set_default, git_remote)
