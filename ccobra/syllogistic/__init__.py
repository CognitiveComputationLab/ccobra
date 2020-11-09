""" Syllogistic submodule.

.. rubric:: Functions

.. autofunction:: decode_response
.. autofunction:: encode_response
.. autofunction:: encode_task

.. rubric:: Classes

.. autoclass:: Syllogism
    :members:

.. autoclass:: SyllogisticTaskEncoder
    :members:
.. autoclass:: SyllogisticResponseEncoder
    :members:

"""

from .task_encoder_syl import SyllogisticTaskEncoder
from .resp_encoder_syl import SyllogisticResponseEncoder

from .syllogism import decode_response, encode_response, encode_task, SYLLOGISMS, RESPONSES, \
    Syllogism, VALID_SYLLOGISMS, INVALID_SYLLOGISMS, SYLLOGISTIC_FOL_RESPONSES, dataset_to_matrix
