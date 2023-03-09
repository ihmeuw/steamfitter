import click

from steamfitter.app.configuration import Configuration

from steamfitter.lib.exceptions import SteamfitterException


class SteamfitterCLIException(SteamfitterException, click.Abort):
    """Base class for exceptions in the Steamfitter CLI."""
    message: str = None

    def __init__(self, *args, **kwargs):
        self.message = self.message.format(*args, **kwargs)


class ConfigurationExistsError(SteamfitterCLIException):
    message = "Configuration file already exists."


class ConfigurationDoesNotExistError(SteamfitterCLIException):
    message = "Configuration file does not exist. Run `steamfitter configure` first."


class NoConfigurationUpdateError(SteamfitterCLIException):
    message = (
        "No configuration update provided. "
        "Must provide at least one of --projects-root or --default-project-name"
    )


class ProjectExistsError(SteamfitterCLIException):
    message = "Project {project_name} already exists."


class ProjectDoesNotExistError(SteamfitterCLIException):
    message = "Project {project_name} does not exist."


class NoDefaultProjectError(SteamfitterCLIException):
    message = "No project provided and no default project set."


class NoProjectsExistError(SteamfitterCLIException):
    message = "No projects exist."


class SourceExistsError(SteamfitterCLIException):
    message = "Source {source_name} already exists in project {project_name}."


class SourceDoesNotExistError(SteamfitterCLIException):
    message = "Source {source_name} does not exist in project {project_name}."


class NoSourcesExistError(SteamfitterCLIException):
    message = "No sources exist in project {project_name}."


class SourceColumnExistsError(SteamfitterCLIException):
    message = "Source column {source_column_name} already exists in project {project_name}."


class SourceColumnDoesNotExistError(SteamfitterCLIException):
    message = "Source column {source_column_name} does not exist in project {project_name}."


class NoSourceColumnsExistError(SteamfitterCLIException):
    message = "No source columns exist in project {project_name}."

