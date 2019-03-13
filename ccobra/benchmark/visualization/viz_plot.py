""" Plot-Based visualizations.

"""

import os
import json

import numpy as np

from . import base

class PlotVisualizer(base.CCobraVisualizer):
    """ Plot visualizer baseclass providing functionality for inserting HTML
    content into the output templates.

    """

    def __init__(self, template_file):
        super(PlotVisualizer, self).__init__()

        # Load the HTML template
        self.template = ''
        template_path = os.path.dirname(__file__) + os.sep + template_file
        with open(template_path) as file_handle:
            self.template = file_handle.read()

    def get_content_dict(self, result_df):
        """ Obtain the dictionary mapping from HTML template placeholders
        to content.

        """

        raise NotImplementedError()

    def to_html(self, result_df):
        """ Fill template with content

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
        super(AccuracyVisualizer, self).__init__('template_accuracy.html')

    def get_content_dict(self, result_df):
        acc_df = result_df.groupby(
            'model', as_index=False)['hit'].agg(['mean', 'std']).sort_values('mean')

        n_models = len(acc_df.index.tolist())
        alpha = '80'
        data = {
            'x': acc_df.index.tolist(),
            'y': acc_df['mean'].tolist(),
            'marker': {
                'color': [base.ccobracolor(x, n_models) + alpha for x in range(n_models)]
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
        super(BoxplotVisualizer, self).__init__('template_box.html')

    def get_content_dict(self, result_df):
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
            datum['marker']['color'] = base.ccobracolor(idx, n_models)

        # Compute the explicit ordering
        ordering = result_df.groupby(
            'model', as_index=False)['hit'].agg('mean').sort_values(
                'hit', ascending=True)['model'].tolist()

        return {
            'PLOT_DATA': json.dumps(data),
            'ORDERING': json.dumps(ordering)
        }
