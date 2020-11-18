""" Squared differences comparator.

"""

import numpy as np

from ccobra import CCobraComparator, unnest


class SquaredDiffComparator(CCobraComparator):
    """ Squared differences comparator.

    """

    @staticmethod
    def compare(num_a, num_b):
        """ Compares two response numbers based on their squared difference.

        Parameters
        ----------
        num_a : tuple
            Tuple containing number A.

        num_b : tuple
            Tuple containing number B.

        Returns
        -------
        float
            Squared difference between the differences.

        """

        inner_a = unnest(num_a)
        inner_b = unnest(num_b)
        
        if isinstance(inner_a, str):
            inner_a = float(inner_a)
        if isinstance(inner_b, str):
            inner_b = float(inner_b)
        if not isinstance(inner_a, (int, float)) or not isinstance(inner_b, (int, float)):
            raise ValueError('Incompatible value types for comparison.')

        return (inner_a - inner_b) ** 2

    def get_name(self):
        """ Returns the name of the comparator.

        Returns
        -------
        string
            Comparator name.

        """

        return "Squared Difference"
