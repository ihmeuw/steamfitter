from typing import List

import click
from click.testing import Result, CliRunner


def invoke_cli(
    command: click.Command,
    args: List[str] = None,
    exit_zero: bool = True,
) -> Result:
    """Invoke a click command.

    This is a convenience function for invoking a click command and providing
    a useful error in the pytest output.

    Parameters
    ----------
    command
        The command to invoke.
    args
        The arguments to pass to the command.
    exit_zero
        Whether to assert that the command exited with a zero exit code.

    Returns
    -------
    Result
        The result of the command invocation.

    """
    runner = CliRunner()
    result = runner.invoke(command, args)
    if exit_zero:
        assert result.exit_code == 0, result.output
    else:
        assert result.exit_code != 0, result.output
    return result
