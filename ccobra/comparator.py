""" Contains different comparator classes for model output data structures.

"""

class CCobraComparator():
    """ Comparator base class.

    """

    def compare(self, prediction, target, response_type, choices):
        """ Base comparison method.

        Parameters
        ----------
        prediction : object
            Prediction object for comparison.

        target : object
            Target object for comparison.
            
        response_type : string
            The response type of the prediction and target.
            
        choices : list(object)
            The choice options that were available for this comparison.

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
