""" CCOBRA data container.

"""

import logging

import pandas as pd
import numpy as np

from .item import Item


# Initialize module-level logger
logger = logging.getLogger(__name__)

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

        # Verify and store the data
        self.verify_data(data)
        self._data = data

        # Normalize the data container
        self.prepare_data()

        # Extract meta information
        self.n_subjects = len(self._data['_key_num_id'].unique())
        self.domains = self._data['domain'].unique().tolist()
        self.response_types = self._data['response_type'].unique().tolist()

    def verify_data(self, data):
        """ Verifies if all required fields are in the data.

        Parameters
        ----------
        data : pd.DataFrame
            DataFrame to verify.

        Raises
        ------
        ValueError
            Thrown if data does not contain required columns.

        """

        missing = set(self.required_fields) - set(data.columns)
        if missing:
            raise ValueError(
                "Data does not contain columns: {}".format(missing))

    def prepare_data(self):
        """ Prepares the dataset by adding internally_used columns

        """

        # Handle already existing key identifiers
        if '_key_num_id' in self._data:
            logger.debug('_key_num_id already in supplied data. Could be due to list data.')

            # Check uniqueness of key num id
            combs = set(zip(self._data['id'], self._data['_key_num_id']))
            key_num_id = [y for x, y in combs]

            num = sorted(key_num_id)
            uni = sorted(np.unique(key_num_id))

            if len(key_num_id) != len(np.unique(key_num_id)):
                raise ValueError('Dataframe provided with pre-existing non-unique _key_num_id')

            # If keys are unique, simply return
            return

        # Add unique numerical subject identifier
        # if pd.api.types.is_numeric_dtype(self._data['id']):
        #     self._data['_key_num_id'] = self._data['id']
        # else:
        ids = self._data['id'].unique().tolist()
        self._data['_key_num_id'] = self._data['id'].apply(lambda x: ids.index(x))

    def offset_identifiers(self, offset):
        """ Offsets the subject identifier keys.

        Parameters
        ----------
        offset : int
            Offset to apply to key numerical identifiers.

        """

        self._data['_key_num_id'] += offset

    def get(self):
        """ Returns the contained data.

        Returns
        -------
        pd.DataFrame
            Dataframe containing the data.

        """

        return self._data

    def head(self):
        return self._data.head()

    def to_eval_dict(self):
        # Prepare the dictionary of subjects containing lists of tasks they responded to
        df = self._data

        dataset = {}
        for subj, subj_df in df.groupby('_key_num_id'):
            assert subj not in dataset

            subj_df = subj_df.sort_values('sequence')

            subj_data = []
            for _, task_series in subj_df.iterrows():
                task_dict = {}

                # Extract the task information
                item = Item(
                    task_series['id'], task_series['domain'],
                    task_series['task'], task_series['response_type'],
                    task_series['choices'], task_series['sequence']
                )
                task_dict['item'] = item

                # Parse the responses
                responses = []
                for response in task_series['response'].split('|'):
                    responses.append([x.split(';') for x in response.split('/')])
                if task_series['response_type'] != 'multiple-choice':
                    responses = responses[0]
                task_dict['response'] = responses

                # Add auxiliary elements from the data
                aux = {}
                for key, value in task_series.iteritems():
                    if key not in self.required_fields + ['_key_num_id']:
                        aux[key] = value
                task_dict['aux'] = aux

                subj_data.append(task_dict)
            dataset[subj] = subj_data

        return dataset
