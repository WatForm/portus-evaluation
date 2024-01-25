import csv
import io
import os
import subprocess
import itertools
import functools
import logging
import sys
import time
import typing
import shlex

import psutil
from tqdm.auto import tqdm

from typing import *
from time import monotonic as monotonic_timer
from util import partition

OptionInfo = Union[str, int, float, bool]
OptionValue = Union[OptionInfo, Dict[str, OptionInfo]]
# Option name to info
OptionDict = Dict[str, OptionValue]
# Time, stdout, stderr, OptionsDictionary -> output to write
OutputHandler = Callable[[int, str, str, OptionDict], str]

CommandFunc = Callable[[OptionDict], List[str]]
# You should probably use a command function when your options contain a list
Command = Union[CommandFunc, str, List[str]]


class Option:
    """An option with one or more possible values to be chosen from."""

    def __init__(self, opt_name: str, option_values: List[OptionValue]):
        self.opt_name = opt_name
        if type(option_values) != list:
            option_values = list(option_values)
        if len(option_values) == 0:
            raise ValueError("Cannot have no option values! In option " + self.opt_name)
        self.option_values: List[OptionInfo] = option_values

    def get_option_values(self) -> List[OptionValue]:
        return self.option_values.copy()

    def __iter__(self):
        return iter(self.option_values)

    def __len__(self):
        return len(self.option_values)

    @property
    def is_constant(self):
        return len(self.option_values) == 1

    def __str__(self):
        return f'<<{[x for x in self.get_option_values()]}>>'


class FromFileOption(Option):
    """Creates options where the value is each line of the given file"""

    def __init__(self, opt_name: str, filename):
        values = []
        with open(filename, 'r') as f:
            values = f.readlines()
        values = list(map(lambda x: x.strip(), values))
        super().__init__(opt_name, values)


class FilesOption(Option):
    """Creates an option where the value is every file in the given folder, optionally filtered."""

    def __init__(self, opt_name: str, folder_path: os.PathLike, recursive: bool = False,
                 folder_filter: Optional[Callable[[Union[bytes, str]], bool]] = None,
                 file_filter: Optional[Callable[[Union[bytes, str]], bool]] =None,
                 abs_path: bool = True,
                 ):
        """
        opt_name: the name of the option
        folder_path: the root folder to explore for files
        recursive: look into subfolders
        pred: A predicate to filter files
        abs_path: True will return the absolute paths of the file, False will return paths relaive to folder_path"""
        option_values = self._create_option_values(folder_path, recursive, folder_filter, file_filter, abs_path)
        super().__init__(opt_name, option_values)

    @staticmethod
    def _create_option_values(folder_path: os.PathLike, recursive: bool,
                              folder_filter: Optional[Callable[[Union[bytes, str]], bool]],
                              file_filter: Optional[Callable[[Union[bytes, str]], bool]],
                              abs_path: bool,
                              ) -> List[OptionInfo]:
        files_kept = []
        for root, dirs, files in os.walk(folder_path):
            # Filter or keep files
            for file_name in files:
                file_name_from_root = os.path.join(root, file_name)
                if file_filter is None or file_filter(file_name_from_root):
                    if abs_path:
                        # This is the absolute path from the file system root
                        files_kept.append(os.path.abspath(file_name_from_root))
                    else:
                        files_kept.append(file_name_from_root)
                        
            # If we don't want to recurse into directories, skip them all
            if not recursive:
                dirs.clear()
            elif folder_filter is not None:
                #  Filter or keep folders for recursive calls
                dirs[:] = filter(lambda dir: folder_filter(os.path.join(root, dir)), dirs)
            
        return files_kept

class CSVOption(Option):
    """Reads in lines from a csv file.
    Provides `kept_headers` as options, synchronized so each line of the csv file is one command."""
    def __init__(self, opt_name: str, file_name: str,
                 all_headers: Optional[List[str]] = None, kept_headers: Optional[List[str]] = None):
        with open(file_name, 'r') as csv_file:
            if all_headers is None:
                reader = csv.DictReader(csv_file)
            else:
                reader = csv.DictReader(csv_file, fieldnames=all_headers)

            option_values = []
            for row in reader:
                if kept_headers is not None:
                    # row = dict(filter(lambda k, v: k in kept_headers, row))
                    row = {key: row[key] for key in kept_headers}
                option_values.append(row)
        super().__init__(opt_name, option_values)


# todo multiple options from csv?

