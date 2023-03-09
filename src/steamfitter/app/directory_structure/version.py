"""
=================
Version Directory
=================

A version directory is a project subdirectory for storing versioned data and models. It is
the terminal directory for most project subdirectories and is intended to provide a
consistent versioning scheme for all project subdirectories so provenance can be tracked
and data and models can be reproduced.

"""
import datetime
from pathlib import Path

from steamfitter.lib.filesystem import Directory


class VersionDirectory(Directory):
    NAME_TEMPLATE = "{launch_time}.{run_version:0>2}"
    DESCRIPTION_TEMPLATE = "Version {version} of {versionable_dir_name}."

    @classmethod
    def make_name(cls, root: Path, **kwargs) -> str:
        launch_time = datetime.datetime.now().strftime("%Y_%m_%d")
        today_runs = [
            int(run_dir.name.split(".")[1])
            for run_dir in root.iterdir()
            if run_dir.name.startswith(launch_time)
        ]
        run_version = max(today_runs) + 1 if today_runs else 1
        return cls.NAME_TEMPLATE.format(
            launch_time=launch_time,
            run_version=run_version,
        )
