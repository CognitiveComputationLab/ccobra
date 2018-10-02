""" Module containing syllogistic data containers.

"""

import pandas as pd
import numpy as np

from ..data import CCobraData, RawData
from .syllogisms import get_responses, get_syllogisms

class SylData(CCobraData):
    """ Base class for syllogistic data.

    """

    def __init__(self):
        """ Sets up abstract syllogistic data containers by loading the list
        of syllogisti problem and response identifiers.

        """

        super(SylData, self).__init__('Syllogistic')

        self.syllogisms = get_syllogisms()
        self.responses = get_responses()

class RawSylData(SylData, RawData):
    """ Container class for raw syllogistic data containing string
    representations for problems (e.g., 'AA1') and responses (e.g., 'Aac').

    """

    def __init__(self, data):
        """ Initializes the raw syllogistic data container by checking the
        given dataset.

        Parameters
        ----------
        data : pd.DataFrame
            DataFrame containing information about syllogisms.

        """

        super(RawSylData, self).__init__()

        # Assert data validity
        required_cols = [
            'id', 'sequence', 'task', 'response',
            'task_text', 'response_order', 'rt_ms',
            'age', 'gender', 'education', 'affinity', 'experience'
        ]
        for required_col in required_cols:
            if required_col not in data:
                raise ValueError(
                    "Data does not contain required col '{}'".format(
                        required_col))
        if not np.all(x in self.responses for x in data['response'].unique()):
            raise ValueError('Data contains invalid responses.')
        if not np.all(x in self.syllogisms for x in data['task'].unique()):
            raise ValueError('Data contains invalid tasks.')

        # Make syllogism sortable
        data['task'] = pd.Categorical(
            data['task'], categories=self.syllogisms, ordered=True)
        data = data.sort_values(['id', 'task'])

        self._data = data

    def get(self):
        """ Returns the raw syllogistic data.

        Returns
        -------
        pd.DataFrame
            Dataframe containing the raw syllogistic data.

        """

        return self._data

class EncSylData(SylData):
    """ Container class for encoded syllogistic data. Is constructed on the
    basis of raw syllogistic data and an encoder.

    """

    def __init__(self, syldata, encoder):
        """ Constructs the encoded syllogistic data container based on raw
        data and an encoder.

        Parameters
        ----------
        syldata : :class:RawSylData
            Raw syllogistic data to encode.

        encoder : :class:SylEncoding
            Encoder to use for encoding the raw dataset.

        """

        super(EncSylData, self).__init__()

        if not isinstance(syldata, RawSylData):
            raise ValueError('Given data is not RawSylData.')

        data = syldata.get()
        encoded_data = []
        for _, series in data.iterrows():
            encoded_data.append({
                'id': series['id'],
                'sequence': series['sequence'],
                'task': encoder.encode_syllogism(series['task']),
                'response': encoder.encode_response(series['response'])
            })
        encoded = pd.DataFrame(encoded_data)

        self._data = encoded

    def get(self):
        """ Returns the encoded syllogistic dataset.

        Returns
        -------
        pd.DataFrame
            Dataframe containing the encoded syllogistic data.

        """
        return self._data
