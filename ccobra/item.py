""" CCOBRA task item container.

"""

from . import convert_to_basic_types

class Item():
    """ Container class for representing task items.

    """

    def __init__(self, identifier, domain, task, resp_type, choices, sequence_number):
        """ Constructs the task item container with information about the
        domain, task premises, response type, and response choices.

        Parameters
        ----------
        identifier : object
            Unique identifier for the participant.

        domain : str
            Task domain (e.g., 'syllogistic').

        task : str
            Task text in tuple string encoding (e.g.,
            'All;pilots;gardeners/Some;gardeners;cooks').

        resp_type : str
            Response type (e.g., 'single-choice').

        choices : list(str)
            Response options in string representation.

        sequence_number : int
            Position of the item in the experimental sequence.

        """

        #: Unique identifier of the participant
        self.identifier = identifier

        #: Response type of the task
        self.response_type = resp_type

        #: Task string representation
        self.task_str = task

        #: Task in list representation
        self.task = [x.split(";") for x in task.split("/") if x]

        #: Choices string representation
        self.choices_str = choices

        #: Choices in list representation
        self.choices = [x.split('/') for x in choices.split('|')]
        for idx in range(len(self.choices)):
            self.choices[idx] = [x.split(';') for x in self.choices[idx]]
        self.choices = convert_to_basic_types(self.choices)

        #: Domain of the task
        self.domain = domain

        #: Position of the task in the experimental sequence
        self.sequence_number = sequence_number

    def __eq__(self, other):
        """ Equality comparator.

        Parameters
        ----------
        other : object
            Object to compare with.

        Returns
        -------
        bool
            True, if object is equal, false otherwise.

        """

        if not isinstance(other, Item):
            return False

        if self.identifier != other.identifier:
            return False
        if self.response_type != other.response_type:
            return False
        if self.task_str != other.task_str:
            return False
        if self.choices_str != other.choices_str:
            return False
        if self.domain != other.domain:
            return False
        if self.sequence_number != other.sequence_number:
            return False

        return True

    def __ne__(self, other):
        """ Not-Equal comparator. Defines unequality as the converse of equality.

        Parameters
        ----------
        other : object
            Object to compare to.

        Returns
        -------
        bool
            True, if object is unequal.

        """

        return not self.__eq__(other)

    def __str__(self):
        """ String representation of the item.

        Returns
        -------
        str
            String representation of the item.

        """

        rep = 'CCOBRA Item:\n'
        rep += '\tIdentifier: {}\n'.format(self.identifier)
        rep += '\tTask: {}\n'.format(self.task)
        rep += '\tSequence Number: {}\n'.format(self.sequence_number)
        rep += '\tDomain: {}\n'.format(self.domain)
        rep += '\tResponse Type: {}\n'.format(self.response_type)
        rep += '\tChoices: {}'.format(self.choices)
        return rep
