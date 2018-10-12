""" CCOBRA data interfaces.

"""


class CCobraData():
    """ Abstract base class for CCOBRA datasets.

    """

    def __init__(self, data, required_fields=None):
        """ Initializes the CCOBRA data container by assigning a domain.

        """

        self.required_fields = [
            'id', 'sequence', 'task', 'choices', 'response',
            'response_type', 'domain'
        ]
        if required_fields:
            self.required_fields = required_fields


        self.verify_data(data)
        self._data = data

    def verify_data(self, data):
        """ Verify if all required fields are in the data

        """
        missing = set(self.required_fields) - set(data.columns)
        if missing:
            raise ValueError(
                "Data does not contain columns: {}".format(missing))

    def get(self):
        """ Returns the contained data.
        Returns
        -------
        pd.DataFrame
            Dataframe containing the data.
        """

        return self._data


class Item():
    """ Container class for representing task items

    """

    def __init__(self, domain, task, resp_type, choices):
        self.response_type = resp_type
        self.task = [x.split(";") for x in task.split("/")]
        self.choices = [x.split(";") for x in choices.split("/")]
        self.domain = domain
