"""Module for the sample adapter classes. """

from ..common.action_support.base import BaseAction
from ..pythonutils.models.template_launch_params import TemplateLaunchParams
from ..pythonutils.models.MySQL_Target import MySQLTarget
from ..pythonutils.models.MySQL_User import MySQLUser
from ..pythonutils.mysql_adapter import MySQLAdapter
from ..pythonutils.mysql_error import MySQLError
from ..common.action_support.base import raise_action_error, check_input_params


class ActionQuery2(BaseAction):
    """Sample Class for creating some template using post request with template_name parameter."""

    TEMPLATE_NAME = "template_name"

    def invoke(self, data, context):
        """Invoke this action class. """
        self.logger.info('Invoked ActionQuery2')
        check_input_params(data, self.TEMPLATE_NAME)
        template_name = data[self.TEMPLATE_NAME]
        target = MySQLTarget(data)
        user = MySQLUser(data)
        params = TemplateLaunchParams(data)
        template_adapter = MySQLAdapter(target, self.logger)

        try:
            # Verify target here: (check password/token/etc , try to connect).
            # Sample:
            adapter.connect_to_mysql(user)

            return {
                'verified': True,
            }
        except MySQLError as e:
            self.logger.error("Failed to verify target. Cause=%s", e.__cause__)
            self.raise_action_error('101', e.__cause__)
        # try:
        #     token = template_adapter.get_auth_token(user, self.proxies)
        #     info = template_adapter.create_template(token, template_name, params, self.proxies)
        #     return info
        # except TemplateError as e:
        #     self.logger.error("Action failed. Status=%s, Response=%s", e.status_code, e.response)
        #     raise_action_error(400, e)
