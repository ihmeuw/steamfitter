"""
=========
Utilities
=========

This module contains utility functions for the steamfitter CLI.

"""
from pathlib import Path
from typing import List, NamedTuple, Union

import click
import inflection

from steamfitter.app.configuration import Configuration
from steamfitter.app.directory_structure import ProjectDirectory
from steamfitter.app.validation import (
    ConfigurationDoesNotExistError,
    NoDefaultProjectError,
    NoProjectsExistError,
    ProjectDoesNotExistError,
)
from steamfitter.lib.shell_tools import mkdir


def get_configuration():
    if not Configuration.exists():
        raise ConfigurationDoesNotExistError()
    return Configuration()


class ProjectsRoot(NamedTuple):
    path: Path
    projects: List[str]
    root_existed: bool


def setup_projects_root(projects_root: Union[str, Path]) -> ProjectsRoot:
    projects_root = Path(projects_root).expanduser().resolve()
    projects = []

    if projects_root.exists():
        click.echo(f"Projects root {projects_root} already exists. Using it.")
        for child in projects_root.iterdir():
            if child.is_dir() and ProjectDirectory.is_directory_type(child):
                click.echo(f"Found project {child.name} in {projects_root}. Adding it.")
                projects.append(child.name)
        root_existed = True
    else:
        click.echo(f"Projects root {projects_root} does not exist. Creating it.")
        mkdir(projects_root, parents=True)
        root_existed = False

    return ProjectsRoot(projects_root, projects, root_existed)


def clean_string(raw_string: Union[str, None], dasherize=True) -> Union[str, None]:
    if raw_string is not None:
        raw_string = raw_string.replace(" ", "_").lower()
        if dasherize:
            raw_string = inflection.dasherize(raw_string)
    return raw_string


def get_project_name(project_name: str = None) -> str:
    config = get_configuration()
    project_name = project_name if project_name else config.default_project

    if not config.projects:
        raise NoProjectsExistError()
    elif not project_name:
        raise NoDefaultProjectError()
    elif project_name not in config.projects:
        raise ProjectDoesNotExistError(project_name=project_name)

    return project_name


def get_project_directory(project_name: str = None) -> ProjectDirectory:
    project_name = get_project_name(project_name)
    config = get_configuration()
    return ProjectDirectory(config.projects_root / project_name)
