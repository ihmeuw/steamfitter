"""
==========
Monitoring
==========

This module contains functions for monitoring the status of a running CLI application.

"""
from bdb import BdbQuit
import functools
import pdb
from typing import Callable, Dict, ParamSpec, Tuple, TypeVar

import click

from steamfitter.lib.cli_tools.logging import logger
from steamfitter.lib.filesystem.metadata import RunMetadata


T = TypeVar('T')
P = ParamSpec('P')


def handle_exceptions(
    application_main: Callable[P, T],
    logger_: type(logger),
    with_debugger: bool,
) -> Callable[P, T]:
    """Wraps a function so that it drops a user into a debugger if it raises an error.

    This is intended to be used as a wrapper for the main function of a CLI application.
    It will catch all errors and drop a user into a debugger if the error is not a
    KeyboardInterrupt. If the error is a KeyboardInterrupt, it will raise the error.
    If the error is not a KeyboardInterrupt, it will log the error and drop a user into a
    debugger if with_debugger is True. If with_debugger is False, it will raise the error.

    Parameters
    ----------
    application_main
        The function to wrap.
    logger_
        The application logger.
    with_debugger
        Whether to drop a user into a debugger if an error is raised.

    Returns
    -------
    Callable
        The wrapped function.

    """
    @functools.wraps(application_main)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return application_main(*args, **kwargs)
        except (BdbQuit, KeyboardInterrupt, click.Abort):
            raise
        except Exception as e:
            msg = f"Uncaught exception {e}"
            logger_.exception(msg)
            if with_debugger:
                pdb.post_mortem()
            else:
                raise

    return wrapped


def monitor_application(
    application_main: Callable[P, T],
    logger_: type(logger),
    with_debugger: bool,
    metadata: RunMetadata = None,
) -> Callable:
    """Monitors an application for errors and injects a metadata container.

    Catches errors and records them if they occur. Can also be configured to drop
    a user into an interactive debugger on failure.

    Parameters
    ----------
    application_main
        The application function to monitor.
    logger_
        The application logger
    with_debugger
        Whether the monitor drops a user into a pdb session on application
        failure.
    metadata
        Record for application metadata.

    Returns
    -------
    Callable
        The wrapped application function.

    """
    if metadata is None:
        metadata = RunMetadata(
            application_name=application_main.__name__,
        )

    @functools.wraps(application_main)
    def _wrapped(*args: P.args, **kwargs: P.kwargs) -> Tuple[RunMetadata, T]:
        result = None
        try:
            # Record arguments for the run and inject the metadata
            module = getattr(application_main, "__module__", "")
            metadata["entry_point"] = f"{module}:{application_main.__name__}"
            metadata["run_arguments"] = get_function_full_argument_mapping(
                application_main, *args, **kwargs
            )
            result = application_main(*args, **kwargs)
            metadata["success"] = "True"
        except Exception as e:
            metadata["success"] = "False"
            metadata["error_info"] = {
                "exception_type": str(type(e)),
                "exception_value": str(e),
            }
            if not isinstance(e, (BdbQuit, KeyboardInterrupt, click.Abort)) and with_debugger:
                msg = f"Uncaught exception {e}"
                logger_.exception(msg)
                pdb.post_mortem()
        finally:
            return metadata, result

    return _wrapped


def get_function_full_argument_mapping(
    func: Callable[P, T],
    *args: P.args,
    **kwargs: P.kwargs,
) -> Dict[str, str]:
    """Get a dict representation of all args and kwargs for a function.

    Parameters
    ----------
    func
        The function to inspect.
    args
        The positional arguments to the function.
    kwargs
        The keyword arguments to the function.

    Returns
    -------
    Dict[str, str]
        A dict mapping the function's argument names to their string
        representations.

    """
    # Grab all variables in the enclosing namespace.  Args will be first.
    # Note: This may rely on the CPython implementation.  Not sure.
    func_code = getattr(func, "__code__", None)
    if not func_code:
        raise AttributeError("Function must have a __code__ attribute.")

    arg_names = func_code.co_varnames
    arg_vals = [str(arg) for arg in args]
    # Zip ignores extra items in the second arg.  Use that property to catch
    # all positional args and ignore kwargs.
    run_args = dict(zip(arg_names, arg_vals))
    run_args.update({str(k): str(v) for k, v in kwargs.items()})
    return run_args
