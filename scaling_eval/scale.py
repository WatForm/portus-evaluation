import logging
from pathlib import Path

from scaling_eval import run


def base_filename(filename):
    return Path(filename).parts[-1]


def format_result(result: run.CommandResult) -> str:
    if result.timeout:
        return "timeout"
    elif result.stats is None:
        return "error getting stats"
    else:
        return f"{result.stats.cpu_time_s:.2f}s"


def scale_until_timeout(runner: run.Runner, filename, command_num, sig_num, scopes=range(1, 21), timeout_s=60):
    """Run portus and kodkod, setting sig_num's scope to each value from 1 to max_scope inclusive,
    stopping if either portus or kodkod timeout.
    """
    for scope in scopes:
        portus_result, kodkod_result = runner.eval_portus_kodkod(
            filename,
            command_num=command_num,
            sig_scope=(sig_num, scope),
            timeout_s=timeout_s,
        )
        sat_result = portus_result.sat_result if not portus_result.timeout else kodkod_result.sat_result
        logging.info(
            f"{base_filename(filename)}[cmd {command_num}], sig {sig_num} @ scope {scope} ({sat_result.name}): "
            f"portus={format_result(portus_result)}, kodkod={format_result(kodkod_result)}"
        )
        yield filename, command_num, sig_num, scope, portus_result, kodkod_result
        if portus_result.timeout or kodkod_result.timeout:
            break


def scale_all_sigs(runner: run.Runner, filename, command_num, scopes=range(1, 21), timeout_s=60):
    num_sigs = runner.get_num_sigs(filename)
    logging.info(f"Scaling all sigs in: {base_filename(filename)}[cmd {command_num}]; {num_sigs} sigs total")
    for sig_num in range(1, num_sigs+1):
        yield from scale_until_timeout(
            runner, filename, command_num, sig_num, scopes=scopes, timeout_s=timeout_s)
