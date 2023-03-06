from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, Set, Tuple, Type
import shutil

import inflection

from steamfitter.exceptions import SteamfitterException
from steamfitter.app.filesystem.archive import ARCHIVE_POLICIES
from steamfitter.app.filesystem.metadata import Metadata
from steamfitter.shell_tools import mkdir


DEFAULT_VALUE_FACTORY = Callable[[], Any]


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

    def __init__(self, path: Path, parent: Directory = None):
        self._parent = parent
        self._metadata = Metadata(path)

    @property
    def path(self) -> Path:
        return self._metadata["root"]

    @property
    def metadata(self) -> dict:
        return self._metadata.as_dict()

    def __getitem__(self, item):
        """Return the value of a directory property."""
        return self._metadata[item]

    def __getattr__(self, key: str):
        """Return the value of a directory property."""
        if key in self._metadata:
            return self._metadata[key]
        raise AttributeError(f"{self.metadata_type} metadata has no attribute {key}.")

    ##############################
    # On-disk directory creation #
    ##############################

    @classmethod
    def create(
        cls,
        root: Path,
        parent: Directory = None,
        exists_ok: bool = False,
        **kwargs,
    ) -> Directory:
        """Create a new directory."""
        name = cls.make_name(root=root, **kwargs)
        path = root / name

        metadata_args = {
            "root": path,
            "name": name,
            "description": cls.make_description(**kwargs),
            "directory_type": cls.make_directory_type(),
            "directory_class": f"{cls.__module__}.{cls.__name__}",
            "archive_policy": kwargs.get("archive_policy", cls.DEFAULT_ARCHIVE_POLICY),
        }
        extra_fields = cls.make_extra_metadata_fields(metadata_args, **kwargs)
        metadata_args.update(extra_fields)

        mkdir(path, exists_ok=exists_ok)

        Metadata.create(**metadata_args)

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
    def remove(cls, root: Path, safe=True, **kwargs):
        """Rollback the creation of a directory."""
        if safe:
            instance = cls(root, **kwargs)
            managed = instance["directory_type"] == cls.make_directory_type()
            if not managed:
                raise SteamfitterDirectoryError(
                    f"Cannot remove {str(root)} because it is not managed by steamfitter."
                )
        name = cls.make_name(root=root, **kwargs)
        path = root / name
        shutil.rmtree(path, ignore_errors=True)

    @classmethod
    def add_subdirectory_creation_args(cls, metadata_kwargs, inherited_kwargs):
        """Add kwargs to be used in name and description templates for child directories."""
        return inherited_kwargs

    @classmethod
    def make_directory_type(cls) -> str:
        return inflection.underscore(cls.__name__.split("Metadata")[0])

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
