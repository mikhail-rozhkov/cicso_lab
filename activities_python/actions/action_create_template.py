"""Module for the sample adapter classes. """

from ..common.action_support.base import BaseAction
from ..pythonutils.models.template_launch_params import TemplateLaunchParams
from ..pythonutils.models.MySQL_Target import TemplateTarget
from ..pythonutils.models.MySQL_User import TemplateUser
from ..pythonutils.mysql_adapter import TemplateAdapter
from ..pythonutils.mysql_error import TemplateError
from ..common.action_support.base import raise_action_error, check_input_params


class ActionQuery2(BaseAction):
    """Sample Class for creating some template using post request with template_name parameter."""

    TEMPLATE_NAME = "template_name"

    def invoke(self, data, context):
        """Invoke this action class. """
        self.logger.info('Invoked ActionQuery2')
        check_input_params(data, self.TEMPLATE_NAME)
        template_name = data[self.TEMPLATE_NAME]
        target = TemplateTarget(data)
        user = TemplateUser(data)
        params = TemplateLaunchParams(data)
        template_adapter = TemplateAdapter(target, self.logger)
        try:
            token = template_adapter.get_auth_token(user, self.proxies)
            info = template_adapter.create_template(token, template_name, params, self.proxies)
            return info
        except TemplateError as e:
            self.logger.error("Action failed. Status=%s, Response=%s", e.status_code, e.response)
            raise_action_error(400, e)
