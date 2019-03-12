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

    benchmark['data.train'] = fix_rel_path(benchmark.get('data.train'), base_path)
    benchmark['data.train_person'] = fix_rel_path(benchmark.get('data.train_person', ''), base_path)
    benchmark['data.test'] = fix_rel_path(benchmark.get('data.test', ''), base_path)
    benchmark['models'] = dict([parse_model_info(x, base_path) for x in benchmark['models']])

    return benchmark

def parse_model_info(model_info, base_path):
    if isinstance(model_info, str):
        return (fix_model_path(model_info, base_path), {})

    model_file = None
    kwargs = {}
    for key, value in model_info.items():
        if key == 'filename':
            model_file = fix_model_path(value, base_path)
        else:
            kwargs[key] = value
    return (model_file, kwargs)

def fix_rel_path(path, base_path):
    if path and not os.path.isabs(path):
        return os.path.normpath(base_path + os.sep + path)
    return path
    
def fix_model_path(path, base_path=None):
    abs_path = path
    if base_path:
        abs_path = fix_rel_path(path, base_path)
    
    if os.path.isfile(abs_path) and abs_path[-2:] == "py":
        return abs_path
        
    python_files = []
    sub_directories = []
    for f in os.listdir(abs_path):
        f_path = os.path.join(abs_path, f)
        
        if os.path.isfile(f_path) and f[-2:] == "py":
            python_files.append(f_path)
        elif os.path.isdir(f_path) and f[0] != "." and f[:2] != "__":
            sub_directories.append(f_path)

    if len(python_files) > 0:
        return abs_path
        
    if len(sub_directories) == 1:
        python_files = [
            os.path.join(sub_directories[0], f) for f in os.listdir(
                sub_directories[0]) if os.path.isfile(
                    os.path.join(sub_directories[0], f)) and f[-2:] == "py"]
        if len(python_files) > 0:
            return sub_directories[0]
    
    raise ValueError("Could not identify model to load for '{}'".format(path))
        
        