def check_process_running(process_name):
    """
    Check if there is any running process that contains the given name processName.
    from: https://thispointer.com/python-check-if-a-process-is-running-by-name-and-find-its-process-id-pid/
    """
    process_name = process_name.lower()
    # Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if process_name in proc.name().lower():
                logging.debug(f"process '{process_name}' exists: " + str(proc.pid))
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def kill_process(p, name):
    try:
        # occasionally the child process dies by itself and this then
        # causes an exception b/c child.pid does not exist
        # so the try/except is needed
        p.kill()
        # the following seems to have processlookup errors even though process
        # exists
        # os.killpg(p.pid, signal.SIGKILL)
        logging.info("killed: " + name + "\n")
    except ProcessLookupError:
        logging.warning("os.killpg could not find: " + str(p.pid) + "\n")
        if check_process_running(name):
            logging.error(f'process {p.pid} was unable to be killed, but is still running!')
            exit(1)
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        logging.exception(message + '\n' + "Did not kill: " + str(p.pid) + " " + name)


def kill_child_processes():
    # have to kill sh, java, z3 child processes
    current_process = psutil.Process()
    children = current_process.children(recursive=True)
    children.sort(key=lambda x: x.pid, reverse=True)  # NOTE: Why is this done? Can it be skipped?
    for c in children:
        logging.debug("Need to kill: " + str(c.pid) + " " + c.name() + "\n")
    for c in children:
        logging.debug("Trying to kill: " + str(c.pid) + " " + c.name() + "\n")
        kill_process(c, c.name())

    if children:
        time.sleep(30)  # seconds
    # have to wait to make sure processes killed
    # When the time was set to 15 seconds, there's still a small possibility of Z3 process
    # hasn't been cleaned up yet. We increased it to 30 seconds to avoid that.


class TestRunner:
    def __init__(self, command: Command, *options: Option, timeout: int,
                 output_file: typing.TextIO = None):
        # Command should be formed for `Popen` but can have {kwarg} style formatting in place
        self.command = command
        static_options, self.dynamic_options = partition(lambda x: x.is_constant, options)
        self.static_option_values: OptionDict = self._flatten_options({opt.opt_name: opt.get_option_values()[0] for opt in static_options})
        self.timeout = timeout
        self.output_file = output_file if output_file else sys.stdout

    @property
    def dynamic_option_names(self):
        return list(map(lambda x: x.opt_name, self.dynamic_options))

    @staticmethod
    def format_command(command: Command, option_dict: OptionDict) -> List[str]:
        """Fills out the command with the given options."""
        if type(command) == str:
            return shlex.split(command.format(**option_dict))
        elif type(command) == list:
            return list(map(lambda x: x.format(**option_dict), command))
        else:
            return command(option_dict)

    def get_num_commands_to_run(self):
        return functools.reduce(lambda x, y: x * len(y), self.dynamic_options, 1)

    def run(self, iterations: int = 1, skip: int = 0):
        """
        Runs the given command over all the options `iterations` times, skipping the first `skip` values.
        Skip counts command executions, not commands themselves. ie if iterations is 2, skip=2 will skip the first command entirely
        Calls `handle_result` and `handle_timeout` which can be overwritten to change behavior
        """
        command_count = 0  # Counts each distinct command
        iteration_count = 0  # Counts each use of a command (each iteration)
        logging.info("Beginning test run...")
        logging.debug(f"static options: {self.static_option_values}")
        dynamic_option_names = list(map(lambda x: x.opt_name, self.dynamic_options))

        num_commands_to_run = self.get_num_commands_to_run()
        num_command_calls = num_commands_to_run * iterations
        logging.info("Expecting %d commands, each run %d times. Total %d executions.",
                     num_commands_to_run, iterations, num_command_calls)
        try:
            for dynamic_option_values in tqdm(itertools.product(*self.dynamic_options), desc="tests", total=num_commands_to_run, disable=self.output_file == sys.stdout):
                # Create a dictionary with option names -> option value for dynamic options then add static
                dynamic_option_values: Dict[str, OptionInfo] = dict(zip(dynamic_option_names, dynamic_option_values))
                dynamic_option_values = self._flatten_options(dynamic_option_values)
                option_values: OptionDict = dynamic_option_values.copy()
                option_values.update(self.static_option_values)

                # Format the command
                formatted_command = self.format_command(self.command, option_values)

                command_count += 1
                logging.info(f"Command #{command_count}: {shlex.join(formatted_command)}")
                logging.debug('Dynamic values: ' + str(dynamic_option_values))
                for iteration_number in range(iterations):
                    iteration_count += 1
                    # Skip commands
                    if iteration_count <= skip:
                        continue
                    if skip and iteration_count == skip:
                        logging.info('Done skipping!')

                    try:
                        start = monotonic_timer()
                        result = subprocess.run(formatted_command, capture_output=True, text=True, timeout=self.timeout)
                        time_elapsed: float = monotonic_timer() - start

                        logging.debug(f'Returned with code {result.returncode} in {time_elapsed:.4f} seconds')

                        self.handle_result(option_values, result, time_elapsed)

                    except subprocess.TimeoutExpired as timeout_error:
                        logging.debug('Timed out')
                        self.handle_timeout(option_values, timeout_error)
                    kill_child_processes()
        except:
            logging.critical("UNCAUGHT ERROR: Currently working on iteration count  #%d.", iteration_count,
                             exc_info=True)
            raise
        logging.info("Done!")

    @staticmethod
    def _flatten_options(option_values: OptionDict) -> OptionDict:
        flat = {}
        for key, value in option_values.items():
            if type(value) == dict:
                flat.update(value)
            else:
                flat[key] = value
        return flat

    def handle_timeout(self, options_values: OptionDict, timeout: subprocess.TimeoutExpired) -> None:
        pass

    def handle_result(self, option_values: OptionDict, result: subprocess.CompletedProcess, time_elapsed: float) -> None:
        pass

    def _filter_only_dynamic_options(self, options: OptionDict) -> OptionDict:
        filtered_dict = {}
        for option in self.dynamic_options:
            option_name = option.opt_name
            filtered_dict[option_name] = options[option_name]
        return filtered_dict


