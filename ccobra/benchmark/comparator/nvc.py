""" No Valid Conclusion (NVC) comparator.

"""

import ccobra.benchmark.comparator as comparator


class NVCComparator(comparator.Comparator):
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

        is_nvc_a = comparator.tuple_to_string(obj_a) == 'NVC'
        is_nvc_b = comparator.tuple_to_string(obj_b) == 'NVC'
        return int(is_nvc_a == is_nvc_b)

    def get_name(self):
        """ Returns the name of the comparator

        Returns
        -------
        string
            Comparator name

        """

        return 'NVC Accuracy'
