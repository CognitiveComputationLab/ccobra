""" ORCA Module

.. rubric:: Submodules

.. autosummary::
   :toctree: _autosummary

   ccobra.benchmark
   ccobra.propositional
   ccobra.syllogistic

.. rubric:: Classes

.. autoclass:: CCobraData
    :members:
.. autoclass:: CCobraDomainEncoder
    :members:
.. autoclass:: CCobraModel
    :members:
.. autoclass:: Item
    :members:

"""


from .data import CCobraData, Item
from .model import CCobraModel
from .domainhandler import CCobraDomainEncoder

from . import syllogistic
from . import benchmark

__version__ = '0.16.0'
