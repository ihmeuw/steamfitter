import functools
from pathlib import Path
from typing import Callable, TypeVar, ParamSpec

import click

from steamfitter.lib.filesystem.metadata import RunMetadata
from steamfitter.lib.cli_tools.monitoring import get_function_full_argument_mapping


T = TypeVar('T')
P = ParamSpec('P')

verbose = click.option(
    "-v",
    "verbose",
    count=True,
    help="Logging level.",
)
with_debugger = click.option(
    "--pdb",
    "with_debugger",
    is_flag=True,
    help="Drop into python debugger if an error occurs.",
)


def verbose_and_with_debugger(func: Callable[P, T]) -> Callable[P, T]:
    """Add verbose and with_debugger options."""
    func = verbose(func)
    func = with_debugger(func)
    return func


with_mark_best = click.option(
    "-b",
    "--mark-best",
    is_flag=True,
    help='Mark this run as "best"',
)


def with_output_root(default_output_root: Path) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Adds output root option with a default."""

    def wrapper(entry_point: Callable[P, T]) -> Callable[P, T]:
        entry_point = click.option(
            "-o",
            "--output-root",
            type=click.Path(file_okay=False),
            default=default_output_root,
            help=(
                f"Directory to outputs. Defaults to {default_output_root}/YYYY_MM_DD.VV "
                f"for today's date and the newest uncreated version."
            ),
        )(entry_point)
        return entry_point

    return wrapper


def add_output_options(default_output_root: Path):
    """Decorator to set CLI command options required when producing outputs."""

    def wrapper(entry_point: Callable[P, T]) -> Callable[P, T]:
        entry_point = with_output_root(default_output_root)(entry_point)
        entry_point = with_mark_best(entry_point)
        return entry_point

    return wrapper


def pass_run_metadata(app_entry_point: Callable[P, T]) -> Callable[P, T]:
    run_metadata = RunMetadata(application_name=app_entry_point.__name__)

    @functools.wraps(app_entry_point)
    def _wrapped(*args, **kwargs):
        # Record arguments for the run and inject the metadata.
        module = getattr(app_entry_point, "__module__", "")
        run_metadata["cli_tool_name"] = f"{module}:{app_entry_point.__name__}"

        run_metadata["run_arguments"] = get_function_full_argument_mapping(
            app_entry_point, run_metadata, *args, **kwargs
        )
        return app_entry_point(run_metadata, *args, **kwargs)

    return _wrapped
