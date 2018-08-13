""" ORCA data containers for syllogistic data.

The :mod:`orca.data.syllogistic` module contains the following classes:

.. autosummary::
   :toctree: _autosummary

   orca.data.syllogistic.encoding
   orca.data.syllogistic.syldata
   orca.data.syllogistic.syllogisms

"""

from .encoding import SylEncoding, OnehotEncoding, AtmosphereEncoding, Dancoding
from .orcadata import OrcaData, RawData
from .syldata import EncSylData, SylData, RawSylData
from .syllogisms import get_responses, get_syllogisms
