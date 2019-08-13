""" Syllogistic submodule.

.. rubric:: Functions

.. autofunction:: decode_response
.. autofunction:: encode_response
.. autofunction:: encode_task

.. rubric:: Classes

.. autoclass:: Syllogism
    :members:

"""

from .syllogism import decode_response, encode_response, encode_task, SYLLOGISMS, RESPONSES, \
    Syllogism, VALID_SYLLOGISMS, INVALID_SYLLOGISMS, SYLLOGISTIC_FOL_RESPONSES
