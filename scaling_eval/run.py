import re
import resource
import shlex
import subprocess
import time
from typing import Tuple, Type

from testrunner.testrunner import kill_child_processes
from testrunner.util import PORTUS_METHODS


TIMEOUT = "timeout"
Timeout = Type[TIMEOUT]


def run_command_for_output(command: str, timeout_s=None, stderr=False) -> str:
    result = subprocess.run(shlex.split(command), capture_output=True, text=True, timeout=timeout_s)
    return result.stderr if stderr else result.stdout


def time_command(command: str, timeout_s=None, cpu_time=True) -> float: # float seconds
    def get_time_s():
        if cpu_time:
            rusage = resource.getrusage(resource.RUSAGE_CHILDREN)
            return rusage.ru_utime + rusage.ru_stime # user + system time
        else:
            return time.monotonic()

    init_time = get_time_s()
    subprocess.run(shlex.split(command), timeout=timeout_s, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return get_time_s() - init_time


class Runner:

    def __init__(self, base_command: str):
        self.base_command = base_command

    def format_command(self, filename, method='portus-full', command_num=1, sig_scope=None) -> str:
        sig_scope_arg = ""
        if sig_scope is not None:
            sig_num, scope = sig_scope
            sig_scope_arg = f"-scope {sig_num} {scope}"

        return (
            f"{self.base_command} {filename} {PORTUS_METHODS[method]} "
            f"-command {command_num} {sig_scope_arg}"
        )

    def get_num_sigs(self, filename) -> int:
        # HACK: Run with a super large sig number and then parse the error message (sad)
        command = self.format_command(filename, sig_scope=(100000, 1))
        output = run_command_for_output(command, stderr=True)
        pattern = r"^Error: invalid sig number '\d+' \(1-indexed\) for -scope: there are only (\d+) non-one, non-lone top-level sigs$"
        match = re.search(pattern, output, flags=re.MULTILINE)
        if match is None:
            raise ValueError("Getting num sigs failed!")
        return int(match.group(1))

    def time_run(self, filename, method='portus-full', command_num=1, sig_scope=None, timeout_s=30, cpu_time=True) -> float | Timeout:
        command = self.format_command(filename, method=method, command_num=command_num, sig_scope=sig_scope)
        try:
            return time_command(command, timeout_s=timeout_s, cpu_time=cpu_time)
        except subprocess.TimeoutExpired:
            return TIMEOUT
        finally:
            kill_child_processes()

    def time_portus_kodkod(self, filename, command_num=1, sig_scope=None, timeout_s=30, cpu_time=True) -> Tuple[float | Timeout, float | Timeout]:
        return (
            self.time_run(filename, method='portus-full', command_num=command_num, sig_scope=sig_scope, timeout_s=timeout_s, cpu_time=cpu_time),
            self.time_run(filename, method='kodkod', command_num=command_num, sig_scope=sig_scope, timeout_s=timeout_s, cpu_time=cpu_time),
        )
