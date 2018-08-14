""" ORCA data containers.

.. autosummary::
   :toctree: _autosummary

   orca.data.encoding
   orca.data.orcadata
   orca.data.syldata
   orca.data.syllogisms

"""

from .encoding import SylEncoding, OnehotEncoding, AtmosphereEncoding, Dancoding
from .orcadata import OrcaData, RawData
from .syldata import EncSylData, SylData, RawSylData
from .syllogisms import get_responses, get_syllogisms
