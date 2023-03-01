=======================
Installing ght-scrapers
=======================

.. contents::
   :depth: 1
   :local:
   :backlinks: none

.. highlight:: console

Overview
--------

`steamfitter` is written in `Python`__ and supports Python 3.8+.

__ http://docs.python-guide.org/en/latest/

.. _install-pypi:

Installation from PyPI
----------------------

`steamfitter` packages are published on the `Python Package Index
<https://pypi.org/project/steamfitter/>`_. The preferred tool for installing
packages from *PyPI* is :command:`pip`.  This tool is provided with all modern
versions of Python

On Linux or MacOS, you should open your terminal and run the following command.

::

   $ pip install -U steamfitter

On Windows, you should open *Command Prompt* and run the same command.

.. code-block:: doscon

   C:\> pip install -U steamfitter


Installation from source
------------------------

You can install `steamfitter` directly from a clone of the
`Git repository <https://github.com/ihmeuw/steamfitter>`_.
You can clone the repository locally and install from the local clone::

    $ git clone https://github.com/ihmeuw/steamfitter.git
    $ cd steamfitter
    $ pip install .

You can also install directly from the git repository with pip::

    $ pip install git+https://github.com/ihmeuw/steamfitter.git

Additionally, you can download a snapshot of the Git repository in either
`tar.gz <https://github.com/ihmeuw/steamfitter/archive/develop.tar.gz>`_ or
`zip <https://github.com/ihmeuw/steamfitter/archive/develop.zip>`_ format.  Once downloaded
and extracted, these can be installed with :command:`pip` as above.
