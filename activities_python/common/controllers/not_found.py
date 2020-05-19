"""Module for the not-found controller."""

from .base import BaseController
from ..models.response import ControllerResponse
from ..factories.logger import produce_logger


class NotFoundController(BaseController):
    """Class for sending not found."""

    def __init__(self, options):
        self.logger = produce_logger(options)
        BaseController.__init__(NotFoundController, self)

    def handle(self, data, context):
        """Handle incoming requests to this controller. """
        return ControllerResponse(status=404)
