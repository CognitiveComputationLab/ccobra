""" Base classes for CCOBRA encoders.

"""

class CCobraResponseEncoder():
    """ Domain encoder class interface. Specifies the functions to be implemented by the
    domain-specific encoder instances.

    """

    def encode_response(self, response, task):
        """ Encodes a response

        Parameters
        ----------
        response : list(str)
            Response in tuple representation.

        task : list(list(str))
            Task in tuple representation.

        Returns
        -------
        str
            Response representation.

        """

        raise NotImplementedError()

class CCobraTaskEncoder():
    """ Domain encoder class interface. Specifies the functions to be implemented by the
    domain-specific encoder instances.

    """

    def encode_task(self, task):
        """ Encodes a task.

        Parameters
        ----------
        task : list(list(str))
            Task in tuple representation.

        Returns
        -------
        str
            Task representation.

        """

        raise NotImplementedError()
