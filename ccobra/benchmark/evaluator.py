""" CCOBRA evaluation module.

"""

import copy
import logging
import time

import numpy as np
import pandas as pd

from ..model import CCobraModel

from . import contextmanager
from . import modelimporter


# Initialize module-level logger
logger = logging.getLogger(__name__)

class Evaluator():
    """ CCOBRA evaluation routine.

    """

    def __init__(self, benchmark, is_silent=False, cache_df=None):
        """ Initializes the evaluator object by preparing the data representations and precomputing
        the required training and adaption steps.

        Parameters
        ----------
        benchmarks : ccobra.Benchmark
            Benchmark container.

        is_silent : bool, optional
            Flag indicating that output is supposed to be suppressed.

        cache_df : pandas.DataFrame, option
            Cache result dataframe.

        """

        logger.info('Setting up evaluator...')

        # Store the information
        self.benchmark = benchmark
        self.is_silent = is_silent
        self.cache_df = cache_df

        # Extract the dataset information
        self.dict_test = benchmark.data_test.to_eval_dict()

        self.dict_pre_train = None
        self.dict_pre_train_person = None
        self.dict_pre_person_background = None

        if benchmark.data_pre_train is not None:
            logger.debug('Supplied training data to evaluation.')
            self.dict_pre_train = benchmark.data_pre_train.to_eval_dict()
        if benchmark.data_pre_train_person is not None:
            logger.debug('Supplied person training data to evaluation.')
            self.dict_pre_train_person = benchmark.data_pre_train_person.to_eval_dict()
        if benchmark.data_pre_person_background is not None:
            logger.debug('Supplied person background data to evaluation.')
            self.dict_pre_person_background = benchmark.data_pre_person_background.to_eval_dict()

        if benchmark.type == 'coverage':
            self.dict_pre_train_person = self.dict_test

        # Extract the functionality to apply
        self.do_adapt = (benchmark.type == 'adaption')
        self.do_pre_train_global = (self.dict_pre_train is not None) and not benchmark.corresponding_data
        self.do_pre_train_leaveoneout = (self.dict_pre_train is not None) and benchmark.corresponding_data
        self.do_pre_train_person = (self.dict_pre_train_person is not None)
        self.do_pre_person_background = (self.dict_pre_person_background is not None)

        logger.debug('Evaluation ready:')
        logger.debug('   do_adapt: %s', self.do_adapt)
        logger.debug('   do_pre_train_global: %s', self.do_pre_train_global)
        logger.debug('   do_pre_train_leaveoneout: %s', self.do_pre_train_leaveoneout)
        logger.debug('   do_pre_train_person: %s', self.do_pre_train_person)
        logger.debug('   do_pre_person_background: %s', self.do_pre_person_background)

    def evaluate(self):
        """ Core evaluation routine.

        Returns
        -------
        pd.DataFrame
            Pandas dataframe containing the evaluation results.

        """

        logger.info('Starting evaluation routine...')

        result_data = []
        model_logging_results = {}
        model_name_cache = set() if self.cache_df is None else set(self.cache_df['model'].unique())

        # Activate model context
        for model_idx, modelinfo in enumerate(self.benchmark.models):
            # Print the progress
            log_str = "Evaluating '{}' ({}/{})...".format(
                modelinfo.path, model_idx + 1, len(self.benchmark.models))
            logger.debug(''.join(['='] * 80))
            logger.info(log_str)
            logger.debug(''.join(['='] * 80))

            if not self.is_silent:
                print(log_str)

            # Initialize the dictionary for the models logging output
            model_logging_dict = {}

            # Setup model context
            with contextmanager.dir_context(modelinfo.path):
                # Dynamically import the CCOBRA model
                importer = modelimporter.ModelImporter(
                    modelinfo.path, CCobraModel,
                    load_specific_class=modelinfo.load_specific_class
                )

                # Instantiate and prepare the model for predictions
                pre_model = importer.instantiate(modelinfo.args)
                pre_model.setup_environment(self.benchmark.type)

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
                    logger.warning(
                        'Duplicate model name detected ("%s"). Changed to "%s".',
                        original_model_name, model_name
                    )

                # Only perform general pre-training if training data is
                # supplied and corresponding data is false. Otherwise, the
                # model has to be re-trained for each subject.
                if self.do_pre_train_global:
                    logger.debug('General pre-training for %s...', model_name)
                    pre_model.pre_train(list(self.dict_pre_train.values()))

                # Iterate subject
                for subj_key_identifier, subj_data in self.dict_test.items():
                    start_subject = time.time()

                    subj_id = subj_data[0]['item'].identifier
                    model = copy.deepcopy(pre_model)

                    # Set the model to new participant
                    model.start_participant(id=subj_id)

                    # Perform pre-training for individual subjects only if
                    # corresponding data is set to true
                    if self.do_pre_train_leaveoneout:
                        logger.debug('Individual pre-training for %s...', model_name)
                        cur_train_data = [
                            value for key, value in self.dict_pre_train.items() if key != subj_id]
                        model.pre_train(cur_train_data)

                    # Perform background fitting
                    if self.do_pre_person_background:
                        logger.debug('Person background training for %s...', model_name)
                        cur_train_data = self.dict_pre_person_background.get(subj_key_identifier, [])
                        model.pre_person_background(cur_train_data)

                    # Perform person training
                    if self.do_pre_train_person:
                        logger.debug('Person training for %s...', model_name)
                        subj_person_train_data = self.dict_pre_train_person.get(subj_key_identifier, [])
                        model.pre_train_person(subj_person_train_data)

                    # Iterate over individual tasks
                    start_eval = time.time()
                    for task_idx, task in enumerate(subj_data):
                        start_task = time.time()
                        logger.debug('Querying for task %s/%s...', task_idx + 1, len(subj_data))

                        # Integrity checks
                        assert task['item'].identifier == subj_id

                        # Query models for predictions
                        for eh in self.benchmark.evaluation_handlers:
                            target = task[eh.data_column]
                            eh.predict(model, model_name, task['item'], target, task['aux'])

                        # Perform model adaption
                        if self.do_adapt:
                            for eh in self.benchmark.evaluation_handlers:
                                target = task[eh.data_column]
                                eh.adapt(model, task['item'], task['full'])

                        logger.debug(
                            'Task {} took {:4f}s'.format(task_idx + 1, time.time() - start_task))

                    # Finalize subject evaluation and allow the model to store parameters
                    model_log = {}
                    model.end_participant(subj_id, model_log)
                    if len(model_log) > 0:
                        model_logging_dict[subj_id]= model_log

                    logger.debug('Subject evaluation took {:.4}s'.format(time.time() - start_eval))
                    logger.debug('Subject {} done. took {:.4}s'.format(
                        subj_id, time.time() - start_subject))

                # Save the models logging information if available
                if len(model_logging_dict) > 0:
                    model_logging_results[model_name] = model_logging_dict

                # Unload the imported model and its dependencies. Might cause garbage collection
                # issues
                importer.unimport()

        res_df = None
        on_list = [
            'model',
            'id',
            'domain',
            'response_type',
            'sequence',
            'task',
            'choices'
        ]

        for enc in self.benchmark.evaluation_handlers:
            if res_df is None:
                res_df = enc.get_result_df()
            else:
                res_df = res_df.merge(enc.get_result_df(), on=on_list, suffixes=('', '_' + enc.data_column))

        res_df = res_df.rename(columns={'score' : 'score_response'})
        #res_df = res_df.rename(columns={
        #    'score': 'hit',
        #    'truth_enc': 'truth_enc',
        #    'prediction_enc': 'prediction_enc'
        #})

        if self.cache_df is None:
            return res_df, model_logging_results

        if not result_data:
            return self.cache_df, {}

        assert sorted(list(res_df)) == sorted(list(self.cache_df)), 'Incompatible cache'
        return pd.concat([res_df, self.cache_df]), model_logging_results

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
