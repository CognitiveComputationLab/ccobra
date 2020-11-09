""" Encoder handlers for tasks and responses.

.. rubric:: Classes

.. autoclass:: CCobraResponseEncoder
    :members:
.. autoclass:: CCobraTaskEncoder
    :members:
.. autoclass:: IdentityResponseEncoder
    :members:

"""

from .response_encoder import CCobraResponseEncoder
from .task_encoder import CCobraTaskEncoder
from .response_encoder_identity import IdentityResponseEncoder
