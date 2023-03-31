"""
========================
Extracted Data Directory
========================

An extracted data directory is a project subdirectory for storing data extracted from
external sources.

"""
import shutil
from pathlib import Path

from steamfitter.app import git
from steamfitter.app.directory_structure.version import VersionDirectory
from steamfitter.lib.exceptions import SteamfitterException
from steamfitter.lib.filesystem import ARCHIVE_POLICIES, Directory, templates


class ExtractionSourceDirectory(Directory):
    DEFAULT_ARCHIVE_POLICY = ARCHIVE_POLICIES.archive

    NAME_TEMPLATE = "{source_count:>06}-{source_name}"

    DEFAULT_EMPTY_ARGS = {
        ("last_updated", lambda: ""),
        ("latest_version", lambda: ""),
        ("best_version", lambda: ""),
    }

    SUBDIRECTORY_TYPES = (VersionDirectory,)

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
        ("sources", lambda: {}),
        ("source_columns", lambda: {}),
    }

    SUBDIRECTORY_TYPES = (ExtractionSourceDirectory,)

    @property
    def sources(self):
        return self["sources"].copy()

    @property
    def source_columns(self):
        return self["source_columns"].copy()

    def add_source(self, source_name: str, description: str):
        """Add a source to the extracted data directory."""
        sources = self["sources"].copy()
        if source_name in sources:
            raise SteamfitterException(f"Source {source_name} already exists.")

        source_count = self["source_count"] + 1
        ExtractionSourceDirectory.create(
            root=self.path,
            parent=self,
            source_count=source_count,
            source_name=source_name,
            description=description,
        )
        self.update(
            {
                "source_count": source_count,
                "sources": {**sources, source_name: source_count},
            }
        )
        self._metadata.persist()

        git.add_and_commit(self.path, f"Added source {source_name}.")

    def remove_source(
        self, source_name: str, serialize: bool = False, destructive: bool = False
    ) -> dict:
        """Remove a source from the extracted data directory."""
        sources = self.sources
        if source_name not in sources:
            raise SteamfitterException(f"Source {source_name} does not exist.")

        source_count = sources.pop(source_name)
        source_path = self.path / ExtractionSourceDirectory.make_name(
            root=self.path,
            source_count=source_count,
            source_name=source_name,
        )
        if serialize:
            source_directory_dict = ExtractionSourceDirectory(source_path, self).serialize()
        else:
            source_directory_dict = {}
        shutil.rmtree(source_path, ignore_errors=True)

        if destructive:
            self.update(
                {
                    "source_count": self["source_count"] - 1,
                    "sources": sources,
                }
            )
        else:
            source_path.touch(mode=0o600)
            # Preserve the count so we can keep adding new sources to the end.
            self.update(
                {
                    "sources": self["sources"],
                }
            )

        self._metadata.persist()
        git.add_and_commit(self.path, f"Removed source {source_name}.")

        return source_directory_dict

    def add_source_column(
        self,
        source_column_name: str,
        source_column_type: str,
        is_nullable: bool,
        description: str,
    ):
        """Add a source column to the extracted data directory."""
        if source_column_name in self.source_columns:
            raise SteamfitterException(f"Source column {source_column_name} already exists.")
        self.update(
            {
                "source_columns": {
                    **self["source_columns"],
                    source_column_name: (source_column_type, is_nullable, description),
                },
            }
        )
        self._metadata.persist()

        git.add_and_commit(self.path, f"Added source column {source_column_name}.")

    def remove_source_column(self, source_column_name: str):
        """Remove a source column from the extracted data directory."""
        source_columns = self.source_columns
        if source_column_name not in source_columns:
            raise SteamfitterException(f"Source column {source_column_name} does not exist.")

        source_column_features = source_columns.pop(source_column_name)
        self["source_columns"] = source_columns

        self._metadata.persist()

        git.add_and_commit(self.path, f"Removed source column {source_column_name}.")

        return source_column_features

    @classmethod
    def add_initial_content(cls, path: Path, **kwargs):
        git.init(path)
