""" Syllogistic convenience class.

"""

from ..data import Item
from .encoder_syl import SyllogisticEncoder


#: List of syllogistic task identifiers.
SYLLOGISMS = []
for _prem1 in ['A', 'I', 'E', 'O']:
    for _prem2 in ['A', 'I', 'E', 'O']:
        for _fig in ['1', '2', '3', '4']:
            SYLLOGISMS.append(_prem1 + _prem2 + _fig)

#: List of syllogistic responses.
RESPONSES = []
for _quant in ['A', 'I', 'E', 'O']:
    for _direction in ['ac', 'ca']:
        RESPONSES.append(_quant + _direction)
RESPONSES.append('NVC')

#: List of valid syllogisms
VALID_SYLLOGISMS = [
    'AA1', 'AA2', 'AA4', 'AE1', 'AE2', 'AE3', 'AE4', 'AI2', 'AI4', 'AO3', 'AO4', 'EA1', 'EA2',
    'EA3', 'EA4', 'EI1', 'EI2', 'EI3', 'EI4', 'IA1', 'IA4', 'IE1', 'IE2', 'IE3', 'IE4', 'OA3',
    'OA4'
]

#: List of invalid syllogisms
INVALID_SYLLOGISMS = [
    'AA3', 'AI1', 'AI3', 'AO1', 'AO2', 'EE1', 'EE2', 'EE3', 'EE4', 'EO1', 'EO2', 'EO3', 'EO4',
    'IA2', 'IA3', 'II1', 'II2', 'II3', 'II4', 'IO1', 'IO2', 'IO3', 'IO4', 'OA1', 'OA2', 'OE1',
    'OE2', 'OE3', 'OE4', 'OI1', 'OI2', 'OI3', 'OI4', 'OO1', 'OO2', 'OO3', 'OO4'
]

#: Mapping of syllogisms to logically valid (first-order logics) conclusions
SYLLOGISTIC_FOL_RESPONSES = {
    'AA1': ['Aac', 'Iac', 'Ica'],
    'AA2': ['Aca', 'Iac', 'Ica'],
    'AA3': ['NVC'],
    'AA4': ['Iac', 'Ica'],
    'AI1': ['NVC'],
    'AI2': ['Iac', 'Ica'],
    'AI3': ['NVC'],
    'AI4': ['Iac', 'Ica'],
    'AE1': ['Eac', 'Eca', 'Oac', 'Oca'],
    'AE2': ['Oac'],
    'AE3': ['Eac', 'Eca', 'Oac', 'Oca'],
    'AE4': ['Oac'],
    'AO1': ['NVC'],
    'AO2': ['NVC'],
    'AO3': ['Oca'],
    'AO4': ['Oac'],
    'IA1': ['Iac', 'Ica'],
    'IA2': ['NVC'],
    'IA3': ['NVC'],
    'IA4': ['Iac', 'Ica'],
    'II1': ['NVC'],
    'II2': ['NVC'],
    'II3': ['NVC'],
    'II4': ['NVC'],
    'IE1': ['Oac'],
    'IE2': ['Oac'],
    'IE3': ['Oac'],
    'IE4': ['Oac'],
    'IO1': ['NVC'],
    'IO2': ['NVC'],
    'IO3': ['NVC'],
    'IO4': ['NVC'],
    'EA1': ['Oca'],
    'EA2': ['Eac', 'Eca', 'Oac', 'Oca'],
    'EA3': ['Eac', 'Eca', 'Oac', 'Oca'],
    'EA4': ['Oca'],
    'EI1': ['Oca'],
    'EI2': ['Oca'],
    'EI3': ['Oca'],
    'EI4': ['Oca'],
    'EE1': ['NVC'],
    'EE2': ['NVC'],
    'EE3': ['NVC'],
    'EE4': ['NVC'],
    'EO1': ['NVC'],
    'EO2': ['NVC'],
    'EO3': ['NVC'],
    'EO4': ['NVC'],
    'OA1': ['NVC'],
    'OA2': ['NVC'],
    'OA3': ['Oac'],
    'OA4': ['Oca'],
    'OI1': ['NVC'],
    'OI2': ['NVC'],
    'OI3': ['NVC'],
    'OI4': ['NVC'],
    'OE1': ['NVC'],
    'OE2': ['NVC'],
    'OE3': ['NVC'],
    'OE4': ['NVC'],
    'OO1': ['NVC'],
    'OO2': ['NVC'],
    'OO3': ['NVC'],
    'OO4': ['NVC']
}

def encode_task(task):
    """ Encodes a syllogistic task.

    Parameters
    ----------
    task : list(list(str))
        List representation of the syllogism (e.g., [['All', 'A', 'B'], ['Some', 'B', 'C']]).

    Returns
    -------
    str
        Syllogistic task encoding (e.g., 'AI1').

    """

    return SyllogisticEncoder.encode_task(task)

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

    return SyllogisticEncoder.encode_response(response, task)


def decode_response(enc_response, task):
    """ Decodes an encoded syllogistic response by transforming it to the
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

    quant = enc_response[0].replace('A', 'All').replace(
        'I', 'Some').replace('O', 'Some not').replace('E', 'No')
    if enc_response[1:] == 'ac':
        return [[quant, list(obj_a)[0], list(obj_c)[0]]]

    return [[quant, list(obj_c)[0], list(obj_a)[0]]]


class Syllogism():
    """ Syllogistic helper class. Facilitates the extraction of premise
    information as well as encoding and decoding of responses.

    """

    def __init__(self, item):
        """ Constructs the Syllogism based on a given task item.

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

    def is_valid_syllogism(self):
        """ Returns true if syllogism is valid, i.e., has a logically valid conclusion.

        Returns
        -------
        bool
            True, if syllogism is valid, i.e., has a logically valid conclusion. False otherwise.

        """

        return self.encoded_task in VALID_SYLLOGISMS

    def logically_valid_conclusions(self):
        """ Returns the list of logically valid (according to first-order logics) conclusions for
        the syllogism.

        Returns
        -------
        list(str)
            List of logically valid conclusions.

        """

        return SYLLOGISTIC_FOL_RESPONSES[self.encoded_task]

    def __str__(self):
        """ Constructs a string representation for the Syllogism object.

        Returns
        -------
        str
            String representation containing the premise, quantifier, figure,
            and term information.

        """

        rep = 'Syllogism:\n'
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
