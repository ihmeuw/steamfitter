from pathlib import Path

import click
from steamfitter.shell_tools import mkdir
import yaml


SOURCE_DIR_FORMAT = "{count:0>5d}_{name}"
SOURCE_METADATA_FILE = SOURCE_DIR_FORMAT.format(count=0, name="sources") + ".yaml"



def setup_extraction_root_metadata(extraction_root: Path) -> None:
    """Create the extraction metadata file for the extraction root."""
    extraction_metadata = {
        "source_count": 0,
        "sources": [],
    }
    extraction_metadata_path = extraction_root / SOURCE_METADATA_FILE

    if extraction_metadata_path.exists():
        raise FileExistsError(
            f"Extraction metadata file {extraction_metadata_path} already exists."
        )

    with extraction_metadata_path.open("w") as f:
        yaml.dump(extraction_metadata, f)


CUSTOM_EXTRACTION_TEMPLATE = '''

def extract_{source_name}(output_directory: Path) -> None:
    """Extract {source_name}."""
    # Custom code here.
    pass
    
    
if __name__ == "__main__":
    output_directory = __file__.parent
    extract_{source_name}(output_directory)

'''


def add_source(extraction_root: Path, source_name: str, extraction_method: str) -> None:
    """Add a source to the extraction root."""
    extraction_metadata_path = extraction_root / SOURCE_METADATA_FILE
    with extraction_metadata_path.open() as f:
        extraction_metadata = yaml.full_load(f)

    source_count = extraction_metadata["source_count"]
    source_dir_name = SOURCE_DIR_FORMAT.format(count=source_count + 1, name=source_name)
    source_dir = extraction_root / source_dir_name

    source_metadata = {
        "name": source_name,
        "source_dir": str(source_dir),
    }
    extraction_metadata["sources"].append(source_metadata)
    extraction_metadata["source_count"] += 1

    source_metadata["extraction_method"] = extraction_method

    # Do all our side effects
    mkdir(source_dir)

    source_metadata_path = source_dir / "description.yaml"
    with source_metadata_path.open("w") as f:
        yaml.dump(source_metadata, f)

    if extraction_method == "custom":
        custom_extraction_path = source_dir / "extract.py"
        extraction_template = CUSTOM_EXTRACTION_TEMPLATE.format(source_name=source_name)
        with custom_extraction_path.open("w") as f:
            f.write(extraction_template)

    with extraction_metadata_path.open("w") as f:
        yaml.dump(extraction_metadata, f)

    click.echo(f"Source {source_name} added to {extraction_root}")
