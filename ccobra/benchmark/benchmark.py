""" File containing classes required for benchmark handling.

"""

import json
import logging
import os

import pandas as pd

from . import comparator
from . import contextmanager
from . import modelimporter
from . import evaluation_handler
from ..data import CCobraData
from ..taskhandler import CCobraTaskEncoder
from ..responsehandler import CCobraResponseEncoder
from ..propositional.task_encoder_prop import PropositionalTaskEncoder
from ..syllogistic.task_encoder_syl import SyllogisticTaskEncoder

# Initialize logging
logger = logging.getLogger(__name__)

def fix_rel_path(path, base_path):
    """ Fixes relative paths by prepending the benchmark filepath.

    Parameters
    ----------
    path : str
        Path to fix.

    base_path : str
        Basepath used to fix relative paths with. Is prepended to the relative path.

    Returns
    -------
    str
        Fixed absolute path.

    """

    # Replace internal ccobra path
    if '%ccobra%' in path:
        package_path = os.path.split(os.path.split(__file__)[0])[0]
        path = path.replace('%ccobra%', package_path)

    if path and not os.path.isabs(path):
        return os.path.normpath(base_path + os.sep + path)

    return path

def fix_model_path(path, base_path=None):
    """ Fixes the model path by checking if the path directly refers to a python file. Otherwise
    searches for a subdirectory containing possible modules.

    Parameters
    ----------
    path : str
        Model path to fix.

    base_path : str, optional
        Base path to fix the model path with if it is relative.

    Returns
    -------
    str
        Path pointing to the file assumed to contain the model.

    """

    abs_path = path
    if base_path:
        abs_path = fix_rel_path(path, base_path)

    if os.path.isfile(abs_path) and abs_path[-2:] == "py":
        return abs_path

    python_files = []
    sub_directories = []
    for f_name in os.listdir(abs_path):
        f_path = os.path.join(abs_path, f_name)

        if os.path.isfile(f_path) and f_name[-2:] == "py":
            python_files.append(f_path)
        elif os.path.isdir(f_path) and f_name[0] != "." and f_name[:2] != "__":
            sub_directories.append(f_path)

    if python_files:
        return abs_path

    if len(sub_directories) == 1:
        python_files = [
            os.path.join(sub_directories[0], f) for f in os.listdir(
                sub_directories[0]) if os.path.isfile(
                    os.path.join(sub_directories[0], f)) and f[-2:] == "py"]
        if python_files:
            return sub_directories[0]

    raise ValueError("Could not identify model to load for '{}'".format(path))

def prepare_task_encoders(encoder_paths, base_path):
    """ Processes the task encoder information from the benchmark specification. Handles
    relative paths or path placeholders (e.g., '%ccobra%' mapping to the module directory of
    the local CCOBRA installation).

    Parameters
    ----------
    encoder_paths : dict(str, str)
        Dictionary mapping from domains to task encoders with absolute paths.

    Returns
    -------
    dict(str, str)
        Dictionary mapping from domains to paths containing task encoders.

    """

    encoders = {}
    for domain, encoder_path in encoder_paths.items():
        # Normalize encoder path
        encoder_path = fix_rel_path(encoder_path, base_path)

        # To instantiate the encoder we need to change to its context (i.e., set the PATH variable
        # accordingly).
        enc = None
        with contextmanager.dir_context(encoder_path):
            imp = modelimporter.ModelImporter(encoder_path, superclass=CCobraTaskEncoder)
            enc = imp.instantiate()

        if not enc:
            raise ValueError('Failed to instantiate encoder class.')
        encoders[domain] = enc

    return encoders

def prepare_resp_encoders(encoder_paths, base_path):
    """ Processes the response encoder information from the benchmark specification. Handles
    relative paths or path placeholders (e.g., '%ccobra%' mapping to the module directory of
    the local CCOBRA installation).

    Parameters
    ----------
    encoder_paths : dict(str, str)
        Dictionary mapping from domains to response encoders with absolute paths.

    Returns
    -------
    dict(str, str)
        Dictionary mapping from domains to paths containing response encoders.

    """

    encoders = {}
    for domain, encoder_path in encoder_paths.items():
        # Normalize encoder path
        encoder_path = fix_rel_path(encoder_path, base_path)

        # To instantiate the encoder we need to change to its context (i.e., set the PATH variable
        # accordingly).
        enc = None
        with contextmanager.dir_context(encoder_path):
            imp = modelimporter.ModelImporter(encoder_path, superclass=CCobraResponseEncoder)
            enc = imp.instantiate()

        if not enc:
            raise ValueError('Failed to instantiate encoder class.')
        encoders[domain] = enc

    return encoders

