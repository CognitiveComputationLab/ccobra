""" Helper classes for generalized syllogisms.

"""

from .task_encoder_sylgen import GeneralizedSyllogisticTaskEncoder, QUANTIFIERS_SYLLOGISTIC_GENERALIZED_ENCODING
from .resp_encoder_sylgen import GeneralizedSyllogisticResponseEncoder
from ..item import Item


def encode_task(task):
    """ Encodes a generalized syllogistic task.

    Parameters
    ----------
    task : list(list(str))
        List representation of the syllogism (e.g., [['All', 'A', 'B'], ['Most', 'B', 'C']]).

    Returns
    -------
    str
        Syllogistic task encoding (e.g., 'AI1').

    """

    return GeneralizedSyllogisticTaskEncoder.encode_task(task)

def encode_response(response, task):
    """ Encodes a response to its generalized syllogistic encoding.

    Parameters
    ----------
    response : list(str)
        Syllogistc response in list representation (e.g., ['Most', 'A', 'C'])

    task : list(list(str))
        Syllogistic task in list representation (e.g., [['All', 'A', 'B'], ['Most', 'B', 'C']]).

    Returns
    -------
    str
        Syllogistic response encoding (e.g., 'Tac').

    """

    return GeneralizedSyllogisticResponseEncoder.encode_response(response, task)

def decode_response(enc_response, task):
    """ Decodes an encoded generalized syllogistic response by transforming it to the
    corresponding tuple representation and inserting the appropriate terms.

    Parameters
    ----------
    enc_response : str
        Encoded syllogistic response (e.g., 'Aac').

    task : list(str)
        Syllogistic task in the tuple list representation (e.g.,
        [['Some', 'models', 'managers'], ['All', 'models', 'clerks']]).

    Returns
    -------
    list
        List representation of the response to decode.

    """

    if enc_response == 'NVC':
        return [['NVC']]
    if enc_response == ['NVC']:
        return [enc_response]
    if enc_response == [['NVC']]:
        return enc_response

    obj_a = set(task[0][1:]) - set(task[1][1:])
    obj_c = set(task[1][1:]) - set(task[0][1:])

    # Determine quantifier
    quant = None
    for resp, enc in QUANTIFIERS_SYLLOGISTIC_GENERALIZED_ENCODING.items():
        if enc == enc_response[0]:
            quant = resp
            break

    if quant is None:
        raise ValueError('Invalid Quantifier in response encoding: {}'.format(enc_response))

    # Handle response direction
    if enc_response[1:] == 'ac':
        return [[quant, list(obj_a)[0], list(obj_c)[0]]]
    return [[quant, list(obj_c)[0], list(obj_a)[0]]]

class GeneralizedSyllogism():
    """ Generalized syllogistic helper class.

    """

    def __init__(self, item):
        """ Constructs the generalized Syllogism based on a given task item.

        Parameters
        ----------
        item : ccobra.Item
            CCOBRA task item container to base this Syllogism helper on.

        """

        #: Instance of the item the Syllogism is constructed on. The instance
        #: is copied in order to prevent reference mismatches from happening.
        self.item = Item(
            item.identifier,
            item.domain,
            item.task_str,
            item.response_type,
            item.choices_str,
            item.sequence_number)

        #: Reference to the task the Syllogism is constructed on.
        self.task = self.item.task

        #: String representation of the task
        self.encoded_task = encode_task(self.task)

        #: List representation of the first premise
        self.p1 = self.task[0]

        #: List representation of the second premise
        self.p2 = self.task[1]

        #: Quantifier of the first premise
        self.quantifier_p1 = self.task[0][0]

        #: Quantifier of the second premise
        self.quantifier_p2 = self.task[1][0]

        #: Figure of the syllogism
        self.figure = int(self.encoded_task[-1])

        # Figure out the figure and identify the terms
        if self.figure == 1:
            self.A, self.B, self.C = self.task[0][1], self.task[0][2], self.task[1][2]
        elif self.figure == 2:
            self.A, self.B, self.C = self.task[0][2], self.task[0][1], self.task[1][1]
        elif self.figure == 3:
            self.A, self.B, self.C = self.task[0][1], self.task[0][2], self.task[1][1]
        elif self.figure == 4:
            self.A, self.B, self.C = self.task[0][2], self.task[0][1], self.task[1][2]

    def encode_response(self, response):
        """ Encodes a given syllogistic response based on the information
        contained in the premises.

        Parameters
        ----------
        response : list(str)
            Syllogistic response in list representation (e.g.,
            ['All', 'clerks', 'managers']).

        Returns
        -------
        str
            String encoding of the response (e.g., 'Aac').

        """

        return encode_response(response, self.item.task)

    def decode_response(self, encoded_response):
        """ Decodes a syllogistic response in string representation based on
        the information stored in the syllogism's premises.

        Parameters
        ----------
        encoded_response : str
            Encoded syllogistic response (e.g., 'Aac').

        Returns
        -------
        list(str)
            List representation of the encoded response (e.g.,
            ['All', 'clerks', 'managers']).

        """

        return decode_response(encoded_response, self.item.task)

    def is_classical(self):
        """ Checks if the represented syllogism is in the classical set of 64 problems.

        """

        if self.quantifier_p1 not in ['A', 'I', 'E', 'O']:
            return False

        if self.quantifier_p2 not in ['A', 'I', 'E', 'O']:
            return False

        return True

    def __str__(self):
        """ Constructs a string representation for the Syllogism object.

        Returns
        -------
        str
            String representation containing the premise, quantifier, figure,
            and term information.

        """

        rep = 'Generalized Syllogism:\n'
        rep += '\ttask: {}\n'.format(self.task)
        rep += '\tencoded_task: {}\n'.format(self.encoded_task)
        rep += '\tp1: {}\n'.format(self.p1)
        rep += '\tp2: {}\n'.format(self.p2)
        rep += '\tquantifier_p1: {}\n'.format(self.quantifier_p1)
        rep += '\tquantifier_p2: {}\n'.format(self.quantifier_p2)
        rep += '\tfigure: {}\n'.format(self.figure)
        rep += '\tTerms:\n'
        rep += '\t\tA: {}\n'.format(self.A)
        rep += '\t\tB: {}\n'.format(self.B)
        rep += '\t\tC: {}\n'.format(self.C)
        return rep
