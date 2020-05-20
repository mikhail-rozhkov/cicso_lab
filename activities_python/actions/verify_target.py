"""Module for the sample adapter classes."""

from ..common.action_support.base import BaseAction
from ..pythonutils.models.MySQL_Target import MySQLTarget
from ..pythonutils.models.MySQL_User import MySQLUser
from ..pythonutils.mysql_adapter import MySQLAdapter
from ..pythonutils.mysql_error import MySQLError
from ..common.action_support.base import raise_action_error


class VerifyTargetQuery(BaseAction):
    """Sample Class for verifying target."""

    def invoke(self, data, context):
        """Invoke this action class. """
        self.logger.info('Invoked VerifyTargetQuery')

        # Put your code here to get/parse some adapter properties.
        # Sample:
        target = MySQLTarget(data)
        user = MySQLUser(data)
        adapter = MySQLAdapter(target, self.logger)

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
