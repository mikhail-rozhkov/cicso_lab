"""Module for the sample adapter classes. """

from ..common.action_support.base import BaseAction
from ..pythonutils.mysql_error import MySQLError
from ..pythonutils.models.MySQL_Target import MySQLTarget
from ..pythonutils.models.MySQL_User import MySQLUser
from ..pythonutils.mysql_adapter import MySQLAdapter
from ..pythonutils.utils import get_optional_value
from ..common.action_support.base import raise_action_error, check_input_params


class MySQLSelect(BaseAction):
    """Sample Class to demonstrator input and output parameters."""

    def __init__(self):
        """Constructor."""
        super(MySQLSelect, self).__init__()
        self.select_query = "select_query"
        self.return_query = "return_query"
        self.row_count = "row_count"
        # self.hello_world = "input_one"
        # self.input_name = "input_two"

        # self.output1 = "output_one"
        # self.output2 = "output_two"

    def invoke(self, data, context):
        """Invoke this action class. """
        self.logger.info('Invoked MySQLSelect with Data: {}'.format(data))

        check_input_params(data, self.select_query)
        sql = data[self.select_query]
        target = MySQLTarget(data)
        user = MySQLUser(data)
        adapter = MySQLAdapter(target, self.logger)
        result = {}
        try:
            connection = adapter.connect_to_mysql(user)
            with connection.cursor() as cursor:
                cursor.execute(sql)
                result[self.return_query] = cursor.fetchall()
                result[self.row_count] = len(result[self.return_query])
                self.logger.info("Returning {} to Result Engine.".format(result))
            return result
        except MySQLError as e:
            self.logger.error("Filed to verify target. Caused=%s", e.__cause__)
            self.raise_action_error('102', e.__cause__)
        finally:
            connection.close()

        # check_input_params(data, self.input_name)
        # output1 = data[self.input_name]
        #
        # check_input_params(data, self.hello_world)
        # output2 = data[self.hello_world]
        #
        # result = {}
        #
        # try:
        #     result[self.output1] = output1
        #     result[self.output2] = output2 + output1
        #
        #     return result
        # except MySQLError as e:
        #     self.logger.error("Action failed. Status=%s, Response=%s", e.status_code, e.response)
        #     raise_action_error(400, e)
