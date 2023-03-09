"""
==============
Data Directory
==============

A data directory is a project subdirectory for storing extracted and processed data as well
as data diagnostics such as data quality reports, data dictionaries, and plotting outputs.

"""
from steamfitter.lib.filesystem import Directory
from steamfitter.app.directory_structure.extracted_data import ExtractedDataDirectory
from steamfitter.app.directory_structure.processed_data import ProcessedDataDirectory
from steamfitter.app.directory_structure.data_diagnostics import DataDiagnosticsDirectory


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
