""" Syllogistic encoder functions.

"""

from ccobra import CCobraResponseEncoder


class SyllogisticResponseEncoder(CCobraResponseEncoder):
    """ Syllogistic encoder. Provides functions for abbreviating syllogistic responses.

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

        quant = response[0][0].replace('All', 'A').replace(
            'Some not', 'O').replace('Some', 'I').replace('No', 'E')

        return quant + ('ac' if response[0][1] == list(obj_a)[0] else 'ca')
