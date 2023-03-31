"""
====================
Update Configuration
====================

Update the steamfitter configuration.

"""
from pathlib import Path
import shutil
from typing import Tuple, Union

import click

from steamfitter.app import options
from steamfitter.app.utilities import get_configuration, setup_projects_root
from steamfitter.app.validation import (
    NoConfigurationUpdateError,
    ProjectDoesNotExistError,
)
from steamfitter.lib.cli_tools import (
    click_options,
    configure_logging_to_terminal,
    logger,
    monitoring,
)


def run(
    projects_root: Union[str, None],
    default_project_name: Union[str, None],
) -> Tuple[str, list, str, Union[bool, None]]:
    """Update the user configuration for steamfitter."""
    if projects_root is None and default_project_name is None:
        raise NoConfigurationUpdateError()

    config = get_configuration()

    if default_project_name is not None and default_project_name not in config.projects:
        raise ProjectDoesNotExistError(project_name=default_project_name)

    old_projects_root = config.projects_root
    old_projects = config.projects
    old_default_project = config.default_project

    if projects_root is not None:
        projects_root = setup_projects_root(projects_root)
        config.projects_root = str(projects_root.path)
        config.projects = projects_root.projects
        config.default_project = ""
        click.echo(f"Projects root updated to {config.projects_root}.")
        root_existed = projects_root.root_existed
    else:
        root_existed = True

    if default_project_name is not None:
        config.default_project = default_project_name
        click.echo(f"Default project updated to {config.default_project}.")

    config.persist()

    return old_projects_root, old_projects, old_default_project, root_existed


def unrun(
    old_projects_root: str,
    old_projects: list,
    old_default_project: str,
    root_existed: bool,
    *_,
) -> None:
    config = get_configuration()

    new_root = Path(config.projects_root)
    if not root_existed:
        shutil.rmtree(new_root)

    config.projects_root = old_projects_root
    config.projects = old_projects
    config.default_project = old_default_project
    config.persist()


@click.command(name="update_config")
@options.projects_root
@options.default_project_name
@click_options.verbose_and_with_debugger
def main(
    projects_root: Union[str, None],
    default_project_name: Union[str, None],
    verbose: int,
    with_debugger: bool,
):
    """Update the user configuration for steamfitter."""
    configure_logging_to_terminal(verbose)
    main_ = monitoring.handle_exceptions(run, logger, with_debugger)
    return main_(projects_root, default_project_name)
