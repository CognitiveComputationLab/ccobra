""" CCOBRA model interfaces.

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
            
        supported_domains : list
            List containing the domains that are supported by the model
            
        supported_response_types : list
            List containing the response types that are supported by the model

        """

        self.name = name
        self.supported_domains = supported_domains
        self.supported_response_types = supported_response_types

    def start_participant(self, **kwargs):
        """ Model initialization method. Used to setup the initial state of its
        datastructures, memory, etc.

        **Attention**: Should reset the internal state of the model. Will be
        called between experimental runs.

        """

        pass

    def pre_train(self, dataset):
        """ Pre-trains the model based on one or more datasets.

        Parameters
        ----------
        dataset : :class:`ccobra.data.RawData`
            CCOBRA raw data container.

        """

        pass

    def predict(self, item, **kwargs):
        """ Predicts weighted responses to a given syllogism.

        Parameters
        ----------
        task : str
            Reasoning task to produce a prediction for.

        Returns
        -------
        ndarray
            Model prediction.

        """

        raise NotImplementedError()

    def adapt(self, item, target, **kwargs):
        """ Trains the model based on a given task-target combination.

        Parameters
        ----------
        syllogism : str
            Task to produce a response for.

        target : str
            True target answer.

        """

        pass
