from typing import Callable, List, Union

import click
from click.testing import CliRunner, Result


def invoke_cli(
    command: Union[click.Command, Callable],
    args: List[str] = None,
    input: str = None,
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
    input
        The input to pass to the command.
    exit_zero
        Whether to assert that the command exited with a zero exit code.

    Returns
    -------
    Result
        The result of the command invocation.

    """
    runner = CliRunner()
    result = runner.invoke(command, args=args, input=input)
    if exit_zero:
        assert result.exit_code == 0, result.output
    else:
        assert result.exit_code != 0, result.output
    return result
