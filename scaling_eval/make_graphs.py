import argparse
from collections import defaultdict
import csv
from pathlib import Path

import matplotlib.pyplot as plt
from tqdm import tqdm


FIGS_PATH = "figs"


def parse_results(results_paths):
    results = defaultdict(lambda: defaultdict(list)) # (model, command, sig) -> method -> list[(scope, time)]
    for result_path in results_paths:
        with open(result_path, "r") as csv_file:
            reader = csv.reader(csv_file)
            next(reader) # skip header
            for method, model, command, sig, scope, time in reader:
                results[model, int(command), int(sig)][method].append({
                    "scope": int(scope),
                    "time": float(time) if time != "timeout" else time,
                })
    return results


def plot(method_to_results, title, path, timeout=60):
    portus_scopes = [res["scope"] for res in method_to_results["portus-full"]]
    portus_times = [res["time"] if res["time"] != "timeout" else timeout for res in method_to_results["portus-full"]]
    kodkod_scopes = [res["scope"] for res in method_to_results["kodkod"]]
    kodkod_times = [res["time"] if res["time"] != "timeout" else timeout for res in method_to_results["kodkod"]]
    plt.plot(portus_scopes, portus_times, label="portus")
    plt.plot(kodkod_scopes, kodkod_times, label="kodkod")
    if portus_times[-1] == "timeout":
        plt.plot(portus_scopes[-1], timeout, "rx", label="timeout")
    if kodkod_times[-1] == "timeout":
        plt.plot(kodkod_scopes[-1], timeout, "rx", label="timeout")
    plt.title(title)
    plt.legend(loc="upper left")
    plt.xlabel("Scope")
    plt.ylabel("Solving time (s)")
    plt.yscale("log")
    # plt.hlines(timeout, *plt.xlim(), linestyle="--", linewidth=1.0, color="black")
    # plt.ylim(top=timeout * 1.1)
    plt.savefig(path)
    plt.clf()


def make_title_and_path(model_path, command, sig):
    model = Path(model_path).name
    title = f"{model}, cmd {command}, sig {sig}"
    path = Path(FIGS_PATH) / f"{model}-cmd{command}-sig{sig}.png"
    return title, str(path)


def main():
    parser = argparse.ArgumentParser(prog="make_graphs", description="Make graphs from scaling_eval CSV output")
    parser.add_argument("paths", nargs="+", help="Paths to the results CSVs")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout used when running scaling_eval")
    args = parser.parse_args()

    # ensure figs dir exists
    figs_path = Path(FIGS_PATH)
    figs_path.mkdir(parents=True, exist_ok=True)
    print(f"Outputting figures to {figs_path.absolute()}.")

    results = parse_results(args.paths)
    print(f"Loaded {len(results)} results.")

    for (model, command, sig), method_to_results in tqdm(results.items()):
        if "kodkod" in method_to_results and "portus-full" in method_to_results:
            title, path = make_title_and_path(model, command, sig)
            plot(method_to_results, title, path, timeout=args.timeout)


if __name__ == "__main__":
    main()
