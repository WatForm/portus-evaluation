import argparse
import csv
import logging
import sys
from typing import Optional

from scaling_eval import run
from scaling_eval.scale import scale_all_sigs
from setup_scripts.config import ALLOY_JAR, PORTUS_JAR
from testrunner.util import Satisfiablity


def read_models(models_filename):
    with open(models_filename, "r") as models_file:
        reader = csv.reader(models_file)
        next(reader) # skip header
        for model_filename, command_num in reader:
            yield model_filename, int(command_num)


def scale_all_models(runner: run.Runner, models_filename, scopes=range(1, 21), timeout_s=60):
    for filename, command_num in read_models(models_filename):
        yield from scale_all_sigs(
            runner, filename, command_num, scopes=scopes, timeout_s=timeout_s)


def write_results_to_csv(csv_filename, scale_iter):
    headings = [
        "model", "command", "sig", "scope",
        "correctness",
        "portus.timeout",
        "portus.sat_result",
        "portus.retcode",
        "portus.stats_ok",
        "portus.wall_clock_time_s",
        "portus.user_time_s",
        "portus.sys_time_s",
        "portus.cpu_time_s",
        "portus.peak_rss_kb",
        "portus.avg_rss_kb",
        "portus.avg_total_mem_kb",
        "portus.num_page_faults",
        "portus.num_minor_page_faults",
        "kodkod.timeout",
        "kodkod.sat_result",
        "kodkod.retcode",
        "kodkod.stats_ok",
        "kodkod.wall_clock_time_s",
        "kodkod.user_time_s",
        "kodkod.sys_time_s",
        "kodkod.cpu_time_s",
        "kodkod.peak_rss_kb",
        "kodkod.avg_rss_kb",
        "kodkod.avg_total_mem_kb",
        "kodkod.num_page_faults",
        "kodkod.num_minor_page_faults",
    ]

    def make_stats_dict(prefix: str, stats: Optional[run.CommandStats]) -> dict:
        if stats is None:
            return {}
        return {
            f"{prefix}.wall_clock_time_s": stats.wall_clock_time_s,
            f"{prefix}.user_time_s": stats.user_time_s,
            f"{prefix}.sys_time_s": stats.sys_time_s,
            f"{prefix}.cpu_time_s": stats.cpu_time_s,
            f"{prefix}.peak_rss_kb": stats.peak_rss_kb,
            f"{prefix}.avg_rss_kb": stats.avg_rss_kb,
            f"{prefix}.avg_total_mem_kb": stats.avg_total_mem_kb,
            f"{prefix}.num_page_faults": stats.num_page_faults,
            f"{prefix}.num_minor_page_faults": stats.num_minor_page_faults,
        }

    def make_result_dict(prefix: str, result: run.CommandResult) -> dict:
        return {
            f"{prefix}.timeout": result.timeout,
            f"{prefix}.sat_result": result.sat_result,
            f"{prefix}.retcode": result.retcode,
            f"{prefix}.stats_ok": result.stats is not None,
            **make_stats_dict(prefix, result.stats),
        }

    with open(csv_filename, "w") as output_file:
        writer = csv.DictWriter(output_file, headings)
        writer.writeheader()
        for filename, command_num, sig_num, scope, portus, kodkod in scale_iter:
            writer.writerow({
                "model": filename,
                "command": command_num,
                "sig": sig_num,
                "scope": scope,
                "correctness": (
                    portus.sat_result == kodkod.sat_result
                    and portus.sat_result in (Satisfiablity.SAT, Satisfiablity.UNSAT)
                ),
                **make_result_dict("portus", portus),
                **make_result_dict("kodkod", kodkod),
            })
            output_file.flush()


def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(prog="scaling_eval", description="Evaluate Portus signature scope scaling.")
    parser.add_argument("--gnu-time", default="/usr/bin/time", help="Path to GNU time executable.")
    parser.add_argument("--gnu-timeout", default="timeout", help="Path to GNU coreutils timeout executable.")
    parser.add_argument("--java", default="java", help="The Java command to run Alloy with.")
    parser.add_argument("--jar", default=str(ALLOY_JAR.absolute()), help="Path to the Portus jar.")
    parser.add_argument("--models", default="models-supported-command.txt", help="Path to models-supported-command.txt.")
    parser.add_argument("--out", default="scale.csv", help="Output CSV filename.")
    parser.add_argument("--start", type=int, default=1, help="Starting scope of a model to try.")
    parser.add_argument("--end", type=int, default=30, help="Maximum scope of a model to try.")
    parser.add_argument("--step", type=int, default=1, help="Step of scopes to try.")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout for both Portus and Kodkod (secs).")
    parser.add_argument("--memory", default="30g", help="Amount of memory for Java to allocate using -Xmx and -Xms.")
    parser.add_argument("--stack", default="1g", help="Amount of stack for Java to allocation using -Xss.")
    args = parser.parse_args()

    base_command = f"{args.java} -Xss{args.stack} -Xmx{args.memory} -Xms{args.memory} -cp {args.jar} {PORTUS_JAR} -nt"
    runner = run.Runner(base_command, args.gnu_time, args.gnu_timeout)

    print(f"Base command: {base_command}")
    print(f"Timeout: {args.timeout} secs")
    print(f"Args: {args}")
    sys.stdout.flush()

    scopes = range(args.start, args.end+1, args.step)
    scale_iter = scale_all_models(runner, args.models, scopes, timeout_s=args.timeout)
    write_results_to_csv(args.out, scale_iter)


if __name__ == "__main__":
    main()
