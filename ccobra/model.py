""" CCOBRA model interface. Defines the general structure a model needs to
implement for being used in the CCOBRA framework.

"""

import logging


# Initialize module-level logger
logger = logging.getLogger(__name__)

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

        self.evaluation_type = None

    def setup_environment(self, evaluation_type):
        """ Setup environment of the model using information about the prediction setting and the
        information provided during training.

        Parameters
        ----------
        evaluation_type : str
            Type of the CCOBRA evaluation (adaption, coverage).

        """

        self.evaluation_type = evaluation_type

    def start_participant(self, **kwargs):
        """ Callback to indicate participant start.

        """

        pass

    def end_participant(self, identifier, model_log, **kwargs):
        """ Hook for when participant simulation ends.

        Parameters
        ----------
        identifier : str or int
            Participant identifier.

        model_log : dict(str, object)
            Dictionary to allow the model to log information for the final output (e.g., parameter
            configurations for this participant).
        """

        pass

    def pre_train(self, dataset):
        """ Pre-trains the model based on given group data. This data is not necessarily other
        participants from the same experiment, but can also refer to an unrelated external dataset.
        The information supplied here represents the information known about the general population
        in the domain of interest.

        Parameters
        ----------
        dataset : list(list(dict(str, object)))
            Training data for the model. List of participants which each
            contain lists of tasks represented as dictionaries with the
            corresponding task information (e.g., the item container and
            given response).

        """

        pass

    def pre_train_person(self, dataset):
        """ Excerpt of the prediction data containing responses of the individual. Is supposed to
        combat the cold-start problem by supplying models with information about the exact
        individual to be predicted for. Allows to fit models to a specific individual. For
        example, in coverage settings, the responses given by the individual are supplied here.

        If not overriden by the model implemenation, uses adapt to perform the training.

        Parameters
        ----------
        dataset : list(dict(str, object))
            Training data for the model. List of tasks containing the items
            and corresponding responses.

        """

        if len(dataset) == 0:
            return

        for task_data in dataset:
            self.adapt(
                task_data['item'],
                task_data['response'],
                **dict([x for x in task_data.items() if x[0] not in ['item', 'response']])
            )

    def pre_person_background(self, dataset):
        """ Background information about the person to be predicted for. In contrast to the
        data supplied by pre_adapt, the data given here is not extracted from the test data.
        For example, could be responses given by the individual in question to an external
        independent experiment (e.g., participated in a spatial-relation experiment and later
        in a syllogistic experiment which serve as the test data).

        Parameters
        ----------
        dataset : list(dict(str, object))
            Training data for the model. List of tasks containing the items
            and corresponding responses.

        """

        pass

    def predict(self, item, model_log, **kwargs):
        """ Generates a single response prediction for a given task.

        Parameters
        ----------
        item : ccobra.Item
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
        item : ccobra.Item
            Task information container. Holds the task text, response type,
            response choices, etc.

        target : str
            True response given by the human reasoner.

        """

        pass
