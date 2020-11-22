""" Equality comparator.

"""

import numpy as np

from ccobra import CCobraComparator, tuple_to_string


class EqualityComparator(CCobraComparator):
    """ Equality comparator. Checks if both responses are equal.

    """

    def compare(self, prediction, target, response_type, choices):
        """ Compares two response objects based on equality.
        When using the multiple-choice response type, the predictions and
        targets are interpreted as mask-vectors for the choices.
        In this case, the score corresponds to the overlap of the vectors.

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
            True if both objects are equal, false otherwise.

        """
        
        if response_type == "multiple-choice":

            string_choices = [tuple_to_string(x) for x in choices]
            string_preds = [tuple_to_string(x) for x in prediction]
            string_target = [tuple_to_string(x) for x in target]
            
            choices_pred = [x in string_preds for x in string_choices]
            choices_target = [x in string_target for x in string_choices]

            overlap = np.array(choices_pred) == np.array(choices_target)
            score = np.sum(overlap) / len(choices)
            return score
        
        return int(tuple_to_string(prediction) == tuple_to_string(target))

    def get_name(self):
        """ Returns the name of the comparator.

        Returns
        -------
        string
            Comparator name.

        """

        return 'Accuracy'
