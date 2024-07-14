import re
import resource
import shlex
import subprocess
import logging
import tempfile
import time
from pathlib import Path
from subprocess import PIPE
from typing import NamedTuple, Optional, Tuple, Type

import psutil

from testrunner.testrunner import kill_child_processes
from testrunner.util import PORTUS_METHODS, Satisfiablity, satisfiability_of_output


TIMEOUT = "timeout"
Timeout = Type[TIMEOUT]


class CommandStats(NamedTuple):
    # time
    wall_clock_time_s: float  # real time
    user_time_s: float        # time spent actually running the program
    sys_time_s: float         # time spent in system calls called by the program

    # memory
    peak_rss_kb: int       # RSS = resident set size: memory used by process held in RAM (not swapped out)
    avg_rss_kb: int
    avg_total_mem_kb: int  # average total memory used by the process
    num_page_faults: int   # indication of whether we're being swapped out

    @property
    def cpu_time_s(self) -> float:
        return self.user_time_s + self.sys_time_s


class CommandResult(NamedTuple):
    timeout: bool
    stdout: str
    stderr: str
    sat_result: Satisfiablity
    retcode: int  # will be the return code from GNU timeout if timed out; -1 if somehow we timed out
    stats: Optional[CommandStats]  # None if somehow stats collection didn't work


def kill_children(process: psutil.Process):
    for child in process.children(recursive=True):
        child.kill()
    process.kill()


def run_command_impl(command: str, timeout_s=None) -> Tuple[str, str, int]:
    # copy subprocess.run to customize the kill behaviour on timeout
    with psutil.Popen(shlex.split(command), stdout=PIPE, stderr=PIPE) as process:
        try:
            stdout, stderr = process.communicate(timeout=timeout_s)
        except subprocess.TimeoutExpired:
            kill_children(process)
            process.wait()
            raise
        except:  # e.g. KeyboardInterrupt
            kill_children(process)
            raise
        retcode = process.poll()
    return stdout, stderr, retcode


def run_command(command: str, timeout_s=None, gnu_time="/usr/bin/time", gnu_timeout="timeout") -> CommandResult:
    time_outpath = Path(tempfile.gettempdir()) / "portus-scaling-time-out"

    # Clear the output file to ensure we aren't reading an old version
    time_outpath.unlink(missing_ok=True)

    # timeout will send SIGTERM, which should allow Portus to exit smoothly; however send SIGKILL after 5s otherwise
    timeout_command = f"{gnu_timeout} --kill-after=5 {timeout_s} {command}"

    # %e: wall-clock time, s
    # %U: CPU time in user mode, s
    # %S: CPU time in system mode, s
    # %M: peak resident set size (memory not swapped out), KB
    # %t: average resident set size, KB
    # %K: average total memory, KB - there is no way to get peak total memory
    # %F: number of major page faults (if high then we're being swapped out)
    time_command = f"{gnu_time} -f '%e %U %S %M %t %K %F' -o '{time_outpath.absolute()}' -q -- {timeout_command}"

    try:
        # coreutils timeout should kill it after timeout_s, or timeout_s+5 if SIGTERM didn't work, so we really
        # should never time out from here
        stdout, stderr, retcode = run_command_impl(time_command, timeout_s=timeout_s + 10)
    except subprocess.TimeoutExpired as ex:
        logging.warn("Timed out from Python rather than coreutils timeout: this shouldn't happen!")
        stdout, stderr, retcode = ex.stdout, ex.stderr, -1

    stdout = stdout.decode()
    stderr = stderr.decode()

    # -1 if we time out from python (shouldn't happen), 124 for timeout via coreutils timeout, 137 if timeout sends SIGKILL
    timeout = retcode in (-1, 124, 137)

    if retcode == 137:
        logging.warn("Coreutils timeout had to send SIGKILL! Check that Portus is well-behaved on SIGTERM.")

    def parse_time_output() -> Optional[CommandStats]:
        # Parse the time output
        with open(time_outpath, mode="r") as time_out:
            time_output = time_out.readlines()

        if len(time_output) != 1:
            logging.warn(
                f"time output file has incorrect number of lines! Expected 1 line, got {len(time_output)}.\n"
                f"Command: {command}\n"
                f"Output file: {time_output}")
            return None
        time_output_line = time_output[0]

        try:
            # Parse the output line
            wc_time, user_time, sys_time, peak_rss, avg_rss, avg_tot_mem, num_page_faults = time_output_line.split()
            return CommandStats(
                wall_clock_time_s=float(wc_time),
                user_time_s=float(user_time),
                sys_time_s=float(sys_time),
                peak_rss_kb=int(peak_rss),
                avg_rss_kb=int(avg_rss),
                avg_total_mem_kb=int(avg_tot_mem),
                num_page_faults=int(num_page_faults)
            )
        except ValueError:
            # something went wrong with parsing
            logging.warn(
                f"time output file has incorrect formatting!\n"
                f"Command: {command}\n"
                f"Output file: {time_output}")
            return None

    stats = parse_time_output()
    sat_result = satisfiability_of_output(stdout)
    if not timeout and sat_result == Satisfiablity.UNSURE:
        logging.warn(f"Could not determine SAT result!\nCommand: {command}\nStdout: {stdout}")
    return CommandResult(timeout, stdout, stderr, sat_result, retcode, stats)


