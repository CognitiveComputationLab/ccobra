""" Definition of the evaluative metrics used by CCOBRA.

"""

import http.server as httpserver
import webbrowser

def load_in_default_browser(html):
    """ Opens the html content in the default web browser by temporarily launching a http get
    server and providing the CCOBRA html output.

    Parameters
    ----------
    html : str
        Html content to serve.

    """

    class RequestHandler(httpserver.BaseHTTPRequestHandler):
        """ CCOBRA html request handler.

        """

        def do_GET(self):
            """ Implement the get request handler responding with the html content.

            """

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
