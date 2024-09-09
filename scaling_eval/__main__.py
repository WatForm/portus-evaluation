import argparse
import csv
import logging
import os
import sys

from scaling_eval import run
from scaling_eval.scale import scale_all_sigs, scale_sig
from setup_scripts.config import ALLOY_JAR, PORTUS_JAR, models_dir

from eval_portus import PORTUS_METHODS


def read_models(models_filename, specify_sigs=False):
    with open(models_filename, "r") as models_file:
        reader = csv.reader(models_file)
        next(reader) # skip header
        if specify_sigs:
            for model_filename, command_num, sig_num in reader:
                yield model_filename, int(command_num), int(sig_num)
        else:
            for model_filename, command_num in reader:
                yield model_filename, int(command_num)


def scale_all_models(
        runner: run.Runner, methods, models_filename, scopes=range(1, 21), timeout_s=60, cpu_time=True, specify_sigs=False):
    if specify_sigs:
        for filename, command_num, sig_num in read_models(models_filename, specify_sigs=True):
            yield from scale_sig(
                runner, methods, filename, command_num, sig_num, scopes=scopes, timeout_s=timeout_s, cpu_time=cpu_time)
    else:
        for filename, command_num in read_models(models_filename, specify_sigs=False):
            yield from scale_all_sigs(
                runner, methods, filename, command_num, scopes=scopes, timeout_s=timeout_s, cpu_time=cpu_time)


def write_results_to_csv(csv_filename, scale_iter):
    with open(csv_filename, "w") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(["method", "model", "command", "sig", "scope", "time"])
        for row in scale_iter:
            writer.writerow(row)
            output_file.flush()


def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(prog="scaling_eval", description="Evaluate Portus signature scope scaling.")
    parser.add_argument("--methods", default=["portus-full", "kodkod"], nargs="+", help="Methods to run with.", choices=PORTUS_METHODS)
    parser.add_argument("--java", default="java", help="The Java command to run Alloy with.")
    parser.add_argument("--alloy-jar", default=str(ALLOY_JAR.absolute()), help="Path to the Portus jar.")
    parser.add_argument('--corpus-root',
                        default=os.path.dirname(os.path.abspath(models_dir)),  # Remove top-level folder name
                        help="Base path for model filenames in models-supported-command.txt.")
    parser.add_argument("--models", default="models-supported-command.txt", help="Path to models-supported-command.txt.")
    parser.add_argument("--sigs", default="all", choices=["all", "specified"],
        help="Run all sigs (all) or specified in the models csv (specified).")
    parser.add_argument("--out", default="scale.csv", help="Output CSV filename.")
    parser.add_argument("--start", type=int, default=1, help="Starting scope of a model to try.")
    parser.add_argument("--end", type=int, default=30, help="Maximum scope of a model to try.")
    parser.add_argument("--step", type=int, default=1, help="Step of scopes to try.")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout for both Portus and Kodkod (secs).")
    parser.add_argument("--repeat", type=int, default=3, help="Number of times to repeat each run (output is average time).")
    parser.add_argument("--memory", default="30g", help="Amount of memory for Java to allocate using -Xmx and -Xms.")
    parser.add_argument("--stack", default="1g", help="Amount of stack for Java to allocation using -Xss.")
    parser.add_argument("--cpu-time", type=str, default="false", help="CPU time (true) or wall-clock time (false).")
    args = parser.parse_args()

    base_command = f"{args.java} -Xss{args.stack} -Xmx{args.memory} -Xms{args.memory} -cp {args.alloy_jar} {PORTUS_JAR} -nt"
    runner = run.Runner(base_command, args.corpus_root, args.repeat)

    print(f"Base command: {base_command}")
    print(f"Timeout: {args.timeout} secs")
    print(f"Args: {args}")
    sys.stdout.flush()

    scopes = range(args.start, args.end+1, args.step)
    cpu_time = args.cpu_time == "true"
    specify_sigs = args.sigs == "specified"
    scale_iter = scale_all_models(
        runner, args.methods, args.models, scopes, timeout_s=args.timeout, cpu_time=cpu_time, specify_sigs=specify_sigs)
    write_results_to_csv(args.out, scale_iter)


if __name__ == "__main__":
    main()
