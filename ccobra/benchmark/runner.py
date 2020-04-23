""" Imports a given python script and instantiates the contained model if
available.

Copyright 2018 Cognitive Computation Lab
University of Freiburg
Nicolas Riesterer <riestern@tf.uni-freiburg.de>
Daniel Brand <daniel.brand@cognition.uni-freiburg.de>

"""

import argparse
import os
import sys
import logging
from contextlib import contextmanager

import pandas as pd

from . import evaluator
from . import server
from . import benchmark as bmark
from .visualization import html_creator, viz_plot

def parse_arguments():
    """ Parses the command line arguments for the benchmark runner.

    Returns
    -------
    dict
        Dictionary mapping from cmd arguments to values.

    """

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('benchmark', type=str, help='Benchmark file.')
    parser.add_argument('-m', '--model', type=str, help='Model file.')
    parser.add_argument(
        '-o', '--output', type=str, default='browser', help='Output style (browser/html).')
    parser.add_argument('-c', '--cache', type=str, help='Load specified cache file.')
    parser.add_argument('-s', '--save', type=str, help='Store results as csv table.')
    parser.add_argument(
        '-cn', '--classname', type=str,
        help='Load a specific class from a folder containing multiple classes.')
    parser.add_argument(
        '-ll', '--logginglevel', type=str, default='NONE',
        help='Set logging level [NONE, DEBUG, INFO, WARNING].'
    )

    args = vars(parser.parse_args())

    # Check for validity of command line arguments
    if not args['model'] and not args['benchmark']:
        print('ERROR: Must specify either model or benchmark.')
        parser.print_help()
        sys.exit(99)

    # Setup logging
    if args['logginglevel'].lower() == 'debug':
        logging.basicConfig(level=logging.DEBUG)
    elif args['logginglevel'].lower() == 'info':
        logging.basicConfig(level=logging.INFO)
    elif args['logginglevel'].lower() == 'warning':
        logging.basicConfig(level=logging.WARNING)

    return args

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

    Parameters
    ----------
    args : dict
        Command line argument dictionary.

    """

    # Load cache information
    cache_df = None
    if args['cache']:
        cache_df = pd.read_csv(args['cache'])

    # Load the benchmark settings
    cached = args.get('cache', False)
    benchmark = bmark.Benchmark(args['benchmark'], argmodel=args['model'], cached=(cache_df != None))

    # Run the model evaluation
    is_silent = (args['output'] in ['html', 'server'])
    eva = None
    if benchmark.type == 'adaption':
        eva = evaluator.AdaptionEvaluator(
            benchmark.models,
            benchmark.eval_comparator,
            benchmark.path_data_test,
            train_datafile=benchmark.path_data_train,
            train_data_person=benchmark.path_data_train_person,
            silent=is_silent,
            corresponding_data=benchmark.corresponding_data,
            domain_encoders=benchmark.encoders,
            cache_df=cache_df
        )
    elif benchmark.type == 'coverage':
        eva = evaluator.CoverageEvaluator(
            benchmark.models,
            benchmark.eval_comparator,
            benchmark.path_data_test,
            train_datafile=benchmark.path_data_train,
            train_data_person=benchmark.path_data_train_person,
            silent=is_silent,
            corresponding_data=benchmark.corresponding_data,
            domain_encoders=benchmark.encoders,
            cache_df=cache_df
        )
    else:
        raise ValueError('Unknown benchmark type: {}'.format(benchmark['type']))

    with silence_stdout(is_silent):
        res_df = eva.evaluate()

    if 'save' in args:
        res_df.to_csv(args['save'], index=False)

    # Run the metric visualizer
    htmlcrtr = html_creator.HTMLCreator([
        viz_plot.AccuracyVisualizer(),
        viz_plot.BoxplotVisualizer(),
        viz_plot.TableVisualizer()
    ])

    # Prepare the benchmark output information and visualize the evaluation results
    benchmark_info = {
        'name': os.path.basename(args['benchmark']),
        'data.train': os.path.basename(
            benchmark.path_data_train) if benchmark.path_data_train else '',
        'data.train_person': os.path.basename(
            benchmark.path_data_train_person) if benchmark.path_data_train_person else '',
        'data.test': os.path.basename(benchmark.path_data_test),
        'type': benchmark.type,
        'domains': list(res_df['domain'].unique()),
        'response_types': list(res_df['response_type'].unique()),
    }

    benchmark_info['corresponding_data'] = benchmark.corresponding_data

    # Generate the HTML output
    if args['output'] == 'browser':
        html = htmlcrtr.to_html(res_df, benchmark_info, embedded=False)
        server.load_in_default_browser(html.encode('utf8'))
    elif args['output'] == 'server':
        html = htmlcrtr.to_html(res_df, benchmark_info, embedded=True)
        sys.stdout.buffer.write(html.encode('utf-8'))
    elif args['output'] == 'html':
        html = htmlcrtr.to_html(res_df, benchmark_info, embedded=False)
        print(html)

def entry_point():
    """ Entry point for the CCOBRA executables.

    """

    args = parse_arguments()

    try:
        main(args)
    except Exception as exc:
        if args['output'] != 'html':
            raise
        msg = 'Error: ' + str(exc)
        if args['output'] == 'html':
            print('<p>{}</p><script>document.getElementById(\"result\").style.backgroundColor ' \
                '= \"Tomato\";</script>'.format(msg))
        else:
            print(exc)
        sys.exit()

if __name__ == '__main__':
    entry_point()
