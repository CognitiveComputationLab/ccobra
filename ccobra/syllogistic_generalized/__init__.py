""" Generalized Syllogistic submodule that contains utility functionality to facilitate
modeling and analyses in the domain of syllogistic reasoning with generalized quantifiers.

.. rubric:: Functions

.. autofunction:: decode_response
.. autofunction:: encode_response
.. autofunction:: encode_task

.. rubric:: Classes

.. autoclass:: GeneralizedSyllogism
    :members:
.. autoclass:: GeneralizedSyllogisticTaskEncoder
    :members:
.. autoclass:: GeneralizedSyllogisticResponseEncoder
    :members:

"""

from .task_encoder_sylgen import GeneralizedSyllogisticTaskEncoder, QUANTIFIERS_SYLLOGISTIC_GENERALIZED_ENCODING
from .resp_encoder_sylgen import GeneralizedSyllogisticResponseEncoder
from .syllogism_gen import decode_response, encode_response, encode_task, GeneralizedSyllogism
