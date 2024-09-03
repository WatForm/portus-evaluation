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


def scale_until_timeout(runner: run.Runner, method, filename, command_num, sig_num, scopes=range(1, 21), timeout_s=60, cpu_time=True):
    """Run the specified method, setting sig_num's scope to each value from 1 to max_scope inclusive,
    stopping on timeout.
    """
    for scope in scopes:
        time = runner.time_run(
            filename,
            method=method,
            command_num=command_num,
            sig_scope=(sig_num, scope),
            timeout_s=timeout_s,
            cpu_time=cpu_time,
        )
        logging.info(f"{base_filename(filename)}[cmd {command_num}], sig {sig_num} @ scope {scope}: "
                     f"{method} {format_result(time)}")
        yield method, filename, command_num, sig_num, scope, time
        if time == run.TIMEOUT:
            break


def scale_all_sigs(runner: run.Runner, methods, filename, command_num, scopes=range(1, 21), timeout_s=60, cpu_time=True):
    num_sigs = runner.get_num_sigs(filename)
    logging.info(f"Scaling all sigs in: {base_filename(filename)}[cmd {command_num}]; {num_sigs} sigs total")
    for sig_num in range(1, num_sigs+1):
        for method in methods:
            yield from scale_until_timeout(
                runner, method, filename, command_num, sig_num, scopes=scopes, timeout_s=timeout_s, cpu_time=cpu_time)
