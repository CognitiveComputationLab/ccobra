""" CCOBRA evaluation module.

"""

from contextlib import contextmanager
import os
import sys
import copy
import warnings

import pandas as pd
import numpy as np

import ccobra

from . import modelimporter
from . import comparator

import seaborn as sns
import matplotlib.pyplot as plt


pre_train_str = 'pre_train'
main_train_str = 'main_train'
adapt_str = 'adapt'
start_participant_str = 'start_participant'
person_train_str = 'person_train'

@contextmanager
def dir_context(path):
    """ Context manager for the working directory. Stores the current working directory before
    switching it. Finally, resets to the old wd.

    Parameters
    ----------
    path : str
        String to set the working directory to.

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

    def __init__(self, modellist, eval_comparator, test_datafile, train_datafile=None,
                 train_data_person=None, silent=False, corresponding_data=False):
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

        """

        self.modellist = modellist
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
            context = os.path.abspath(modelinfo.path)
            if os.path.isfile(context):
                context = os.path.dirname(context)

            with dir_context(context):
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
                        result_data.append({
                            'model': model_name,
                            'id': subj_id,
                            'domain': domain,
                            'sequence': sequence,
                            'task': task,
                            'choices': choices,
                            'truth': row['response'],
                            'prediction': comparator.tuple_to_string(prediction),
                            'hit': hit
                        })

                    # Call the end participant hook
                    model.end_participant(subj_id, **optionals)

                # De-load the imported model and its dependencies. Might
                # cause garbage collection issues.
                importer.unimport()

        return pd.DataFrame(result_data)


