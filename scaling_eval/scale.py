import logging
from pathlib import Path

from scaling_eval import run


def base_filename(filename):
    return Path(filename).parts[-1]


def format_result(result: float | run.Timeout) -> str:
    if result == run.TIMEOUT:
        return result
    else:
        return f"{result:.2f}s"


def scale_until_timeout(runner: run.Runner, filename, command_num, sig_num, max_scope=20, step=1, timeout_s=60, cpu_time=True):
    """Run portus and kodkod, setting sig_num's scope to each value from 1 to max_scope inclusive,
    stopping if either portus or kodkod timeout.
    """
    for scope in range(1, max_scope+1, step):
        portus_time, kodkod_time = runner.time_portus_kodkod(
            filename,
            command_num=command_num,
            sig_scope=(sig_num, scope),
            timeout_s=timeout_s,
            cpu_time=cpu_time,
        )
        logging.info(
            f"{base_filename(filename)}[cmd {command_num}], sig {sig_num} @ scope {scope}: "
            f"portus={format_result(portus_time)}, kodkod={format_result(kodkod_time)}"
        )
        yield filename, command_num, sig_num, scope, portus_time, kodkod_time
        if portus_time == run.TIMEOUT or kodkod_time == run.TIMEOUT:
            break


def scale_all_sigs(runner: run.Runner, filename, command_num, max_scope=20, step=1, timeout_s=60, cpu_time=True):
    num_sigs = runner.get_num_sigs(filename)
    for sig_num in range(1, num_sigs+1):
        logging.info(f"Scaling all sigs in: {base_filename(filename)}[cmd {command_num}]; {num_sigs} sigs total")
        yield from scale_until_timeout(
            runner, filename, command_num, sig_num, max_scope=max_scope, step=step, timeout_s=timeout_s, cpu_time=cpu_time)
