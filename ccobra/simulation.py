""" Simulation class based on a list of models as well as a pre-recorded
dataset.

"""

import time

import pandas as pd

from .data import RawData

class Simulation():
    """ Class defining a simulation experiment for the ORCA framework. Provides
    facilities to evaluate a set of models based on a dataset consisting of
    sequential reasoning data.

    """

    def __init__(self, simulation_data, train_data=None):
        """ Initializes an empty Simulation object.

        """

        if not isinstance(simulation_data, RawData):
            raise ValueError('Simulation data is not CCobraData.')

        if train_data and not isinstance(train_data, RawData):
            raise ValueError('Training data is not CCobraData.')

        if train_data and simulation_data.domain != train_data.domain:
            raise ValueError('Invalid data domains.')

        self.domain = simulation_data.domain
        self.simulation_data = simulation_data
        self.train_data = train_data

        self.models = []

    def add_model(self, model):
        """ Adds a model to the simulaiton.

        Parameters
        ----------
        model : ccobra.model.CCobraModel
            Model to add to the simulation.

        """

        if self.domain != model.domain:
            raise ValueError('Invalid model domain.')

        self.models.append(model)

    def run(self):
        """ Runs the simulation. First, pre-trains the model based on the given
        dataset. Then, iterates over individual subjects and computes the
        individual model performance.

        Returns
        -------
        pd.DataFrame
            Diagnostics.

        """

        data_df = self.simulation_data.get()

        # Pre-train the models
        if self.train_data:
            train_df = self.train_data.get()
            for model in self.models:
                print('Pre-training {}...'.format(model.name))
                model.pre_train(train_df)
            print()

        # Run the simulation per participant
        result_df = pd.DataFrame()
        time_mean = 0
        time_nums = 0
        for subj_id, subj_df in data_df.groupby('id'):
            print('Simulating subject {:03d}...'.format(subj_id))

            start = time.time()
            res = self._run(subj_df)
            time_mean = time_mean * time_nums + (time.time() - start)
            time_nums += 1
            time_mean /= time_nums

            res['id'] = subj_id
            result_df = pd.concat([result_df, res])

            remaining = len(data_df['id'].unique()) - len(result_df['id'].unique())
            print('   ... done (~{:.2f}s remaining)'.format(remaining * time_mean))

        return result_df

    def _run(self, data_df):
        """ Executes the simulation based on a given dataset. Iterates over
        individuals in the dataset and computes the accuracy-based performance
        of the list of models.

        Parameters
        ----------
        data_df : pd.DataFrame
            DataFrame providing the data for the simulation. Must contain the
            columns ['sequence', 'task', 'response'].

        Returns
        -------
        pd.DataFrame
            Simulation results consisting of the following columns:
            ['model', 'sequence', 'task', 'response', 'prediction', 'hit']

        """

        # Extract the subject demographics
        demographics_df = data_df[[
            'age', 'gender', 'education', 'affinity', 'experience']]
        demographics = demographics_df.iloc[0].to_dict()

        # Set the models to new participant
        for model in self.models:
            model.start_participant(demographics=demographics)

        results = []
        for _, row in data_df.sort_values('sequence').iterrows():
            sequence = row['sequence']
            task = row['task']
            task_text = row['task_text']
            response_order = row['response_order']
            response = row['response']
            rt_ms = row['rt_ms']

            for model in self.models:
                # Generate the prediction
                time_pred = time.time()
                pred = model.predict(
                    task, task_text=task_text, response_order=response_order)
                time_pred = time.time() - time_pred

                # Train on this task-target combination
                time_adapt = time.time()
                model.adapt(task, response, rt_ms=rt_ms)
                time_adapt = time.time() - time_adapt

                results.append({
                    'model': model.name,
                    'sequence': sequence,
                    'task': task,
                    'response': response,
                    'prediction': pred,
                    'hit': pred == response,
                    't_pred_ms': time_pred * 1000,
                    't_adapt_ms': time_adapt * 1000
                })

        return pd.DataFrame(results)

    def __str__(self):
        """ Pretty prints the simulation object's properties, i.e., the list
        of models.

        Returns
        -------
        str
            Pretty-print representation of the simulation's contents.

        """

        res = 'Simulation Object ({}) containing:'.format(self.domain)
        for model in self.models:
            res += '\n   ' + model.name
        return res
