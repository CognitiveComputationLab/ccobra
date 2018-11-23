""" CCOBRA model interface. Defines the general structure a model needs to
implement for being used in the CCOBRA framework.

"""


class CCobraModel():
    """ Base class for CCOBRA models.

    """

    def __init__(self, name, supported_domains, supported_response_types):
        """ Base constructor of CCOBRA models.

        Parameters
        ----------
        name : str
            Unique name of the model. Will be used throughout the CCOBRA
            framework as a means for identifying the model.

        supported_domains : list(str)
            List containing the domains that are supported by the model (e.g.
            'syllogistic').

        supported_response_types : list(str)
            List containing the response types that are supported by the model
            (e.g., 'single-choice')

        """

        self.name = name
        self.supported_domains = supported_domains
        self.supported_response_types = supported_response_types

    def start_participant(self, **kwargs):
        """ Model initialization method. Used to setup the initial state of its
        datastructures, memory, etc.

        **Attention**: Should reset the internal state of the model.

        """

        pass

    def pre_train(self, dataset):
        """ Pre-trains the model based on given training data.

        Parameters
        ----------
        dataset : list(list(dict(str, object)))
            Training data for the model. List of participants which each
            contain lists of tasks represented as dictionaries with the
            corresponding task information (e.g., the item container and
            given response).

        """

        pass

    def predict(self, item, **kwargs):
        """ Generates a single response prediction for a given task.

        Parameters
        ----------
        item : ccobra.data.Item
            Task information container. Holds the task text, response type,
            response choices, etc.

        Returns
        -------
        str
            Response prediction.

        """

        raise NotImplementedError()

    def adapt(self, item, target, **kwargs):
        """ Trains the model based on a given task-target combination.

        Parameters
        ----------
        item : ccobra.data.Item
            Task information container. Holds the task text, response type,
            response choices, etc.

        target : str
            True response given by the human reasoner.

        """

        pass
