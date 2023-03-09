"""
==================
Modeling Directory
==================

A modeling directory is a project subdirectory for storing model results. Models are the
intermediate products of a project, such as a data pipeline, a machine learning model,
or a statistical model. The modeling directory contains subdirectories for each stage of
the modeling pipeline. Each modeling stage subdirectory contains model results from a
particular stage of the modeling pipeline. For example, a modeling stage might contain
versions of the results of a data cleaning step, a feature engineering step, or a
machine learning model.

"""
from steamfitter.app.directory_structure.version import VersionDirectory
from steamfitter.lib.filesystem import ARCHIVE_POLICIES, Directory


class ModelingStageDirectory(Directory):
    DEFAULT_ARCHIVE_POLICY = ARCHIVE_POLICIES.archive

    DEFAULT_EMPTY_ARGS = {
        ("last_updated", lambda: ""),
        ("latest_version", lambda: ""),
        ("best_version", lambda: ""),
    }

    SUBDIRECTORY_TYPES = (VersionDirectory,)


class ModelingDirectory(Directory):
    IS_INITIAL_DIRECTORY = True

    NAME_TEMPLATE = "modeling"
    DESCRIPTION_TEMPLATE = (
        "Outputs from the modeling pipeline for the {project_name} project."
    )

    DEFAULT_EMPTY_ARGS = {
        ("pipeline_stages", lambda: []),
    }

    SUBDIRECTORY_TYPES = (ModelingStageDirectory,)
