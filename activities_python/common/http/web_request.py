"""Module for handling http requests."""

import json

from six.moves import BaseHTTPServer
from ..models.response import ControllerResponse


class WebRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """Class for handling http requests."""

    GET_METHOD = 'GET'
    POST_METHOD = 'POST'
    timeout = None

    def do_GET(self):
        """Handling GET requests."""
        # pylint: disable=invalid-name
        self.handle_method(self.GET_METHOD)

    def do_POST(self):
        """Handling POST requests."""
        # pylint: disable=invalid-name
        self.handle_method(self.POST_METHOD)

    def get_payload(self, max_size):
        """Getting payload."""
        # pylint: disable=protected-access
        self.timeout = (self.server.options.read_timeout_milliseconds/1000)
        payload_len = int(self.headers.get('content-length', 0))
        payload_len = min(payload_len, max_size)
        payload = self.rfile.read(payload_len)
        return payload

    def handle_method(self, method):
        """Handling arbitrary requests."""
        # pylint: disable=protected-access
        self.timeout = (self.server.options.write_timeout_milliseconds/1000)
        controller = self.server.routes_repo.get_controller(method, self.path, self.server.options)
        data = None
        if method == self.POST_METHOD:
            data = self.get_payload(self.server.options.max_request_size)
        result = controller.handle(data, None)
        if result.jsonize:
            result = ControllerResponse(
                response=json.dumps(result.response),
                status=result.status,
                mime=result.mime
            )
        self.send_response(result.status)
        self.send_header('Content-type', result.mime)
        self.end_headers()
        self.wfile.write(result.response.encode())
