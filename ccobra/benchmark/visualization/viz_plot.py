""" Plot-Based visualizations of the CCOBRA evaluation results.

"""

import os
import json

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

    def __init__(self, template_file):
        """ Initializes the Plot visualizer based on a template HTML filepath.

        Parameters
        ----------
        template_file : str
            Path to the template file underlying this visualizer.

        """

        super(PlotVisualizer, self).__init__()

        # Load the HTML template
        self.template = ''
        template_path = os.path.dirname(__file__) + os.sep + template_file
        with open(template_path) as file_handle:
            self.template = file_handle.read()

    def get_content_dict(self, result_df):
        """ Obtain the dictionary mapping from HTML template placeholders
        to content.

        Parameters
        ----------
        result_df : pd.DataFrame
            CCOBRA result dataframe.

        Returns
        -------
        dict(str, str)
            Returns the content dictionary mapping from template placeholders to html snippets.

        """

        raise NotImplementedError()

    def to_html(self, result_df):
        """ Fill template with content

        Parameters
        ----------
        result_df : pd.DataFrame
            CCOBRA result dataframe.

        Returns
        -------
        str
            Html content string for this visualizer.

        """

        # Obtain the template content
        content_dict = self.get_content_dict(result_df)

        # Fill the template and return the resulting HTML
        template = self.template
        for key, value in content_dict.items():
            template = template.replace('{{{{{}}}}}'.format(key), value)
        return template

class AccuracyVisualizer(PlotVisualizer):
    """ Accuracy visualizer depicting average numbers of hits for the set of
    models.

    """

    def __init__(self):
        """ Constructs the visualizer by providing the super class with the html template.

        """

        super(AccuracyVisualizer, self).__init__('template_accuracy.html')

    def get_content_dict(self, result_df):
        """ Constructs the template-html mapping dictionary.

        Parameters
        ----------
        result_df : pd.DataFrame
            CCOBRA result dataframe.

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

class BoxplotVisualizer(PlotVisualizer):
    """ Subject-Based boxplot visualizer for the CCOBRA evaluation results.
    Depicts boxplots for predictive accuracies on individuals as well as
    a swarmplot with corresponding values.

    """

    def __init__(self):
        """ Constructs the visualizer by providing the super class with the html template.

        """

        super(BoxplotVisualizer, self).__init__('template_box.html')

    def get_content_dict(self, result_df):
        """ Constructs the template-html mapping dictionary.

        Parameters
        ----------
        result_df : pd.DataFrame
            CCOBRA result dataframe.

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
