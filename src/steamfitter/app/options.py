"""
==========================
Steamfitter Shared Options
==========================

This module contains shared options for the steamfitter CLI.

"""
import click


#############
# Arguments #
#############

projects_root_arg = click.argument("projects_root")
project_name_arg = click.argument("project_name")
source_name_arg = click.argument("source_name")


###########
# Options #
###########

project_name = click.option(
    "--project-name",
    "-P",
    default=None,
    help="The project to use. If not provided, the default project will be used.",
)
description = click.option(
    "--description",
    "-m",
    help="A description of the created entity.",
    required=True,
)
set_default = click.option(
    "--set-default",
    "-d",
    is_flag=True,
    help="Whether to set the new entity as the default."
)
