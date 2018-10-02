""" Syllogistic ORCA model base class implementation.

"""

from ..model import CCobraModel

class SylModel(CCobraModel):
    """ Base class for syllogistic models.

    """

    def __init__(self, name='SylModel'):
        """ Initializes the model with a given name.

        Parameters
        ----------
        name : str
            Unique name of the model. Will be used throughout the ORCA
            framework as a means for identifying the model.

        """

        super(SylModel, self).__init__(name=name, domain='Syllogistic')

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

        pass
