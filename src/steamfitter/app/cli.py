"""
===============
Steamfitter CLI
===============

This module contains the CLI for steamfitter.

"""
import click

from steamfitter.app import commands


@click.group()
def steamfitter():
    """A CLI for managing data science projects."""
    pass


steamfitter.add_command(commands.self_destruct.cli, name="self-destruct")


############################
# Function first interface #
############################


@steamfitter.group()
def add():
    """Adds new projects, data sources, modeling stages, etc."""
    pass


add.add_command(commands.add_project.cli, name="project")
add.add_command(commands.add_source.cli, name="source")


@steamfitter.group()
def remove():
    """Removes projects, data source, modeling stages, etc."""
    pass


remove.add_command(commands.remove_project.cli, name="project")
remove.add_command(commands.remove_source.cli, name="source")


@steamfitter.group()
def list():
    """Lists projects, data sources, modeling stages, etc."""
    pass


list.add_command(commands.list_project.cli, name="project")
list.add_command(commands.list_source.cli, name="source")
list.add_command(commands.list_config.cli, name="config")


##########################
# Entity first interface #
##########################


@steamfitter.group()
def config():
    """Creates, updates, or lists steamfitter configuration."""
    pass


config.add_command(commands.create_config.cli, name="create")
config.add_command(commands.update_config.cli, name="update")
config.add_command(commands.list_config.cli, name="list")


@steamfitter.group()
def project():
    """Adds, removes, or lists steamfitter projects."""
    pass


project.add_command(commands.add_project.cli, name="add")
project.add_command(commands.remove_project.cli, name="remove")
project.add_command(commands.list_project.cli, name="list")


@steamfitter.group()
def source():
    """Adds, removes, or lists steamfitter data sources."""
    pass


source.add_command(commands.add_source.cli, name="add")
source.add_command(commands.remove_source.cli, name="remove")
source.add_command(commands.list_source.cli, name="list")
