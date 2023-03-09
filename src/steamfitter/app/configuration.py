"""
=============
Configuration
=============

This module contains the :class:`Configuration` class, which is used to represent
the user configuration of steamfitter. The configuration is stored in a YAML file in the
user's home directory.

"""
import shutil
from pathlib import Path
from typing import Union

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

    @projects_root.setter
    def projects_root(self, projects_root: Union[str, Path]):
        self._config["projects_root"] = str(projects_root)
        self.persist()

    @property
    def projects(self) -> dict:
        return self._config["projects"].copy()

    @projects.setter
    def projects(self, projects: list):
        self._config["projects"] = projects
        self.persist()

    @property
    def default_project(self) -> str:
        return self._config["default_project"]

    @default_project.setter
    def default_project(self, default_project: str):
        self._previous_default_project = self._config["default_project"]
        self._config["default_project"] = default_project
        self.persist()

    def remove(self):
        """Remove the configuration file from disk."""
        shutil.rmtree(self._path.parent)

    @classmethod
    def create(cls, projects_root: str) -> "Configuration":
        """Create a new configuration on disk and return this object representation of it."""

        config = {
            "projects_root": projects_root,
            "projects": {},
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
            raise SteamfitterConfigurationError(f"Project {project_name} already exists.")

        self._config["projects"].append(project_name)
        if set_default:
            self._config["default_project"] = project_name

        self.persist()

    def remove_project(self, project_name: str, new_default: str = "") -> None:
        """Remove a project from the configuration."""
        if project_name not in self._config["projects"].values():
            raise SteamfitterConfigurationError(
                f"Project {project_name} does not exist in the configuration."
            )
        project_number = {v: k for k, v in self._config["projects"].items()}[project_name]

        self._config["projects"].remove(project_number)
        if self._config["default_project"] == project_name:
            self._config["default_project"] = new_default

        self.persist()

    def persist(self):
        """Save the configuration to disk."""
        io.dump(self._path, self._config, exist_ok=True)

    def __repr__(self):
        config_list = [f"{k}={v}" for k, v in self._config.items()]
        return f"Configuration(', '.join({config_list}))"

    def __new__(cls):
        """The configuration is a singleton.

        This, along with the persistence calls in all state modification methods, ensures
        that the in memory configuration and the on-disk configuration are always in sync.

        """
        if not hasattr(cls, "_instance"):
            cls._instance = super(Configuration, cls).__new__(cls)
        return cls._instance
