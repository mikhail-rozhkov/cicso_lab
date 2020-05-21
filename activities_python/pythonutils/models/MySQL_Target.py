"""Module for the adapter target classes. """

import pymysql.cursors

from ..utils import get_optional_value
from ...common.action_support.base import check_input_params


class MySQLTarget():
    """Class representing the adapter target. """

    # PROTOCOL = "protocol"
    HOST = "host"
    # PORT = "port"
    # DISABLE_SSL = "disable_certificate_validation"
    CHARSET = "charset"
    DB = "db"

    def fill_host(self, data):
        """Set the target host. """
        check_input_params(data, self.HOST)
        self.host = data[self.HOST]

    # def fill_protocol(self, data):
    #     """Set the target protocol, or use 'http' as default if not provided. """
    #     self.protocol = get_optional_value(data, self.PROTOCOL, "http")
    #     self.protocol = self.protocol or "http"
    #
    # def fill_port(self, data):
    #     """Set the target port. """
    #     self.port = get_optional_value(data, self.PORT, None)
    #     if self.port:
    #         self.port = ":" + str(self.port)
    #     else:
    #         self.port = ""
    #
    # def fill_disable_ssl_verification(self, data):
    #     """Set the option to enable/disable SSL verification. """
    #     disable_ssl_verification = get_optional_value(data, self.DISABLE_SSL, False)
    #     self.verify_ssl = not bool(disable_ssl_verification)

    def __init__(self, data):
        self.fill_host(data)
        self.fill_charset(data)
        self.fill_db(data)
        self.cursor = pymysql.cursors.DictCursor
        # self.fill_protocol(data)
        # self.fill_port(data)
        # self.fill_disable_ssl_verification(data)

    def fill_charset(self, data):
        """Set the target charset, or use a default if not provided. """
        self.charset = get_optional_value(data, self.CHARSET, "utf8mb4")
        self.charset = self.charset or "utf8mb4"

    def fill_db(self, data):
        """Set the target DB. """
        check_input_params(data, self.DB)
        self.db = data[self.DB]

    def get_params(self):
        return {
            'host': self.host,
            'db': self.db,
            'charset': self.charset,
            'cursor': self.cursor
        }

    # def get_host(self):
    #     """Return the host in URI format. """
    #     return '{}://{}{}'.format(self.protocol, self.host, self.port)
