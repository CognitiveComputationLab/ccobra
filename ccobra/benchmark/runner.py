""" Imports a given python script and instantiates the contained model if
available.

Copyright 2018 Cognitive Computation Lab
University of Freiburg
Nicolas Riesterer <riestern@tf.uni-freiburg.de>
Daniel Brand <daniel.brand@cognition.uni-freiburg.de>

"""

import argparse
import codecs
import datetime
import logging
import os
import sys
import webbrowser
from contextlib import contextmanager

import pandas as pd

from . import benchmark as bmark
from . import evaluator
from .visualization import html_creator, viz_plot

from ..version import __version__


def parse_arguments():
    """ Parses the command line arguments for the benchmark runner.

    Returns
    -------
    dict
        Dictionary mapping from cmd arguments to values.

    """

    parser = argparse.ArgumentParser(description='CCOBRA version {}.'.format(__version__))
    parser.add_argument('benchmark', type=str, help='Benchmark file.')
    parser.add_argument('-m', '--model', type=str, help='Model file.')
    parser.add_argument(
        '-o', '--output', type=str, default='browser', help='Output style (browser/server).')
    parser.add_argument('-c', '--cache', type=str, help='Load specified cache file.')
    parser.add_argument('-s', '--save', type=str, help='Store results as csv table.')
    parser.add_argument(
        '-cn', '--classname', type=str, default=None,
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
    benchmark = bmark.Benchmark(
        args['benchmark'],
        argmodel=(args['model'], args['classname']),
        cached=(cache_df is not None)
    )

    # Run the model evaluation
    is_silent = (args['output'] in ['html', 'server'])
    eva = evaluator.Evaluator(benchmark, is_silent=is_silent, cache_df=cache_df)
    with silence_stdout(is_silent):
        res_df, model_log = eva.evaluate()

    if 'save' in args:
        res_df.to_csv(args['save'], index=False)

    # Create metrics dictionary
    #(TODO: check if there is a good way of dynamically specify the visualization)
    default_list = [
        viz_plot.AccuracyVisualizer(),
        viz_plot.BoxplotVisualizer(),
        viz_plot.SubjectTableVisualizer()
    ]
    metrics = []
    for idx, eva in enumerate(benchmark.evaluation_handlers):
        if idx == 0:
            metrics.append((
                eva, [
                    viz_plot.AccuracyVisualizer(),
                    viz_plot.BoxplotVisualizer(),
                    viz_plot.SubjectTableVisualizer(),
                    viz_plot.MFATableVisualizer(),
                    viz_plot.ModelLogVisualizer()
                ]))
        else:
            metrics.append((
                eva, default_list
            ))

    # Run the metric visualizer
    htmlcrtr = html_creator.HTMLCreator(metrics)

    # Prepare the benchmark output information and visualize the evaluation results
    path_pre_train = ''
    path_pre_train_person = ''
    path_pre_person_background = ''
    path_test = os.path.basename(benchmark.data_test_path)

    if benchmark.data_pre_train_path:
        path_pre_train = ';'.join([
            os.path.basename(x) for x in benchmark.data_pre_train_path.split(';')])
    if benchmark.data_pre_train_person_path:
        path_pre_train_person = ';'.join([
            os.path.basename(x) for x in benchmark.data_pre_train_person_path.split(';')])
    if benchmark.data_pre_person_background_path:
        path_pre_person_background = ';'.join([
            os.path.basename(x) for x in benchmark.data_pre_person_background_path.split(';')])

    benchmark_info = {
        'name': os.path.basename(args['benchmark']),
        'data.test': path_test,
        'data.pre_train': path_pre_train,
        'data.pre_train_person': path_pre_train_person,
        'data.pre_person_background': path_pre_person_background,
        'type': benchmark.type,
        'domains': list(res_df['domain'].unique()),
        'response_types': list(res_df['response_type'].unique()),
    }

    benchmark_info['corresponding_data'] = benchmark.corresponding_data

    # Generate the HTML output
    if args['output'] == 'server':
        html = htmlcrtr.to_html(res_df, benchmark_info, model_log, embedded=True)
        sys.stdout.buffer.write(html.encode('utf-8'))
    else:
        html = htmlcrtr.to_html(res_df, benchmark_info, model_log, embedded=False)

        # Save HTML output to file
        benchmark_filename = os.path.splitext(os.path.basename(args['benchmark']))[0]
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        html_filename = '_'.join([benchmark_filename, timestamp, '.html'])
        html_filepath = os.path.join(benchmark.base_path, html_filename)

        with codecs.open(html_filepath, 'w', 'utf-8') as html_out:
            html_out.write(html)

        # Open HTML output in default browser
        webbrowser.open('file://' + os.path.realpath(html_filepath))

def entry_point():
    """ Entry point for the CCOBRA executables.

    """

    # Manually catch version command line argument
    if len(sys.argv) > 1 and sys.argv[1] == '--version':
        print('CCOBRA version {}'.format(__version__))
        exit()

    # Parse command line arguments
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
