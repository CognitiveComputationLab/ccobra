""" ORCA data interfaces.

"""

class OrcaData(object):
    """ Abstract base class for ORCA datasets.

    """

    def __init__(self, domain):
        """ Initializes the ORCA data container by assigning a domain.

        """

        self.domain = domain

    def get(self):
        """ Returns the contained dataset.

        """

        raise NotImplementedError

class RawData(object):
    """ Interface label for raw datasets. Used for inheritance-based
    instance-checking magic.

    """

    pass
