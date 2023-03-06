from pathlib import Path

import click
from steamfitter.shell_tools import mkdir
import yaml

from steamfitter.app.scraping.add_source import (
    add_source,
)
from steamfitter.app.configuration import (
    get_configuration_path,
    get_configuration,
    setup_extraction_root_metadata,
)


@click.group()
def scrape():
    pass


@scrape.command()
def configure():
    """First time configuration for the GHT scrapers."""
    config_path = get_configuration_path()
    if config_path.exists():
        click.echo("Configuration file already exists. Aborting.")
        return

    extraction_root = click.prompt(
        "Enter the path to the root of the GHT extraction data",
    )
    extraction_root = Path(extraction_root).expanduser().resolve()
    if not extraction_root.exists():
        create_extraction_root = click.prompt(
            f"Extraction root {str(extraction_root)} does not exist. Should we create it?",
            type=bool,
        )
        if not create_extraction_root:
            click.echo("Aborting.")
            return
        mkdir(extraction_root, parents=True)
        setup_extraction_root_metadata(extraction_root)

    config = {
        "ght_extraction_root": str(extraction_root),
    }
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with config_path.open("w") as f:
        yaml.dump(config, f)
    click.echo("Configuration file written to {}".format(config_path))


@scrape.command()
@click.option(
    "--extraction-method",
    "-m",
    type=click.Choice(["custom"]),
    default="custom",
)
def add(extraction_method):
    """Create the directory structure and python skeleton for a new scraper."""
    configuration = get_configuration()
    extraction_root = Path(configuration["ght_extraction_root"])

    raw_scraper_name = click.prompt("Enter the name of the source")
    scraper_name = raw_scraper_name.replace(" ", "_").lower()

    formatting_okay = click.prompt(
        f"Using computer friendly name {scraper_name}. Is this okay?", type=bool
    )
    if not formatting_okay:
        click.echo("Aborting.")
        return

    add_source(extraction_root, scraper_name, extraction_method)
