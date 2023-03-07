from pathlib import Path
from typing import Dict

import yaml


class Metadata:
    """An in-memory representation of a metadata file.

    A metadata file is a YAML file that contains information about a directory.

    """

    _FILE_NAME: str = "metadata.yaml"

    def __init__(self, root: Path):
        self._metadata = self._load(root / self._FILE_NAME)

    def as_dict(self) -> Dict:
        """Return a copy of the metadata as a dictionary."""
        return self._metadata.copy()

    def __getitem__(self, item):
        """Return the value of a metadata property."""
        return self._metadata[item]

    def __contains__(self, item):
        """Return True if the metadata contains the item."""
        return item in self._metadata

    def __setitem__(self, key, value):
        """Set the value of a metadata property."""
        self._metadata[key] = value
        self._dump(self._metadata["root"] / self._FILE_NAME, self._metadata, exist_ok=True)

    def update(self, **kwargs):
        """Update the metadata of a directory."""
        self._metadata.update(**kwargs)
        self._dump(self._metadata["root"] / self._FILE_NAME, self._metadata, exist_ok=True)

    ################################
    # First time class generation #
    ################################
    @classmethod
    def create(cls, root: Path, **kwargs) -> "Metadata":
        """Create a new metadata file.

        Parameters
        ----------
        root
            The root directory of the metadata file.
        kwargs
            A dictionary of keyword arguments and values to initialize the metadata file with.
            These should be a superset of the CREATION_ARGS of the metadata file class.

        Returns
        -------
        Metadata
            The representation of the metadata file after it has been created on disk.

        Raises
        ------
        ValueError
            If the arguments are not passed as keyword arguments or the keyword arguments
            do not match the creation arguments of the metadata file.

        """
        metadata_path = root / cls._FILE_NAME
        metadata_dict = {
            "root": str(root),
            **kwargs,
        }
        cls._dump(metadata_path, metadata_dict, exist_ok=False)
        return cls(root)

    #################################
    # Serialization/Deserialization #
    #################################
    @staticmethod
    def _load(path: Path) -> Dict:
        """Load the metadata file.

        Parameters
        ----------
        path
            The path to the metadata file.

        Returns
        -------
        dict
            The metadata dictionary.

        """
        if not path.exists():
            raise FileNotFoundError(f"Metadata file {path} does not exist.")
        with path.open() as f:
            metadata = yaml.full_load(f)

        return metadata

    @staticmethod
    def _dump(path: Path, metadata: dict, exist_ok: bool = False) -> None:
        """Dump the metadata file to disk.

        Parameters
        ----------
        path
            The path to the metadata file.
        metadata
            The metadata dictionary to dump.
        exist_ok
            Whether to raise an error if the metadata file already exists.

        Raises
        ------
        ValueError
            If the metadata file already exists and `exist_ok` is False.

        """
        path.touch(mode=0o664, exist_ok=exist_ok)
        with path.open("w") as f:
            yaml.dump(metadata, f)
