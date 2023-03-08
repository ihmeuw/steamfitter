"""
=============
Configuration
=============

This module contains the :class:`Configuration` class, which is used to represent
the user configuration of steamfitter. The configuration is stored in a YAML file in the
user's home directory.

"""
from pathlib import Path
import shutil

from steamfitter.lib.exceptions import SteamfitterException
from steamfitter.lib.io import yaml as io


class SteamfitterConfigurationError(SteamfitterException):
    """An exception raised when there is an error with the configuration."""
    pass


class Configuration:

    _path = Path.home() / ".config" / "steamfitter" / "steamfitter.conf"

    def __init__(self):
        self._config = io.load(self._path)
        self._previous_default_project = None

    @property
    def projects_root(self) -> Path:
        return Path(self._config["projects_root"])

    @property
    def projects(self) -> list:
        return self._config["projects"].copy()

    @property
    def default_project(self) -> str:
        return self._config["default_project"]

    def remove(self):
        """Remove the configuration file from disk."""
        shutil.rmtree(self._path.parent)

    @classmethod
    def create(cls, projects_root: str) -> "Configuration":
        """Create a new configuration on disk and return this object representation of it."""

        config = {
            "projects_root": projects_root,
            "projects": [],
            "default_project": "",
        }
        cls._path.parent.mkdir(parents=True, exist_ok=True)
        io.dump(cls._path, config, exist_ok=True)
        return cls()

    @classmethod
    def exists(cls) -> bool:
        """Check if the configuration file exists."""
        return cls._path.exists()

    @property
    def path(self) -> Path:
        return self._path

    def add_project(self, project_name: str, set_default: bool) -> None:
        """Add a project to the configuration."""
        if project_name in self._config["projects"]:
            raise SteamfitterConfigurationError(
                f"Project {project_name} already exists."
            )

        self._config["projects"].append(project_name)
        if set_default:
            self._previous_default_project = self._config["default_project"]
            self._config["default_project"] = project_name

        io.dump(self._path, self._config, exist_ok=True)

    def remove_project(self, project_name: str, new_default: str = "") -> None:
        """Remove a project from the configuration."""
        if project_name not in self._config["projects"]:
            raise SteamfitterConfigurationError(
                f"Project {project_name} does not exist in the configuration."
            )

        self._config["projects"].remove(project_name)
        if self._config["default_project"] == project_name:
            self._config["default_project"] = new_default

        io.dump(self._path, self._config, exist_ok=True)

    def rollback_add_project(self, project_name: str) -> None:
        """Rollback the addition of a project to the configuration."""
        self.remove_project(project_name, new_default=self._previous_default_project)
