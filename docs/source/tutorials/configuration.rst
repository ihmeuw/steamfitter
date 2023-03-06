.. _steamfitter-configuration:

====================================
Steamfitter first-time configuration
====================================

Steamfitter is a tool for creating and maintaining high-throughput data science and
modeling pipelines. After :ref:`installation <installation-guide>`, it needs to run some
first time configuration to set up a project work space. This is done with the
``steamfitter configure`` command. For configuration, you will need to provide a
root directory in which projects will be organized. This directory will be saved to a user
configuration file located at `~/.config/steamfitter/config.yaml` and a root directory for
projects will be created at the provided path if it does not already exist. If the root
directory already exists, only the user configuration will be generated and the existing
directory will be used as the root directory for projects, allowing multiple users to
collaborate on the same projects. To configure Steamfitter, run the following command:

.. code-block:: bash

    $ steamfitter configure /path/to/projects/root

Where ``/path/to/projects/root`` is the path to the root directory for projects.
