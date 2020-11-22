""" No Valid Conclusion (NVC) comparator.

"""

from ccobra import CCobraComparator, tuple_to_string


class NVCComparator(CCobraComparator):
    """ NVC response comparator. Performs the evaluation based on NVC and non-NVC classes.

    """

    def compare(self, prediction, target, response_type, choices):
        """ Compares two response objects based on their NVCness. Only returns true if both
        responses are in agreement with either responding NVC or not NVC.

        Parameters
        ----------
        prediction : tuple
            Response tuple A for comparison.

        target : tuple
            Response tuple B for comparison.
            
        response_type : string
            The response type of the prediction and target.
            
        choices : list(object)
            The choice options that were available for this comparison.

        Returns
        -------
        bool
            True only if both objects agree on whether the response is NVC or not.

        """

        if response_type == "multiple-choice":
            raise ValueError('NVC Accuracy Comparator is incompatible with the multiple-choice response type.')

        is_nvc_a = tuple_to_string(prediction) == 'NVC'
        is_nvc_b = tuple_to_string(target) == 'NVC'
        return int(is_nvc_a == is_nvc_b)

    def get_name(self):
        """ Returns the name of the comparator.

        Returns
        -------
        string
            Comparator name.

        """

        return 'NVC Accuracy'
