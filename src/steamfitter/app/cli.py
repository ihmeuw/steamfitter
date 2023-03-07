from pathlib import Path
import click
import inflection

from steamfitter.lib.shell_tools import mkdir
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


@steamfitter.group()
def add():
    """Adds new projects, data sources, modeling stages, etc."""
    pass


@steamfitter.group()
def remove():
    """Removes projects, data sources, modeling stages, etc."""
    pass


##########################
# Project level commands #
##########################

@add.command(name="project")
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
def add_project(project_name: str, description: str, set_default: bool):
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
        ProjectDirectory.remove(config.projects_root)
        config.rollback_add_project(project_name)
        raise

    click.echo(f"Project {project_name} added to the configuration.")
    if set_default:
        click.echo(f"Project {project_name} set as the default project.")


@remove.command(name="project")
@click.argument("project_name")
def remove_project(project_name: str):
    """Remove a project from the configuration."""
    if not Configuration.exists():
        click.echo("Configuration file does not exist. Run `steamfitter configure` first.")
        return

    config = Configuration()
    project_name = inflection.dasherize(project_name.replace(' ', '_').lower())
    config.remove_project(project_name)
    ProjectDirectory.remove(config.projects_root)
    click.echo(f"Project {project_name} removed from the configuration.")


@add.command(name="source")
@click.argument("source_name")
@click.option(
    "--project",
    "-P",
    default=None,
    help="The project to which the data source should be added. If not provided, "
         "the default project will be used.",
)
@click.option(
    "--description",
    "-m",
    default="",
    help="A description of the data source.",
)
def add_source(source_name: str, project: str, description: str):
    """Add a data source to a project."""
    if not Configuration.exists():
        click.echo("Configuration file does not exist. Run `steamfitter configure` first.")
        return

    config = Configuration()
    if not (project or config.default_project):
        click.echo("No project provided and no default project set. Aborting.")
        return
    elif not project:
        project_name = config.default_project

    project_name = inflection.dasherize(project_name.replace(' ', '_').lower())
    source_name = inflection.dasherize(source_name.replace(' ', '_').lower())

    project_dir = ProjectDirectory(config.projects_root / project_name)
    extracted_data_dir = project_dir.data_directory.extracted_data_directory
    extracted_data_dir.add_source(source_name=source_name, description=description)
    click.echo(f"Source {source_name} added to project {project_name}.")


@remove.command(name="source")
@click.argument("source_name")
@click.option(
    "--project",
    "-P",
    default=None,
    help="The project from which the data source should be removed. If not provided, "
            "the default project will be used.",
)
def remove_source(source_name: str, project: str):
    """Remove a data source from a project."""
    project_root = get_project_root(project)

    source_name = inflection.dasherize(source_name.replace(' ', '_').lower())

    extracted_data_dir = project_root.data_directory.extracted_data_directory
    extracted_data_dir.remove_source(source_name=source_name)
    click.echo(f"Source {source_name} removed from project {project_name}.")


def get_project_root(project: str = None) -> ProjectDirectory:
    config = get_configuration()
    if not (project or config.default_project):
        click.echo("No project provided and no default project set. Aborting.")
        click.Abort()
    elif not project:
        project = config.default_project

    project_name = inflection.dasherize(project.replace(' ', '_').lower())

    return ProjectDirectory(config.projects_root / project_name)


def get_configuration():
    if not Configuration.exists():
        click.echo("Configuration file does not exist. Run `steamfitter configure` first.")
        click.Abort()
    return Configuration()


@steamfitter.command()
def self_destruct():
    """Destroy the configuration file and all projects managed by steamfitter."""
    configuration = get_configuration()
    click.confirm(
        "Are you sure you want to destroy all projects and configuration? [y/N]",
        abort=True,
    )
    for project in configuration.projects:
        click.echo(f"Removing project: {project}")
        ProjectDirectory.remove(configuration.projects_root / project)
    click.echo("Removing configuration file.")
    configuration.remove()
    click.echo("All projects and configuration removed.")
