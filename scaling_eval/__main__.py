import argparse
import csv
import logging

from scaling_eval import run
from scaling_eval.scale import scale_all_sigs
from setup_scripts.config import ALLOY_JAR, PORTUS_JAR


def read_models(models_filename):
    with open(models_filename, "r") as models_file:
        reader = csv.reader(models_file)
        next(reader) # skip header
        for model_filename, command_num in reader:
            yield model_filename, int(command_num)


def scale_all_models(runner: run.Runner, models_filename, scopes=range(1, 21), timeout_s=60, cpu_time=True):
    for filename, command_num in read_models(models_filename):
        yield from scale_all_sigs(
            runner, filename, command_num, scopes=scopes, timeout_s=timeout_s, cpu_time=cpu_time)


def write_results_to_csv(csv_filename, scale_iter):
    with open(csv_filename, "w") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(["model", "command", "sig", "scope", "portus", "kodkod"])
        for row in scale_iter:
            writer.writerow(row)
            output_file.flush()


def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(prog="scaling_eval", description="Evaluate Portus signature scope scaling.")
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
    parser.add_argument("--cpu-time", type=bool, default=True, help="CPU time or wall-clock time.")
    args = parser.parse_args()

    base_command = f"{args.java} -Xss{args.stack} -Xmx{args.memory} -Xms{args.memory} -cp {args.jar} {PORTUS_JAR} -nt"
    runner = run.Runner(base_command)

    scopes = range(args.start, args.end+1, args.step)
    scale_iter = scale_all_models(runner, args.models, scopes, timeout_s=args.timeout, cpu_time=args.cpu_time)
    write_results_to_csv(args.out, scale_iter)


if __name__ == "__main__":
    main()
