"""
====
yaml
====

YAML file I/O.

"""
from pathlib import Path
from typing import Dict

import yaml


def load(path: Path) -> Dict:
    """Load a YAML file.

    Parameters
    ----------
    path
        The path to the file.

    Returns
    -------
    Dict
        The data dictionary.

    """
    if not path.exists():
        raise FileNotFoundError(f"Metadata file {path} does not exist.")
    with path.open() as f:
        data = yaml.safe_load(f)

    return data


def dump(path: Path, data: Dict, exist_ok: bool = False) -> None:
    """Dump the data to disk.

    Parameters
    ----------
    path
        The path to the file to write.
    data
        The data to dump.
    exist_ok
        Whether to raise an error if the file already exists.

    Raises
    ------
    ValueError
        If the metadata file already exists and `exist_ok` is False.

    """
    if path.exists() and not exist_ok:
        raise FileExistsError(f"File {path} already exists.")

    with path.open("w") as f:
        yaml.safe_dump(data, f)
