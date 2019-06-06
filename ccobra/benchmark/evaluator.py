""" CCOBRA evaluation module.

"""

import os
import sys
import copy
import warnings

import pandas as pd
import numpy as np

import ccobra

from . import modelimporter
from . import comparator
from . import contextmanager


class Evaluator():
    """ Main CCOBRA evaluation class. Hosts training data loading and model evaluation loop.

    """

    def __init__(self, modellist, eval_comparator, test_datafile, train_datafile=None,
                 train_data_person=None, silent=False, corresponding_data=False,
                 domain_encoders=None):
        """

        Parameters
        ----------
        modellist : list(ccobra.ModelInfo)
            List containing model paths and additional arguments for model initialization.

        eval_comparator : Comparator
            Comparator to be used for computing hits/misses.

        test_datafile : str
            Path to the test data file.

        train_datafile : str
            Path to the general training data file.

        train_data_person : str
            Path to the person training data file.

        silent : bool
            Indicates whether evaluation progress should be logged using print statements.

        corresponding_data : bool
            Indicates whether test and training data should contain the same
            user ids.

        domain_encoders : dict(str, ccobra.CCobraDomainEncoder)
            Mapping from domain to encoder object.

        """

        self.modellist = modellist
        self.silent = silent

        self.domains = set()
        self.response_types = set()

        self.comparator = eval_comparator
        self.corresponding_data = corresponding_data
        self.domain_encoders = domain_encoders

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

        Parameters
        ----------
        data : pd.Series
            Pandas series (i.e. row of the data) to extract optional information from.

        Returns
        -------
        dict(str, object)
            Dictionary containing optional information stored in the data (e.g., age, gender).

        """

        essential = self.test_data.required_fields
        optionals = set(data.keys()) - set(essential)
        return {key: data[key] for key in optionals}

    def extract_demographics(self, data_df):
        """ Extracts demographic information (age, gender, education, affinity, experience) from
        a given dataset if the corresponding columns are available.

        Parameters
        ----------
        data_df : pd.DataFrame
            Dataframe to extract demographic information from.

        Returns
        -------
        dict(str, object)
            Dictionary containing demographic information.

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

        Parameters
        ----------
        pre_model : CCobraModel
            Model to check applicability for.

        Raises
        ------
        ValueError
            Exception thrown when model is not applicable to some domains or response types
            in the test data.

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

        Parameters
        ----------
        ccobra_data : ccobra.CCobraData
            Data to convert to the training data representation.

        Returns
        -------
        dict
            Dictionary containing the training information (item, response, etc.).

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

        Returns
        -------
        pd.DataFrame
            DataFrame containing the CCOBRA evaluation results.

        """

        result_data = []
        model_name_cache = set()

        # Pre-compute the training data dictionaries
        train_data_dict = None
        if self.train_data is not None:
            train_data_dict = self.get_train_data_dict(self.train_data)

        # Activate model context
        for idx, modelinfo in enumerate(self.modellist):
            # Print the progress
            if not self.silent:
                print("Evaluating '{}' ({}/{})...".format(
                    modelinfo.path, idx + 1, len(self.modellist)))

            # Setup the model context
            with contextmanager.dir_context(modelinfo.path):
                # Dynamically import the CCOBRA model
                importer = modelimporter.ModelImporter(
                    modelinfo.path, ccobra.CCobraModel,
                    load_specific_class=modelinfo.load_specific_class)

                # Instantiate and prepare the model for predictions
                pre_model = importer.instantiate(modelinfo.args)

                # Check if model is applicable to domains/response types
                self.check_model_applicability(pre_model)

                # Only use the model's name if no override is specified
                model_name = modelinfo.override_name
                if not model_name:
                    model_name = pre_model.name

                # Ensure that names are unique and show a warning if duplicates are detected
                original_model_name = model_name
                changed = False
                while model_name in model_name_cache:
                    model_name = model_name + '\''
                    changed = True
                model_name_cache.add(model_name)

                if changed:
                    warnings.warn('Duplicate model name detected ("{}"). Changed to "{}".'.format(
                        original_model_name, model_name))

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

                    # Iterate over individual tasks
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
                            subj_id, domain, task, response_type, choices, sequence)

                        prediction = model.predict(item, **optionals)
                        hit = int(self.comparator.compare(prediction, truth))

                        # Adapt to true response
                        adapt_item = ccobra.data.Item(
                            subj_id, domain, task, response_type, choices,
                            sequence)
                        model.adapt(adapt_item, truth, **optionals)

                        # Collect the evaluation result data
                        prediction_data = {
                            'model': model_name,
                            'id': subj_id,
                            'domain': domain,
                            'sequence': sequence,
                            'task': task,
                            'choices': choices,
                            'truth': row['response'],
                            'prediction': comparator.tuple_to_string(prediction),
                            'hit': hit
                        }

                        # If domain encoders are specified, attach encodings to the result
                        if self.domain_encoders:
                            prediction_data.update({
                                'task_enc': self.domain_encoders[domain].encode_task(item.task) if domain in self.domain_encoders else np.nan,
                                'truth_enc': self.domain_encoders[domain].encode_response(truth, item.task) if domain in self.domain_encoders else np.nan,
                                'prediction_enc': self.domain_encoders[domain].encode_response(prediction, item.task) if domain in self.domain_encoders else np.nan
                            })

                        result_data.append(prediction_data)

                    # Call the end participant hook
                    model.end_participant(subj_id, **optionals)

                # De-load the imported model and its dependencies. Might
                # cause garbage collection issues.
                importer.unimport()

        return pd.DataFrame(result_data)
