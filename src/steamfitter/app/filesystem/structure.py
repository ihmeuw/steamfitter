import datetime
from pathlib import Path


from steamfitter.app.filesystem.archive import ARCHIVE_POLICIES
from steamfitter.app.filesystem.directory import Directory


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


class ExtractionSourceDirectory(Directory):

    DEFAULT_ARCHIVE_POLICY = ARCHIVE_POLICIES.archive

    NAME_TEMPLATE = "{source_count:>06}_{source_name}"

    DEFAULT_EMPTY_ARGS = {
        ("last_updated", lambda: ""),
        ("latest_version", lambda: ""),
        ("best_version", lambda: ""),
    }

    SUBDIRECTORY_TYPES = (
        VersionDirectory,
    )

    @classmethod
    def make_name(cls, root: Path, **kwargs) -> str:
        if "source_count" not in kwargs:
            raise ValueError("Must provide a source count.")
        if "source_name" not in kwargs:
            raise ValueError("Must provide a source name.")
        return cls.NAME_TEMPLATE.format(**kwargs)


class ExtractedDataDirectory(Directory):

    IS_INITIAL_DIRECTORY = True

    NAME_TEMPLATE = "extracted_data"
    DESCRIPTION_TEMPLATE = "Extracted data for the {project_name} project."

    DEFAULT_EMPTY_ARGS = {
        ("source_count", lambda: 0),
        ("sources", lambda: []),
    }

    SUBDIRECTORY_TYPES = (
        ExtractionSourceDirectory,
    )


class ProcessedMeasureDirectory(Directory):

    DEFAULT_ARCHIVE_POLICY = ARCHIVE_POLICIES.archive

    DEFAULT_EMPTY_ARGS = {
        ("last_updated", lambda: ""),
        ("latest_version", lambda: ""),
        ("best_version", lambda: ""),
    }

    SUBDIRECTORY_TYPES = (
        VersionDirectory,
    )


class ProcessedDataDirectory(Directory):
    IS_INITIAL_DIRECTORY = True

    NAME_TEMPLATE = "processed_data"
    DESCRIPTION_TEMPLATE = "Processed measure data for the {project_name} project."

    DEFAULT_EMPTY_ARGS = {
        ("measure_count", lambda: 0),
        ("measures", lambda: []),
    }

    SUBDIRECTORY_TYPES = (
        ProcessedMeasureDirectory,
    )


class DataDiagnosticsDirectory(Directory):
    IS_INITIAL_DIRECTORY = True
    DEFAULT_ARCHIVE_POLICY = ARCHIVE_POLICIES.delete

    NAME_TEMPLATE = "data_diagnostics"
    DESCRIPTION_TEMPLATE = "Data diagnostics for the {project_name} project."

    SUBDIRECTORY_TYPES = (
        VersionDirectory,
    )


class DataDirectory(Directory):
    IS_INITIAL_DIRECTORY = True

    NAME_TEMPLATE = "data"
    DESCRIPTION_TEMPLATE = "Data for the {project_name} project."

    SUBDIRECTORY_TYPES = (
        ExtractedDataDirectory,
        ProcessedDataDirectory,
        DataDiagnosticsDirectory,
    )


class ModelingStageDirectory(Directory):
    DEFAULT_ARCHIVE_POLICY = ARCHIVE_POLICIES.archive

    DEFAULT_EMPTY_ARGS = {
        ("last_updated", lambda: ""),
        ("latest_version", lambda: ""),
        ("best_version", lambda: ""),
    }

    SUBDIRECTORY_TYPES = (
        VersionDirectory,
    )


class ModelingDirectory(Directory):
    IS_INITIAL_DIRECTORY = True

    NAME_TEMPLATE = "modeling"
    DESCRIPTION_TEMPLATE = "Outputs from the modeling pipeline for the {project_name} project."

    DEFAULT_EMPTY_ARGS = {
        ("pipeline_stages", lambda: []),
    }

    SUBDIRECTORY_TYPES = (
        ModelingStageDirectory,
    )


class DeliverablesDirectory(Directory):
    IS_INITIAL_DIRECTORY = True

    NAME_TEMPLATE = "deliverables"
    DESCRIPTION_TEMPLATE = "Deliverables for the {project_name} project."

    SUBDIRECTORY_TYPES = ()


class ArchiveDirectory(Directory):
    IS_INITIAL_DIRECTORY = True

    NAME_TEMPLATE = "archive"
    DESCRIPTION_TEMPLATE = "Archived data for the {project_name} project."

    DEFAULT_EMPTY_ARGS = {
        ("archived_file_count", lambda: 0),
        ("archived_data_size", lambda: "0 GB"),
    }

    SUBDIRECTORY_TYPES = (
        DataDirectory,
        ModelingDirectory,
    )


class ProjectDirectory(Directory):
    IS_INITIAL_DIRECTORY = True

    SUBDIRECTORY_TYPES = (
#        ArchiveDirectory,
        DataDirectory,
        ModelingDirectory,
    )

    @classmethod
    def add_subdirectory_creation_args(cls, metadata_kwargs, inherited_kwargs):
        inherited_kwargs["project_name"] = metadata_kwargs["name"]
        return inherited_kwargs

