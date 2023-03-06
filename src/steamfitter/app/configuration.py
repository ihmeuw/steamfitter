from pathlib import Path

import yaml


class ConfigurationError(Exception):
    """An exception raised when there is an error with the configuration."""
    pass


class Configuration:

    _path = Path.home() / ".config" / "steamfitter" / "steamfitter.conf"

    def __init__(self):
        self._config = self._load()
        self._previous_default_project = None

    @property
    def projects_root(self) -> Path:
        return Path(self._config["projects_root"])

    @classmethod
    def create(cls, projects_root: str) -> "Configuration":
        """Create a new configuration on disk and return this object representation of it."""

        config = {
            "projects_root": projects_root,
            "projects": [],
            "default_project": "",
        }
        cls._dump(config)
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
            raise ConfigurationError(
                f"Project {project_name} already exists in the configuration."
            )

        self._config["projects"].append(project_name)
        if set_default:
            self._previous_default_project = self._config["default_project"]
            self._config["default_project"] = project_name

        self._dump(self._config)

    def remove_project(self, project_name: str, new_default: str = "") -> None:
        """Remove a project from the configuration."""
        if project_name not in self._config["projects"]:
            raise ConfigurationError(
                f"Project {project_name} does not exist in the configuration."
            )

        self._config["projects"].remove(project_name)
        if self._config["default_project"] == project_name:
            self._config["default_project"] = new_default

        self._dump(self._config)

    def rollback_add_project(self, project_name: str) -> None:
        """Rollback the addition of a project to the configuration."""
        self.remove_project(project_name, new_default=self._previous_default_project)

    @classmethod
    def _load(cls) -> dict:
        if not cls._path.exists():
            raise ConfigurationError(f"Configuration file {cls._path} does not exist.")
        with cls._path.open() as f:
            config = yaml.full_load(f)
        return config

    @classmethod
    def _dump(cls, config) -> None:
        cls._path.parent.mkdir(parents=True, exist_ok=True)
        with cls._path.open("w") as f:
            yaml.dump(config, f)