class LC_Evaluator(Evaluator):
    def __init__(self, *args, learning_curves_folder=None,
                 learning_curves_for=None, **kwargs):
        super().__init__(*args, **kwargs)
        if learning_curves_folder:
            learning_curves_folder = learning_curves_folder.rstrip('/')
        assert os.path.isdir(learning_curves_folder)
        learning_curves_folder = os.path.abspath(learning_curves_folder)
        self.learning_curves_folder = learning_curves_folder
        self.learning_curves_for = learning_curves_for

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
            model_evaluations = {}
            # Print the progress
            if not self.silent:
                print("Evaluating '{}' ({}/{})...".format(
                    modelinfo.path, idx + 1, len(self.modellist)))

            # Setup the model context
            context = os.path.abspath(modelinfo.path)
            if os.path.isfile(context):
                context = os.path.dirname(context)

            with dir_context(context):
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

                    model_evaluations[subj_id] = {}

                    # Perform pre-training for individual subjects only if
                    # corresponding data is set to true.
                    if self.train_data is not None and self.corresponding_data:
                        # Remove one participant
                        cur_train_data_dict = [
                            value for key, value in train_data_dict.items() if key != subj_id]

                        model_checkpoints = []
                        # Train on incomplete training data
                        model.pre_train(cur_train_data_dict,
                                        checkpoints=model_checkpoints)

                        if pre_train_str in self.learning_curves_for:
                            model_evaluations[subj_id][
                                pre_train_str] = self.evaluate_checkpoints(
                                model_checkpoints, subj_id)

                    # Perform the personalized pre-training
                    if self.train_data_person is not None:
                        # Pick out the person training data for the current
                        # individual
                        subj_pre_train_data_person = self.train_data_person.get().loc[
                            self.train_data_person.get()['id'] == subj_id]

                        model_checkpoints = []

                        person_train_data = self.get_train_data_dict(
                            ccobra.CCobraData(subj_pre_train_data_person))
                        model.person_train(person_train_data[subj_id],
                                           checkpoints=model_checkpoints)

                        if person_train_str in self.learning_curves_for:
                            model_evaluations[subj_id][
                                person_train_str] = self.evaluate_checkpoints(
                                model_checkpoints, subj_id)

                    # Extract the subject demographics
                    demographics = self.extract_demographics(subj_df)

                    model_checkpoints = []

                    # Set the models to new participant
                    model.start_participant(
                        id=subj_id, checkpoints=model_checkpoints,
                        **demographics)

                    if start_participant_str in self.learning_curves_for:
                        model_evaluations[subj_id][
                            start_participant_str] = self.evaluate_checkpoints(
                            model_checkpoints, subj_id)

                    if main_train_str in self.learning_curves_for:
                        model_evaluations[subj_id][
                            main_train_str] = self.evaluate_checkpoints(
                            [copy.deepcopy(model)], subj_id)

                    if adapt_str in self.learning_curves_for:
                        model_evaluations[subj_id][adapt_str] = {}

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

                        model_checkpoints = []

                        # Adapt to true response
                        adapt_item = ccobra.data.Item(
                            subj_id, domain, task, response_type, choices,
                            sequence)
                        model.adapt(adapt_item, truth,
                                    checkpoints=model_checkpoints,
                                    **optionals)

                        if adapt_str in self.learning_curves_for:
                            model_evaluations[subj_id][adapt_str][
                                sequence] = self.evaluate_checkpoints(
                                model_checkpoints, subj_id)

                        if main_train_str in self.learning_curves_for:
                            model_evaluations[subj_id][
                                main_train_str].append(
                                    self.evaluate_checkpoints(
                                        [copy.deepcopy(model)], subj_id)[0])

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

                if self.learning_curves_folder:
                    self.generate_learning_curves(model.name,
                                                  model_evaluations)

        return pd.DataFrame(result_data)

    def item_from_row(self, row, subj_id):
        optionals = self.extract_optionals(row)

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

        return tuple((item, optionals))

    def rollout(self, checkpoint, subj_id):
        subj_train_data = self.train_data._data.loc[
            self.train_data._data['id'] == subj_id].sort_values('sequence')
        subj_test_data = self.test_data._data.loc[
            self.test_data._data['id'] == subj_id].sort_values('sequence')

        train_items = [self.item_from_row(r, subj_id) for _, r in
                       subj_train_data.iterrows()]
        test_items = [self.item_from_row(r, subj_id) for _, r in
                      subj_test_data.iterrows()]

        train_targets = [r['response'] for _, r in subj_train_data.iterrows()]
        test_targets = [r['response'] for _, r in subj_test_data.iterrows()]

        train_accuracy = np.mean([int(self.comparator.compare(
            checkpoint.predict(i[0], **i[1]), t))
            for i, t in zip(train_items, train_targets)])

        test_accuracy = np.mean([int(self.comparator.compare(
            checkpoint.predict(i[0], **i[1]), t))
            for i, t in zip(test_items, test_targets)])

        return (train_accuracy, test_accuracy)

    def evaluate_checkpoints(self, checkpoint_list, subj_id):
        res = []
        for checkpoint in checkpoint_list:
            res.append(self.rollout(checkpoint, subj_id))
        return res

    def generate_learning_curves(self, model, model_evaluations):
        # eval all checkpoints
        data = []
        for subject, phase_dictionary in model_evaluations.items():
            for phase, checkpoint_evaluations in phase_dictionary.items():
                if phase == adapt_str:
                    continue  # handled seperately below
                else:
                    e = 0
                    for value_pair in checkpoint_evaluations:
                        e += 1
                        train_acc, test_acc = value_pair
                        data.append({'Model': model,
                                     'Subject': subject,
                                     'Phase': phase,
                                     'Epoch': e,
                                     'Acc': train_acc,
                                     'Train/Test': 'train'
                                     })
                        data.append({'Model': model,
                                     'Subject': subject,
                                     'Phase': phase,
                                     'Epoch': e,
                                     'Acc': test_acc,
                                     'Train/Test': 'test'
                                     })

        df1 = pd.DataFrame(data)

        # handle adaption: similar to other phases but exec per item, so avg!
        data = []
        for subject, phase_dictionary in model_evaluations.items():
            if adapt_str in phase_dictionary:
                phase = adapt_str
                item_dict = phase_dictionary[phase]
                for item, checkpoint_evaluations in item_dict.items():
                    e = 0
                    for value_pair in checkpoint_evaluations:
                        e += 1
                        train_acc, test_acc = value_pair
                        data.append({'Model': model,
                                     'Subject': subject,
                                     'Phase': phase,
                                     'Epoch': e,
                                     'Acc': train_acc,
                                     'Train/Test': 'train',
                                     'Item': item
                                     })
                        data.append({'Model': model,
                                     'Subject': subject,
                                     'Phase': phase,
                                     'Epoch': e,
                                     'Acc': test_acc,
                                     'Train/Test': 'test',
                                     'Item': item
                                     })
            df2 = pd.DataFrame(data)

        if not df2.empty:
            # average over adaption runs of one model and subject
            df2.groupby(['Model', 'Subject', 'Epoch', 'Train/Test']).mean()

            df2.drop('Item', axis=1, inplace=True)
            df = pd.concat([df1, df2])
        else:
            df = df1

        sns.set(style='whitegrid')

        for phase in set(df['Phase']):
            sns.lineplot(x="Epoch", y="Acc", hue='Train/Test',
                         data=df.loc[(df['Model'] == model)
                                     & (df['Phase'] == phase)])

            handles, labels = plt.gca().get_legend_handles_labels()
            plt.gca().legend(
                handles=handles[1:], labels=labels[1:],
                bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                ncol=2, mode="expand", borderaxespad=0., frameon=False)

            plt.title('Network Training\nPerformance')
            plt.xlabel('Epochs')
            plt.ylabel('Predictive Accuracy')

            plt.tight_layout()
            plt.savefig('{}/{}_{}.png'.format(self.learning_curves_folder,
                                              model, phase))
            plt.clf()


