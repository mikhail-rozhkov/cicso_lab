"""Module for the sample adapter classes. """

from ..common.action_support.base import BaseAction
from ..pythonutils.template_error import TemplateError
from ..common.action_support.base import raise_action_error, check_input_params


class ActionQuery1(BaseAction):
    """Sample Class to demonstrator input and output parameters."""

    def __init__(self):
        """Constructor."""
        super(ActionQuery1, self).__init__()
        self.hello_world = "input_one"
        self.input_name = "input_two"

        self.output1 = "output_one"
        self.output2 = "output_two"

    def invoke(self, data, context):
        """Invoke this action class. """
        self.logger.info('Invoked ActionQuery1')

        check_input_params(data, self.input_name)
        output1 = data[self.input_name]

        check_input_params(data, self.hello_world)
        output2 = data[self.hello_world]

        result = {}

        try:
            result[self.output1] = output1
            result[self.output2] = output2 + output1

            return result
        except TemplateError as e:
            self.logger.error("Action failed. Status=%s, Response=%s", e.status_code, e.response)
            raise_action_error(400, e)
