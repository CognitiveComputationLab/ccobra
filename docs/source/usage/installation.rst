.. _installation:

Installation
============

From PyPI
---------

To install CCOBRA via pip, run the following command:

    .. code::

        $> pip install ccobra

To update your installation of CCOBRA, run the following command:

    .. code::

        $> pip install -U ccobra

From the Repository
-------------------

Currently, the only way of installing the CCOBRA package is directly from the
repository. The following steps are required to install the package on your
system:

1. Either clone or download the repository from `Github <https://github.com/CognitiveComputationLab/ccobra>`_.
2. Navigate a terminal to the your local copy of the repository folder:

    .. code::

        $> cd /path/to/repository
3. Install the package by executing pip on the local respository:

    .. code::

        $> pip install .

.. note:: If you wish to keep your local version of CCOBRA consistent with the
    repository, use ``git clone`` and ``pip install --editable .`` during the
    installation. This directly references your local version of the library
    instead of creating separate copies. Changes to the repository (vial
    ``git pull``, etc.) are directly applied when referencing CCOBRA in your
    work.
