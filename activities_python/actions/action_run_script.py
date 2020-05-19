"""Module with action execute python script."""

import os
import sys
import traceback
from multiprocessing import Process, Queue
import six

from ..common.action_support.base import BaseAction, raise_action_error, check_input_params
from ..common.constants.controller import ControllerConstants


class ActionQuery3(BaseAction):
    """Main Class for executing a python script action."""

    def __init__(self, jail_options):
        """Constructor."""
        self.jail_options = jail_options
        super(ActionQuery3, self).__init__()

    def invoke(self, data, context):
        """Invoke adapter action."""
        # pylint: disable=broad-except
        try:
            self.logger.info('Invoked ActionQuery3')

            # check input parameters
            check_input_params(data, "script")

            script = data["script"]
            timeout = abs(data.get("action_timeout", 180))  # same default as in console

            script_queries = {}
            script_arguments = []
            if "script_queries" in data:
                for sqs in data['script_queries']:
                    script_queries[sqs['script_query_name']] = sqs['script_query_type'] + " " + sqs['script_query']
            if "script_arguments" in data:
                for query in data["script_arguments"]:
                    if isinstance(query, six.string_types):
                        script_arguments.append(query)
                    else:
                        script_arguments.append(str(query))

            opts = ExecuterOptions()
            opts.timeout = timeout
            opts.script = script
            opts.script_arguments = script_arguments
            opts.script_queries = script_queries
            opts.jail_options = self.jail_options
            opts.logger = self.logger
            executer = Executer(opts)

            result = executer.run_parent()
            if "Error:" in result:
                raise_action_error(400, result)
            return result
        except Exception as e:
            raise_action_error(400, e)


class ExecuterOptions:
    """Class for Executer options."""

    timeout = 0
    script = ""
    script_arguments = []
    script_queries = {}
    jail_options = {}
    logger = None


class Executer(Process):
    """Class for running a Python scripts."""

    __STARTED = "started"
    __OUTPUT = "output"
    __EXCEPTION = "exception"

    def __init__(self, options):
        """Constructor."""
        self.options = options
        self.queue = Queue()
        super(Executer, self).__init__()

    # override Process.run
    def run(self):
        """Function to run specified command in subprocess."""
        # pylint: disable=broad-except
        # jailing

        if self.options.jail_options[ControllerConstants.IS_JAILED]:
            self.options.logger.info("Executing script in chroot jail")
            os.chroot(self.options.jail_options[ControllerConstants.JAIL_DIR])
            os.chdir('/')
            os.setgid(self.options.jail_options[ControllerConstants.USER_GID])  # Important! Set GID first
            os.setuid(self.options.jail_options[ControllerConstants.USER_UID])
        else:
            self.options.logger.info("Executing script unjailed")
        try:
            output = run_script(self.options.script, self.options.script_arguments, self.options.script_queries)
            self.queue.put(output)

        except Exception as e:
            raise Exception(e)

    def run_parent(self):
        """Function to run specified command in parent process."""
        # execute self.run in forked process
        self.start()
        self.join(self.options.timeout)
        output = self.queue.get()
        if self.is_alive():
            self.terminate()
            raise Exception('Activity timeout')
        return output


class FileCacher:
    """Class for caching the stdout text."""

    def __init__(self):
        """Constructor."""
        self.reset()

    def reset(self):
        """Function to reset cacher."""
        self.out = []

    def write(self, line):
        """Function to write data."""
        self.out.append(line)

    def flush(self):
        """Function to flush buffer."""
        if '\n' in self.out:
            self.out.remove('\n')
        output = '\n'.join(self.out)
        self.reset()
        return output


class Shell:
    """Class for running a Python script as interactive interpreter."""

    def __init__(self, arguments):
        """Constructor."""
        self.stdout = sys.stdout
        self.cache = FileCacher()
        set_arguments(arguments)
        self.locals = {"__name__": "__console__", "__doc__": None}

    def run_code(self, script):
        """Function to run code."""
        # pylint: disable=broad-except, exec-used, try-except-raise
        try:
            sys.stdout = self.cache
            try:
                exec(script, self.locals)
            except SystemExit:
                raise
            except SyntaxError:
                formatted_lines = traceback.format_exc().splitlines()
                e = str(formatted_lines[-3]) + "\n" + str(formatted_lines[-2]) + "\n" + str(formatted_lines[-1])
                return "Error: " + e
            except Exception:
                formatted_lines = traceback.format_exc().splitlines()
                e = str(formatted_lines[-2]) + "\n" + str(formatted_lines[-1])
                return "Error: " + e
            sys.stdout = self.stdout
            output = self.cache.flush()
            return output
        except BaseException:
            formatted_lines = traceback.format_exc().splitlines()
            e = str(formatted_lines[-2]) + " " + str(formatted_lines[-1])
            return "Error: " + e


def run_script(script, script_arguments, script_queries):
    """Run the Python script with arguments and interactive queries."""
    try:
        shell = Shell(script_arguments)
        result = {}
        out = shell.run_code(script)
        if "Error:" in out:
            return out
        result["response_body"] = out
        if script_queries:
            result["script_queries"] = {}
            for key in list(script_queries.keys()):
                query_val = script_queries[key]
                parts = query_val.split()
                query = "print(" + parts[1] + ")"
                out = shell.run_code(query)
                if parts[0] == "string":
                    if isinstance(out, six.string_types):
                        output = out
                    else:
                        output = str(out)
                elif parts[0] == "integer":
                    output = int(out)
                elif parts[0] == "boolean":
                    output = out.lower() in ("yes", "true", "t", "1")
                elif parts[0] == "number":
                    output = float(out)
                else:
                    output = out
                if "Error:" in out:
                    return out
                result["script_queries"][key] = output

        return result
    except Exception as e:
        raise Exception(e)


def set_arguments(arguments):
    """Function to set arguments."""
    if arguments:
        sys.argv[1:] = ""
        for arg in arguments:
            sys.argv.append(arg)
