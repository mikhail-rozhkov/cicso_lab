import logging
import unittest
from activities_python.actions.action_run_script import ActionQuery3
from activities_python.common.action_support.action_error import ActionError
from activities_python.common.constants.controller import ControllerConstants


class TestExecutePythonScript(unittest.TestCase):
    def getExecutePythonScriptQuery(self):
        query = ActionQuery3({
            ControllerConstants.IS_JAILED: False,
        })
        query.logger = logging.getLogger()
        return query

    def test_empty(self):
        query = self.getExecutePythonScriptQuery()
        with self.assertRaises(ActionError):
            query.invoke({}, {})

    def test_timeout(self):
        query = self.getExecutePythonScriptQuery()
        with self.assertRaises(ActionError) as context:
            query.invoke({
                "script": """
import time
time.sleep(2)
                """,
                "action_timeout": 1
            }, {})
        self.assertEqual("Activity timeout", str(context.exception))

    def test_default_timeout(self):
        query = self.getExecutePythonScriptQuery()
        result = query.invoke({
            "script": """
import time
time.sleep(2)
print(1)
            """,
        }, {})
        self.assertEqual({"response_body": "1"}, result)

    def test_bad_script(self):
        query = self.getExecutePythonScriptQuery()
        with self.assertRaises(ActionError):
            query.invoke({
                "script": "bad_script_content",
                "action_timeout": 100
            }, {})

    def test_exit_in_script(self):
        query = self.getExecutePythonScriptQuery()
        with self.assertRaises(ActionError) as context:
            query.invoke({
                "script": """
import sys
sys.exit(1)
""",
                "action_timeout": 100
            }, {})
        self.assertEqual('Error:   File "<string>", line 3, in <module> SystemExit: 1', str(context.exception))

    def test_action_raise(self):
        query = self.getExecutePythonScriptQuery()
        with self.assertRaises(ActionError) as context:
            query.invoke({
                "script": "raise ValueError()",
                "action_timeout": 100
            }, {})
        self.assertEqual('Error:   File "<string>", line 1, in <module>\nValueError', str(context.exception))

    def test_run(self):
        query = self.getExecutePythonScriptQuery()
        result = query.invoke({
            "script": "print(1)",
            "action_timeout": 100
        }, {})
        self.assertEqual({"response_body": "1"}, result)

    def test_run_with_args(self):
        query = self.getExecutePythonScriptQuery()
        result = query.invoke({
            "script": """
import sys
c = sys.argv[1] + sys.argv[2]
print(c)
            """,
            "script_arguments": ["a", "b"],
            "script_queries": [
                {"script_query_name": "c", "script_query": "c", "script_query_type": "str"},
            ],
            "action_timeout": 100
        }, {})
        self.assertEqual({"response_body": "ab", "script_queries": {'c': 'ab'}}, result)

    def test_run_with_argserror(self):
        query = self.getExecutePythonScriptQuery()
        with self.assertRaises(ActionError):
            query.invoke({
                "script": "c = 3",
                "script_queries": [
                    {"script_query_name": "c", "script_query": "invalid", "script_query_type": "str"},
                ],
                "action_timeout": 100
            }, {})

    def test_run_with_args2(self):
        query = self.getExecutePythonScriptQuery()
        result = query.invoke({
                'script_arguments': ['"{\\"name\\":\\"Patrick M\xe9zard\\",}"'],
                'script_queries': [
                    {"script_query_name": "c", "script_query":  "c", "script_query_type": "str"},
                ],
                'display_name': 'Execute Python Script',
                "script": """
import sys
c = sys.argv[1]
print(c)
"""
            }, {})
        self.assertEqual({
            "response_body": '"{\\"name\\":\\"Patrick M\xe9zard\\",}"',
            "script_queries": {'c': '"{\\"name\\":\\"Patrick M\xe9zard\\",}"'}
        }, result)


if __name__ == '__main__':
    unittest.main()
