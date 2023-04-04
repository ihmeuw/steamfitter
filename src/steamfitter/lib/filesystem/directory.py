from __future__ import annotations

import shutil
from collections import defaultdict
from importlib import import_module
from itertools import chain
from pathlib import Path
from typing import Any, Callable, Dict, List, Set, Tuple, Type, TypeVar

import inflection

from steamfitter.lib.exceptions import SteamfitterException
from steamfitter.lib.filesystem.archive import ARCHIVE_POLICIES
from steamfitter.lib.filesystem.metadata import Metadata
from steamfitter.lib.shell_tools import mkdir

DEFAULT_VALUE_FACTORY = Callable[[], Any]

DirectoryType = TypeVar("DirectoryType", bound="Directory")


class SteamfitterDirectoryError(SteamfitterException):
    """Exception raised for issues managing steamfitter directories."""

    pass


class Directory:
    """Base class for all directories in a project."""

    IS_INITIAL_DIRECTORY: bool = False
    DEFAULT_ARCHIVE_POLICY: bool = ARCHIVE_POLICIES.invalid

    NAME_TEMPLATE: str = "{name}"
    DESCRIPTION_TEMPLATE: str = "{description}"

    CREATION_ARGS: Set[str] = set()
    DEFAULT_EMPTY_ARGS: Set[Tuple[str, DEFAULT_VALUE_FACTORY]] = set()

    SUBDIRECTORY_TYPES: Tuple[Type[Directory], ...] = ()

    ##########################
    # Public class interface #
    ##########################

    @classmethod
    def create(
        cls,
        root: Path,
        parent: DirectoryType = None,
        exists_ok: bool = False,
        **kwargs,
    ) -> DirectoryType:
        """Create a new directory."""
        name = cls.make_name(root=root, **kwargs)
        path = root / name

        metadata_args = {
            "root": path,
            "name": name,
            "description": cls.make_description(**kwargs),
            "directory_type": cls.directory_type(),
            "directory_class": f"{cls.__module__}.{cls.__name__}",
            "archive_policy": kwargs.get("archive_policy", cls.DEFAULT_ARCHIVE_POLICY),
        }
        extra_fields = cls.make_extra_metadata_fields(metadata_args, **kwargs)
        metadata_args.update(extra_fields)

        mkdir(path, exists_ok=exists_ok)

        Metadata.create(**metadata_args)
        cls.add_initial_content(path, **kwargs)

        kwargs = cls.add_subdirectory_creation_args(metadata_args, kwargs)
        directory = cls(path, parent=parent)
        for subdirectory_type in directory.SUBDIRECTORY_TYPES:
            if subdirectory_type.IS_INITIAL_DIRECTORY:
                subdirectory_type.create(
                    root=path,
                    parent=directory,
                    exists_ok=exists_ok,
                    **kwargs,
                )

        return cls(path)

    @classmethod
    def create_from_dict(cls, serialized_directory: Dict) -> DirectoryType:
        """Return a directory instance from a serialized directory dictionary."""
        metadata = serialized_directory["metadata"]

        path = Path(metadata["root"])
        if path.exists() and path.is_file():
            # Should have been replaced with a tombstone file, remove
            # first and recreate directory
            path.unlink()
        del metadata["root"]
        mkdir(path)
        Metadata.create(path, **metadata)
        for subdirectory in serialized_directory["subdirectories"]:
            cls.create_from_dict(subdirectory)
        directory = cls.__from_on_disk_directory(path)
        return directory

    @classmethod
    def remove(cls, path: Path, safe=True, **kwargs):
        """Rollback the creation of a directory."""
        if safe:
            instance = cls(path, **kwargs)
            managed = instance["directory_type"] == cls.directory_type()
            if not managed:
                raise SteamfitterDirectoryError(
                    f"Cannot remove {str(path)} because it is not managed by steamfitter."
                )
        shutil.rmtree(path, ignore_errors=True)

    @classmethod
    def directory_type(cls) -> str:
        return inflection.underscore(cls.__name__.split("Directory")[0])

    @classmethod
    def is_directory_type(cls, path: Path) -> bool:
        """Return True if the given path is a directory of the given type."""
        try:
            metadata = Metadata.from_directory(path)
            return metadata["directory_type"] == cls.directory_type()
        except FileNotFoundError:
            return False

    ##########################
    # Class generation hooks #
    ##########################

    @classmethod
    def add_subdirectory_creation_args(cls, metadata_kwargs, inherited_kwargs):
        """Add kwargs to be used in name and description templates for child directories."""
        return inherited_kwargs

    @classmethod
    def add_initial_content(cls, path: Path, **kwargs):
        """Add initial content to a directory."""
        pass

    @classmethod
    def make_name(cls, root: Path, **kwargs) -> str:
        """Make a name for a directory."""
        return cls.NAME_TEMPLATE.format(**kwargs)

    @classmethod
    def make_description(cls, **kwargs) -> str:
        """Make a description for a directory."""
        return cls.DESCRIPTION_TEMPLATE.format(**kwargs)

    @classmethod
    def make_extra_metadata_fields(cls, metadata_args: Dict, **kwargs) -> Dict:
        """Make extra arguments for a directory."""
        directory_type = metadata_args["directory_type"]
        extra_fields = {}
        for field_name in cls.CREATION_ARGS:
            if field_name not in kwargs:
                raise ValueError(
                    f"{directory_type} directory must be initialized with "
                    f"a {field_name} argument."
                )
            extra_fields[field_name] = kwargs[field_name]

        for field_name, default_value_factory in cls.DEFAULT_EMPTY_ARGS:
            if field_name not in kwargs:
                extra_fields[field_name] = default_value_factory()

        return extra_fields

    ###########################
    # Public object interface #
    ###########################

    def __init__(self, path: Path, parent: DirectoryType = None):
        if not self.is_directory_type(path):
            raise SteamfitterDirectoryError(
                f"Directory {path} is not of type {self.directory_type()}."
            )

        self._parent = parent
        self._metadata = Metadata.from_directory(path)
        self._subdirectories = self.__collect_subdirectories(path)

    def get_subdirectory(
        self,
        *,
        directory_name: str = None,
        directory_class: Type[DirectoryType] = None,
    ) -> DirectoryType:
        """Return a subdirectory of the given name and class."""
        no_args = directory_name is None and directory_class is None
        both_args = directory_name is not None and directory_class is not None
        if no_args or both_args:
            raise ValueError("Must specify either directory_name or directory_class.")

        if directory_name:
            return self.__get_subdirectory_by_name(directory_name)
        else:
            return self.__get_subdirectory_by_class(directory_class)

    @property
    def path(self) -> Path:
        return Path(self._metadata["root"])

    @property
    def metadata(self) -> dict:
        return self._metadata.as_dict()

    def update(self, new_metadata: Dict[str, Any]):
        """Update the metadata of a directory."""
        self._metadata.update(new_metadata)

    def as_dict(self) -> Dict:
        """Return a dictionary representation of the directory."""
        return {
            "metadata": self.metadata,
            "subdirectories": [
                subdirectory.as_dict()
                for subdirectory in chain(*self._subdirectories.values())
            ],
        }

    def __getitem__(self, item):
        """Return the value of a directory property."""
        return self._metadata[item]

    def __setitem__(self, key, value):
        """Set the value of a directory property."""
        self._metadata[key] = value

    def __repr__(self):
        return f"{self.__class__.__name__}(path={self.path}, metadata={self.metadata})"

    ##################
    # Helper methods #
    ##################

    def __collect_subdirectories(self, path: Path) -> Dict[str, List[DirectoryType]]:
        """Collect all subdirectories of this directory."""
        subdirectories = defaultdict(list)
        for subdirectory in path.iterdir():
            if subdirectory.is_dir():
                try:
                    subdirectory = self.__from_on_disk_directory(subdirectory, parent=self)
                    subdirectory_type = subdirectory["directory_type"]
                    subdirectories[subdirectory_type].append(subdirectory)
                except FileNotFoundError:
                    pass
        return subdirectories

    @staticmethod
    def __from_on_disk_directory(path: Path, parent: DirectoryType = None) -> DirectoryType:
        """Return a directory instance from an on-disk directory."""
        metadata = Metadata.from_directory(path)
        directory_import_path = metadata["directory_class"]
        module_path, _, class_name = directory_import_path.rpartition(".")
        directory_class = getattr(import_module(module_path), class_name)
        directory = directory_class(path, parent)
        return directory

    def __get_subdirectory_by_name(self, directory_name: str) -> DirectoryType:
        """Return the directory of the given name in the current directory."""
        for subdirectory in chain(*self._subdirectories.values()):
            if subdirectory["name"] == directory_name:
                return subdirectory
        raise SteamfitterDirectoryError(f"Directory {directory_name} not found.")

    def __get_subdirectory_by_class(
        self, directory_class: Type[DirectoryType]
    ) -> DirectoryType:
        """Return the directory of the given class in the current directory."""
        directory_type = directory_class.directory_type()
        directory = self._subdirectories[directory_type]
        assert len(directory) == 1
        return directory[0]
