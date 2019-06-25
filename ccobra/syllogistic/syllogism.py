""" Syllogistic convenience class.

"""

from ..data import Item
from .parsing import encode_response, encode_task, decode_response


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
