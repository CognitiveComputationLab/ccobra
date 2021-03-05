""" CCOBRA data container.

"""

import copy
import logging

from . import convert_to_basic_types
from .item import Item

# Initialize module-level logger
logger = logging.getLogger(__name__)

class CCobraData():
    """ CCobra experimental data container.

    """

    def __init__(self, data, target_columns):
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

        self.target_columns = target_columns
        self.required_fields = [
            'id', 'sequence', 'task', 'choices', 'response_type', 'domain'
        ] + target_columns

        # Verify and store the data
        self.verify_data(data)
        self._data = data

        # Normalize the data container
        self.prepare_data()

        # Extract meta information
        self.n_subjects = len(self._data['_unique_id'].unique())
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

        assert '_unique_id' not in self._data

        # Add unique numerical subject identifier
        self._data['_unique_id'] = self._data['id']

    def prefix_identifiers(self, prefix='_train_'):
        """ Prefixes the subject identifier keys.

        Parameters
        ----------
        prefix : str
            Prefix to apply to key numerical identifiers.

        """

        self._data['_unique_id'] = self._data['_unique_id'].apply(lambda x: prefix + str(x))

    def get(self):
        """ Returns the contained data.

        Returns
        -------
        pd.DataFrame
            Dataframe containing the data.

        """

        return self._data

    def head(self):
        """ Displays the first 10 lines of the dataframe.

        """

        return self._data.head()

    def to_eval_dict(self):
        """ Converts the dataset to an evaluation dictionary mapping from individuals to data.

        Returns
        -------
        dict(object, list)
            Dictionary mapping from subject identifiers to lists of experimental data.

        """

        # Prepare the dictionary of subjects containing lists of tasks they responded to
        df = self._data

        dataset = {}
        for subj, subj_df in df.groupby('_unique_id'):
            assert subj not in dataset

            subj_df = subj_df.sort_values('sequence')

            subj_data = []
            for task_series in subj_df.itertuples():
                task_series = task_series._asdict()
                task_dict = {}

                # Extract the task information
                item = Item(
                    task_series['id'], task_series['domain'],
                    task_series['task'], task_series['response_type'],
                    task_series['choices'], task_series['sequence']
                )
                task_dict['item'] = item

                # Parse the main response
                responses = None
                if isinstance(task_series['response'], str):
                    responses = []
                    for response in task_series['response'].split('|'):
                        responses.append([x.split(';') for x in response.split('/')])
                    if task_series['response_type'] != 'multiple-choice':
                        responses = responses[0]
                else:
                    responses = task_series['response']
                task_dict['response'] = convert_to_basic_types(responses)

                # Parse the auxiliary targets
                for target_col in self.target_columns:
                    if target_col == 'response':
                        continue

                    if isinstance(task_series[target_col], str):
                        responses = []
                        for response in task_series[target_col].split('|'):
                            responses.append([x.split(';') for x in response.split('/')])
                    else:
                        responses = task_series[target_col]
                    task_dict[target_col] = responses

                # Add auxiliary elements from the data
                aux = {}
                for key, value in task_series.items():
                    if key not in self.required_fields + ['_unique_id']:
                        aux[key] = value
                task_dict['aux'] = aux

                task_dict['full'] = copy.deepcopy(task_dict['aux'])
                for target_col in self.target_columns:
                    task_dict['full'][target_col] = task_dict[target_col]

                subj_data.append(task_dict)
            dataset[subj] = subj_data

        return dataset
