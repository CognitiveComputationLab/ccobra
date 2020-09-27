""" Returns the response without further encoding. Useful, if values like reaction times
should be shown in the results.

"""

import ccobra

class IdentityResponseEncoder(ccobra.CCobraResponseEncoder):
    """ Identity encoder. Returns the response without further encoding

    """

    @staticmethod
    def encode_response(response, task):
        """ Encodes a response to its syllogistic encoding.

        Parameters
        ----------
        response : list(str)
            Any response that should be returned

        task : list(list(str))
            Unused

        Returns
        -------
        str
            The response

        """
        return response
