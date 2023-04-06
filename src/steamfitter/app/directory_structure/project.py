"""
=================
Project Directory
=================

A project is the coarsest level of organization in steamfitter and represents a collection
of data sources and models aimed at a particular business problem, grant, or other
initiative. A project directory contains a data directory and a modeling directory.

"""
from steamfitter.app.directory_structure.archive import ArchiveDirectory
from steamfitter.app.directory_structure.data import DataDirectory
from steamfitter.app.directory_structure.deliverables import DeliverablesDirectory
from steamfitter.app.directory_structure.modeling import ModelingDirectory
from steamfitter.lib.filesystem import Directory


class ProjectDirectory(Directory):
    IS_INITIAL_DIRECTORY = True
    IS_GIT_ROOT = True

    CREATION_ARGS = {'git_remote'}

    SUBDIRECTORY_TYPES = (
        ArchiveDirectory,
        DataDirectory,
        DeliverablesDirectory,
        ModelingDirectory,
    )

    @classmethod
    def add_subdirectory_creation_args(cls, metadata_kwargs, inherited_kwargs):
        inherited_kwargs["project_name"] = metadata_kwargs["name"]
        return inherited_kwargs

    @property
    def archive_directory(self) -> ArchiveDirectory:
        if not hasattr(self, "_archive_directory"):
            # noinspection PyAttributeOutsideInit
            self._archive_directory = self.get_subdirectory(
                directory_class=ArchiveDirectory,
            )
        return self._archive_directory

    @property
    def data_directory(self) -> DataDirectory:
        if not hasattr(self, "_data_directory"):
            # noinspection PyAttributeOutsideInit
            self._data_directory = self.get_subdirectory(
                directory_class=DataDirectory,
            )
        return self._data_directory

    @property
    def deliverables_directory(self) -> DeliverablesDirectory:
        if not hasattr(self, "_deliverables_directory"):
            # noinspection PyAttributeOutsideInit
            self._deliverables_directory = self.get_subdirectory(
                directory_class=DeliverablesDirectory,
            )
        return self._deliverables_directory

    @property
    def modeling_directory(self) -> ModelingDirectory:
        if not hasattr(self, "_modeling_directory"):
            # noinspection PyAttributeOutsideInit
            self._modeling_directory = self.get_subdirectory(
                directory_class=ModelingDirectory,
            )
        return self._modeling_directory
