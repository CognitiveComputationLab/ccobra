""" Module for the html output creation class.

"""

import os
import datetime
import json
import codecs

class HTMLCreator():
    """ Html output construction class.

    """

    def __init__(self, metrics):
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
            'cssness': 'html_style.css'
        }
        for key, path in ext_content_paths.items():
            path = os.path.dirname(__file__) + os.sep + path
            with codecs.open(path, "r", "utf-8") as file_handle:
                self.external_contents[key] = file_handle.read()

    def to_html(self, result_df, benchmark_name, embedded=False):
        """ Generates the html output string.

        """

        result_data = json.dumps(result_df.to_csv(index=False).split('\n'))
        benchmark_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        content = []
        for metric in self.metrics:
            metric_html = metric.to_html(result_df)
            content.append(metric_html)
            content.append('<hr>')

        # Generate auxiliary scripts
        scripts = []
        if not embedded:
            scripts.append('\n'.join([
                "           window.onresize = function() {",
                "           var arr = document.getElementsByTagName('script')",
                "           for (var n = 0; n < arr.length; n++)",
                "               eval(arr[n].innerHTML);",
                "           }"
            ]))

        content_dict = {
            'CSSNESS': self.external_contents['cssness'],
            'PLOTLY_LIB': self.external_contents['plotly'],
            'HTML2CANVAS_LIB': self.external_contents['html2canvas'],
            'RESULT_DATA': result_data,
            'BENCHMARK_NAME': benchmark_name,
            'BENCHMARK_DATE': benchmark_date,
            'CONTENT': '\n\n'.join(content),
            'SCRIPTS': '\n\n'.join(scripts)
        }

        template = self.external_contents['template']
        for key, value in content_dict.items():
            template = template.replace('{{{{{}}}}}'.format(key), value)
        return template
