"""
=================
Archive Directory
=================

An archive directory is a project subdirectory for storing archived data and models.

"""
from steamfitter.lib.filesystem import Directory


class ArchiveDirectory(Directory):
    IS_INITIAL_DIRECTORY = True

    NAME_TEMPLATE = "archive"
    DESCRIPTION_TEMPLATE = "Archived data for the {project_name} project."

    DEFAULT_EMPTY_ARGS = {
        ("archived_file_count", lambda: 0),
        ("archived_data_size", lambda: "0 GB"),
    }

