""" Contains different comparator classes for model output data structures.

"""

import copy

def tuple_to_string(tuptup):
    """ Converts a tuple to its string representation.

    """

    def join_deepest(tup, sep=';'):
        """ Recursive method to create the string representation for the deepest level of the
        tuptup list.

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

        """

        raise NotImplementedError()

class EqualityComparator():
    """ Equality comparator. Checks if both responses are equal.

    """

    def compare(self, obj_a, obj_b):
        """ Compares two response objects based on equality.

        """

        return tuple_to_string(obj_a) == tuple_to_string(obj_b)

class NVCComparator():
    """ NVC response comparator. Performs the evaluation based on NVC and non-NVC classes.

    """

    def compare(self, obj_a, obj_b):
        """ Compares two response objects based on their NVCness. Only returns true if both
        responses are in agreement with either responding NVC or not NVC.

        """

        return (tuple_to_string(obj_a) == 'NVC') == (tuple_to_string(obj_b) == 'NVC')
