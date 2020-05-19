"""Module with base class for actions."""

import abc
import six

from ..factories.logger import produce_logger
from .action_error import ActionError


@six.add_metaclass(abc.ABCMeta)
class BaseAction:
    """Base class for actions."""

    logger = {}
    lh_options = {}
    proxies = {}

    def __init__(self):
        """Constructor."""

    def create_logger(self, options):
        """Function to create logger from factory."""
        self.logger = produce_logger(options)
        return self

    def add_lh_options(self, lh_options):
        """lh_options setter."""
        self.lh_options = lh_options

    def add_proxies(self, proxies):
        """proxies setter."""
        self.proxies = proxies

    @abc.abstractmethod
    def invoke(self, data, context):
        """Abstract method for invoke action."""


def raise_action_error(code, message):
    """Function to raise standard error."""
    raise ActionError(code, message)


def check_input_params(data, param):
    """Function to check input parameters."""
    return param in data or raise_action_error(400, param + ' field is required')
