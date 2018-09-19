.. _installation:

Installation
============

From the Repository
-------------------

Currently, the only way of installing the ORCA package is directly from the
repository. The following steps are required to install the package on your
system:

1. Either clone or download the repository from `Github <https://github.com/CognitiveComputationLab/orca>`_.
2. Navigate a terminal to the your local copy of the repository folder:

    .. code::

        $> cd /path/to/repository
3. Install the package by executing the following command (if ORCA is to be
   installed for your user only, add ``--user`` to the following command):

    .. code::

        $> python setup.py install

.. note:: If you wish to keep your local version of ORCA consistent with the repository, use ``git clone`` and ``python setup.py develop`` during the installation. This directly references your local version of the library instead of creating separate copies. Changes to the repository (vial ``git pull``, etc.) are directly applied when referencing ORCA in your work.

Uninstallation
--------------

If ORCA was installed using ``python setup.py install``, you can determine its
location using ``python -c "import orca; print(orca.__file__)"``. Simply
delete the displayed folder (e.g., ``/usr/lib/python3.5/dist-packages/orca``).

If ORCA was installed using ``python setup.py develop``, run the following
command from within your local repository folder:

.. code::

    $> python setup.py develop --uninstall
