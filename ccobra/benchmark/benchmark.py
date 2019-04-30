""" CCOBRA benchmarking module.

"""

import os
import json

class ModelInfo():
    def __init__(self, model_info, base_path, load_specific_class=None):
        self.path = None
        self.override_name = None
        self.load_specific_class = load_specific_class
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
    dict(str, str)
        Dictionary containing benchmark information (e.g., paths to data and models).

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

    return benchmark

def parse_model_info(model_info, base_path):
    """ Parses the model information. Strings are directly interpreted as files. Otherwise,
    dictionaries are parsed for the filename and constructor kwargs.

    Parameters
    ----------
    model_info : object
        Model info object. Can be either str if the benchmark directly contained the model's path
        or a dictionary if extended model specification (kwargs) are available.

    base_path : str
        Base path of the benchmark file to fix relative paths with.

    Returns
    -------
    tuple(str, dict)
        Tuple consisting of the absolute model path information and the dictionary containing
        keyword arguments for model construction.

    """

    if isinstance(model_info, str):
        return (fix_model_path(model_info, base_path), '', {})

    model_file = fix_model_path(model_info['filename'], base_path)
    override_name = model_info.get('override_name', None)

    kwargs = model_info.get('args', {})

    return (model_file, override_name, kwargs)

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
