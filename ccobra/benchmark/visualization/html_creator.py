""" Module for the html output creation class.

"""

import os
import datetime
import json
import codecs

class HTMLCreator():
    """ Html output creator. Constructs the HTML string for displaying the CCOBRA evaluation
    results.

    """

    def __init__(self, metrics):
        """ Initializes the html creator with a list of metrics, i.e., components for constructing
        different views on the data (e.g., an accuracy plot).

        Parameters
        ----------
        metrics : list
            List of metric visualization objects, i.e., components for creating html snippets
            representing views (e.g., plots) on the data.

        """

        self.metrics = metrics

        # Load the template
        self.external_contents = {
            'template': '',
            'plotly': '',
            'html2canvas': '',
            'cssness': ''
        }

        ext_content_paths = {
            'template': 'template_page.html',
            'plotly': 'plotly-latest.min.js',
            'html2canvas': 'html2canvas.min.js',
            'cssness': 'template_page.css'
        }

        for key, path in ext_content_paths.items():
            path = os.path.dirname(__file__) + os.sep + path
            with codecs.open(path, "r", "utf-8") as file_handle:
                self.external_contents[key] = file_handle.read() + '\n'

    def to_html(self, result_df, benchmark, embedded=False):
        """ Generates the html output string.

        Returns
        -------
        str
            String containing html code representing the CCOBRA evaluation results.

        """

        result_data = json.dumps(result_df.to_csv(index=False).split('\n'))
        benchmark['date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        # Construct the content for the website
        content = []
        css_dependencies = []
        for metric in self.metrics:
            # Add dependencies
            if metric.template_CSS:
                css_dependencies.append(metric.template_CSS)

            # Add HTML content div
            metric_html = metric.to_html(result_df)
            metric_tab_data = (metric.shorttitle().lower(), metric.shorttitle())

            metric_content = '<div id="{}-bar" class="bar">{}</div>'.format(metric_tab_data[0], metric_tab_data[0], metric_tab_data[1])
            metric_content += '<div id="{}" class="bar-content">{}</div>'.format(metric_tab_data[0], metric_html)

            content.append(metric_content)

        # Generate auxiliary scripts
        scripts = []
        if not embedded:
            scripts.append('\n'.join([
                "           window.addEventListener('resize', function() {",
                "           var arr = document.getElementsByTagName('script')",
                "           for (var n = 0; n < arr.length; n++)",
                "               eval(arr[n].innerHTML);",
                "           });"
            ]))

        # Construct CSS from visualizer dependencies
        css_content = self.external_contents['cssness']
        for fname in css_dependencies:
            path = os.path.dirname(__file__) + os.sep + fname
            with codecs.open(path, "r", "utf-8") as file_handle:
                css_content += file_handle.read() + '\n'

        content_dict = {
            'CSSNESS': css_content,
            'PLOTLY_LIB': self.external_contents['plotly'],
            'HTML2CANVAS_LIB': self.external_contents['html2canvas'],
            'RESULT_DATA': result_data,
            'BENCHMARK': json.dumps(benchmark),
            'CONTENT': '\n\n'.join(content),
            'SCRIPTS': '\n\n'.join(scripts)
        }

        template = self.external_contents['template']
        for key, value in content_dict.items():
            template = template.replace('{{{{{}}}}}'.format(key), value)
        return template
