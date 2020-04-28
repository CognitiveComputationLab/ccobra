""" CCOBRA data container.

"""

import pandas as pd

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

        # Extract meta information
        self.n_subjects = len(self._data['id'].unique())
        self.domains = self._data['domain'].unique().tolist()
        self.response_types = self._data['response_type'].unique().tolist()

        # Normalize the data container
        self.prepare_data()

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

        # Add unique numerical subject identifier
        if pd.api.types.is_numeric_dtype(self._data['id']):
            self._data['_key_num_id'] = self._data['id']
        else:
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
