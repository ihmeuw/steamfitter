import click

from steamfitter.app.configuration import Configuration


from steamfitter.lib.cli_tools.logging import logger


def main():
    if Configuration.exists():
        config = Configuration()
        click.echo(f"Projects root: {config.projects_root}")
        click.echo(f"Default project: {config.default_project}")
        click.echo(f"Projects: {', '.join(config.projects)}")
    else:
        click.echo("Steamfitter is not configured. "
                   "Run `steamfitter configure` to get started.")


@click.command()

def status():
    """Prints the status of the Steamfitter project."""

