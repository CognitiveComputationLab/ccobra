""" CCOBRA data containers.

"""


class CCobraData():
    """ CCobra experimental data container.

    """

    def __init__(self, data, required_fields=None):
        """ Initializes the CCOBRA data container by passing a data frame
        and validating its contents.

        Parameters
        ----------
        data : pd.DataFrame
            DataFrame to store in the CCOBRA data container.

        required_fields : list(str), optional
            List of required columns in the data. Defaults to ['id', 'sequence',
            'task', 'choices', 'response', 'response_type', 'domain']

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
        """ Verifies if all required fields are in the data.

        Parameters
        ----------
        data : pd.DataFrame
            DataFrame to verify.

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
    """ Container class for representing task items.

    """

    def __init__(self, domain, task, resp_type, choices):
        """ Constructs the task item container with information about the
        domain, task premises, response type, and response choices.

        Parameters
        ----------
        domain : str
            Task domain (e.g., 'syllogistic').

        task : str
            Task text in tuple string encoding (e.g.,
            'All;pilots;gardeners/Some;gardeners;cooks').

        """

        self.response_type = resp_type
        self.task = [x.split(";") for x in task.split("/")]
        self.choices = [x.split(";") for x in choices.split("/")]
        self.domain = domain

    def __str__(self):
        rep = 'CCOBRA Item:\n'
        rep += '\tTask: {}\n'.format(self.task)
        rep += '\tDomain: {}\n'.format(self.domain)
        rep += '\tResponse Type: {}\n'.format(self.response_type)
        rep += '\tChoices: {}'.format(self.choices)
        return rep
