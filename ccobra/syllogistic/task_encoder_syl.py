""" Syllogistic encoder functions.

"""

import ccobra

class SyllogisticTaskEncoder(ccobra.encoders.CCobraTaskEncoder):
    """ Syllogistic encoder. Provides functions for abbreviating syllogistic tasks.

    """

    @staticmethod
    def encode_task(task):
        """ Encodes a task to its syllogistic encoding.

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

        quant1 = prem_1[0].replace('All', 'A').replace(
            'Some not', 'O').replace('Some', 'I').replace('No', 'E')
        quant2 = prem_2[0].replace('All', 'A').replace(
            'Some not', 'O').replace('Some', 'I').replace('No', 'E')
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
