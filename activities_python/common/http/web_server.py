"""Module for creating web server."""

from six.moves.socketserver import ForkingMixIn  # pylint: disable=relative-import
from six.moves import BaseHTTPServer


class WebServer(ForkingMixIn, BaseHTTPServer.HTTPServer):
    """Class for creating web server."""

    def __init__(self, routes_repo, options, *args, **kw):
        self.timeout = options.timeout_milliseconds/1000
        BaseHTTPServer.HTTPServer.__init__(self, *args, **kw)
        self.routes_repo = routes_repo
        self.options = options
