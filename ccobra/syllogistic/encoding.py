""" Syllogistic encoding classes.

Defines a base Encoding class which is extended to implement some basic
encoding types:

- :class:`OnehotEncoding`
- :class:`AtmosphereEncoding`

"""

import numpy as np

from .syllogisms import get_responses

class SylEncoding():
    """ Base class for syllogistic encodings. Provides methods for encoding
    and decoding syllogistic tasks and responses.

    """

    def encode_syllogism(self, syllogism):
        """ Encodes a given syllogism.

        Parameters
        ----------
        syllogism : str
            Syllogistic task identifier (e.g., 'AA1').

        Returns
        -------
        ndarray
            Syllogistic task encoding.

        """

        raise NotImplementedError()

    def encode_response(self, response):
        """ Encodes a given syllogistic response.

        Parameters
        ----------
        response : str
            Syllogistic response identifier (e.g., 'Aac').

        Returns
        -------
        ndarray
            Syllogistic response encoding.

        """

        raise NotImplementedError()

    def decode_syllogism(self, encoded):
        """ Decodes a given syllogistic task encoding.

        Parameters
        ----------
        encoded : ndarray
            Syllogistic task encoding to decode.

        Returns
        -------
        str
            Syllogistic task identifier (e.g., 'AA1').

        """

        raise NotImplementedError()

    def decode_response(self, encoded):
        """ Decodes a given syllogistic response encoding.

        Parameters
        ----------
        encoded : ndarray
            Syllogistic response encoding to decode.

        Returns
        -------
        str
            Syllogistic response identifier (e.g., 'Aac').

        """

        raise NotImplementedError()

class OnehotEncoding(SylEncoding):
    """ Defines the syllogistic onehot encoding. Syllogistic responses are
    encoded as vectors with 9 dimensions. Syllogistic tasks are represented
    with their parts (quantifiers, figures) being individually encoded as
    onehot vectors and concatenated.

    """

    @staticmethod
    def encode_syllogism(syllogism):
        """ Encodes a syllogistic problem into its corresponding onehot
        encoding by individually encoding the quantifiers and figure, and
        concatenating the result.

        Parameters
        ----------
        syllogism : str
            String representation of the syllogism to encode (e.g., 'AA1').

        Returns
        -------
        ndarray
            Onehot-encoded syllogism of dimensionality 12.

        """

        # Extract information
        quantifier_p1 = syllogism[0]
        quantifier_p2 = syllogism[1]
        figure = int(syllogism[2])

        # Create the encoded vector
        quantifiers = ['A', 'I', 'E', 'O']
        encoding = np.zeros((3, 4), dtype='int')
        encoding[0, quantifiers.index(quantifier_p1)] = 1
        encoding[1, quantifiers.index(quantifier_p2)] = 1
        encoding[2, figure - 1] = 1

        return encoding.flatten()

    @staticmethod
    def encode_response(response):
        """ Encodes a syllogistic response into its corresponding onehot
        encoded vector of dimensionality 9. Misc responses are treated as a
        special case being assigned the all-zeros vector.

        Parameters
        ----------
        response : str
            Syllogistic response identifier (e.g., 'Aac').

        Returns
        -------
        ndarray
            Onehot-encoded vector of the syllogistic response (dim 9).

        """

        encoding = np.zeros((9,), dtype=int)

        if response == 'Misc':
            return encoding

        encoding[get_responses().index(response)] = 1
        return encoding

    @staticmethod
    def decode_syllogism(encoded):
        """ Decodes a syllogistic task from in its onehot encoding.

        Parameters
        ----------
        encoded : ndarray
            Onehot-encoding to decode. Must be of dimensionality 12.

        Returns
        -------
        str
            Syllogistic task identifier (e.g., 'AA1').

        """

        if len(encoded) != 12:
            raise ValueError(
                'Syllogistic task encodings are expected to be of dim 12.')

        quantifiers = ['A', 'I', 'E', 'O']
        reshaped = encoded.reshape(3, -1)
        return quantifiers[np.argmax(reshaped[0])] + \
            quantifiers[np.argmax(reshaped[1])] + \
            str(np.argmax(reshaped[2]) + 1)

    @staticmethod
    def decode_response(encoded):
        """ Decodes a syllogistic response from its onehot encoding.

        Parameters
        ----------
        encoded : ndarray
            Onehot-encoding to decode. Must be of dimensionality 9.

        Returns
        -------
        str
            Syllogistic response identifier (e.g., 'Aac').

        """

        if len(encoded) != 9:
            raise ValueError(
                'Syllogistic response encodings are expected to be of dim 9.')

        if np.all(encoded == 0):
            return 'Misc'
        return get_responses()[np.argmax(encoded)]

