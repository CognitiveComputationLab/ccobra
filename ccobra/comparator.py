""" Contains different comparator classes for model output data structures.

"""

class CCobraComparator():
    """ Comparator base class.

    """

    def compare(self, prediction, target):
        """ Base comparison method.

        Parameters
        ----------
        prediction : object
            Prediction object for comparison.

        target : object
            Target object for comparison.

        Returns
        -------
        float
            Comparison result.

        """

        raise NotImplementedError()

    def get_name(self):
        """ Returns the name of the comparator.

        Returns
        -------
        string
            Comparator name.

        """

        raise NotImplementedError()
