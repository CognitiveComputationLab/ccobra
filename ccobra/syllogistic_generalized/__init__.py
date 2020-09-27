""" Generalized Syllogistic submodule.

.. rubric:: Functions

.. autofunction:: decode_response
.. autofunction:: encode_response
.. autofunction:: encode_task

.. rubric:: Classes

.. autoclass:: GeneralizedSyllogism
    :members:
.. autoclass:: GeneralizedSyllogisticEncoder
    :members:

"""

from .task_encoder_sylgen import GeneralizedSyllogisticTaskEncoder, QUANTIFIERS_SYLLOGISTIC_GENERALIZED_ENCODING
from .resp_encoder_sylgen import GeneralizedSyllogisticResponseEncoder
from .syllogism_gen import decode_response, encode_response, encode_task, GeneralizedSyllogism
