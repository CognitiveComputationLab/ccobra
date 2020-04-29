""" CCOBRA evaluation module.

"""

import copy
import warnings
import logging
import sys
import time

import pandas as pd
import numpy as np

import ccobra

from . import modelimporter
from . import comparator
from . import contextmanager


# Initialize module-level logger
logger = logging.getLogger(__name__)

class Evaluator():
    def __init__(self, benchmark, is_silent=False, cache_df=None):
        logger.info('Setting up evaluator...')

        # Store the information
        self.benchmark = benchmark
        self.is_silent = is_silent
        self.cache_df = cache_df

        # Extract the dataset information
        self.data_train = None
        self.data_train_person = None
        self.data_test = benchmark.data_test.to_eval_dict()

        if benchmark.data_train != None:
            logger.debug('Supplied training data for evaluation.')
            self.data_train = benchmark.data_train.to_eval_dict()
        if benchmark.data_train_person != None:
            logger.debug('Supplied person training data for evaluation.')
            self.data_train_person = benchmark.data_train_person.to_eval_dict()

    def evaluate(self):
        logger.info('Starting evaluation routine...')

        result_data = []
        model_name_cache = set() if self.cache_df is None else set(self.cache_df['model'].unique())

        # Activate model context
        for idx, modelinfo in enumerate(self.benchmark.models):
            # Print the progress
            log_str = "Evaluating '{}' ({}/{})...".format(
                modelinfo.path, idx + 1, len(self.benchmark.models))
            logger.debug(''.join(['='] * 80))
            logger.info(log_str)
            logger.debug(''.join(['='] * 80))

            if not self.is_silent:
                print(log_str)

            # Setup model context
            with contextmanager.dir_context(modelinfo.path):
                # Dynamically import the CCOBRA model
                importer = modelimporter.ModelImporter(
                    modelinfo.path, ccobra.CCobraModel,
                    load_specific_class=modelinfo.load_specific_class
                )

                # Instantiate and prepare the model for predictions
                pre_model = importer.instantiate(modelinfo.args)
                pre_model.setup_environment(
                    evaluation_type='adaption',
                    pre_train_domains=self.benchmark.data_train.domains if self.data_train else None,
                    person_train_domains=self.benchmark.data_train_person.domains if self.data_train_person else None,
                    prediction_domains=self.benchmark.data_test.domains
                )

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
                    logger.warning('Duplicate model name detected ("{}"). Changed to "{}".'.format(
                        original_model_name, model_name))

                # Only perform general pre-training if training data is
                # supplied and corresponding data is false. Otherwise, the
                # model has to be re-trained for each subject.
                if self.data_train is not None and not self.benchmark.corresponding_data:
                    logger.debug('General pre-training for %s...', model_name)
                    pre_model.pre_train(list(train_data_dict.values()))

                # Iterate subject
                for subj_key_identifier, subj_data in self.data_test.items():
                    start_subject = time.time()

                    subj_id = subj_data[0]['item'].identifier
                    model = copy.deepcopy(pre_model)

                    # Set the model to new participant
                    model.start_participant(id=subj_id)

                    # Perform pre-training for individual subjects only if
                    # corresponding data is set to true
                    if self.data_train is not None and self.benchmark.corresponding_data:
                        cur_train_data = [
                            value for key, value in self.data_train.items() if key != subj_id]
                        logger.debug('Individual pre-training for %s...', model_name)
                        model.pre_train(cur_train_data)

                    # Perform personalized pre-training
                    if self.benchmark.type == 'coverage':
                        # In case of coverage, provide test data of the participant
                        subj_person_train_data = self.data_test[subj_key_identifier]
                        logger.debug('Person training for %s...', model_name)
                        model.person_train(subj_person_train_data)
                    elif self.data_train_person is not None:
                        # Extract person training data for current individual
                        subj_person_train_data = [
                            value for key, value in self.data_train_person.items() if key == subj_id]
                        logger.debug('Person training for %s...', model_name)
                        model.person_train(subj_person_train_data)

                    # Iterate over individual tasks
                    start_eval = time.time()
                    for idx, task in enumerate(subj_data):
                        start_task = time.time()
                        logger.debug('Querying for task %s/%s...', idx + 1, len(subj_data))

                        # Integrity checks
                        assert task['item'].identifier == subj_id

                        # Obtain prediction from the model
                        prediction = model.predict(copy.deepcopy(task['item']), **task['aux'])
                        hit = int(self.benchmark.eval_comparator.compare(prediction, task['response']))

                        logger.debug('Prediction to %s is %s', task['item'].task, prediction)

                        # Adapt to true response
                        if self.benchmark.type == 'adapt':
                            model.adapt(copy.deepcopy(task['item']), task['response'], **task['aux'])

                        # Collect the evaluation result data
                        domain = task['item'].domain
                        prediction_data = {
                            'model': model_name,
                            'id': subj_id,
                            'domain': task['item'].domain,
                            'response_type': task['item'].response_type,
                            'sequence': task['item'].sequence_number,
                            'task': comparator.tuple_to_string(task['item'].task),
                            'choices': comparator.tuple_to_string(task['item'].choices),
                            'truth': task['response'],
                            'prediction': comparator.tuple_to_string(prediction),
                            'hit': hit,
                            'type': self.benchmark.type
                        }

                        # If domain encoders are specified, attach encodings to the result
                        task_enc = ''
                        truth_enc = ''
                        pred_enc = ''
                        if domain in self.benchmark.encoders:
                            task_enc = self.benchmark.encoders[domain].encode_task(
                                task['item'].task) if domain in self.benchmark.encoders else np.nan
                            truth_enc = self.benchmark.encoders[domain].encode_response(
                                task['response'], task['item'].task) if domain in self.benchmark.encoders else np.nan
                            pred_enc = self.benchmark.encoders[domain].encode_response(
                                prediction, task['item'].task) if domain in self.benchmark.encoders else np.nan

                        prediction_data.update({
                            'task_enc': task_enc,
                            'truth_enc': truth_enc,
                            'prediction_enc': pred_enc
                        })

                        result_data.append(prediction_data)

                        logger.debug('Task {} took {:4f}s'.format(
                            idx, time.time() - start_task))

                    # Finalize subject evaluation
                    model.end_participant(subj_id)

                    logger.debug('Subject evaluation took {:.4}s'.format(time.time() - start_eval))
                    logger.debug('Subject {} done. took {:.4}s'.format(
                        subj_id, time.time() - start_subject))

                # Unload the imported model and its dependencies. Might cause garbage collection
                # issues
                importer.unimport()

        res_df = pd.DataFrame(result_data)
        if self.cache_df is None:
            return res_df

        if not result_data:
            return self.cache_df

        assert sorted(list(res_df)) == sorted(list(self.cache_df)), 'Incompatible cache'
        return pd.concat([res_df, self.cache_df])

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

        missing_domains = set(self.benchmark.data_test.domains) - set(pre_model.supported_domains)
        if missing_domains:
            raise ValueError(
                'Model {} is not applicable to domains {} found in ' \
                'the test dataset.'.format(
                    pre_model.name, missing_domains))

        missing_response_types = set(self.benchmark.data_test.response_types) - set(pre_model.supported_response_types)
        if missing_response_types:
            raise ValueError(
                'Model {} is not applicable to response_types {} ' \
                'found in the test dataset.'.format(
                    pre_model.name, missing_response_types))