class Split_Evaluator(Evaluator):
    """Evaluate models on a train-test split of data of a single individual."""

    def __init__(self, modellist, eval_comparator, datafile=None,
                 train_data_person=None, silent=False,
                 split_ratio=0.5):
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

        """

        self.modellist = modellist
        self.silent = silent

        self.domains = set()
        self.response_types = set()

        self.comparator = eval_comparator

        # Load the data set
        self.data = ccobra.CCobraData(pd.read_csv(datafile))
        self.split_ratio = split_ratio

        # Load the personal training data
        self.train_data_person = None
        if train_data_person:
            self.train_data_person = ccobra.CCobraData(
                pd.read_csv(train_data_person))

    def evaluate(self):
        """ CCobra evaluation loop. Iterates over the models and performs training and evaluation.
        Returns
        -------
        pd.DataFrame
            DataFrame containing the CCOBRA evaluation results.
        """

        assert self.data is not None

        result_data = []
        model_name_cache = set()

        # Pre-compute the training data dictionaries
        train_data_dict = None
        train_data_dict = self.get_train_data_dict(self.data)

        # Activate model context
        for idx, modelinfo in enumerate(self.modellist):
            # Print the progress
            if not self.silent:
                print("Evaluating '{}' ({}/{})...".format(
                    modelinfo.path, idx + 1, len(self.modellist)))

            # Setup the model context
            context = os.path.abspath(modelinfo.path)
            if os.path.isfile(context):
                context = os.path.dirname(context)

            with dir_context(context):
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

                # Iterate subject
                for subj_id, subj_df in self.data.get().groupby('id'):
                    model = copy.deepcopy(pre_model)

                    # Perform pre-training for individual subjects
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

                    # split the individuals data in train and test set
                    perm = np.random.permutation(np.arange(len(subj_df)))
                    split_id = int(self.split_ratio * len(subj_df))
                    train_ids, test_ids = perm[:split_id], perm[split_id:]
                    train_set, test_set = subj_df.iloc[train_ids], subj_df.iloc[test_ids]

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
                        result_data.append({
                            'model': model_name,
                            'id': subj_id,
                            'domain': domain,
                            'sequence': sequence,
                            'task': task,
                            'choices': choices,
                            'truth': row['response'],
                            'prediction': comparator.tuple_to_string(prediction),
                            'hit': hit
                        })

                    # Call the end participant hook
                    model.end_participant(subj_id, **optionals)

                # De-load the imported model and its dependencies. Might
                # cause garbage collection issues.
                importer.unimport()

        return pd.DataFrame(result_data)
