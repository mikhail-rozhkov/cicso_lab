"""Module containing use case for executing inside usual server."""
import ssl

from ..factories.options import produce_options
from ..factories.logger import produce_logger
from ..http.web_server import WebServer
from ..http.web_request import WebRequestHandler
from ..repositories.routes import RoutesRepository


class ServerUseCase:
    """Class containing use case for executing inside usual server."""

    def execute(self):
        """Main function for execution of use case."""
        # pylint: disable=no-self-use
        opts = produce_options(False)
        logger = produce_logger(opts)
        try:
            logger.info('Options %s', opts.__dict__)
            opts.validate()
            routes_repo = RoutesRepository()
            http_server = WebServer(routes_repo, opts, ('', opts.port), WebRequestHandler)
            if opts.cert_file == "" or opts.pkey_file == "":
                logger.exception("Failed to start server, missing certs")
                exit()
            cert_reqs = ssl.CERT_REQUIRED
            if opts.disable_cert_validation:
                cert_reqs = ssl.CERT_NONE
            http_server.socket = ssl.wrap_socket(
                http_server.socket,
                certfile=opts.cert_file,
                keyfile=opts.pkey_file,
                ca_certs=opts.ca_file,
                cert_reqs=cert_reqs,
                server_side=True,
                ssl_version=ssl.PROTOCOL_TLSv1_2
            )
            logger.info('Starting HTTP server at port %d', opts.port)
            try:
                http_server.serve_forever()
            except KeyboardInterrupt:
                pass
            logger.info('Stopping HTTP server')
            http_server.server_close()
        except ValueError:
            logger.exception("Value error")
            exit()
