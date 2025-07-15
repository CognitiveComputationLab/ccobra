""" Plot-Based visualizations of the CCOBRA evaluation results.

"""

import os
import json
import collections

import numpy as np

def ccobracolor(idx, n_models, lightness=0.5):
    """ Generates the CCOBRA plot color palette.

    Parameters
    ----------
    idx : int
        Position in the CCOBRA color spectrum.

    n_models : int
        Number of models, i.e., number of colors to construct the color spectrum for.

    lightness : float, optional
        Lightness scaling factor of the color.

    Returns
    -------
    str
        Hexadecimal representation of the color (e.g, '#a65959')

    """

    val = (idx + 1) / (n_models + 1)
    col_r = (np.sin(val * 2 * np.pi * 1.247 + np.pi) * 127 + 128) * lightness
    col_g = (np.sin(val * 2 * np.pi * 0.373) * 127 + 128) * lightness
    col_b = (np.cos(val * 2 * np.pi * 0.91113) * 127 + 128) * lightness
    return '#' + ''.join(
        [('0' + hex(int(y)).replace('0x', ''))[-2:] for y in [col_r, col_g, col_b]])

class PlotVisualizer():
    """ Plot visualizer base class providing functionality for inserting HTML
    content into the output templates.

    """

    def __init__(self, benchmark, template_file, template_CSS=None):
        """ Initializes the Plot visualizer based on a template HTML filepath.

        Parameters
        ----------
        benchmark : dict(str, object)
            Benchmark properties.

        template_file : str
            Path to the template file underlying this visualizer.

        template_CSS : str
            Path to the template CSS file.

        """

        super(PlotVisualizer, self).__init__()

        # Member variables
        self.template_CSS = template_CSS
        self.benchmark = benchmark

        # Load the HTML template
        self.template = ''
        template_path = os.path.dirname(__file__) + os.sep + template_file
        with open(template_path) as file_handle:
            self.template = file_handle.read()

    def get_content_dict(self, result_df, eval_handler, model_log):
        """ Obtain the dictionary mapping from HTML template placeholders
        to content.

        Parameters
        ----------
        result_df : pd.DataFrame
            CCOBRA result dataframe.

        eval_handler : EvaluationHandler
            EvaluationHandler objects of the current evaluation

        model_log : dict(str, dict(str, object))
            Dictionary containing logging information that models supplied via end_participant.

        Returns
        -------
        dict(str, str)
            Returns the content dictionary mapping from template placeholders to html snippets.
            None is returned, if the prerequisites for the visualization are not met.

        """

        raise NotImplementedError()

    def to_html(self, result_df, eval_handler, model_log=None):
        """ Fill template with content

        Parameters
        ----------
        result_df : pd.DataFrame
            CCOBRA result dataframe.

        eval_handler : EvaluationHandler
            EvaluationHandler objects of the current evaluation

        model_log : dict(str, dict(str, object))
            Dictionary containing logging information that models supplied via end_participant.

        Returns
        -------
        str
            Html content string for this visualizer. None is returned, if the prerequisites
            for the visualization are not met.

        """

        # Obtain the template content
        content_dict = self.get_content_dict(result_df, eval_handler, model_log)

        # If the content dict is empty, the complete section can be skipped
        if content_dict is None:
            return None

        content_dict['PLOT_TYPE'] = eval_handler.data_column
        content_dict['COMPARATOR'] = eval_handler.comparator.get_name()

        # Fill the template and return the resulting HTML
        template = self.template
        for key, value in content_dict.items():
            template = template.replace('{{{{{}}}}}'.format(key), value)
        return template

    def shorttitle(self, eval_handler):
        """ Shorttitle for the visualizer.

        Parameters
        ----------
        eval_handler : EvaluationHandler
            EvaluationHandler objects of the current evaluation

        Returns
        -------
        str
            Shorttitle for the visualizer.

        """

        raise NotImplementedError('Shorttitle not defined.')

