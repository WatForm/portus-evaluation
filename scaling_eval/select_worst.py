"""
Given a CSV file produced by scaling_eval, for each (model, command) pair, find the
worst-performing sig as measured by highest scope achieved before timeout (among any method)
and output to another CSV file with columns (model, command, sig).
"""

from collections import defaultdict
import csv
import random
import sys

# specific seed for reproducibility
random.seed(1)

if len(sys.argv) <= 2:
    print("Usage: select_worst.py <scale_csv_filename> <output_csv_filename>")
    sys.exit(-1)

scale_csv_filename = sys.argv[1]
output_csv_filename = sys.argv[2]

# For each (model, command), map sig -> list of scopes achieved
command_to_sig_to_scopes = defaultdict(lambda: defaultdict(list))
with open(scale_csv_filename, "r") as scale_csv:
    reader = csv.reader(scale_csv)
    next(reader) # skip header
    for method, model, command, sig, scope, time in reader:
        if time != "timeout":
            command_to_sig_to_scopes[model, command][int(sig)].append(int(scope))

command_to_worst_sig = {}
for (model, command), sig_to_scopes in command_to_sig_to_scopes.items():
    sig_to_max_scope = {
        sig: max(scopes, default=-1)
        for sig, scopes in sig_to_scopes.items()
    }
    worst_max_scope = min(sig_to_max_scope.values())
    worst_sigs = [sig for sig, max_scope in sig_to_max_scope.items() if max_scope == worst_max_scope]
    # randomly break any ties
    worst_sig = random.choice(worst_sigs)
    command_to_worst_sig[model, command] = worst_sig

with open(output_csv_filename, "w") as output_csv:
    writer = csv.writer(output_csv)
    writer.writerow(["model", "command_number", "sig_number"])
    for (model, command), sig in sorted(command_to_worst_sig.items()):
        writer.writerow([model, command, sig])
