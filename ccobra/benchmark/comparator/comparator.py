""" Contains different comparator classes for model output data structures.

"""

import copy

import numpy as np


def tuple_to_string(tuptup):
    """ Converts a tuple to its string representation. Uses different separators (';', '/', '|') for
    different depths of the representation.

    Parameters
    ----------
    tuptup : list
        Tuple to convert to its string representation.

    Returns
    -------
    str
        String representation of the input tuple.

    """

    def join_deepest(tup, sep=';'):
        """ Recursive function to create the string representation for the deepest level of the
        tuptup list.

        Parameters
        ----------
        tup : object
            Element to join if list or list of lists.

        sep : str, optional
            Separation character to join the list elements by.

        Returns
        -------
        object
            List containing joined string in max depth. Str if input depth = 1.

        """

        if not isinstance(tup, list):
            return tup
        if not isinstance(tup[0], list):
            return sep.join(tup)

        for idx, val in enumerate(tup):
            tup[idx] = join_deepest(val, sep)
        return tup

    tup = copy.deepcopy(tuptup)
    tup = join_deepest(tup, ';')
    tup = join_deepest(tup, '/')
    tup = join_deepest(tup, '|')
    return tup


class Comparator():
    """ Comparator base class.

    """

    def compare(self, obj_a, obj_b):
        """ Base comparison method.

        Parameters
        ----------
        obj_a : object
            Object A for comparison.

        obj_b : object
            Object B for comparison.

        Returns
        -------
        object
            Comparison result.

        """

        raise NotImplementedError()

    def get_name(self):
        """ Returns the name of the comparator

        Returns
        -------
        string
            Comparator name

        """

        raise NotImplementedError()
