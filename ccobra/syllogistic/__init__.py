""" Syllogistic submodule that contains utility functionality to facilitate
modeling and analyses in the domain of syllogistic reasoning.

.. rubric:: Constants

.. note:: Since the built-in lists and dictionaries are intended to be constants,
    avoid altering them to avoid unwanted behavior.

.. py:data:: SYLLOGISMS
    :type: = list(str)
    
    List containing all 64 syllogisms.

.. py:data:: RESPONSES
    :type: = list(str)
    
    List containing the 9 response options.

.. py:data:: VALID_SYLLOGISMS
    :type: = list(str)
    
    List containing the valid syllogisms.

.. py:data:: INVALID_SYLLOGISMS
    :type: = list(str)
    
    List containing the invalid syllogisms.

.. py:data:: SYLLOGISTIC_FOL_RESPONSES
    :type: = dict(str, list(str))
    
    Dictionary containing the logically valid responses for each syllogism.


.. rubric:: Functions

.. autofunction:: create_data_string_task
.. autofunction:: create_data_string_choices
.. autofunction:: create_data_string_response
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
    Syllogism, VALID_SYLLOGISMS, INVALID_SYLLOGISMS, SYLLOGISTIC_FOL_RESPONSES, dataset_to_matrix, \
    create_data_string_task, create_data_string_choices, create_data_string_response
