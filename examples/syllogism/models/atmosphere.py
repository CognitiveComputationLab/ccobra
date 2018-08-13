""" Atmosphere model implementation.

"""

import numpy as np

from orca import OrcaModelSyl

def atmosphere_predictions(premises):
    """ Produces atmosphere predictions to a given tuple of premises.

    Parameters
    ----------
    premises : list(str)
        List of premises (e.g., 'AA').

    Returns
    -------
    list(str)
        List of atmosphere predictions (e.g., ['Aac', 'Aca'])

    """

    responses = []
    if premises == 'AA':
        responses = ['Aac', 'Aca']
    elif premises == 'AI':
        responses = ['Iac', 'Ica']
    elif premises == 'AE':
        responses = ['Eac', 'Eca']
    elif premises == 'AO':
        responses = ['Oac', 'Oca']
    elif premises == 'EE':
        responses = ['Eac', 'Eca']
    elif premises == 'EI':
        responses = ['Oac', 'Oca']
    elif premises == 'EO':
        responses = ['Oac', 'Oca']
    elif premises == 'II':
        responses = ['Iac', 'Ica']
    elif premises == 'IO':
        responses = ['Oac', 'Oca']
    elif premises == 'OO':
        responses = ['Oac', 'Oca']
    return responses


class Atmosphere(OrcaModelSyl):
    """ Atmosphere theory implementation.

    """

    def __init__(self, name='Atmosphere'):
        """ Initializes the Atmosphere model.

        Parameters
        ----------
        name : str
            Unique name of the model. Will be used throughout the ORCA
            framework as a means for identifying the model.

        """

        super(Atmosphere, self).__init__(name)

    def start_participant(self, **kwargs):
        """ The static model does not need to be initialized.

        """

        pass

    def pre_train(self, dataset):
        """ Static model does not need pre-training.

        """

        pass

    def predict(self, syllogism, **kwargs):
        """ Predicts weighted responses to a given syllogism.

        Parameters
        ----------
        syllogism : str
            Syllogism to produce a response for.

        """

        premises = ''.join(sorted(syllogism[:2]))
        return np.random.choice(atmosphere_predictions(premises))

    def adapt(self, syllogism, target, **kwargs):
        """ Static model. Does not need to adapt.

        """

        pass
