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

from .encoder_sylgen import GeneralizedSyllogisticEncoder, QUANTIFIERS_SYLLOGISTIC_GENERALIZED_ENCODING
from .syllogism_gen import decode_response, encode_response, encode_task, GeneralizedSyllogism