class AtmosphereEncoding(SylEncoding):
    """ 'Twohot' encoding based on the atmosphere of a syllogism. Quantifiers
    are encoded as two-dimensional vectors indicating universality
    (universal vs. particular) and polarity (positive vs. negative). Task
    encodings are concatenations of the encoded subparts.

    """

    def encode_syllogism(self, syllogism):
        """ Encodes a given syllogistic problem.

        Parameters
        ----------
        syllogism : str
            Syllogistic task identifier (e.g., 'AA1').

        Returns
        -------
        ndarray
            Syllogistic task encoding.

        """

        # Extract info
        prem_1 = syllogism[0]
        prem_2 = syllogism[1]
        figure = syllogism[2]

        # Encode the syllogism
        encoding = np.zeros((6,), dtype='int')
        encoding[0] = prem_1 in ['A', 'E']
        encoding[1] = prem_1 in ['A', 'I']
        encoding[2] = prem_2 in ['A', 'E']
        encoding[3] = prem_2 in ['A', 'I']
        encoding[4:] = np.array(
            [int(x) for x in '{:02b}'.format(int(figure) - 1)])

        return encoding

    def encode_response(self, response):
        """ Encodes a given syllogistic response.

        Parameters
        ----------
        response : str
            Syllogistic response identifier (e.g., 'Aac').

        Returns
        -------
        ndarray
            Syllogistic response encoding (dim 4).

        """

        if response == 'NVC':
            return np.array([1, 1, 1, 0])
        elif response == 'Misc':
            return np.array([0, 0, 0, 0])

        # Construct encoding
        encoding = np.zeros((4,), dtype='int')
        encoding[0] = response[0] in ['A', 'E']
        encoding[1] = response[0] in ['A', 'I']
        encoding[2] = 0 if response[1:] == 'ac' else 1
        encoding[3] = 1

        return encoding

    def decode_syllogism(self, encoded):
        """ Decodes a given syllogistic task encoding.

        Parameters
        ----------
        encoded : ndarray
            Syllogistic task encoding to decode (dim 6).

        Returns
        -------
        str
            Syllogistic task identifier (e.g., 'AA1').

        """

        if len(encoded) != 6:
            raise ValueError(
                'Atmosphere problem encodings are expected to be of dim 6.')

        prem_1 = encoded[0:2]
        prem_2 = encoded[2:4]
        figure = encoded[4:]

        return self._decode_prem(prem_1) + \
            self._decode_prem(prem_2) + \
            str(int(''.join([str(x) for x in figure]), 2) + 1)

    def decode_response(self, encoded):
        """ Decodes a given syllogistic response encoding.

        Parameters
        ----------
        encoded : ndarray
            Syllogistic response encoding to decode.

        Returns
        -------
        str
            Syllogistic response identifier (e.g., 'Aac').

        """

        if len(encoded) != 4:
            raise ValueError(
                'Atmosphere response encodings are expected to be of dim 4.')

        if encoded[3] == 0:
            if np.all(encoded == 0):
                return 'Misc'
            return 'NVC'

        return self._decode_prem(encoded[0:2]) + \
            ('ac' if encoded[2] == 0 else 'ca')

    @staticmethod
    def _decode_prem(prem):
        """ Helper function to decode atmosphere-encoded premises.

        Parameters
        ----------
        prem : ndarray
            Encoded premise (dim 2).

        Returns
        -------
        char
            Character identifying the quantifier of the premise (i.e.,
            [A, I, E, O]).

        """

        if len(prem) != 2:
            raise ValueError(
                'Atmosphere premise decoding expects vector of dim 2.')

        if np.all(prem == [0, 0]):
            return 'O'
        if np.all(prem == [0, 1]):
            return 'I'
        if np.all(prem == [1, 0]):
            return 'E'
        return 'A'
