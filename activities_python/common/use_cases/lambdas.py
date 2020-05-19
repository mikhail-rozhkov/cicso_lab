"""Module containing use case for executing inside lambda function."""
import logging

from ..factories.options import produce_options
from ..controllers.function import FunctionController


class LambdasUseCase:
    """Class containing use case for executing inside lambda function."""

    def execute(self, event, context):
        """Main function for execution of use case."""
        # pylint: disable=no-self-use
        logger = logging.getLogger(__name__)
        try:
            opts = produce_options(True)
            if opts.log_level:
                logging.basicConfig(level=logging.getLevelName(opts.log_level))
            controller = FunctionController(opts)
            result = controller.handle(event, context)
            return result.response
        except ValueError as e:
            logger.error("Value error: %s", e)
            exit()
