from contextlib import contextmanager
import os
import sys
import copy

import pandas as pd

import ccobra

import modelimporter

@contextmanager
def dir_context(path):
    old_dir = os.getcwd()
    os.chdir(path)
    sys.path.append(path)
    try:
        yield
    finally:
        os.chdir(old_dir)
        sys.path.remove(path)

class Evaluator(object):
    def __init__(self, modellist, test_datafile, train_datafile=None, silent=False):
        self.modellist = modellist
        self.silent = silent

        self.domains = set()
        self.response_types = set()

        # Load the datasets
        self.test_data = ccobra.data.CCobraData(pd.read_csv(test_datafile))
        print(list(self.test_data.get()))
        self.domains.update(self.test_data.get()['domain'].unique())
        self.response_types.update(self.test_data.get()['response_type'].unique())

        self.train_data = None
        if train_datafile:
            self.train_data = ccobra.data.CCobraData(pd.read_csv(train_datafile))
            self.domains.update(self.train_data.get()['domain'].unique())
            self.response_types.update(self.train_data.get()['response_type'].unique())

    def extract_optionals(self, data):
        essential = self.test_data.required_fields
        optionals = set(data.keys()) - set(essential)
        return {key: data[key] for key in optionals}

    def extract_demographics(self, data_df):
        demographics = {}
        demo_data = ['age', 'gender', 'education', 'affinity', 'experience']
        for data in demo_data:
            if data in data_df.columns:
                demographics[data] = data_df[data].values.tolist()
        return demographics

    def tuple_to_string(self, tuptup):
        def join_deepest(tup, sep=';'):
            if not isinstance(tup, list):
                return tup
            if not isinstance(tup[0], list):
                return sep.join(tup)
            else:
                for idx in range(len(tup)):
                    tup[idx] = join_deepest(tup[idx], sep)
                return tup

        tup = copy.deepcopy(tuptup)
        tup = join_deepest(tup, ';')
        tup = join_deepest(tup, '/')

        # Sort the tuples
        tup = sorted(tup) if isinstance(tup, list) else tup

        tup = join_deepest(tup, '|')
        return tup

    def evaluate(self):
        result_data = []

        # Activate model context
        for idx, model in enumerate(self.modellist):
            if not self.silent:
                print("Evaluating '{}' ({}/{})...".format(
                    model, idx + 1, len(self.modellist)))

            # Setup the model context
            context = os.path.dirname(os.path.abspath(model))
            with dir_context(context):
                importer = modelimporter.ModelImporter(
                    model, ccobra.CCobraModel)

                # Instantiate and prepare the model for predictions
                pre_model = importer.instantiate()

                # Check if model is applicable to domains/response types
                missing_domains = self.domains - set(pre_model.supported_domains)
                if len(missing_domains) > 0:
                    raise ValueError(
                        'Model {} is not applicable to domains {}.'.format(
                            pre_model.name, missing_domains))

                missing_response_types = self.response_types - set(pre_model.supported_response_types)
                if len(missing_response_types) > 0:
                    raise ValueError(
                        'Model {} is not applicable to response_types {}.'.format(
                            pre_model.name, missing_response_types))

                if self.train_data is not None:
                    # Prepare training data
                    train_data_dicts = []
                    for id_info, subj_df in self.train_data.get().groupby('id'):
                        subj_data = []
                        for seq_info, row in subj_df.sort_values(['sequence']).iterrows():
                            train_dict = {
                                'id': id_info,
                                'sequence': seq_info,
                                'item': ccobra.data.Item(
                                    row['domain'], row['task'],
                                    row['response_type'], row['choices'])
                            }

                            for key, value in row.iteritems():
                                if key not in train_dict:
                                    train_dict[key] = value

                            if train_dict['response_type'] == 'multiple-choice':
                                train_dict['response'] = [y.split(';') for y in [x.split('/') for x in train_dict['response'].split('|')]]
                            else:
                                train_dict['response'] = [x.split(';') for x in train_dict['response'].split('/')]

                            subj_data.append(train_dict)
                        train_data_dicts.append(subj_data)

                    pre_model.pre_train(train_data_dicts)

                # Iterate subject
                for subj_id, subj_df in self.test_data.get().groupby('id'):

                    model = copy.deepcopy(pre_model)

                    # Extract the subject demographics
                    demographics = self.extract_demographics(self.test_data.get())

                    # Set the models to new participant
                    model.start_participant(demographics=demographics)

                    for _, row in subj_df.sort_values('sequence').iterrows():
                        optionals = self.extract_optionals(row)

                        # Evaluation
                        sequence = row['sequence']
                        task = row['task']
                        choices = row['choices']
                        truth = row['response']
                        response_type = row['response_type']
                        domain = row['domain']

                        if response_type == 'multiple-choice':
                            truth = [y.split(';') for y in [x.split('/') for x in truth.split('|')]]
                        else:
                            truth = [x.split(';') for x in truth.split('/')]


                        item = ccobra.data.Item(domain, task, response_type,\
                        choices)

                        prediction = model.predict(item, **optionals)
                        prediction_str = self.tuple_to_string(prediction)

                        truth_str = self.tuple_to_string(truth)

                        # Adapt to true response
                        model.adapt(item, truth, **optionals)

                        result_data.append({
                            'model': model.name,
                            'id': subj_id,
                            'domain': domain,
                            'sequence': sequence,
                            'task': task,
                            'choices': choices,
                            'truth': truth,
                            'prediction': prediction_str,
                            'hit': prediction_str == truth_str,
                        })

        return pd.DataFrame(result_data)
