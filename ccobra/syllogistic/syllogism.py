""" Syllogistic convenience class.

"""

from .parsing import encode_response, encode_task, decode_response

class Syllogism():
    """ Syllogistic helper class. Facilitates the extraction of premise
    information as well as encoding and decoding of responses.

    """

    def __init__(self, item):
        """ Constructs the Syllogism based on a given task item.

        Parameters
        ----------
        item : ccobra.Item
            CCOBRA task item container.

        """

        #: Reference to the item the Syllogism is constructed on.
        self.item = item

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

    def __str__(self):
        """ Constructs a string representation for the Syllogism object.

        Returns
        -------
        str
            String representation containing the premise, quantifier, figure,
            and term information.

        """

        s = 'Syllogism:\n'
        s += '\ttask: {}\n'.format(self.task)
        s += '\tencoded_task: {}\n'.format(self.encoded_task)
        s += '\tp1: {}\n'.format(self.p1)
        s += '\tp2: {}\n'.format(self.p2)
        s += '\tquantifier_p1: {}\n'.format(self.quantifier_p1)
        s += '\tquantifier_p2: {}\n'.format(self.quantifier_p2)
        s += '\tfigure: {}\n'.format(self.figure)
        s += '\tTerms:\n'
        s += '\t\tA: {}\n'.format(self.A)
        s += '\t\tB: {}\n'.format(self.B)
        s += '\t\tC: {}\n'.format(self.C)
        return s
