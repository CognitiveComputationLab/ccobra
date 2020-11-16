""" Equality comparator.

"""

from ccobra import CCobraComparator


class EqualityComparator(CCobraComparator):
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

        return int(comparator.tuple_to_string(obj_a) == comparator.tuple_to_string(obj_b))

    def get_name(self):
        """ Returns the name of the comparator.

        Returns
        -------
        string
            Comparator name.

        """

        return 'Accuracy'