class AccuracyVisualizer(PlotVisualizer):
    """ Accuracy visualizer depicting average numbers of hits for the set of
    models.

    """

    def __init__(self, benchmark):
        """ Constructs the visualizer by providing the super class with the html template.

            Parameters
            ----------
            benchmark : dict(str, object)
                Benchmark properties.
        """
        super(AccuracyVisualizer, self).__init__(benchmark, 'template_accuracy.html')

    def get_content_dict(self, result_df, eval_handler, model_log):
        """ Constructs the template-html mapping dictionary.

        Parameters
        ----------
        result_df : pd.DataFrame
            CCOBRA result dataframe.

        eval_handler : EvaluationHandler
            EvaluationHandler objects of the current evaluation

        model_log : dict(str, dict(str, object))
            Dictionary containing logging information that models supplied via end_participant.

        Returns
        -------
        dict(str, str)
            Returns the content dictionary mapping from template placeholders to html snippets.

        """

        data_column = "score_{}".format(eval_handler.data_column)

        acc_df = result_df.groupby(
            'model', as_index=True)[data_column].agg(['mean', 'std']).sort_values('mean')

        n_models = len(acc_df.index.tolist())
        alpha = '80'
        data = {
            'x': acc_df.index.tolist(),
            'y': acc_df['mean'].tolist(),
            'marker': {
                'color': [ccobracolor(x, n_models) + alpha for x in range(n_models)]
            },
            'type': 'bar',
            'name': acc_df.index.tolist()
        }

        # Compute the explicit ordering
        ordering = result_df.groupby(
            'model', as_index=False)[data_column].agg('mean').sort_values(
                data_column, ascending=True)['model'].tolist()

        return {
            'PLOT_DATA': json.dumps(data),
            'ORDERING': json.dumps(ordering),
            'RANGEMODE': 'nonnegative' if np.all(acc_df['mean'] >= 0) else 'normal'
        }

    def shorttitle(self, eval_handler):
        """ Shorttitle for the visualizer.

        Returns
        -------
        str
            Shorttitle for the visualizer.

        """
        return "Bar Plot: {} ({})".format(
            eval_handler.comparator.get_name(), eval_handler.data_column)

class BoxplotVisualizer(PlotVisualizer):
    """ Subject-Based boxplot visualizer for the CCOBRA evaluation results.
    Depicts boxplots for predictive accuracies on individuals as well as
    a swarmplot with corresponding values.

    """

    def __init__(self, benchmark):
        """ Constructs the visualizer by providing the super class with the html template.

            Parameters
            ----------
            benchmark : dict(str, object)
                Benchmark properties.
        """

        super(BoxplotVisualizer, self).__init__(benchmark, 'template_box.html')

    def get_content_dict(self, result_df, eval_handler, model_log):
        """ Constructs the template-html mapping dictionary.

        Parameters
        ----------
        result_df : pd.DataFrame
            CCOBRA result dataframe.

        eval_handler : EvaluationHandler
            EvaluationHandler objects of the current evaluation

        model_log : dict(str, dict(str, object))
            Dictionary containing logging information that models supplied via end_participant.

        Returns
        -------
        dict(str, str)
            Returns the content dictionary mapping from template placeholders to html snippets.

        """
        data_column = "score_{}".format(eval_handler.data_column)

        subj_df = result_df.groupby(
            ['model', 'id'], as_index=False)[data_column].agg('mean')
        data = []
        n_models = len(subj_df['model'].unique())

        for model, model_df in subj_df.groupby('model'):
            data.append({
                'y': model_df[data_column].tolist(),
                'type': 'box',
                'name': model,
                'boxpoints': 'all',
                'marker': {
                    'size': 4
                },
                'text': ["Subj.ID: {}".format(x) for x in model_df['id']],
                'hoverinfo': 'text+y',
                #'hoverlabel': {
                #    'bgcolor': 'tomato',
                #    'font': {'color': 'black'}
                #}
            })

        data = sorted(data, key=lambda x: np.mean(x['y']))
        for idx, datum in enumerate(data):
            datum['marker']['color'] = ccobracolor(idx, n_models)

        # Compute the explicit ordering
        ordering = result_df.groupby(
            'model', as_index=False)[data_column].agg('mean').sort_values(
                data_column, ascending=True)['model'].tolist()

        return {
            'PLOT_DATA': json.dumps(data),
            'ORDERING': json.dumps(ordering),
            'RANGEMODE': 'nonnegative' if np.all(model_df[data_column] >= 0) else 'normal'
        }

    def shorttitle(self, eval_handler):
        """ Shorttitle for the visualizer.

        Returns
        -------
        str
            Shorttitle for the visualizer.

        """

        return 'Subject-Based Boxplots ({})'.format(eval_handler.data_column)