def run_command_for_output(command: str, timeout_s=None, stderr=False) -> str:
    """Run a command which is expected to finish quickly and not spawn any subprocesses."""
    result = subprocess.run(shlex.split(command), capture_output=True, text=True, timeout=timeout_s)
    return result.stderr if stderr else result.stdout


def run_command_for_code(command: str, timeout_s=None) -> int:
    # subprocess.run doesn't kill grandchild processes on timeout (including Z3), so do something fancier
    with psutil.Popen(shlex.split(command), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) as process:
        try:
            return process.wait(timeout_s)
        except psutil.TimeoutExpired:
            kill_children(process)
            process.wait()
            raise
        except:  # e.g. KeyboardInterrupt
            kill_children(process)
            raise


def time_command(command: str, timeout_s=None, cpu_time=True) -> float: # float seconds
    def get_time_s():
        if cpu_time:
            rusage = resource.getrusage(resource.RUSAGE_CHILDREN)
            return rusage.ru_utime + rusage.ru_stime # user + system time
        else:
            return time.monotonic()

    init_time = get_time_s()

    code = run_command_for_code(command, timeout_s)
    if code != 0:
        logging.warning(f"{command} got nonzero exit code: {code}")

    return get_time_s() - init_time


class Runner:

    def __init__(self, base_command: str, gnu_time: str, gnu_timeout: str):
        self.base_command = base_command
        self.gnu_time = gnu_time
        self.gnu_timeout = gnu_timeout

    def format_command(self, filename, method='portus-full', command_num=1, sig_scope=None) -> str:
        sig_scope_arg = ""
        if sig_scope is not None:
            sig_num, scope = sig_scope
            sig_scope_arg = f"-scope {sig_num} {scope}"

        return (
            f"{self.base_command} {filename} {PORTUS_METHODS[method]} "
            f"-command {command_num} {sig_scope_arg} -enable-sum-balancing"
        )

    def get_num_sigs(self, filename) -> int:
        # HACK: Run with a super large sig number and then parse the error message (sad)
        command = self.format_command(filename, sig_scope=(100000, 1))
        output = run_command_for_output(command, stderr=True)
        pattern = r"^Error: invalid sig number '\d+' \(1-indexed\) for -scope: there are only (\d+) non-one, non-lone top-level sigs$"
        match = re.search(pattern, output, flags=re.MULTILINE)
        if match is None:
            raise ValueError(f"Getting num sigs failed! Output: {output}")
        return int(match.group(1))

    def eval(self, filename, method='portus-full', command_num=1, sig_scope=None, timeout_s=30) -> CommandResult:
        command = self.format_command(filename, method=method, command_num=command_num, sig_scope=sig_scope)
        try:
            return run_command(command, timeout_s=timeout_s, gnu_time=self.gnu_time, gnu_timeout=self.gnu_timeout)
        finally:
            kill_child_processes()

    def eval_portus_kodkod(self, filename, command_num=1, sig_scope=None, timeout_s=30) -> Tuple[CommandResult, CommandResult]:
        portus_result = self.eval(filename, method='portus-full', command_num=command_num, sig_scope=sig_scope, timeout_s=timeout_s)
        kodkod_result = self.eval(filename, method='kodkod', command_num=command_num, sig_scope=sig_scope, timeout_s=timeout_s)
        if portus_result.sat_result != kodkod_result.sat_result and not portus_result.timeout and not kodkod_result.timeout:
            logging.warn(f"{filename}[cmd {command_num}] sig_scope={sig_scope} had incorrect satisfiability! "
                         f"portus={portus_result.sat_result}, kodkod={kodkod_result.sat_result}")
        return portus_result, kodkod_result

    def time_run(self, filename, method='portus-full', command_num=1, sig_scope=None, timeout_s=30, cpu_time=True) -> float | Timeout:
        command = self.format_command(filename, method=method, command_num=command_num, sig_scope=sig_scope)
        try:
            return time_command(command, timeout_s=timeout_s, cpu_time=cpu_time)
        except (subprocess.TimeoutExpired, psutil.TimeoutExpired):
            return TIMEOUT
        finally:
            kill_child_processes()

    def time_portus_kodkod(self, filename, command_num=1, sig_scope=None, timeout_s=30, cpu_time=True) -> Tuple[float | Timeout, float | Timeout]:
        return (
            self.time_run(filename, method='portus-full', command_num=command_num, sig_scope=sig_scope, timeout_s=timeout_s, cpu_time=cpu_time),
            self.time_run(filename, method='kodkod', command_num=command_num, sig_scope=sig_scope, timeout_s=timeout_s, cpu_time=cpu_time),
        )
