""" Squared differences comparator.

"""

import numpy as np

from ccobra import CCobraComparator


class SquaredDiffComparator(CCobraComparator):
    """ Squared differences comparator.

    """

    @staticmethod
    def compare(num_a, num_b):
        """ Compares two response numbers based on their squared difference.

        Parameters
        ----------
        num_a : float
            Number A.

        num_b : float
            Number B.

        Returns
        -------
        float
            Squared difference between the differences.

        """

        if not isinstance(num_a, (int, float)) or not isinstance(num_b, (int, float)):
            raise ValueError('Incompatible value types for comparison.')

        return (num_a - num_b) ** 2

    def get_name(self):
        """ Returns the name of the comparator.

        Returns
        -------
        string
            Comparator name.

        """

        return "Squared Difference"
