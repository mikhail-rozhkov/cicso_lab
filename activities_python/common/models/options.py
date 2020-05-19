"""Module containing global options"""

import os
import grp
import pwd
from dotenv import load_dotenv, find_dotenv
from ..constants.controller import ControllerConstants


class Options:
    """Class for global options"""
    # pylint: disable=too-many-instance-attributes

    __DAY_IN_MS = 86400000

    __DISABLE_CERT_FILE_PATH = "secrets/ssl/cert/.disable_cert_validation"

    __parser = {}

    port = 8082

    cert_file = "secrets/ssl/cert/certificate.pem"
    pkey_file = "secrets/ssl/cert/private_key.pem"
    ca_file = ""
    secret_key = ""

    user_gid = ""
    user_pid = ""
    user_uid = ""

    log_level = "DEBUG"

    max_header_size = 1 << 12
    max_request_size = 1 << 16

    timeout_milliseconds = 30000
    read_timeout_milliseconds = 10000
    write_timeout_milliseconds = 30000

    disable_cert_validation = False

    enable_jail = True
    jailed_user = ""
    jailed_dir = ""

    def __init__(self, parser):
        self.__parser = parser

    def load_environment(self, is_lambda):
        """Function to load options from env vars."""
        load_dotenv(find_dotenv())
        self.secret_key = os.environ.get("SECRETKEY") or self.secret_key
        self.cert_file = os.environ.get("CERTFILE") or self.cert_file
        self.pkey_file = os.environ.get("PKEYFILE") or self.pkey_file
        self.ca_file = os.environ.get("CAFILE") or self.ca_file
        self.log_level = os.environ.get("LOG_LEVEL") or self.log_level
        self.port = os.environ.get("PORT") or self.port
        self.disable_cert_validation = os.path.isfile(self.__DISABLE_CERT_FILE_PATH)
        if is_lambda:
            self.enable_jail = False
        else:
            self.enable_jail = True
            self.jailed_user = os.environ.get("JAIL_USERNAME") or ""
            self.jailed_dir = os.environ.get("JAIL_DIR") or ""
        self.timeout_milliseconds = os.environ.get("TIMEOUT") or self.timeout_milliseconds
        self.read_timeout_milliseconds = os.environ.get("READ_TIMEOUT") or self.read_timeout_milliseconds
        self.write_timeout_milliseconds = os.environ.get("WRITE_TIMEOUT") or self.write_timeout_milliseconds

    def parse_flags(self):
        """Function to load options from input flags."""
        args = self.__parser.parse_args()
        for arg in vars(args):
            value = getattr(args, arg)
            if value:
                setattr(self, arg, value)

    def validate(self):
        """Function to validate options."""
        self.port = int(self.port)
        self.timeout_milliseconds = int(self.timeout_milliseconds)
        self.write_timeout_milliseconds = int(self.write_timeout_milliseconds)
        self.read_timeout_milliseconds = int(self.read_timeout_milliseconds)

        if self.enable_jail:
            try:
                self.user_uid = pwd.getpwnam(self.jailed_user).pw_uid
                self.user_gid = grp.getgrnam(self.jailed_user).gr_gid
            except KeyError:
                raise ValueError("Jailed user " + self.jailed_user + " not found")

        self.__verify_int64_range("timeout", self.timeout_milliseconds, 10, self.__DAY_IN_MS)
        self.__verify_int64_range("write_timeout", self.write_timeout_milliseconds, 10, self.__DAY_IN_MS)
        self.__verify_int64_range("read_timeout", self.read_timeout_milliseconds, 10, self.__DAY_IN_MS)

    def get_jail_params(self):
        """Function to get params for chroot jail."""
        return {
            ControllerConstants.IS_JAILED: self.enable_jail,
            ControllerConstants.USER_GID: self.user_gid,
            ControllerConstants.USER_UID: self.user_uid,
            ControllerConstants.JAIL_DIR: self.jailed_dir
        }

    def __verify_int64_range(self, name, val, minimum, maximum):
        if val < minimum or val >= maximum:
            self.__parser.print_help()
            raise ValueError(name + " specified incorrectly")
