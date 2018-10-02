""" Syllogistic domain definition. Contains classes for handling syllogistic
data and implementing syllogistic models. Additionally, provides helper methods
for common operations related to the syllogistic domain (e.g., generating task
or response identifiers).

.. autosummary::
   :toctree: _autosummary

   ccobra.syllogistic.encoding
   ccobra.syllogistic.sylmodel
   ccobra.syllogistic.syldata
   ccobra.syllogistic.syllogisms

"""

from .encoding import AtmosphereEncoding, OnehotEncoding, SylEncoding
from .sylmodel import SylModel
from .syldata import EncSylData, RawSylData, SylData
from .syllogisms import get_responses, get_syllogisms, premise_text, response_text, syllog_text
