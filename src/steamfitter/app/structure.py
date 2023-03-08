import datetime
from pathlib import Path

from git import Repo

from steamfitter.lib.filesystem import templates
from steamfitter.lib.filesystem.archive import ARCHIVE_POLICIES
from steamfitter.lib.filesystem.directory import Directory


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

    NAME_TEMPLATE = "{source_count:>06}-{source_name}"

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

    @classmethod
    def add_initial_content(cls, path: Path, **kwargs):
        source_name = kwargs["source_name"]
        extraction_template_path = path / "extraction_template.py"

        extraction_template_path.touch(mode=0o664)
        with open(extraction_template_path, "w") as f:
            f.write(templates.EXTRACTION.format(source_name=source_name))


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

    def add_source(self, source_name: str, description: str):
        """Add a source to the extracted data directory."""

        source_count = self["source_count"] + 1
        source_dir = ExtractionSourceDirectory.create(
            root=self.path,
            parent=self,
            source_count=source_count,
            source_name=source_name,
            description=description,
        )
        self.update(
            source_count=source_count,
            sources=self["sources"] + [source_dir["name"]],
        )


    @classmethod
    def add_initial_content(cls, path: Path, **kwargs):
        repo = Repo.init(path)
        gitignore_path = path / ".gitignore"
        gitignore_path.touch(mode=0o664)
        with open(gitignore_path, "w") as f:
            f.write(templates.GITIGNORE)

        repo.index.add([str(gitignore_path)])
        repo.index.commit("Initial commit.")


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

    @property
    def extracted_data_directory(self) -> ExtractedDataDirectory:
        if not hasattr(self, "_extracted_data_directory"):
            self._extracted_data_directory = self.get_solo_directory_by_class(ExtractedDataDirectory)
        return self._extracted_data_directory

    @property
    def processed_data_directory(self) -> ProcessedDataDirectory:
        if not hasattr(self, "_processed_data_directory"):
            self._processed_data_directory = self.get_solo_directory_by_class(ProcessedDataDirectory)
        return self._processed_data_directory

    @property
    def data_diagnostics_directory(self) -> DataDiagnosticsDirectory:
        if not hasattr(self, "_data_diagnostics_directory"):
            self._data_diagnostics_directory = self.get_solo_directory_by_class(DataDiagnosticsDirectory)
        return self._data_diagnostics_directory


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

    @property
    def data_directory(self) -> DataDirectory:
        if not hasattr(self, "_data_directory"):
            self._data_directory = self.get_solo_directory_by_class(DataDirectory)
        return self._data_directory

    @property
    def modeling_directory(self) -> ModelingDirectory:
        if not hasattr(self, "_modeling_directory"):
            self._modeling_directory = self.get_solo_directory_by_class(ModelingDirectory)
        return self._modeling_directory


class ProjectDirectory(Directory):
    IS_INITIAL_DIRECTORY = True

    SUBDIRECTORY_TYPES = (
        # ArchiveDirectory,
        DataDirectory,
        ModelingDirectory,
    )

    @classmethod
    def add_subdirectory_creation_args(cls, metadata_kwargs, inherited_kwargs):
        inherited_kwargs["project_name"] = metadata_kwargs["name"]
        return inherited_kwargs

    @property
    def data_directory(self) -> DataDirectory:
        if not hasattr(self, "_data_directory"):
            self._data_directory = self.get_solo_directory_by_class(DataDirectory)
        return self._data_directory

    @property
    def modeling_directory(self) -> ModelingDirectory:
        if not hasattr(self, "_modeling_directory"):
            self._modeling_directory = self.get_solo_directory_by_class(ModelingDirectory)
        return self._modeling_directory

