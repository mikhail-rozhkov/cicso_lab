"""Module with base class for controllers."""

import abc
import six


@six.add_metaclass(abc.ABCMeta)
class BaseController():
    """Base controller class."""

    @abc.abstractmethod
    def handle(self, data, context):
        """Abstract method for handling request."""
