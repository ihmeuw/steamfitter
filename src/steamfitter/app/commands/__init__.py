from typing import (
    Callable as _Callable,
    NamedTuple as _NamedTuple
)

from steamfitter.app.commands.config import (
    create as _create_config,
    list as _list_config,
    update as _update_config,
)
from steamfitter.app.commands.project import (
    add as _add_project,
    list as _list_project,
    remove as _remove_project,
)
from steamfitter.app.commands.source import (
    add as _add_source,
    list as _list_source,
    remove as _remove_source,
)
from steamfitter.app.commands.source_column import (
    add as _add_source_column,
    list as _list_source_column,
    remove as _remove_source_column,
)
from steamfitter.app.commands import self_destruct as _self_destruct


class SteamfitterCommand(_NamedTuple):
    """Command wrapper for steamfitter commands.

    This is a wrapper for the commands in the steamfitter app. It is used to
    provide a consistent interface for the CLI and the API.

    Attributes
    ----------
    runner
        The function that runs the command. This is the function that is called
        when the command is run from the CLI, but skips the cli interface (i.e.
        argument parsing, error handling, logging, etc.). This function should check all
        preconditions and raise an exception if any are not met and do so before any
        side effects are applied.
    unrunner
        The function that undoes the command. This function is for testing, but is not
        exposed to users through the steamfitter CLI. This function assumes the runner
        has been executed without error and accepts as arguments exactly the return values
        for the runner.
    cli
        The function that runs the command from the CLI. This function is the click entry
        point for the command. It is responsible for parsing arguments, handling errors,
        and logging.

    """

    runner: _Callable
    unrunner: _Callable
    cli: _Callable

    @classmethod
    def from_module(cls, module):
        """Create a command from a module."""
        return cls(
            runner=module.run,
            unrunner=module.unrun,
            cli=module.main,
        )


create_config = SteamfitterCommand.from_module(_create_config)
list_config = SteamfitterCommand.from_module(_list_config)
update_config = SteamfitterCommand.from_module(_update_config)
add_project = SteamfitterCommand.from_module(_add_project)
list_project = SteamfitterCommand.from_module(_list_project)
remove_project = SteamfitterCommand.from_module(_remove_project)
add_source = SteamfitterCommand.from_module(_add_source)
list_source = SteamfitterCommand.from_module(_list_source)
remove_source = SteamfitterCommand.from_module(_remove_source)
add_source_column = SteamfitterCommand.from_module(_add_source_column)
list_source_column = SteamfitterCommand.from_module(_list_source_column)
remove_source_column = SteamfitterCommand.from_module(_remove_source_column)
self_destruct = SteamfitterCommand.from_module(_self_destruct)