class MFATableVisualizer(PlotVisualizer):
    """ MFA table visualizer.

    """

    def __init__(self, benchmark):
        """ Constructs the visualizer by providing the super class with the html template.

            Parameters
            ----------
            benchmark : dict(str, object)
                Benchmark properties.
        """
        super(MFATableVisualizer, self).__init__(benchmark, 'template_mfa.html', template_CSS='template_mfa.css')

    def get_content_dict(self, result_df, eval_handler, model_log):
        """ Constructs the template-html mapping dictionary.

        Parameters
        ----------
        result_df : pd.DataFrame
            CCOBRA result dataframe.

        eval_handler : EvaluationHandler
            EvaluationHandler objects of the current evaluation

        model_log : dict(str, dict(str, object))
            Dictionary containing logging information that models supplied via end_participant.

        Returns
        -------
        dict(str, str)
            Returns the content dictionary mapping from template placeholders to html snippets.
            If no task encoding or encoder was provided, None is returned.

        """

        if np.any([x not in result_df for x in ['task_enc', 'prediction_enc_response', 'truth_enc_response']]):
            return None

        # Construct the MFA dictionary
        mfa_dict = {}
        for task, task_df in result_df.groupby('task_enc'):
            mfa_dict[task] = {}
            for model, model_df in task_df.groupby('model'):
                pred_counts = collections.Counter(model_df['prediction_enc_response'])
                pred_max_count = max([x[1] for x in pred_counts.items()])
                mfa = '<br>'.join(
                    sorted([x[0] for x in pred_counts.items() if x[1] == pred_max_count]))
                mfa_dict[task][model] = mfa

            # Add data MFA
            truth_counts = collections.Counter(task_df['truth_enc_response'])
            truth_max_count = max([x[1] for x in truth_counts.items()])
                
            mfa = '<br>'.join(
                sorted([x[0] for x in truth_counts.items() if x[1] == truth_max_count]))
            mfa_dict[task]['DATA'] = mfa

        if not mfa_dict:
            return None

        return {
            'MFA_DATA': json.dumps(mfa_dict),
            'RESPONSE_TYPE': json.dumps("multiple" if "multiple-choice" in result_df["response_type"].values else "default"),
            'TEXT': 'The following table summarizes the most-frequent ' \
                + 'predictions from the models to each syllogism.'
        }

    def shorttitle(self, eval_handler):
        """ Shorttitle for the visualizer.

        Returns
        -------
        str
            Shorttitle for the visualizer.

        """

        return 'Most-Frequent Answer Comparison'

class SubjectTableVisualizer(PlotVisualizer):
    """ MFA table visualizer.

    """

    def __init__(self, benchmark):
        """ Constructs the visualizer by providing the super class with the html template.

            Parameters
            ----------
            benchmark : dict(str, object)
                Benchmark properties.
        """
        super(SubjectTableVisualizer, self).__init__(benchmark, 'template_subject_table.html', template_CSS='template_subject_table.css')

    def get_content_dict(self, result_df, eval_handler, model_log):
        """ Constructs the template-html mapping dictionary.

        Parameters
        ----------
        result_df : pd.DataFrame
            CCOBRA result dataframe.

        eval_handler : EvaluationHandler
            EvaluationHandler objects of the current evaluation

        model_log : dict(str, dict(str, object))
            Dictionary containing logging information that models supplied via end_participant.

        Returns
        -------
        dict(str, str)
            Returns the content dictionary mapping from template placeholders to html snippets.
            If no task encoding or encoder was provided, None is returned.

        """

        pred_enc_name = "prediction_enc_{}".format(eval_handler.data_column)
        truth_enc_name = "truth_enc_{}".format(eval_handler.data_column)

        if np.any([x not in result_df for x in ['task_enc', pred_enc_name, truth_enc_name]]):
            return None

        if np.all([isinstance(x, float) and np.isnan(x) for x in result_df[pred_enc_name]]):
            return None

        if np.all([isinstance(x, float) and np.isnan(x) for x in result_df[truth_enc_name]]):
            return None

        return {
            'PRED_ENC_NAME' : pred_enc_name,
            'TRUTH_ENC_NAME' : truth_enc_name,
            'RESPONSE_TYPE': json.dumps("multiple" if "multiple-choice" in result_df["response_type"].values else "default"),
            'TEXT': 'The following section shows the results for specific subjects. Please select the subject' \
            + ' identifier using the selection box below.'
        }

    def shorttitle(self, eval_handler):
        """ Shorttitle for the visualizer.

        Returns
        -------
        str
            Shorttitle for the visualizer.

        """

        return "Subject Tables: {}".format(eval_handler.data_column)

class ModelLogVisualizer(PlotVisualizer):
    """ MFA table visualizer.

    """

    def __init__(self, benchmark):
        """ Constructs the visualizer by providing the super class with the html template.

            Parameters
            ----------
            benchmark : dict(str, object)
                Benchmark properties.
        """
        super(ModelLogVisualizer, self).__init__(benchmark, 'template_model_log.html', template_CSS='template_model_log.css')

    def get_content_dict(self, result_df, eval_handler, model_log):
        """ Constructs the template-html mapping dictionary.

        Parameters
        ----------
        result_df : pd.DataFrame
            CCOBRA result dataframe.

        eval_handler : EvaluationHandler
            EvaluationHandler objects of the current evaluation

        model_log : dict(str, dict(str, object))
            Dictionary containing logging information that models supplied via end_participant.

        Returns
        -------
        dict(str, str)
            Returns the content dictionary mapping from template placeholders to html snippets.
            None is returned if no logged informations are available.

        """

        if model_log is None or len(model_log) == 0:
            return None

        return {
            'MODEL_LOGS' : json.dumps(model_log),
            'ANALYSIS_TYPE': json.dumps(self.benchmark.type),
            'TEXT' : 'Logged information from the models.'
        }

    def shorttitle(self, eval_handler):
        """ Shorttitle for the visualizer.

        Returns
        -------
        str
            Shorttitle for the visualizer.

        """

        return 'Model Logs'
