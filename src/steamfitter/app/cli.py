from pathlib import Path
import click
import inflection

from steamfitter.shell_tools import mkdir
from steamfitter.app.configuration import (
    Configuration,
)
from steamfitter.app.filesystem.structure import ProjectDirectory


@click.group()
def steamfitter():
    """The Steamfitter project CLI."""
    pass


@steamfitter.command()
@click.argument("projects_root")
def configure(projects_root: str):
    """First time configuration for steamfitter.

    This will create a configuration file in the user's home directory and build a root
    directory for projects managed by steamfitter if one does not exist already.

    Usage:

         steamfitter configure /path/to/projects/root

    """
    if Configuration.exists():
        click.echo("Configuration file already exists. Aborting.")
    else:
        projects_root = Path(projects_root).expanduser().resolve()
        if not projects_root.exists():
            click.echo(f"Projects root {projects_root} does not exist. Creating it.")
            mkdir(projects_root, parents=True)
        config = Configuration.create(str(projects_root))
        click.echo(f"Configuration file written to {config.path}")


@steamfitter.command()
@click.argument("project_name")
@click.option(
    "--description",
    "-m",
    default="",
    help="A description of the project.",
)
@click.option(
    "--set-default",
    "-d",
    is_flag=True,
    default=False,
    help="Set this project as the default project.",
)
def add(project_name: str, description: str, set_default: bool):
    """Add a project to the configuration."""
    if not Configuration.exists():
        click.echo("Configuration file does not exist. Run `steamfitter configure` first.")
        return

    config = Configuration()
    project_name = inflection.dasherize(project_name.replace(' ', '_').lower())
    config.add_project(project_name, set_default=set_default)

    try:
        ProjectDirectory.create(
            config.projects_root,
            name=project_name,
            description=description,
        )
    except Exception:
        ProjectDirectory.remove(config.projects_root, name=project_name)
        config.rollback_add_project(project_name)
        raise

    click.echo(f"Project {project_name} added to the configuration.")
    if set_default:
        click.echo(f"Project {project_name} set as the default project.")


@steamfitter.command()
@click.argument("project_name")
def remove(project_name: str):
    """Remove a project from the configuration."""
    if not Configuration.exists():
        click.echo("Configuration file does not exist. Run `steamfitter configure` first.")
        return

    config = Configuration()
    project_name = inflection.dasherize(project_name.replace(' ', '_').lower())
    config.remove_project(project_name)
    ProjectDirectory.remove(config.projects_root, name=project_name)
    click.echo(f"Project {project_name} removed from the configuration.")
