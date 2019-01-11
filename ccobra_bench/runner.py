""" Imports a given python script and instantiates the contained model if
available.

Copyright 2018 Cognitive Computation Lab
University of Freiburg
Nicolas Riesterer <riestern@tf.uni-freiburg.de>

"""

import argparse
import json
import os
import sys
from contextlib import contextmanager

import pandas as pd

import evaluator
import metrics
import comparator

def parse_arguments():
    """ Parses the command line arguments for the benchmark runner.

    """

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('benchmark', type=str, help='Benchmark file.')
    parser.add_argument('-m', '--model', type=str, help='Model file.')
    parser.add_argument('-o', '--output', type=str, default='browser', help='Output style (browser/html).')
    parser.add_argument('-c', '--cache', type=str, help='Load specified cache file.')
    parser.add_argument('-s', '--save', type=str, help='Store results as csv table.')

    args = vars(parser.parse_args())

    if not args['model'] and not args['benchmark']:
        print('ERROR: Must specify either model or benchmark.')
        parser.print_help()
        sys.exit(99)

    return args

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
    def fix_path(path):
        if path and not os.path.isabs(path):
            return os.path.normpath(base_path + os.sep + path)
        return path

    benchmark['data.train'] = fix_path(benchmark['data.train'])
    benchmark['data.test'] = fix_path(benchmark['data.test'])
    benchmark['models'] = [fix_path(x) for x in benchmark['models']]

    return benchmark

@contextmanager
def silence_stdout(silent, target=os.devnull):
    """ Contextmanager to silence stdout printing.

    Parameters
    ----------
    silent : bool
        Flag to indicate whether contextmanager should actually silence stdout.

    target : filepath, optional
        Target to redirect silenced stdout output to. Default is os.devnull.
        Can be modified to point to a log file instead.

    """

    new_target = open(target, 'w') if silent else sys.stdout
    old_target, sys.stdout = sys.stdout, new_target
    try:
        yield new_target
    finally:
        sys.stdout = old_target

def main(args):
    """ Main benchmark routine. Parses the arguments, loads models and data,
    runs the evaluation loop and produces the output.

    """

    # Compose the model list
    modellist = []
    if args['model']:
        modellist.append(args['model'])

    # Load the benchmark settings
    benchmark = None
    benchmark = load_benchmark(args['benchmark'])
    corresponding_data = False
    if 'corresponding_data' in benchmark:
        corresponding_data = benchmark['corresponding_data']

    # Only extend if not cached
    cache_df = pd.DataFrame()
    if not args['cache']:
        modellist.extend(benchmark['models'])
    else:
        cache_df = pd.read_csv(args['cache'])

    # Extract comparator settings from benchmark description
    eval_comparator = comparator.EqualityComparator()
    if 'comparator' in benchmark:
        if benchmark['comparator'] == 'nvc':
            eval_comparator = comparator.NVCComparator()

    # Run the model evaluation
    is_silent = (args['output'] == 'html')
    ev = evaluator.Evaluator(
        modellist,
        eval_comparator,
        benchmark['data.test'],
        train_datafile=benchmark['data.train'],
        silent=is_silent,
        corresponding_data=corresponding_data)

    with silence_stdout(is_silent):
        res_df = ev.evaluate()
        res_df = pd.concat([res_df, cache_df])

    if 'save' in args:
        res_df.to_csv(args['save'], index=False)

    # Run the metric visualizer
    html_viz = metrics.HTMLVisualizer([
        metrics.Accuracy(),
        metrics.SubjectBoxes()
    ])
    html = html_viz.to_html(res_df)

    if args['output'] == 'browser':
        metrics.load_in_default_browser('\n'.join(html).encode('utf8'))
    elif args['output'] == 'html':
        print(' '.join(html))

if __name__ == '__main__':
    args = parse_arguments()

    try:
        main(args)
    except Exception as e:
        if args['output'] != 'html':
            raise
        msg = 'Error: ' + str(e)
        if args['output'] == 'html':
            print('<p>{}</p><script>document.getElementById(\"result\").style.backgroundColor = \"Tomato\";</script>'.format(msg))
        else:
            print(e)
        sys.exit()
