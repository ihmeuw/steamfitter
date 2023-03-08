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


steamfitter.add_command(commands.self_destruct, name='self-destruct')


############################
# Function first interface #
############################

@steamfitter.group()
def add():
    """Adds new projects, data sources, modeling stages, etc."""
    pass


add.add_command(commands.add_project, name='project')
add.add_command(commands.add_source, name='source')


@steamfitter.group()
def remove():
    """Removes projects, data source, modeling stages, etc."""
    pass


remove.add_command(commands.remove_project, name='project')
remove.add_command(commands.remove_source, name='source')


@steamfitter.group()
def list():
    """Lists projects, data sources, modeling stages, etc."""
    pass


list.add_command(commands.list_projects, name='project')
list.add_command(commands.list_sources, name='source')
list.add_command(commands.list_config, name='config')


##########################
# Entity first interface #
##########################

@steamfitter.group()
def config():
    """Creates, updates, or lists steamfitter configuration."""
    pass


config.add_command(commands.create_config, name="create")
config.add_command(commands.update_config, name="update")
config.add_command(commands.list_config, name="list")


@steamfitter.group()
def project():
    """Adds, removes, or lists steamfitter projects."""
    pass


project.add_command(commands.add_project, name="add")
project.add_command(commands.remove_project, name="remove")
project.add_command(commands.list_projects, name="list")


@steamfitter.group()
def source():
    """Adds, removes, or lists steamfitter data sources."""
    pass


source.add_command(commands.add_source, name="add")
source.add_command(commands.remove_source, name="remove")
source.add_command(commands.list_sources, name="list")
