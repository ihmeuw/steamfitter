"""
==========================
Data Diagnostics Directory
==========================

A data diagnostics directory is a project subdirectory for storing data diagnostics such as
data quality reports, data dictionaries, and plotting outputs.

"""
from steamfitter.app.directory_structure.version import VersionDirectory
from steamfitter.lib.filesystem import ARCHIVE_POLICIES, Directory


class DiagnosticDirectory(Directory):
    DEFAULT_ARCHIVE_POLICY = ARCHIVE_POLICIES.archive

    DEFAULT_EMPTY_ARGS = {
        ("last_updated", lambda: ""),
        ("latest_version", lambda: ""),
        ("best_version", lambda: ""),
    }

    SUBDIRECTORY_TYPES = (VersionDirectory,)


class DataDiagnosticsDirectory(Directory):
    IS_INITIAL_DIRECTORY = True
    DEFAULT_ARCHIVE_POLICY = ARCHIVE_POLICIES.delete

    NAME_TEMPLATE = "data-diagnostics"
    DESCRIPTION_TEMPLATE = "Data diagnostics for the {project_name} project."

    SUBDIRECTORY_TYPES = (DiagnosticDirectory,)
