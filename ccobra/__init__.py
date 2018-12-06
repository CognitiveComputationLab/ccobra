""" ORCA Module

.. rubric:: Submodules

.. autosummary::
   :toctree: _autosummary

   ccobra.syllogistic

.. rubric:: Classes

.. autoclass:: CCobraData
    :members:
.. autoclass:: CCobraModel
    :members:
.. autoclass:: Item
    :members:

"""

from . import syllogistic

from .data import CCobraData, Item
from .model import CCobraModel

__version__ = '0.0.9'