def prepare_comparator(comparator_path):
    """ Processes the comparator path from the benchmark specification. Imports the object
    dynamically.

    Parameters
    ----------
    comparator_path : str
        Path to the python script file containing the comparator definition.

    Returns
    -------
    ccobra.benchmark.comparator.Comparator
        Comparator object.

    """

    comp = None

    with contextmanager.dir_context(comparator_path):
        imp = modelimporter.ModelImporter(comparator_path, superclass=comparator.Comparator)
        comp = imp.instantiate()

    if not comp:
        raise ValueError('Failed to instantiate comparator class.')

    return comp

class ModelInfo():
    """ Model information container. Contains the properties required to initialize and identify
    CCOBRA model instances.

    """

    def __init__(self, model_info, base_path, load_specific_class=None):
        """ Model initialization.

        Parameters
        ----------
        model_info : object
            Benchmark information about the model. Can either be string or dictionary.

        base_path : str
            Base path for handling relative path specifications.

        load_specific_class : str, optional
            Specific class name to load. Is used whenever multiple alternative CCOBRA model classes
            are specified within the model file.

        """

        #: Model filepath
        self.path = None

        #: String for overriding model name with
        self.override_name = None

        #: Class name for dynamic loading. Is used whenever multiple alternative CCOBRA model
        #: classes are specified within the model file.
        self.load_specific_class = load_specific_class

        #: Keyword arguments for the dynamic model instantiation
        self.args = {}

        if isinstance(model_info, str):
            self.path = fix_model_path(model_info, base_path)
        else:
            self.path = fix_model_path(model_info['filename'], base_path)
            self.override_name = model_info.get('override_name', self.override_name)
            self.args = model_info.get('args', self.args)
            self.load_specific_class = model_info.get('classname', self.load_specific_class)

    def __repr__(self):
        """ Generates a string representation for the model info container.

        Returns
        -------
        str
            ModelInfo string representation.

        """

        return str(self)

    def __str__(self):
        """ Generates a string representation for the model info container.

        Returns
        -------
        str
            ModelInfo string representation.

        """

        return 'path={}, override_name={}, load_specific_class={}, args={}'.format(
            self.path, self.override_name, self.load_specific_class, self.args)

