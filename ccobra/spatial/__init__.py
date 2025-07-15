""" Spatial reasoning submodule that contains utility functionality to facilitate
modeling and analyses in the domain of spatial reasoning.

.. rubric:: Constants

.. note:: Since the built-in lists and dictionaries are intended to be constants,
    avoid altering them to avoid unwanted behavior.


.. py:data:: CARDINAL_DIRECTIONS
    :annotation: = ['north', 'east', 'south', 'west']
    
    List with the four cardinal directions.

.. py:data:: ORDINAL_DIRECTIONS
    :annotation: = ['north-east', 'north-west', 'south-east', 'south-west']
    
    List with the four ordinal directions.

.. py:data:: OPPOSITES
    :type: dict(str, str)
    
    Dictionary mapping a spatial relation to its opposite.

.. py:data:: CARDINAL_COMBINATIONS
    :type: dict(str, set(set))
    
    Dictionary mapping an ordinal relation to a set of the cardinal direction it is composed of.

.. rubric:: Functions

.. autofunction:: invert
.. autofunction:: combine_cardinal_relations
.. autofunction:: combine_ordinal_relations
.. autofunction:: is_partially_equal

"""

from .spatial import CARDINAL_DIRECTIONS, ORDINAL_DIRECTIONS, OPPOSITES, CARDINAL_COMBINATIONS, \
    invert, combine_cardinal_relations, combine_ordinal_relations, is_partially_equal