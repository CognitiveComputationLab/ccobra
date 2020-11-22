""" Absolute differences comparator.

"""

import numpy as np

from ccobra import CCobraComparator, unnest


class AbsDiffComparator(CCobraComparator):
    """ Absolute differences comparator.

    """

    def compare(self, prediction, target, response_type, choices):
        """ Compares two response numbers based on their absolute difference.

        Parameters
        ----------
        prediction : tuple
            Tuple containing number A.

        target : tuple
            Tuple containing number B.
                
        response_type : string
            The response type of the prediction and target.
            
        choices : list(object)
            The choice options that were available for this comparison.

        Returns
        -------
        float
            Absolute difference between the differences.

        """
        
        if response_type == "multiple-choice":
            raise ValueError('The Absolute Difference Comparator is incompatible with the multiple-choice response type.')
        
        inner_a = unnest(prediction)
        inner_b = unnest(target)
        
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
