"""
========
Metadata
========

An in memory representation of a metadata file for a project directory. Metadata stores
additional information beyond what the filesystem can provide and is especially useful for
providing information about the provenance of a project directory.

Metadata is stored in a YAML file named ``metadata.yaml`` in all directories in a project.
The information it stores is specific to the type of directory. For example, a directory
containing a model will contain information about the model run parameters, the model run
time, the data sources used, etc. A directory representing an extracted data source
on the other hand will contain information about the data source itself, such as the
source URL, the date the data was extracted, etc.

Metadata comes in two flavors. The base class, :class:`Metadata`, is a generic class that
can be used to represent any type of directory. It is intended to be used on directories
that are created with the main project management tool ``steamfitter``.  The second class,
:class:`RunMetadata`, is a subclass of :class:`Metadata` that is used to represent a
versioned directory of an application run. It is intended to be used on directories that
are created with user applications that are built on top of ``steamfitter`` such as source
specific data extraction applications and modeling applications.

"""
import datetime
import time
from pathlib import Path
from typing import Any, Dict, Union

from steamfitter.lib.io import yaml as io


class Metadata:
    """An in-memory representation of a metadata file."""

    _FILE_NAME: str = "metadata.yaml"

    def __init__(self, metadata_dict: Dict = None, **kwargs):
        if kwargs:
            raise ValueError("The base metadata class does not accept keyword arguments.")
        self._metadata = metadata_dict if metadata_dict is not None else {}

    @classmethod
    def from_directory(cls, directory: Path) -> "Metadata":
        """Load a metadata file from disk.

        Parameters
        ----------
        directory
            The directory containing the metadata file.

        Returns
        -------
        Metadata
            The representation of the metadata file.

        """
        metadata_dict = io.load(directory / cls._FILE_NAME)
        return cls(metadata_dict)

    #####################
    # Interface methods #
    #####################

    def __getitem__(self, metadata_key: str) -> Any:
        """Return the value of a metadata property."""
        return self._metadata[metadata_key]

    def __setitem__(self, metadata_key: str, value: Any) -> None:
        """Set the value of a metadata property."""
        self._metadata[metadata_key] = value

    def __contains__(self, metadata_key: str) -> bool:
        """Return True if the metadata contains the item."""
        return metadata_key in self._metadata

    def update(self, new_metadata: Dict[str, Any]) -> None:
        """Update the metadata of a directory."""
        self._metadata.update(**new_metadata)

    def as_dict(self) -> Dict:
        """Return a copy of the metadata as a dictionary."""
        return self._metadata.copy()

    def persist(self):
        """Persist the metadata to disk."""
        io.dump(Path(self._metadata["root"]) / self._FILE_NAME, self._metadata, exist_ok=True)

    #######################
    # Metadata generation #
    #######################
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
        io.dump(metadata_path, metadata_dict, exist_ok=False)
        return cls.from_directory(root)

    def __repr__(self):
        return f"{self.__class__.__name__}({self._metadata})"


class RunMetadata(Metadata):
    """Extension of the base metadata class to store information about a tool run."""

    def __init__(self, metadata_dict: Dict = None, application_name: str = None, **kwargs):
        if application_name is None:
            raise ValueError("RunMetadata requires an application name.")
        super().__init__(metadata_dict, **kwargs)
        self.application_name = application_name

        # Move everything under the application namespace. This makes provenance
        # A lot easier to programmatically access.
        self._metadata[self.application_name] = {
            **self._metadata,
            "run_time": self._get_time(),
            "end_time": None,
            "run_time_seconds": None,
            "provenance": {},
        }

    @staticmethod
    def _get_time():
        """Return the current time in a format suitable for a metadata file."""
        return datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

    def __getitem__(self, metadata_key: str) -> Any:
        return self._metadata[self.application_name][metadata_key]

    def __setitem__(self, metadata_key: str, value: Any) -> None:
        self._metadata[self.application_name][metadata_key] = value

    def __contains__(self, metadata_key: str) -> bool:
        return metadata_key in self._metadata[self.application_name]

    def update(self, new_metadata: Dict[str, Any]) -> None:
        self._metadata[self.application_name].update(**new_metadata)

    def record_prior_stage_provenance(self, prior_stage_metadata_file: Union[str, Path]):
        """Records provenance information from a prior stage."""
        metadata_path = Path(prior_stage_metadata_file)
        if not metadata_path.name == self._FILE_NAME:
            raise ValueError("Can only update from `metadata.yaml` files.")
        self.update(io.load(metadata_path))

    def persist(self):
        """Persist the metadata to disk."""
        final_metrics = {
            "end_time": self._get_time(),
            "run_time_seconds": f"{time.time() - self['start_time']:.4f}",
        }
        self.update(final_metrics)
        super().persist()
