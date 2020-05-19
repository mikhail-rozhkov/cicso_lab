"""Module with class for function controllers."""

import json
import traceback

from activities_python.pythonutils.utils import dump_excluding_secrets, create_proxies

from ...events.event_resolver import resolve_event
from .base import BaseController
from ..models.response import ControllerResponse
from ..constants.controller import ControllerConstants
from ..factories.logger import produce_logger
from ..action_support.action_error import ActionError


class FunctionController(BaseController):
    """Class containing controller for functions."""

    def __init__(self, options):
        """Contructor."""
        self.options = options
        self.logger = produce_logger(options)
        super(FunctionController, self).__init__()

    def handle(self, data, context):
        # pylint: disable=broad-except
        try:
            # if isinstance(data, six.string_types):
            input_object = json.loads(data)
            # else:
            #    input_object = data
            input_type = input_object['type']
            self.logger.info("Got event type %s", input_type)
            lh_options = {}
            proxy_options = {}
            ignore_proxy = False
            if 'lh_options' in input_object:
                lh_options = input_object['lh_options']
                self.logger.info("Got lh_options %s", lh_options)
                if lh_options and 'proxy_options' in lh_options:
                    proxy_options = lh_options['proxy_options']
            event = input_object['config']
            self.logger.info("Got event config %s", dump_excluding_secrets(event, lh_options))
            handler = resolve_event(input_type, self.options)
            if not handler:
                raise ValueError("Unresolved event type: " + input_type)
            handler.add_lh_options(lh_options)
            if 'ignore_proxy' in event:
                ignore_proxy = event['ignore_proxy']
            if proxy_options and not ignore_proxy:
                proxies = create_proxies(proxy_options)
                if proxies:
                    handler.add_proxies(proxies)
            result = handler.invoke(event, context)
            return action_success(result)
        except ActionError as e:
            self.logger.error("Raised action error code=%s, message=%s", e.code, e)
            return action_error(str(e), e.code)
        except Exception:
            formatted_lines = traceback.format_exc().splitlines()
            e = "Error processing request: " + str(formatted_lines[-1])
            self.logger.exception("Exception during processing request")
            return action_error(str(e), None)


def action_success(result):
    """Function to get response in case of success."""
    response = {
        ControllerConstants.ACTIVITY_STATUS: ControllerConstants.SUCCESS_STATUS,
    }
    if result:
        response[ControllerConstants.RESPONSE] = result
    return create_response(response)


def action_error(error_text, code):
    """Function to get response in case of error."""
    response = {
        ControllerConstants.ACTIVITY_STATUS: ControllerConstants.FAILED_STATUS,
        ControllerConstants.ERROR_DESC: {
            ControllerConstants.ERROR_MESSAGE: error_text,
        }
    }
    if code:
        response[ControllerConstants.ERROR_DESC][ControllerConstants.ERROR_CODE] = str(code)
    return create_response(response)


def create_response(result):
    """Function to create response."""
    return ControllerResponse(
        response=result,
        status=200,
        mime='application/json',
        jsonize=True,
    )
