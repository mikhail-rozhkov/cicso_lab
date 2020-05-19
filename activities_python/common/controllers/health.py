"""Module for health check controller classes."""

from .base import BaseController
from ..models.response import ControllerResponse
from ..factories.logger import produce_logger


class HealthController(BaseController):
    """Class for reporting health check."""

    def __init__(self, options):
        self.logger = produce_logger(options)
        BaseController.__init__(self)

    def handle(self, data, context):
        """Handle the incoming request to this controller. """
        return ControllerResponse(response='I am good!')
