import datetime
import functools
import sys
import time
import types
from bdb import BdbQuit
from pathlib import Path
from pprint import pformat
from typing import Any, Callable, Dict, Mapping, Union

import click
import yaml
from loguru import logger

from steamfitter import paths


class Metadata:
    """Silently records profiling and provenance information for an application."""

    def __init__(self, application_name: str):
        self._start = time.time()
        self.application_name = application_name
        self._metadata = {
            self.application_name: {
                "start_time": self._get_time(),
                "end_time": None,
                "run_time_seconds": None,
                "provenance": {},
            },
        }

    @staticmethod
    def _get_time():
        return datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

    def __getitem__(self, metadata_key: str) -> str:
        return self._metadata[self.application_name][metadata_key]

    def __setitem__(self, metadata_key: str, value: Union[str, Dict]) -> None:
        if not isinstance(value, (str, dict)):
            raise TypeError("Metadata values must be strings or dictionaries of strings.")
        self._metadata[self.application_name][metadata_key] = value

    def __contains__(self, metadata_key: str):
        return metadata_key in self._metadata[self.application_name]

    def to_dict(self):
        """Give back a dict version of the metadata."""
        return self._metadata[self.application_name].copy()

    def update(self, metadata_update: Mapping):
        """Dictionary style update of metadata."""
        # Inefficient, by centralizes error handling.
        for key, value in metadata_update.items():
            self[key] = value

    def record_prior_stage_provenance(self, prior_stage_metadata_file: Union[str, Path]):
        """Records provenance information from a prior stage."""
        metadata_path = Path(prior_stage_metadata_file)
        if not metadata_path.name == paths.METADATA_FILE_NAME.name:
            raise ValueError("Can only update from `metadata.yaml` files.")

        with metadata_path.open() as metadata_file:
            self._metadata[self.application_name]["provenance"].update(
                yaml.full_load(metadata_file)
            )

    def dump(self, metadata_file_path: Union[str, Path]):
        self["end_time"] = self._get_time()
        self._metadata["run_time_seconds"] = f"{time.time() - self._start:.4f}"

        try:
            with Path(metadata_file_path).open("w") as metadata_file:
                yaml.dump(self._metadata, metadata_file)
        except FileNotFoundError:
            logger.warning(
                f"Output directory for {metadata_file.name} does not exist. "
                f"Dumping metadata to console."
            )
            click.echo(pformat(self._metadata))


def monitor_application(
    func: types.FunctionType,
    logger_: Any,
    with_debugger: bool,
    app_metadata: Metadata,
) -> Callable:
    """Monitors an application for errors and injects a metadata container.

    Catches errors and records them if they occur. Can also be configured to drop
    a user into an interactive debugger on failure.

    Parameters
    ----------
    func
        The application function to monitor.
    logger_
        The application logger
    with_debugger
        Whether the monitor drops a user into a pdb session on application
        failure.
    app_metadata
        Record for application metadata.

    """

    @functools.wraps(func)
    def _wrapped(*args, **kwargs):
        result = None
        try:
            # Record arguments for the run and inject the metadata
            app_metadata["main_function"] = f"{func.__module__}:{func.__name__}"
            app_metadata["run_arguments"] = get_function_full_argument_mapping(
                func, app_metadata, *args, **kwargs
            )
            result = func(app_metadata, *args, **kwargs)
            app_metadata["success"] = "True"
        except (BdbQuit, KeyboardInterrupt):
            app_metadata["success"] = "False"
            app_metadata["error_info"] = {
                "exception_type": "User interrupt.",
                "exception_value": "User interrupted application.",
            }
        except Exception as e:
            # For general errors, write exception info to the metadata.
            app_metadata["success"] = "False"
            logger_.exception("Uncaught exception {}".format(e))
            exc_type, exc_value, exc_traceback = sys.exc_info()
            app_metadata["error_info"] = {
                "exception_type": str(exc_type),
                "exception_value": str(exc_value),
            }

            if with_debugger:
                import pdb

                pdb.post_mortem()
        finally:
            return app_metadata, result

    return _wrapped


def handle_exceptions(func: Callable, logger_: Any, with_debugger: bool) -> Callable:
    """Drops a user into an interactive debugger if func raises an error."""

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (BdbQuit, KeyboardInterrupt):
            raise
        except Exception as e:
            logger_.exception("Uncaught exception {}".format(e))
            if with_debugger:
                import pdb
                import traceback

                traceback.print_exc()
                pdb.post_mortem()
            else:
                raise

    return wrapped


def get_function_full_argument_mapping(
    func: types.FunctionType,
    *args,
    **kwargs,
) -> Dict[str, str]:
    """Get a dict representation of all args and kwargs for a function."""
    # Grab all variables in the enclosing namespace.  Args will be first.
    # Note: This may rely on the CPython implementation.  Not sure.
    arg_names = func.__code__.co_varnames
    arg_vals = [str(arg) for arg in args]
    # Zip ignores extra items in the second arg.  Use that property to catch
    # all positional args and ignore kwargs.
    run_args = dict(zip(arg_names, arg_vals))
    run_args.update({k: str(v) for k, v in kwargs.items()})
    return run_args
