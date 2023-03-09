"""
========================
Processed Data Directory
========================

A processed data directory is a project subdirectory for storing processed data. It is a
subdirectory of the data directory. It contains a subdirectory for each "measure" that has
been processed where a measure is a domain-specific term for a type of data. For example,
in a project that processes data from a hospital, a measure might be "daily admissions".

"""
from steamfitter.lib.filesystem import Directory, ARCHIVE_POLICIES
from steamfitter.app.directory_structure.version import VersionDirectory


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
