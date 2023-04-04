from typing import Callable as _Callable
from typing import NamedTuple as _NamedTuple

from steamfitter.app.commands import self_destruct as _self_destruct
from steamfitter.app.commands.config import create as _create_config
from steamfitter.app.commands.config import list as _list_config
from steamfitter.app.commands.config import update as _update_config
from steamfitter.app.commands.project import add as _add_project
from steamfitter.app.commands.project import list as _list_project
from steamfitter.app.commands.project import remove as _remove_project
from steamfitter.app.commands.source import add as _add_source
from steamfitter.app.commands.source import extract as _extract_source
from steamfitter.app.commands.source import list as _list_source
from steamfitter.app.commands.source import remove as _remove_source


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
extract_source = SteamfitterCommand.from_module(_extract_source)
list_source = SteamfitterCommand.from_module(_list_source)
remove_source = SteamfitterCommand.from_module(_remove_source)
self_destruct = SteamfitterCommand.from_module(_self_destruct)
