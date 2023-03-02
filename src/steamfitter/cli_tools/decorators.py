import functools
import types
from pathlib import Path

import click

from steamfitter.cli_tools.metadata import Metadata, get_function_full_argument_mapping

add_verbose = click.option(
    "-v",
    "verbose",
    count=True,
    help="Configure logging verbosity.",
)
add_with_debugger = click.option(
    "--pdb",
    "with_debugger",
    is_flag=True,
    help="Drop into python debugger if an error occurs.",
)


def add_verbose_and_with_debugger(func: types.FunctionType):
    """Add both verbose and with debugger options."""
    func = add_verbose(func)
    func = add_with_debugger(func)
    return func


with_production_tag = click.option(
    "-p",
    "--production-tag",
    type=click.STRING,
    help="Tags this run as a production run.",
)
with_mark_best = click.option(
    "-b",
    "--mark-best",
    is_flag=True,
    help='Mark this run as "best"',
)


def with_output_root(default_output_root: Path):
    """Adds output root option with a default."""

    def wrapper(entry_point: types.FunctionType):
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

    def wrapper(entry_point: types.FunctionType):
        entry_point = with_output_root(default_output_root)(entry_point)
        entry_point = with_production_tag(entry_point)
        entry_point = with_mark_best(entry_point)
        return entry_point

    return wrapper


def pass_run_metadata(app_entry_point: types.FunctionType):
    run_metadata = Metadata(app_entry_point.__name__)

    @functools.wraps(app_entry_point)
    def _wrapped(*args, **kwargs):
        # Record arguments for the run and inject the metadata.
        run_metadata["tool_name"] = f"{app_entry_point.__module__}:{app_entry_point.__name__}"

        run_metadata["run_arguments"] = get_function_full_argument_mapping(
            app_entry_point, run_metadata, *args, **kwargs
        )
        return app_entry_point(run_metadata, *args, **kwargs)

    return _wrapped
