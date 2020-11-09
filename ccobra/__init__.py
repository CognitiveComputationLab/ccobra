""" CCOBRA Module

.. rubric:: Submodules

.. autosummary::
   :toctree: _autosummary

   ccobra.benchmark
   ccobra.encoders
   ccobra.propositional
   ccobra.syllogistic
   ccobra.syllogistic_generalized

.. rubric:: Classes

.. autoclass:: CCobraData
    :members:
.. autoclass:: CCobraModel
    :members:
.. autoclass:: Item
    :members:

"""


from .version import __version__

from .data import CCobraData
from .item import Item
from .model import CCobraModel

from . import encoders
from . import benchmark
from . import propositional
from . import syllogistic
from . import syllogistic_generalized

