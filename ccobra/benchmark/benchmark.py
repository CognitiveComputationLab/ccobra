import os
import json

def load_benchmark(benchmark_file):
    """ Loads a benchmark file containing information about the data and models
    to run. Changes relative paths from `benchmark_file` to absolute ones.

    Parameters
    ----------
    benchmark_file : str
        Path to the benchmark file to load.

    """

    benchmark = None

    # Load raw benchmark file content
    with open(benchmark_file) as json_file:
        benchmark = json.load(json_file)

    # Fix relative path information
    base_path = os.path.dirname(os.path.abspath(benchmark_file))

    benchmark['data.train'] = fix_path(benchmark.get('data.train'), base_path)
    benchmark['data.train_person'] = fix_path(benchmark.get('data.train_person', ''), base_path)
    benchmark['data.test'] = fix_path(benchmark.get('data.test', ''), base_path)
    benchmark['models'] = dict([parse_model_info(x, base_path) for x in benchmark['models']])

    return benchmark

def parse_model_info(model_info, base_path):
    if isinstance(model_info, str):
        return (fix_path(model_info, base_path), {})

    model_file = None
    kwargs = {}
    for key, value in model_info.items():
        if key == 'filename':
            model_file = fix_path(value, base_path)
        else:
            kwargs[key] = value
    return (model_file, kwargs)

def fix_path(path, base_path):
    if path and not os.path.isabs(path):
        return os.path.normpath(base_path + os.sep + path)
    return path