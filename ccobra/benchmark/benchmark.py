import logging
import os
import json

import pandas as pd

from . import contextmanager
from . import modelimporter
from . import comparator
from ..domainhandler import CCobraDomainEncoder
from ..syllogistic.encoder_syl import SyllogisticEncoder
from ..propositional.encoder_prop import PropositionalEncoder
from ..data import CCobraData

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
    if python_files:
        return sub_directories[0]

    raise ValueError("Could not identify model to load for '{}'".format(path))
    if python_files:
        return sub_directories[0]

    raise ValueError("Could not identify model to load for '{}'".format(path))

def prepare_domain_encoders(domain_encoder_paths):
    """ Processes the domain encoder information from the benchmark specification. Handles
    relative paths or path placeholders (e.g., '%ccobra%' mapping to the module directory of
    the local CCOBRA installation).

    Parameters
    ----------
    domain_encoder_paths : dict(str, str)
        Dictionary mapping from domains to encoders.

    Returns
    -------
    dict(str, str)
        Dictionary mapping from domains to encoders with absolute paths.

    """

    domain_encoders = {}
    for domain, domain_encoder_path in domain_encoder_paths.items():
        # Replace internal ccobra path
        if '%ccobra%' in domain_encoder_path:
            package_path = os.path.split(os.path.split(__file__)[0])[0]
            domain_encoder_path = os.path.normpath(
                domain_encoder_path.replace('%ccobra%', package_path))

        # To instantiate the encoder we need to change to its context (i.e., set the PATH variable
        # accordingly).
        enc = None
        with contextmanager.dir_context(domain_encoder_path):
            imp = modelimporter.ModelImporter(domain_encoder_path, superclass=CCobraDomainEncoder)
            enc = imp.instantiate()

        if not enc:
            raise ValueError('Failed to instantiate encoder class.')
        domain_encoders[domain] = enc

    return domain_encoders

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
            self.load_specific_class = model_info.get(
                'load_specific_class', self.load_specific_class)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return 'path={}, override_name={}, load_specific_class={}, args={}'.format(
            self.path, self.override_name, self.load_specific_class, self.args)

class Benchmark():
    def __init__(self, json_path, argmodel=None, cached=False):
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
        if argmodel:
            argmodel_path = os.path.abspath(argmodel)
            self.json_content['models'].append(argmodel_path)
            logger.debug('Injected model supplied via arguments')

        # Determine JSON path to fix relative path information
        self.base_path = os.path.dirname(os.path.abspath(json_path))
        logger.debug('base_path: %s', self.base_path)

        # Parse the JSON content
        self.parse_type()
        self.parse_comparator()
        self.parse_data()
        self.parse_models()
        self.parse_domain_encoders()

    def parse_type(self):
        # Set type and validate
        self.type = self.json_content.get('type', 'adaption')
        if self.type not in ['adaption', 'coverage']:
            raise ValueError('Unsupported evaluation type: {}'.format(self.type))
        logger.debug('Evaluation type: %s', self.type)

    def parse_comparator(self):
        # Extract comparator settings from benchmark description
        comparator_type = self.json_content.get('comparator', 'equality')
        logger.debug('Comparator type: %s', comparator_type)
        if comparator_type == 'equality':
            self.eval_comparator = comparator.EqualityComparator()
        elif comparator_type == 'nvc':
            self.eval_comparator = comparator.NVCComparator()
        else:
            raise ValueError('Invalid comparator type specified: {}'.format(comparator_type))
        logger.debug('eval_comparator: %s', self.eval_comparator)

    def parse_data_path(self, path):
        if not path:
            return None, None

        # Resolve relative paths
        full_path = fix_rel_path(path, self.base_path)

        # Load the data and create CCOBRA container
        df = pd.read_csv(full_path)
        dat = CCobraData(df)

        return full_path, dat

    def parse_data(self):
        # Parse data paths
        self.data_train_path, self.data_train = self.parse_data_path(self.json_content.get('data.train', ''))
        logger.debug('data_train_path: %s', self.data_train_path)
        self.data_train_person_path, self.data_train_person = self.parse_data_path(self.json_content.get('data.train_person', ''))
        logger.debug('data_train_person_path: %s', self.data_train_person_path)
        self.data_test_path, self.data_test = self.parse_data_path(self.json_content.get('data.test', ''))
        logger.debug('data_test_path: %s', self.data_test_path)

        if self.data_test is None:
            raise ValueError('Test dataset must be supplied.')

        # Set corresponding data
        self.corresponding_data = self.json_content.get('corresponding_data', False)
        logger.debug('corresponding_data: %s', self.corresponding_data)

        # In case of non-corresponding datasets, make sure that identifiers do not overlap by
        # offsetting the training data (ensures that test identifiers remain identifiable)
        if self.data_train != None and not self.corresponding_data:
            logger.debug('adjusting identifier offsets')
            self.data_train.offset_identifiers(self.data_test.n_subjects)

    def parse_models(self):
        # Prepare the models for loading
        self.models = [ModelInfo(x, self.base_path) for x in self.json_content['models']]
        logger.debug('models:\n%s', '\n'.join([str(x) for x in self.models]))

    def parse_domain_encoders(self):
        # Parse domain encoder information
        self.encoders = {}
        if 'domain_encoders' in self.json_content:
            self.encoders = prepare_domain_encoders(self.json_content['domain_encoders'])

        # Include default encoders if not overridden
        if 'syllogistic' not in self.encoders:
            self.encoders['syllogistic'] = SyllogisticEncoder()
        if 'propositional' not in self.encoders:
            self.encoders['propositional'] = PropositionalEncoder()

        logger.debug('Encoders:\n%s', self.encoders)

    def __str__(self):
        s = []
        s.append('Benchmark:')
        s.append('   type: {}'.format(self.type))
        s.append('   data paths:')
        s.append('      train: {}'.format(self.path_data_train))
        s.append('      train-person: {}'.format(self.path_data_train_person))
        s.append('      test : {}'.format(self.path_data_test))
        s.append('   corresponding_data: {}'.format(self.corresponding_data))
        s.append('   models:')
        for idx, model in enumerate(self.models):
            s.append('      ({}) {}'.format(idx + 1, model))
        s.append('   encoders:')
        for enc, val in self.encoders.items():
            s.append('      {}: {}'.format(enc, val))
        return '\n'.join(s)
