""" Generalized syllogistic encoder functions.

"""

import ccobra


# Quantifier encodings
QUANTIFIERS_SYLLOGISTIC_GENERALIZED_ENCODING = {
    'All': 'A',
    'No': 'E',
    'Few not': 'P',
    'Few': 'B',
    'Most': 'T',
    'Most not': 'D',
    'Many': 'K',
    'Many not': 'G',
    'Some': 'I',
    'Some not': 'O',
}

class GeneralizedSyllogisticResponseEncoder(ccobra.CCobraResponseEncoder):
    """ Generalized Syllogistic encoder. Provides functions for abbreviating generalized
    syllogistic responses.

    """

    @staticmethod
    def encode_response(response, task):
        """ Encodes a response to its syllogistic encoding.

        Parameters
        ----------
        response : list(str)
            Syllogistc response in list representation (e.g., ['All', 'A', 'C'])

        task : list(list(str))
            Syllogistic task in list representation (e.g., [['All', 'A', 'B'], ['Some', 'B', 'C']]).

        Returns
        -------
        str
            Syllogistic response encoding (e.g., 'Aac').

        """

        if not isinstance(response[0], list):
            response = [response]

        if response[0] == 'NVC':
            return 'NVC'

        if response[0][0] == 'NVC':
            return 'NVC'

        object_sets = [set(x[1:]) for x in task]
        midterm = object_sets[0].intersection(object_sets[1])
        obj_a = object_sets[0] - midterm

        quant = QUANTIFIERS_SYLLOGISTIC_GENERALIZED_ENCODING[response[0][0]]

        return quant + ('ac' if response[0][1] == list(obj_a)[0] else 'ca')
