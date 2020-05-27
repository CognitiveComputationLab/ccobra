""" CCOBRA Module

.. rubric:: Submodules

.. autosummary::
   :toctree: _autosummary

   ccobra.benchmark
   ccobra.propositional
   ccobra.syllogistic
   ccobra.syllogistic_generalized

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


from .data import CCobraData
from .item import Item
from .model import CCobraModel
from .domainhandler import CCobraDomainEncoder

from . import benchmark

from . import propositional
from . import syllogistic
from . import syllogistic_generalized

__version__ = '1.0.0'
