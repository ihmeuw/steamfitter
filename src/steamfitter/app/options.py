"""
==========================
Steamfitter Shared Options
==========================

This module contains shared options for the steamfitter CLI.

"""
import click


project_name = click.option(
    "--project-name",
    "-P",
    default=None,
    help="The project to use. If not provided, the default project will be used.",
)
project_name_required = click.option(
    "--project-name",
    "-P",
    required=True,
    help="The project to use.",
)
source_name = click.option(
    "--source-name",
    "-s",
    required=True,
    help="The source to use",
)
description = click.option(
    "--description",
    "-m",
    required=True,
    help="A description of the entity.",
)
set_default = click.option(
    "--set-default",
    "-d",
    is_flag=True,
    help="Whether to set the new entity as the default."
)
projects_root = click.option(
    "--projects-root",
    "-R",
    default=None,
    help="The root directory for all steamfitter projects",
)
projects_root_required = click.option(
    "--projects-root",
    "-R",
    required=True,
    help="The root directory for all steamfitter projects",
)
default_project_name = click.option(
    "--default-project-name",
    "-D",
    default=None,
    help="The name of the default project.",
)
