""" Implements a random uniform model.

"""

import numpy as np

from ._base import OrcaSylModel

class Random(OrcaSylModel):
    """ Model producing randomly generated responses.

    """

    def __init__(self, name='Random'):
        """ Initializes the random model.

        Parameters
        ----------
        name : str
            Unique name of the model. Will be used throughout the ORCA
            framework as a means for identifying the model.

        """

        super(Random, self).__init__(name)

        self.responses = [
            'Aac', 'Aca', 'Iac', 'Ica', 'Eac', 'Eca', 'Oac', 'Oca', 'NVC']

    def predict(self, syllogism, **kwargs):
        """ Predicts weighted responses to a given syllogism.

        Parameters
        ----------
        syllogism : str
            Syllogism to produce a response for.

        """

        return np.random.choice(self.responses, p=[1/9] * 9)
