""" Definition of the evaluative metrics used by CCOBRA.

"""

import json
import http.server as httpserver
import webbrowser

import numpy as np

def load_in_default_browser(html):
    class RequestHandler(httpserver.BaseHTTPRequestHandler):
        def do_GET(self):
            self.protocol_version = 'HTTP/1.0'

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Content-length', len(html))
            self.end_headers()

            buffer_size = 1024 ** 2
            for idx in range(0, len(html), buffer_size):
                self.wfile.write(html[idx:idx+buffer_size])

    server = httpserver.HTTPServer(('127.0.0.1', 0), RequestHandler)
    webbrowser.open('http://127.0.0.1:{}'.format(server.server_port))
    server.handle_request()

def ccobracolor(idx, n_models, lightness=0.5):
    x = (idx + 1) / (n_models + 1)
    r = (np.sin(x * 2 * np.pi * 1.247 + np.pi) * 127 + 128) * lightness
    g = (np.sin(x * 2 * np.pi * 0.373) * 127 + 128) * lightness
    b = (np.cos(x * 2 * np.pi * 0.91113) * 127 + 128) * lightness
    return '#' + ''.join([('0' + hex(int(y)).replace('0x', ''))[-2:] for y in [r, g, b]])

class HTMLVisualizer(object):
    def __init__(self, metrics):
        self.metrics = metrics

    def to_html(self, res_df):
        html_out = [
            "<html>",
            "    <head>",
            "        <script src=\"https://cdn.plot.ly/plotly-latest.min.js\"></script>",
            "    </head>",
            "    <body>",
            "        <h1>CCOBRA Evaluation Demonstration</h1>"
        ]

        for metric in self.metrics:
            metric_data, metric_layout = metric.evaluate(res_df)
            metric_data = json.dumps(metric_data) if not isinstance(metric_data, list) else ','.join(json.dumps(x) for x in metric_data)
            metric_name = metric.__class__.__name__
            metric_div = metric_name.lower()

            html_out.extend([
                "        <h2>{}</h2>".format(metric_name),
                "        <p>",
                metric.description(),
                "        </p>",
                "        <div id='{}'>".format(metric_div),
                "        </div>",
                "        <script>",
                "            var data = [",
                str(metric_data),
                "            ];",
                "            var layout = ",
                str(metric_layout),
                "            ;",
                "            Plotly.newPlot('{}', data, layout);".format(metric_div),
                "        </script>",
                "        <hr>"
            ])

        print('Adding boilerplate')
        html_out.extend([
            "    <script>",
            "        window.onresize = function() {",
            "        var arr = document.getElementsByTagName('script')",
            "        for (var n = 0; n < arr.length; n++)",
            "            eval(arr[n].innerHTML);",
            "        }",
            "    </script>",
            "    </body>",
            "</html>"
        ])

        return html_out

class CCobraMetric(object):
    def description(self):
        return ''

    def evaluate(self, result_df):
        raise NotImplementedError()

class Accuracy(CCobraMetric):
    def description(self):
        return 'Computes the accuracy of the models, i.e., the percentage of ' \
            'correct predictions.'

    def evaluate(self, result_df):
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

        layout = {'showlegend': 'true', 'legend': {'orientation': 'h'}}
        return data, layout

class SubjectBoxes(CCobraMetric):
    def description(self):
        return 'The following plot depicts boxplots for the models indicating ' \
            'individual subject performance. The data used for the plot are ' \
            'accuracies for individuals. Consequently, min and max refer to ' \
            'the accuracy of the worst and best matching subjects. The dots ' \
            'refer to the mean accuracies of individual participants.'

    def evaluate(self, result_df):
        subj_df = result_df.groupby(
            ['model', 'id'], as_index=False)['hit'].agg('mean')
        data = []
        n_models = len(subj_df['model'].unique())

        for model, df in subj_df.groupby('model'):
            data.append({
                'y': df['hit'].tolist(),
                'type': 'box',
                'name': model,
                'boxpoints': 'all',
                'marker': {
                    'size': 4
                }
            })

        data = sorted(data, key=lambda x: np.mean(x['y']))
        for idx, datum in enumerate(data):
            datum['marker']['color'] = ccobracolor(idx, n_models)
        layout = {'showlegend': 'true', 'legend': {'orientation': 'h'}}
        return data, layout
