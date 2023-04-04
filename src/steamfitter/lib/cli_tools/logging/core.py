"""
=================
Logging Utilities
=================

This module contains utilities for configuring logging.

"""
import logging
import sys
from pathlib import Path

from loguru import logger

from steamfitter.lib.cli_tools.logging.jobmon import intercept_jobmon_logs

LOG_MESSAGING_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<cyan>{name}</cyan>:<cyan>{line}</cyan> "
    "- <level>{message}</level>"
)


def configure_logging_to_terminal(verbosity: int) -> None:
    """Configure logging to print to the sys.stdout."""
    _clear_default_configuration()
    _add_logging_sink(
        sink=sys.stdout,
        verbosity=verbosity,
        colorize=True,
        serialize=False,
    )


def configure_logging_to_file(log_file: Path) -> None:
    """Configure logging to write to a file in the provided file.

    Parameters
    ----------
    log_file
        The file to log to.

    """
    _add_logging_sink(
        log_file,
        verbosity=1,
        colorize=False,
        serialize=False,
    )


def _clear_default_configuration():
    try:
        logger.remove(0)  # Clear default configuration
    except ValueError:
        pass


def _add_logging_sink(
    sink,
    verbosity: int,
    colorize: bool,
    serialize: bool,
) -> int:
    """Add a logging sink to the logger.

    Parameters
    ----------
    sink
        The sink to add.  Can be a file path, a file object, or a callable.
    verbosity
        The verbosity level.
    colorize
        Whether to colorize the log messages.
    serialize
        Whether to as_dict log messages.  This is useful when logging to
        a file or a database.

    """
    logging_level = _get_log_level(verbosity)
    intercept_jobmon_logs(logging_level)
    return logger.add(
        sink,
        colorize=colorize,
        level=logging_level,
        format=LOG_MESSAGING_FORMAT,
        serialize=serialize,
        filter={
            # Suppress logs up to the level provided.
            "urllib3": "WARNING",  # Uselessly (for us) noisy.
        },
    )


def _get_log_level(verbosity: int):
    if verbosity == 0:
        return "WARNING"
    elif verbosity == 1:
        return "INFO"
    elif verbosity >= 2:
        return "DEBUG"
    else:
        raise NotImplementedError


def list_loggers():
    """Utility function for analyzing the logging environment."""
    root_logger = logging.getLogger()
    print("Root logger: ", root_logger)
    for h in root_logger.handlers:
        print(f"     %s" % h)

    print("Other loggers")
    print("=============")
    for name, logger_ in logging.Logger.manager.loggerDict.items():
        print("+ [%-20s] %s " % (name, logger_))
        if not isinstance(logger_, logging.PlaceHolder):
            handlers = list(logger_.handlers)
            if not handlers:
                print("     No handlers")
            for h in logger_.handlers:
                print("     %s" % h)
