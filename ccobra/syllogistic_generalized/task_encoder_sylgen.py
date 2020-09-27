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

class GeneralizedSyllogisticTaskEncoder(ccobra.CCobraTaskEncoder):
    """ Generalized Syllogistic encoder. Provides functions for abbreviating generalized
    syllogistic tasks.

    """

    @staticmethod
    def encode_task(task):
        """ Encodes a task to its generalized syllogistic encoding.

        Parameters
        ----------
        task : list(list(str))
            List representation of the syllogism (e.g., [['All', 'A', 'B'], ['Some', 'B', 'C']]).

        Returns
        -------
        str
            Syllogistic task encoding (e.g., 'AI1').

        Raises
        ------
        ValueError
            If figure of syllogism cannot be determined.

        """

        prem_1, prem_2 = task

        quant1 = QUANTIFIERS_SYLLOGISTIC_GENERALIZED_ENCODING[prem_1[0]]
        quant2 = QUANTIFIERS_SYLLOGISTIC_GENERALIZED_ENCODING[prem_2[0]]
        figure = 1

        if prem_1[1] == prem_2[1]:
            figure = 4
        elif prem_1[2] == prem_2[1]:
            figure = 1
        elif prem_1[2] == prem_2[2]:
            figure = 3
        elif prem_1[1] == prem_2[2]:
            figure = 2
        else:
            raise ValueError('Could not determine figure of:', task)

        return quant1 + quant2 + str(figure)

