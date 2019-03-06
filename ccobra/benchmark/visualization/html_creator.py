import os
import datetime
import json
import codecs

class HTMLCreator():
    def __init__(self, metrics):
        self.metrics = metrics

        # Load the template
        self.template = ''
        template_path = os.path.dirname(__file__) + os.sep + 'template_page.html'

        with codecs.open(template_path, "r", "utf-8") as tf:
            self.template = tf.read()

    def to_html(self, result_df, benchmark_name, embedded=False):
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
            'RESULT_DATA': result_data,
            'BENCHMARK_NAME': benchmark_name,
            'BENCHMARK_DATE': benchmark_date,
            'CONTENT': '\n\n'.join(content),
            'SCRIPTS': '\n\n'.join(scripts)
        }

        template = self.template
        for key, value in content_dict.items():
            template = template.replace('{{{{{}}}}}'.format(key), value)
        return template
