import os
from typing import Callable, List, Union

import click
from click.testing import CliRunner, Result

from steamfitter.app.commands import SteamfitterCommand


def invoke_cli(
    command: Union[click.Command, Callable, SteamfitterCommand],
    args_: List[str] = None,
    input_: str = None,
    exit_zero: bool = True,
) -> Result:
    """Invoke a click command.

    This is a convenience function for invoking a click command and providing
    a useful error in the pytest output.

    Parameters
    ----------
    command
        The command to invoke.
    args_
        The arguments to pass to the command.
    input_
        The input to pass to the command.
    exit_zero
        Whether to assert that the command exited with a zero exit code.

    Returns
    -------
    Result
        The result of the command invocation.

    """
    if isinstance(command, SteamfitterCommand):
        command = command.cli

    runner = CliRunner()
    result = runner.invoke(command, args=args_, input=input_, standalone_mode=False)
    if exit_zero:
        assert result.exit_code == 0, result.output
    else:
        assert result.exit_code != 0, result.output
    return result


def list_files(startpath):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, "").count(os.sep)
        indent = " " * 4 * level
        print("{}{}/".format(indent, os.path.basename(root)))
        subindent = " " * 4 * (level + 1)
        for f in files:
            print("{}{}".format(subindent, f))
