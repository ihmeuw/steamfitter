"""
=========
Utilities
=========

This module contains utility functions for the steamfitter CLI.

"""
import click
import inflection

from steamfitter.app.configuration import Configuration
from steamfitter.app.structure import ProjectDirectory


def get_configuration():
    if not Configuration.exists():
        click.echo("Configuration file does not exist. Run `steamfitter configure` first.")
        raise click.Abort()
    return Configuration()


def get_project_directory(project_name: str = None) -> ProjectDirectory:
    config = get_configuration()
    if not (project_name or config.default_project):
        click.echo("No project provided and no default project set. Aborting.")
        raise click.Abort()
    elif not project_name:
        project_name = config.default_project

    project_name = inflection.dasherize(project_name.replace(' ', '_').lower())

    return ProjectDirectory(config.projects_root / project_name)


def clean_string(raw_string: str) -> str:
    return inflection.dasherize(raw_string.replace(' ', '_').lower())
