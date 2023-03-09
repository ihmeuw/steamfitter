"""
======================
Deliverables Directory
======================

A deliverables directory is a project subdirectory for storing deliverables. Deliverables
are the final products of a project, such as a report, presentation, or paper.

The deliverables directory is not managed directly by steamfitter.

"""
from steamfitter.lib.filesystem import Directory


class DeliverablesDirectory(Directory):
    IS_INITIAL_DIRECTORY = True

    NAME_TEMPLATE = "deliverables"
    DESCRIPTION_TEMPLATE = "Deliverables for the {project_name} project."