class CSVTestRunner(TestRunner):
    def __init__(self, command: Command, *options: Option, timeout: int,
                 output_file: typing.TextIO = None,
                 result_fields: Optional[List[str]] = None,
                 fields_from_timeout: Callable[[OptionDict, subprocess.TimeoutExpired], OptionDict],
                 fields_from_result: Callable[[OptionDict, subprocess.CompletedProcess, float], OptionDict],
                 ignore_fields: Optional[List[str]] = None,
                 write_header: bool = True,
                 ):
        """
        Writes output to a csvfile.
        `result_fields` is a list of names of fields in the csv file that are determined by the result of the command
        `fields_from_timeout` and `fields_from_result` provide a dictionary of fieldname -> value for the result_fields
        `ignore_fields` is an optional list of options that will not be documented
        If `write_header` is True the header to the csvfile will be written when not skipping the first line.
            If skipping the first line, `run` can be called with `force_write_header` to be true.
        """
        super().__init__(command, *options, timeout=timeout, output_file=output_file)
        self._result_fields: List[str] = result_fields if result_fields is not None else []
        # Default to including all fields
        if ignore_fields is None:
            ignore_fields = []
        # Specifically delve into csvoptions
        possible_option_names = self._get_option_fieldnames(self.dynamic_options)
        self._fields = list(filter(lambda x: x not in ignore_fields, possible_option_names)) + self._result_fields
        
        self.fields_from_timeout = fields_from_timeout
        self.fields_from_result = fields_from_result
        self.write_header = write_header
        
        self.csv_writer = csv.DictWriter(
            self.output_file,
            fieldnames=self._fields,
            extrasaction='ignore'  # We can put in the whole dict and just ignore the ones we don't want
        )
        
    @staticmethod
    def _get_option_fieldnames(options: List[Option]) -> List[str]:
        """Returns the names of all the fields from options.
        This includes splitting up CSV Options to get their dynamic options.
        Currently ignores dynamic check for csv options. If you have a column that is all the same that's your fault for now."""
        fieldnames = []
        for option in options:
            contains_multiple_options = type(option.option_values[0]) == dict
            if contains_multiple_options:
                headers = option.option_values[0].keys()
                fieldnames.extend(headers)
            else:
                fieldnames.append(option.opt_name)
        return fieldnames
                
    
    def run(self, iterations: int = 1, skip: int = 0, force_write_header: bool = False, force_skip_header=False):
        if (self.write_header and skip == 0 and not force_skip_header) or force_write_header:
            self.csv_writer.writeheader()
        super().run(iterations, skip)
    
    def handle_timeout(self, options_values: OptionDict, timeout: subprocess.TimeoutExpired) -> None:
        result_fields = self.fields_from_timeout(options_values, timeout)
        data = options_values.copy()
        data.update(result_fields)
        self.csv_writer.writerow(data)
        self.output_file.flush()
        
    def handle_result(self, option_values: OptionDict, result: subprocess.CompletedProcess, time_elapsed: float) -> None:
        result_fields = self.fields_from_result(option_values, result, time_elapsed)
        data = option_values.copy()
        data.update(result_fields)
        self.csv_writer.writerow(data)
        self.output_file.flush()
        

if __name__ == '__main__':
    op = Option('op', ['echo'])
    numbers = Option('number', list(range(5)))
    text = FromFileOption('text', 'inputstrings.txt')
    command = ['{op}', '{number}', '{text}', ':)']

    csv_opt = CSVOption('csv_opt', 'test.csv')
    # Not at all needed, but using to test the command
    # command = '{op} {file} {time_elapsed} {return_code} {sat}'
    logging.getLogger().setLevel(logging.DEBUG)
    #command_func = CommandFunc(lambda opts: TestRunner.format_command(command, opts))

    #testRunner = TestRunner(command_func, op, numbers, text, timeout=2000)
    testRunner = TestRunner(command, op, csv_opt, timeout=2000)
    with open('output.txt', 'w') as f:
        testRunner.run()