import csv
from collections import defaultdict


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
