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

class EqualityComparator():
    """ Equality comparator. Checks if both responses are equal.

    """

    @staticmethod
    def compare(obj_a, obj_b):
        """ Compares two response objects based on equality.

        Parameters
        ----------
        obj_a : tuple
            Response tuple A for comparison.

        obj_b : tuple
            Response tuple B for comparison.

        Returns
        -------
        bool
            True if both objects are equal, false otherwise.

        """

        return int(tuple_to_string(obj_a) == tuple_to_string(obj_b))
        
    def get_name(self):
        """ Returns the name of the comparator

        Returns
        -------
        string
            Comparator name

        """
        
        return "Accuracy"

class NVCComparator():
    """ NVC response comparator. Performs the evaluation based on NVC and non-NVC classes.

    """

    @staticmethod
    def compare(obj_a, obj_b):
        """ Compares two response objects based on their NVCness. Only returns true if both
        responses are in agreement with either responding NVC or not NVC.

        Parameters
        ----------
        obj_a : tuple
            Response tuple A for comparison.

        obj_b : tuple
            Response tuple B for comparison.

        Returns
        -------
        bool
            True only if both objects agree on whether the response is NVC or not.

        """

        return int((tuple_to_string(obj_a) == 'NVC') == (tuple_to_string(obj_b) == 'NVC'))
        
    def get_name(self):
        """ Returns the name of the comparator

        Returns
        -------
        string
            Comparator name

        """
        
        return "NVC Accuracy"

class AbsDiffComparator():
    """ Absolute differences comparator.

    """

    @staticmethod
    def compare(num_a, num_b):
        """ Compares two response numbers based on their absolute difference.

        Parameters
        ----------
        num_a : float
            Number A.

        num_b : float
            Number B.

        Returns
        -------
        float
            Absolute difference between the differences.

        """

        if not isinstance(num_a, (int, float)) or not isinstance(num_b, (int, float)):
            raise ValueError('Incompatible value types for comparison.')

        return np.abs(num_a - num_b)
        
    def get_name(self):
        """ Returns the name of the comparator

        Returns
        -------
        string
            Comparator name

        """
        
        return "Absolute Difference"
