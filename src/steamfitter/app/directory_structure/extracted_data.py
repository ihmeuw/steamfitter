"""
========================
Extracted Data Directory
========================

An extracted data directory is a project subdirectory for storing data extracted from
external sources.

"""
import datetime
import importlib.util
from pathlib import Path
import shutil

import pandas as pd

from steamfitter.lib import git
from steamfitter.app.directory_structure.version import VersionDirectory
from steamfitter.lib.exceptions import SteamfitterException
from steamfitter.lib.filesystem import ARCHIVE_POLICIES, Directory, templates


class Extractor:
    def __init__(self, extractor_path: Path):
        self._root = extractor_path.parent
        # Create a module specification using the filepath
        spec = importlib.util.spec_from_file_location("extractor", extractor_path)
        # Load the module using the specification
        self._extractor = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self._extractor)

    def extract(self):
        self._extractor.extract_data(self._root)

    def format(self):
        self._extractor.format_data(self._root)

    def run(self):
        self.extract()
        self.format()


class ExtractionSourceVersionDirectory(VersionDirectory):
    @classmethod
    def add_initial_content(cls, path: Path, **kwargs):
        template_path = path.parent / "extraction_template.py"
        extractor_path = path / "extract.py"
        shutil.copy2(template_path, extractor_path)

    @property
    def extractor_path(self) -> Path:
        return self.path / "extract.py"

    def get_extractor(self) -> Extractor:
        return Extractor(self.extractor_path)


class ExtractionSourceDirectory(Directory):
    DEFAULT_ARCHIVE_POLICY = ARCHIVE_POLICIES.archive

    NAME_TEMPLATE = "{source_count:>06}-{source_name}"

    DEFAULT_EMPTY_ARGS = {
        ("last_updated", lambda: ""),
        ("latest_version", lambda: ""),
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

    def extract_new_version(self) -> ExtractionSourceVersionDirectory:
        source_name = self.path.name.split("-", maxsplit=1)[1]
        self["last_updated"] = datetime.datetime.now().strftime("%Y_%m_%d")

        version_directory = ExtractionSourceVersionDirectory.create(
            root=self.path,
            parent=self,
            parent_name=source_name,
        )
        extractor = version_directory.get_extractor()

        extractor.run()

        self["latest_version"] = str(version_directory.path)
        self._metadata.persist()
        git.commit_and_push(self.path, f"Extracted new version of {source_name}.")

        return version_directory


class ExtractedDataDirectory(Directory):
    IS_INITIAL_DIRECTORY = True

    NAME_TEMPLATE = "extracted_data"
    DESCRIPTION_TEMPLATE = "Extracted data for the {project_name} project."

    DEFAULT_EMPTY_ARGS = {
        ("source_count", lambda: 0),
        ("sources", lambda: {}),
    }

    SUBDIRECTORY_TYPES = (ExtractionSourceDirectory,)

    @classmethod
    def add_initial_content(cls, path: Path, **kwargs):
        source_columns_path = path / "source_columns.yaml"
        source_columns_path.touch(mode=0o664)
        with open(source_columns_path, "w") as f:
            f.write(templates.SOURCE_COLUMNS)

    @property
    def sources(self):
        return self["sources"].copy()

    @property
    def source_columns_path(self) -> Path:
        return self.path / "source_columns.csv"

    @property
    def source_columns(self) -> pd.DataFrame:
        return pd.read_csv(self.source_columns_path)

    def get_source_directory(self, source_name: str) -> ExtractionSourceDirectory:
        if source_name not in self.sources:
            raise SteamfitterException(f"Source {source_name} does not exist.")
        source_count = self.sources[source_name]
        source_path = self.path / ExtractionSourceDirectory.make_name(
            root=self.path,
            source_count=source_count,
            source_name=source_name,
        )
        return ExtractionSourceDirectory(source_path, self)

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

        git.commit_and_push(self.path, f"Added source {source_name}.")

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
            source_directory_dict = ExtractionSourceDirectory(source_path, self).as_dict()
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
        git.commit_and_push(self.path, f"Removed source {source_name}.")

        return source_directory_dict
