""" ORCA model interfaces.

"""

class OrcaModel():
    """ Base class for ORCA models.

    """

    def __init__(self, name, domain):
        """ Base constructor of ORCA models.

        Parameters
        ----------
        name : str
            Unique name of the model. Will be used throughout the ORCA
            framework as a means for identifying the model.

        domain : str
            Reasoning domain.

        """

        self.name = name
        self.domain = domain

    def start_participant(self, **kwargs):
        """ Model initialization method. Used to setup the initial state of its
        datastructures, memory, etc.

        **Attention**: Should reset the internal state of the model. Will be
        called between experimental runs.

        """

        raise NotImplementedError()

    def pre_train(self, dataset):
        """ Pre-trains the model based on one or more datasets.

        Parameters
        ----------
        dataset : :class:`orca.data.orcadata.RawData`
            ORCA raw data container.

        """

        raise NotImplementedError()

    def predict(self, task, **kwargs):
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

    def adapt(self, task, target, **kwargs):
        """ Trains the model based on a given task-target combination.

        Parameters
        ----------
        syllogism : str
            Task to produce a response for.

        target : str
            True target answer.

        """

        raise NotImplementedError()
