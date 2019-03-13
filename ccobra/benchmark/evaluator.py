""" CCOBRA evaluation module.

"""

from contextlib import contextmanager
import os
import sys
import copy

import pandas as pd
import numpy as np

import ccobra

from . import modelimporter
from . import comparator

@contextmanager
def dir_context(path):
    """ Context manager for the working directory. Stores the current working directory before
    switching it. Finally, resets to the old wd.

    """

    old_dir = os.getcwd()
    os.chdir(path)
    sys.path.append(path)
    try:
        yield
    finally:
        os.chdir(old_dir)
        sys.path.remove(path)

class Evaluator():
    """ Main CCOBRA evaluation class. Hosts training data loading and model evaluation loop.

    """

    def __init__(self, modeldict, eval_comparator, test_datafile, train_datafile=None,
                 train_data_person=None, silent=False, corresponding_data=False):
        """

        Parameters
        ----------
        corresponding_data : bool
            Indicates whether test and training data should contain the same
            user ids.

        """

        self.modeldict = modeldict
        self.silent = silent

        self.domains = set()
        self.response_types = set()

        self.comparator = eval_comparator
        self.corresponding_data = corresponding_data

        # Load the test data
        self.test_data = ccobra.CCobraData(pd.read_csv(test_datafile))
        self.domains.update(self.test_data.get()['domain'].unique())
        self.response_types.update(self.test_data.get()['response_type'].unique())

        # Load the general training data
        self.train_data = None
        if train_datafile:
            # Load the data. Domains and response types are not updated,
            # because training is considered optional information the models
            # are not forced to use.
            self.train_data = ccobra.CCobraData(pd.read_csv(train_datafile))

            # If non-corresponding datasets, update with new identification
            if not self.corresponding_data:
                test_ids = self.test_data.get()['id'].unique()

                # Identify the ID offset as the largest numerical index from
                # the test dataset.
                idx_offset = 0
                for identifier in test_ids:
                    # Strings cause the float conversion to throw an exception
                    # Numberness is identified accordingly.
                    try:
                        if idx_offset < float(identifier):
                            idx_offset = float(identifier)
                    except ValueError:
                        pass

                idx_offset = int(np.ceil(idx_offset)) + 1

                # Update the training IDs accordingly
                train_ids = self.train_data.get()['id'].unique()
                new_train_ids = dict(zip(train_ids, range(idx_offset, idx_offset + len(train_ids))))
                self.train_data.get()['id'].replace(new_train_ids, inplace=True)

        # Load the personal training data
        self.train_data_person = None
        if train_data_person:
            self.train_data_person = ccobra.CCobraData(
                pd.read_csv(train_data_person))

    def extract_optionals(self, data):
        """ Extracts optional model information from a given dataset by obtaining all non-essential
        columns (i.e., the non-required fields of CCOBRA datasets).

        """

        essential = self.test_data.required_fields
        optionals = set(data.keys()) - set(essential)
        return {key: data[key] for key in optionals}

    def extract_demographics(self, data_df):
        """ Extracts demographic information (age, gender, education, affinity, experience) from
        a given dataset if the corresponding columns are available.

        """

        demographics = {}
        demo_data = ['age', 'gender', 'education', 'affinity', 'experience']
        for data in demo_data:
            if data in data_df.columns:
                demographics[data] = data_df[data].unique().tolist()

                if len(demographics[data]) == 1:
                    demographics[data] = demographics[data][0]

        return demographics

    def check_model_applicability(self, pre_model):
        """ Verifies the applicability of a model by checking its supported domains and response
        types and comparing them with the evaluation dataset.

        """

        missing_domains = self.domains - set(pre_model.supported_domains)
        if missing_domains:
            raise ValueError(
                'Model {} is not applicable to domains {} found in ' \
                'the test dataset.'.format(
                    pre_model.name, missing_domains))

        missing_response_types = self.response_types - set(pre_model.supported_response_types)
        if missing_response_types:
            raise ValueError(
                'Model {} is not applicable to response_types {} ' \
                'found in the test dataset.'.format(
                    pre_model.name, missing_response_types))

    def get_train_data_dict(self, ccobra_data):
        """ Extracts the training data dict mapping from subject identifiers to their corresponding
        list of tasks and responses.

        """

        train_data_dict = {}
        for id_info, subj_df in ccobra_data.get().groupby('id'):
            subj_data = []
            for _, row in subj_df.sort_values(['sequence']).iterrows():
                train_dict = {}

                # Add the Item
                train_dict['item'] = ccobra.Item(
                    row['id'], row['domain'],
                    row['task'], row['response_type'],
                    row['choices'], row['sequence'])

                # Convert the response to its list representation
                if isinstance(row['response'], str):
                    if row['response_type'] == 'multiple-choice':
                        train_dict['response'] = [y.split(';') for y in [
                            x.split('/') for x in row['response'].split('|')]]
                    else:
                        train_dict['response'] = [x.split(';') for x in row['response'].split('/')]
                else:
                    train_dict['response'] = row['response']

                # Add the remaining elements
                for key, value in row.iteritems():
                    if key not in ccobra_data.required_fields:
                        train_dict[key] = value

                subj_data.append(train_dict)
            train_data_dict[id_info] = subj_data
        return train_data_dict

    def evaluate(self):
        """ CCobra evaluation loop. Iterates over the models and performs training and evaluation.

        """

        result_data = []

        # Pre-compute the training data dictionaries
        train_data_dict = None
        if self.train_data is not None:
            train_data_dict = self.get_train_data_dict(self.train_data)

        # Activate model context
        for idx, modelitem in enumerate(self.modeldict.items()):
            model, model_kwargs = modelitem

            # Print the progress
            if not self.silent:
                print("Evaluating '{}' ({}/{})...".format(
                    model, idx + 1, len(self.modeldict)))

            # Setup the model context
            context = os.path.abspath(model)
            if os.path.isfile(context):
                context = os.path.dirname(context)

            # Extract load_specific_class
            specific_class = None
            if 'load_specific_class' in model_kwargs:
                specific_class = model_kwargs['load_specific_class']
                del model_kwargs['load_specific_class']

            with dir_context(context):
                importer = modelimporter.ModelImporter(
                    model, ccobra.CCobraModel,
                    load_specific_class=specific_class)

                # Instantiate and prepare the model for predictions
                pre_model = importer.instantiate(model_kwargs)

                # Check if model is applicable to domains/response types
                self.check_model_applicability(pre_model)

                # Only perform general pre-training if training data is
                # supplied and corresponding data is false. Otherwise, the
                # model has to be re-trained for each subject.
                if self.train_data is not None and not self.corresponding_data:
                    # Prepare training data
                    pre_model.pre_train(list(train_data_dict.values()))

                # Iterate subject
                for subj_id, subj_df in self.test_data.get().groupby('id'):
                    model = copy.deepcopy(pre_model)

                    # Perform pre-training for individual subjects only if
                    # corresponding data is set to true.
                    if self.train_data is not None and self.corresponding_data:
                        # Remove one participant
                        cur_train_data_dict = [
                            value for key, value in train_data_dict.items() if key != subj_id]

                        # Train on incomplete training data
                        model.pre_train(cur_train_data_dict)

                    # Perform the personalized pre-training
                    if self.train_data_person is not None:
                        # Pick out the person training data for the current
                        # individual
                        subj_pre_train_data_person = self.train_data_person.get().loc[
                            self.train_data_person.get()['id'] == subj_id]

                        person_train_data = self.get_train_data_dict(
                            ccobra.CCobraData(subj_pre_train_data_person))
                        model.person_train(person_train_data[subj_id])

                    # Extract the subject demographics
                    demographics = self.extract_demographics(subj_df)

                    # Set the models to new participant
                    model.start_participant(id=subj_id, **demographics)

                    for _, row in subj_df.sort_values('sequence').iterrows():
                        optionals = self.extract_optionals(row)

                        # Evaluation
                        sequence = row['sequence']
                        task = row['task']
                        choices = row['choices']
                        truth = row['response']
                        response_type = row['response_type']
                        domain = row['domain']

                        if isinstance(truth, str):
                            if response_type == 'multiple-choice':
                                truth = [y.split(';') for y in [
                                    x.split('/') for x in truth.split('|')]]
                            else:
                                truth = [x.split(';') for x in truth.split('/')]

                        item = ccobra.data.Item(
                            subj_id, domain, task, response_type, choices,
                            sequence)

                        prediction = model.predict(item, **optionals)
                        hit = int(self.comparator.compare(prediction, truth))

                        # Adapt to true response
                        adapt_item = ccobra.data.Item(
                            subj_id, domain, task, response_type, choices,
                            sequence)
                        model.adapt(adapt_item, truth, **optionals)

                        result_data.append({
                            'model': model.name,
                            'id': subj_id,
                            'domain': domain,
                            'sequence': sequence,
                            'task': task,
                            'choices': choices,
                            'truth': row['response'],
                            'prediction': comparator.tuple_to_string(prediction),
                            'hit': hit,
                        })

                # De-load the imported model and its dependencies. Might
                # cause garbage collection issues.
                importer.unimport()

        return pd.DataFrame(result_data)
