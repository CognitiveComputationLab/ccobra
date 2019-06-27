""" CCOBRA benchmarking module.

"""

import json
import os

from . import modelimporter
from ..domainhandler import CCobraDomainEncoder
from . import contextmanager

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

    def __str__(self):
        return 'path={}, override_name={}, load_specific_class={}, args={}'.format(
            self.path, self.override_name, self.load_specific_class, self.args)

def load_benchmark(benchmark_file):
    """ Loads a benchmark file containing information about the data and models
    to run. Changes relative paths from `benchmark_file` to absolute ones.

    Parameters
    ----------
    benchmark_file : str
        Path to the benchmark file to load.

    Returns
    -------
    list(ModelInfo)
        List of ModelInfo containers.

    """

    benchmark = None

    # Load raw benchmark file content
    with open(benchmark_file) as json_file:
        benchmark = json.load(json_file)

    # Fix relative path information
    base_path = os.path.dirname(os.path.abspath(benchmark_file))

    benchmark['data.train'] = fix_rel_path(benchmark.get('data.train'), base_path)
    benchmark['data.train_person'] = fix_rel_path(benchmark.get('data.train_person', ''), base_path)
    benchmark['data.test'] = fix_rel_path(benchmark.get('data.test', ''), base_path)
    benchmark['models'] = [ModelInfo(x, base_path) for x in benchmark['models']]

    if 'domain_encoders' in benchmark:
        encoders = prepare_domain_encoders(benchmark['domain_encoders'])
        benchmark['domain_encoders'] = encoders
    else:
        benchmark['domain_encoders'] = None

    return benchmark

def prepare_domain_encoders(domain_encoder_paths):
    domain_encoders = {}
    for domain, domain_encoder_path in domain_encoder_paths.items():
        # Replace internal ccobra path
        if '%ccobra%' in domain_encoder_path:
            package_path = os.path.split(os.path.split(__file__)[0])[0]
            domain_encoder_path = os.path.normpath(domain_encoder_path.replace('%ccobra%', package_path))

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
