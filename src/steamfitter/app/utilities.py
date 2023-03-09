"""
=========
Utilities
=========

This module contains utility functions for the steamfitter CLI.

"""
from pathlib import Path
from typing import List, Tuple, Union

import click
import inflection

from steamfitter.app.configuration import Configuration
from steamfitter.app.validation import (
    ConfigurationDoesNotExistError,
    ProjectDoesNotExistError,
    NoDefaultProjectError,
    NoProjectsExistError,
)

from steamfitter.app.directory_structure import ProjectDirectory
from steamfitter.lib.shell_tools import mkdir


def get_configuration():
    if not Configuration.exists():
        raise ConfigurationDoesNotExistError()
    return Configuration()


def setup_projects_root(projects_root: Union[str, Path]) -> Tuple[Path, List[str]]:
    projects_root = Path(projects_root).expanduser().resolve()
    projects = []
    if not projects_root.exists():
        click.echo(f"Projects root {projects_root} does not exist. Creating it.")
        mkdir(projects_root, parents=True)
    else:
        click.echo(f"Projects root {projects_root} already exists. Using it.")
        for child in projects_root.iterdir():
            if child.is_dir() and ProjectDirectory.is_directory_type(child):
                click.echo(f"Found project {child.name} in {projects_root}. Adding it.")
                projects.append(child.name)

    return projects_root, projects


def get_project_directory(project_name: str = None) -> ProjectDirectory:
    config = get_configuration()
    project_name = project_name if project_name else config.default_project

    if not config.projects:
        raise NoProjectsExistError()
    elif not project_name:
        raise NoDefaultProjectError()
    elif project_name not in config.projects:
        raise ProjectDoesNotExistError(project_name)

    return ProjectDirectory(config.projects_root / project_name)


def clean_string(raw_string: str) -> str:
    return inflection.dasherize(raw_string.replace(" ", "_").lower())
