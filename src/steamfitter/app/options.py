"""
==========================
Steamfitter Shared Options
==========================

This module contains shared options for the steamfitter CLI.

"""
import click

from steamfitter.app.utilities import clean_string


def clean_string_callback(ctx, param, value):
    return clean_string(value)


def clean_string_underscore_callback(ctx, param, value):
    return clean_string(value, dasherize=False)


project_name = click.option(
    "--project-name",
    "-P",
    default=None,
    help="The project to use. If not provided, the default project will be used.",
    callback=clean_string_callback,
)
project_name_required = click.argument(
    "project-name",
    callback=clean_string_callback,
)
source_name = click.argument(
    "source-name",
    callback=clean_string_callback,
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
    help="Whether to set the new entity as the default.",
)
projects_root = click.option(
    "--projects-root",
    "-R",
    default=None,
    help="The root directory for all steamfitter projects",
)
projects_root_required = click.argument("projects-root")
default_project_name = click.option(
    "--default-project-name",
    "-D",
    default=None,
    help="The name of the default project.",
    callback=clean_string_callback,
)
serialize = click.option(
    "--as_dict",
    "-s",
    is_flag=True,
    help="Whether to as_dict a directory upon removal. Used for testing.",
    hidden=True,
)
git_remote = click.option(
    "--git-remote",
    help="The url for the remote git repository.",
)