class Benchmark():
    """ Benchmark class to handle and provide information from JSON benchmark specification files.

    """

    def __init__(self, json_path, argmodel=None, cached=False):
        """ Initializes the benchmark instance by reading the JSON benchmark specification file
        content.

        Parameters
        ----------
        json_path : str
            Path to the JSON benchmark specification file.

        argmodel : (str, str), optional
            Tuple containing the path to a specific model to load and the classname information.

        cached : bool, optional
            Flag to indicate whether the benchmark is cached or not. If true, the benchmark models
            are ignored.

        """

        logger.debug('Opening benchmark: "%s"', json_path)

        # Load raw benchmark file content
        self.json_content = None
        with open(json_path) as json_file:
            self.json_content = json.load(json_file)
        logger.debug('JSON content:\n%s', self.json_content)

        # Remove models in case of a cached run
        if cached:
            self.json_content['models'] = []
            logger.debug('Cached run. Removed models from benchmark')

        # Inject model added via arguments
        if argmodel != (None, None):
            argmodel_path = os.path.abspath(argmodel[0])
            self.json_content['models'].append(
                {"filename": argmodel_path, "classname": argmodel[1]})
            logger.debug('Injected model supplied via arguments')

        # Determine JSON path to fix relative path information
        self.base_path = os.path.dirname(os.path.abspath(json_path))
        logger.debug('base_path: %s', self.base_path)

        # Parse the JSON content
        self.parse_type()
        self.parse_auxiliary_evaluations()
        self.parse_models()
        self.parse_data()

        # Verify
        if self.type == 'coverage':
            if self.data_pre_train_person is not None:
                raise ValueError('data.pre_train_person is not allowed in coverage evaluation.')

    def parse_type(self):
        """ Parses the benchmark type (prediction, adaption, coverage).

        """

        # Set type and validate
        self.type = self.json_content.get('type', 'adaption')
        if self.type not in ['prediction', 'adaption', 'coverage']:
            raise ValueError('Unsupported evaluation type: {}'.format(self.type))
        logger.debug('Evaluation type: %s', self.type)

    def parse_comparator(self, comparator_str):
        """ Parses the comparator information.

        Parameters
        ----------
        comparator_str : str
            Either is one of the library-defined comparator labels (equality, nvc, absdiff) or
            a path to a comparator implementation to load dynamically.

        Returns
        -------
        ccobra.benchmark.comparator.Comparator
            Comparator object.

        """

        # Create the comparator instance
        logger.debug('Comparator string: %s', comparator_str)
        if comparator_str == 'equality':
            return comparator.EqualityComparator()
        elif comparator_str == 'nvc':
            return comparator.NVCComparator()
        elif comparator_str == 'absdiff':
            return comparator.AbsDiffComparator()

        logger.debug('Nonlabel comparator string: %s', comparator_str)

        # Normalize path string
        comparator_str = fix_rel_path(comparator_str, self.base_path)
        logger.debug('Absolute comparator path: %s', comparator_str)

        if not os.path.isfile(comparator_str):
            raise ValueError('Comparator string is not a file: {}'.format(comparator_str))

        return prepare_comparator(comparator_str)

    def parse_auxiliary_evaluations(self):
        """ Parses auxiliary evaluation configurations from the benchmark content.

        """

        evaluations = self.json_content.get('aux_evaluations', [])

        task_encoders = self.json_content.get('task_encoders', {})
        if 'syllogistic' not in task_encoders:
            task_encoders['syllogistic'] = '%ccobra%/syllogistic/task_encoder_syl.py'
        if 'propositional' not in task_encoders:
            task_encoders['propositional'] = '%ccobra%/propositional/task_encoder_prop.py'

        resp_encoders = self.json_content.get('response_encoders', {})
        if 'syllogistic' not in resp_encoders:
            resp_encoders['syllogistic'] = '%ccobra%/syllogistic/resp_encoder_syl.py'
        if 'propositional' not in resp_encoders:
            resp_encoders['propositional'] = '%ccobra%/propositional/resp_encoder_prop.py'

        response_eval = {
            'data_column': 'response',
            'comparator': self.json_content.get('comparator', 'equality'),
            'prediction_fn_name': 'predict',
            'adapt_fn_name': 'adapt',
            'task_encoders': task_encoders,
            'response_encoders': resp_encoders
        }
        evaluations.insert(0, response_eval)

        evaluation_handlers = []
        evaluation_targets = []
        for eva in evaluations:
            task_encoders = None
            if 'task_encoders' in eva:
                task_encoders = prepare_task_encoders(eva['task_encoders'], self.base_path)

            resp_encoders = None
            if 'response_encoders' in eva:
                resp_encoders = prepare_resp_encoders(eva['response_encoders'], self.base_path)

            eh = evaluation_handler.EvaluationHandler(
                data_column=eva['data_column'],
                comparator=self.parse_comparator(eva.get('comparator', 'equality')),
                predict_fn_name=eva['prediction_fn_name'],
                adapt_fn_name=eva.get('adapt_fn_name', None),
                task_encoders=task_encoders,
                resp_encoders=resp_encoders
            )
            evaluation_handlers.append(eh)
            evaluation_targets.append(eva['data_column'])

            logger.debug('Added evaluation handler: %s', eh)

        self.evaluation_handlers = evaluation_handlers
        self.evaluation_targets = evaluation_targets

    def parse_data_path(self, path):
        """ Reads in a dataset CSV file and returns it as a pandas.DataFrame object. If a list
        of paths is supplied, the datasets are combined.

        Parameters
        ----------
        path : str
            Path to the data file.

        Returns
        -------
        (str, pandas.DataFrame)
            A tuple consisting of the filepath and the corresponding data frame. If a list of data
            paths was provided, the resulting string represents a ;-joined representation of the
            paths and the dataframe is the combination of the individual dataframes.

        """

        if not path:
            return None, None

        if isinstance(path, list):
            logger.debug('List data path encountered: %s', path)
            parts = [self.parse_data_path(x) for x in path]
            paths = ';'.join([x[0] for x in parts])

            # Combine the datasets
            comb_df = pd.concat([df for _, df in parts])
            return paths, comb_df

        logger.debug('Regular data path encountered: %s', path)

        # Resolve relative paths
        full_path = fix_rel_path(path, self.base_path)

        # Load the data and create CCOBRA container
        df = pd.read_csv(full_path)
        return full_path, df

    def parse_data(self):
        """ Parses the benchmark data information. Reads in an preprocesses the datasets.

        """

        # Verify information
        if 'data.test' not in self.json_content:
            raise ValueError('Test dataset (data.test) must be supplied.')

        # Parse training data fields
        self.data_pre_train_path, data_pre_train_df = self.parse_data_path(self.json_content.get('data.pre_train', ''))
        logger.debug('data_pre_train_path: %s', self.data_pre_train_path)
        self.data_pre_train_person_path, data_pre_train_person_df = self.parse_data_path(self.json_content.get('data.pre_train_person', ''))
        logger.debug('data_pre_train_person_path: %s', self.data_pre_train_person_path)
        self.data_pre_person_background_path, data_pre_person_background_df = self.parse_data_path(self.json_content.get('data.pre_person_background', ''))
        logger.debug('data_pre_person_background_path: %s', self.data_pre_person_background_path)

        # Parse test data field
        self.data_test_path, data_test_df = self.parse_data_path(self.json_content['data.test'])
        logger.debug('data_test_path: %s', self.data_test_path)

        # Filter person data so that only test ids are present
        test_ids = data_test_df['id'].unique()
        if data_pre_train_person_df is not None:
            data_pre_train_person_df = data_pre_train_person_df.loc[
                data_pre_train_person_df['id'].isin(test_ids)]
        if data_pre_person_background_df is not None:
            data_pre_person_background_df = data_pre_person_background_df.loc[
                data_pre_person_background_df['id'].isin(test_ids)]

        # Set corresponding data
        self.corresponding_data = self.json_content.get('corresponding_data', False)
        logger.debug('corresponding_data: %s', self.corresponding_data)

        # Construct CCOBRA datasets
        self.data_test = CCobraData(data_test_df, target_columns=self.evaluation_targets)
        self.data_pre_train = CCobraData(data_pre_train_df, target_columns=self.evaluation_targets) if data_pre_train_df is not None else None
        self.data_pre_train_person = CCobraData(data_pre_train_person_df, target_columns=self.evaluation_targets) if data_pre_train_person_df is not None else None
        self.data_pre_person_background = CCobraData(data_pre_person_background_df, target_columns=self.evaluation_targets) if data_pre_person_background_df is not None else None

        # In case of non-corresponding datasets, make sure that identifiers do not overlap by
        # offsetting the training data (ensures that test identifiers remain identifiable)
        if self.data_pre_train is not None and not self.corresponding_data:
            logger.debug('adjusting identifier offsets...')
            self.data_pre_train.prefix_identifiers()
        elif self.data_pre_train is not None and self.corresponding_data:
            logger.debug('extracting additional person data from comparing data_pre_train with data_test...')

            # Identify the columns which are present only in the training data
            merge = data_pre_train_df.merge(data_test_df, how='left', indicator=True)
            data_train_only_df = merge.loc[merge['_merge'] == 'left_only'].drop(columns=['_merge'])

            # Append domain related data to pre_train_person
            domain_related_df = data_train_only_df.loc[data_train_only_df['domain'].isin(self.data_test.domains)]

            if data_pre_train_person_df is not None:
                domain_related_df = pd.concat(domain_related_df, data_pre_train_person_df)

            if not domain_related_df.empty:
                self.data_pre_train_person = CCobraData(domain_related_df.drop(columns='_unique_id'), target_columns=self.evaluation_targets)

            # Append domain unrelated data to pre_person_background
            domain_unrelated_df = data_train_only_df.loc[~data_train_only_df['domain'].isin(self.data_test.domains)]

            if data_pre_person_background_df is not None:
                domain_unrelated_df = pd.concat(domain_unrelated_df, data_pre_person_background_df)

            if not domain_unrelated_df.empty:
                self.data_pre_person_background = CCobraData(domain_unrelated_df.drop(columns='_unique_id'), target_columns=self.evaluation_targets)

    def parse_models(self):
        """ Parses the benchmark model information.

        """

        # Prepare the models for loading
        self.models = [ModelInfo(x, self.base_path) for x in self.json_content['models']]
        logger.debug('models:\n%s', '\n'.join([str(x) for x in self.models]))

    def __str__(self):
        """ Generates a string representation of the benchmark information.

        """

        s = []
        s.append('Benchmark:')
        s.append('   type: {}'.format(self.type))
        s.append('   data paths:')
        s.append('      pre_train: {}'.format(self.data_pre_train_path))
        s.append('      pre_train_person: {}'.format(self.data_pre_train_person_path))
        s.append('      pre_person_background: {}'.format(self.data_pre_person_background_path))
        s.append('      test : {}'.format(self.data_test_path))
        s.append('   corresponding_data: {}'.format(self.corresponding_data))
        s.append('   models:')
        for idx, model in enumerate(self.models):
            s.append('      ({}) {}'.format(idx + 1, model))
        s.append('   evaluation handlers:')
        for eh in self.evaluation_handlers:
            s.append('      {}'.format(str(eh)))
        s.append('   evaluation targets: {}'.format(self.evaluation_targets))
        return '\n'.join(s)
