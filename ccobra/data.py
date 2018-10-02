""" CCOBRA data interfaces.

"""

class CCobraData():
    """ Abstract base class for CCOBRA datasets.

    """

    def __init__(self, domain):
        """ Initializes the CCOBRA data container by assigning a domain.

        """

        self.domain = domain

    def get(self):
        """ Returns the contained dataset.

        """

        raise NotImplementedError

class RawData():
    """ Interface label for raw datasets. Used for inheritance-based
    instance-checking magic.

    """

    pass
