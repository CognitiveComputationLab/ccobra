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

    def __init__(self, template_file, template_CSS=None):
        """ Initializes the Plot visualizer based on a template HTML filepath.

        Parameters
        ----------
        template_file : str
            Path to the template file underlying this visualizer.

        template_CSS : str
            Path to the template CSS file.

        """

        super(PlotVisualizer, self).__init__()

        # Member variables
        self.template_CSS = template_CSS

        # Load the HTML template
        self.template = ''
        template_path = os.path.dirname(__file__) + os.sep + template_file
        with open(template_path) as file_handle:
            self.template = file_handle.read()

    def get_content_dict(self, result_df, model_log):
        """ Obtain the dictionary mapping from HTML template placeholders
        to content.

        Parameters
        ----------
        result_df : pd.DataFrame
            CCOBRA result dataframe.
            
        model_log : dict(str, dict(str, object))
            Dictionary containing logging information that models supplied via end_participant.

        Returns
        -------
        dict(str, str)
            Returns the content dictionary mapping from template placeholders to html snippets.
            None is returned, if the prerequisites for the visualization are not met.

        """

        raise NotImplementedError()

    def to_html(self, result_df, model_log=None):
        """ Fill template with content

        Parameters
        ----------
        result_df : pd.DataFrame
            CCOBRA result dataframe.
            
        model_log : dict(str, dict(str, object))
            Dictionary containing logging information that models supplied via end_participant.
            
        Returns
        -------
        str
            Html content string for this visualizer. None is returned, if the prerequisites
            for the visualization are not met.

        """

        # Obtain the template content
        content_dict = self.get_content_dict(result_df, model_log)
        
        # If the content dict is empty, the complete section can be skipped
        if content_dict is None:
            return None

        # Fill the template and return the resulting HTML
        template = self.template
        for key, value in content_dict.items():
            template = template.replace('{{{{{}}}}}'.format(key), value)
        return template

    def shorttitle(self):
        """ Shorttitle for the visualizer.

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

    def __init__(self):
        """ Constructs the visualizer by providing the super class with the html template.

        """

        super(AccuracyVisualizer, self).__init__('template_accuracy.html')

    def get_content_dict(self, result_df, model_log):
        """ Constructs the template-html mapping dictionary.

        Parameters
        ----------
        result_df : pd.DataFrame
            CCOBRA result dataframe.
            
        model_log : dict(str, dict(str, object))
            Dictionary containing logging information that models supplied via end_participant.

        Returns
        -------
        dict(str, str)
            Returns the content dictionary mapping from template placeholders to html snippets.

        """

        acc_df = result_df.groupby(
            'model', as_index=False)['hit'].agg(['mean', 'std']).sort_values('mean')

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
            'model', as_index=False)['hit'].agg('mean').sort_values(
                'hit', ascending=True)['model'].tolist()

        return {
            'PLOT_DATA': json.dumps(data),
            'ORDERING': json.dumps(ordering)
        }

    def shorttitle(self):
        """ Shorttitle for the visualizer.

        Returns
        -------
        str
            Shorttitle for the visualizer.

        """

        return 'Prediction Accuracy'

class BoxplotVisualizer(PlotVisualizer):
    """ Subject-Based boxplot visualizer for the CCOBRA evaluation results.
    Depicts boxplots for predictive accuracies on individuals as well as
    a swarmplot with corresponding values.

    """

    def __init__(self):
        """ Constructs the visualizer by providing the super class with the html template.

        """

        super(BoxplotVisualizer, self).__init__('template_box.html')

    def get_content_dict(self, result_df, model_log):
        """ Constructs the template-html mapping dictionary.

        Parameters
        ----------
        result_df : pd.DataFrame
            CCOBRA result dataframe.
            
        model_log : dict(str, dict(str, object))
            Dictionary containing logging information that models supplied via end_participant.

        Returns
        -------
        dict(str, str)
            Returns the content dictionary mapping from template placeholders to html snippets.

        """

        subj_df = result_df.groupby(
            ['model', 'id'], as_index=False)['hit'].agg('mean')
        data = []
        n_models = len(subj_df['model'].unique())

        for model, model_df in subj_df.groupby('model'):
            data.append({
                'y': model_df['hit'].tolist(),
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
            'model', as_index=False)['hit'].agg('mean').sort_values(
                'hit', ascending=True)['model'].tolist()

        return {
            'PLOT_DATA': json.dumps(data),
            'ORDERING': json.dumps(ordering)
        }

    def shorttitle(self):
        """ Shorttitle for the visualizer.

        Returns
        -------
        str
            Shorttitle for the visualizer.

        """

        return 'Subject-Based Boxplots'

class MFATableVisualizer(PlotVisualizer):
    """ MFA table visualizer.

    """

    def __init__(self):
        super(MFATableVisualizer, self).__init__('template_mfa.html', 'template_mfa.css')

    def get_content_dict(self, result_df, model_log):
        """ Constructs the template-html mapping dictionary.

        Parameters
        ----------
        result_df : pd.DataFrame
            CCOBRA result dataframe.
            
        model_log : dict(str, dict(str, object))
            Dictionary containing logging information that models supplied via end_participant.

        Returns
        -------
        dict(str, str)
            Returns the content dictionary mapping from template placeholders to html snippets.
            If no task encoding or encoder was provided, None is returned.

        """

        is_broken = result_df[['task_enc', 'prediction_enc', 'truth_enc']].apply(
            lambda x: len(x[0]) == len(x[1]) == len(x[2]) == 0, axis=1)

        if np.all(is_broken):
            return None

        # Construct the MFA dictionary
        mfa_dict = {}
        for task, task_df in result_df.groupby('task_enc'):
            mfa_dict[task] = {}
            for model, model_df in task_df.groupby('model'):
                pred_counts = collections.Counter(model_df['prediction_enc'])
                pred_max_count = max([x[1] for x in pred_counts.items()])
                mfa = '<br>'.join(
                    sorted([x[0] for x in pred_counts.items() if x[1] == pred_max_count]))
                mfa_dict[task][model] = mfa

            # Add data MFA
            truth_counts = collections.Counter(task_df['truth_enc'])
            truth_max_count = max([x[1] for x in truth_counts.items()])
            mfa = '<br>'.join(
                sorted([x[0] for x in truth_counts.items() if x[1] == truth_max_count]))
            mfa_dict[task]['DATA'] = mfa

        if not mfa_dict:
            return None

        return {
            'MFA_DATA': json.dumps(mfa_dict),
            'TEXT': 'The following table summarizes the most-frequent ' \
                + 'predictions from the models to each syllogism.'
        }

    def shorttitle(self):
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

    def __init__(self):
        super(SubjectTableVisualizer, self).__init__('template_subject_table.html', 'template_subject_table.css')

    def get_content_dict(self, result_df, model_log):
        """ Constructs the template-html mapping dictionary.

        Parameters
        ----------
        result_df : pd.DataFrame
            CCOBRA result dataframe.

        Returns
        -------
        dict(str, str)
            Returns the content dictionary mapping from template placeholders to html snippets.
            If no task encoding or encoder was provided, None is returned.

        """

        is_broken = result_df[['task_enc', 'prediction_enc', 'truth_enc']].apply(
            lambda x: len(x[0]) == len(x[1]) == len(x[2]) == 0, axis=1)

        if np.all(is_broken):
            return None

        return {
            'TEXT': 'The following section shows the results for specific subjects. Please select the subject' \
            + ' identifier using the selection box below.'
        }

    def shorttitle(self):
        """ Shorttitle for the visualizer.

        Returns
        -------
        str
            Shorttitle for the visualizer.

        """

        return 'Subject Results'

class ModelLogVisualizer(PlotVisualizer):
    """ MFA table visualizer.

    """

    def __init__(self):
        super(ModelLogVisualizer, self).__init__('template_model_log.html', 'template_model_log.css')

    def get_content_dict(self, result_df, model_log):
        """ Constructs the template-html mapping dictionary.

        Parameters
        ----------
        result_df : pd.DataFrame
            CCOBRA result dataframe.
            
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
            'TEXT' : 'Logged information from the models.'
        }

    def shorttitle(self):
        """ Shorttitle for the visualizer.

        Returns
        -------
        str
            Shorttitle for the visualizer.

        """

        return 'Model Logs'