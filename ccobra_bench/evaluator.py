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

        # Load the datasets
        self.test_df = ccobra.data.CCobraData(pd.read_csv(test_datafile))
        self.train_df = None
        if train_datafile:
            self.train_df = ccobra.data.CCobraData(pd.read_csv(train_datafile))

    def extract_optionals(self, data):
        essential = self.test_df.required_fields
        optionals = set(data.keys()) - set(essential)
        return {key: data[key] for key in optionals}

    def extract_demographics(self, data_df):
        demographics = {}
        demo_data = ['age', 'gender', 'education', 'affinity', 'experience']
        for data in demo_data:
            if data in data_df.columns:
                demographics[data] = data_df[data].values.tolist()
        return demographics
         
    def tuple_to_string(self, tuple):
        if not isinstance(tuple, list):
            return tuple
        else:
            return ";".join(tuple)

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
                if self.train_df is not None:
                    pre_model.pre_train(self.train_df)

                # Iterate subject
                for subj_id, subj_df in self.test_df.get().groupby('id'):

                    model = copy.deepcopy(pre_model)
                    
                    # Extract the subject demographics
                    demographics = self.extract_demographics(self.test_df.get())

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

                        item = ccobra.data.Item(domain, task, response_type,\
                        choices)

                        prediction = model.predict(item, **optionals)
                        prediction = self.tuple_to_string(prediction)

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
                            'prediction': prediction,
                            'hit': prediction == truth,
                        })

        return pd.DataFrame(result_data)
