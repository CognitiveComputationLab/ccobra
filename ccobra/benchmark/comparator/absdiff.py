""" Absolute differences comparator.

"""

import numpy as np

import ccobra.benchmark.comparator as comparator


class AbsDiffComparator(comparator.Comparator):
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
