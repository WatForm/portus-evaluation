import argparse
from collections import defaultdict
import csv
from pathlib import Path

import matplotlib.pyplot as plt
from tqdm import tqdm


FIGS_PATH = "figs"


def parse_results(results_path):
    results = defaultdict(list)
    with open(results_path, "r") as csv_file:
        reader = csv.reader(csv_file)
        next(reader) # skip header
        for model, command, sig, scope, portus, kodkod in reader:
            results[(model, int(command), int(sig))].append({
                "scope": int(scope),
                "portus": float(portus) if portus != "timeout" else portus,
                "kodkod": float(kodkod) if kodkod != "timeout" else kodkod,
            })
    return results


def plot(result, title, path, timeout=60):
    scopes = [res["scope"] for res in result]
    portus = [res["portus"] if res["portus"] != "timeout" else timeout for res in result]
    kodkod = [res["kodkod"] if res["kodkod"] != "timeout" else timeout for res in result]
    plt.plot(scopes, portus, label="portus")
    plt.plot(scopes, kodkod, label="kodkod")
    if result[-1]["portus"] == "timeout" or result[-1]["kodkod"] == "timeout":
        plt.plot(scopes[-1], timeout, "rx", label="timeout")
    plt.title(title)
    plt.legend(loc="upper left")
    plt.xlabel("Scope")
    plt.ylabel("Solving time (s)")
    plt.yscale("log")
    plt.savefig(path)
    plt.clf()


def make_title_and_path(model_path, command, sig):
    model = Path(model_path).name
    title = f"{model}, cmd {command}, sig {sig}"
    path = Path(FIGS_PATH) / f"{model}-cmd{command}-sig{sig}.png"
    return title, str(path)


def main():
    parser = argparse.ArgumentParser(prog="make_graphs", description="Make graphs from scaling_eval CSV output")
    parser.add_argument("path", help="Path to the results CSV")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout used when running scaling_eval")
    args = parser.parse_args()

    # ensure figs dir exists
    figs_path = Path(FIGS_PATH)
    figs_path.mkdir(parents=True, exist_ok=True)
    print(f"Outputting figures to {figs_path.absolute()}.")

    results = parse_results(args.path)
    print(f"Loaded {len(results)} results.")

    for (model, command, sig), result in tqdm(results.items()):
        title, path = make_title_and_path(model, command, sig)
        plot(result, title, path, timeout=args.timeout)


if __name__ == "__main__":
    main()
