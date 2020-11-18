""" Absolute differences comparator.

"""

import numpy as np

from ccobra import CCobraComparator, unnest


class AbsDiffComparator(CCobraComparator):
    """ Absolute differences comparator.

    """

    @staticmethod
    def compare(num_a, num_b):
        """ Compares two response numbers based on their absolute difference.

        Parameters
        ----------
        num_a : tuple
            Tuple containing number A.

        num_b : tuple
            Tuple containing number B.

        Returns
        -------
        float
            Absolute difference between the differences.

        """
        inner_a = unnest(num_a)
        inner_b = unnest(num_b)
        
        if isinstance(inner_a, str):
            inner_a = float(inner_a)
        if isinstance(inner_b, str):
            inner_b = float(inner_b)
        if not isinstance(inner_a, (int, float)) or not isinstance(inner_b, (int, float)):
            raise ValueError('Incompatible value types for comparison.')

        return np.abs(inner_a - inner_b)

    def get_name(self):
        """ Returns the name of the comparator.

        Returns
        -------
        string
            Comparator name.

        """

        return "Absolute Difference"
