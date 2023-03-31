"""
====================
Create configuration
====================

Creates the steamfitter configuration file and builds a root directory for projects.

"""
import shutil
from pathlib import Path

import click

from steamfitter.app import options
from steamfitter.app.configuration import Configuration
from steamfitter.app.utilities import setup_projects_root
from steamfitter.app.validation import ConfigurationExistsError
from steamfitter.lib.cli_tools import (
    click_options,
    configure_logging_to_terminal,
    logger,
    monitoring,
)


def run(projects_root: str) -> bool:
    if Configuration.exists():
        raise ConfigurationExistsError()

    projects_root = setup_projects_root(projects_root)
    config = Configuration.create(str(projects_root.path))
    config.projects = projects_root.projects
    config.persist()
    click.echo(f"Configuration file written to {config.path}")

    return projects_root.root_existed


def unrun(root_existed: bool, *_) -> None:
    config = Configuration()
    project_root = Path(config.projects_root)

    config.remove()
    if not root_existed:
        shutil.rmtree(project_root)


@click.command(name="create_config")
@options.projects_root_required
@click_options.verbose_and_with_debugger
def main(
    projects_root: str,
    verbose: int,
    with_debugger: bool,
):
    """Create the user configuration for steamfitter.

    This will create a configuration file in the user's home directory and build a root
    directory for projects managed by steamfitter if one does not exist already.

    """
    configure_logging_to_terminal(verbose)
    main_ = monitoring.handle_exceptions(run, logger, with_debugger)
    return main_(projects_root)
