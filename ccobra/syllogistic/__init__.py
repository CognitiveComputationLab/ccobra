""" Syllogistic submodule.

.. rubric:: Functions

.. autofunction:: decode_response
.. autofunction:: encode_response
.. autofunction:: encode_task

.. rubric:: Classes

.. autoclass:: Syllogism
    :members:

"""

from .parsing import decode_response, encode_response, encode_task, SYLLOGISMS, RESPONSES
from .syllogism import Syllogism
